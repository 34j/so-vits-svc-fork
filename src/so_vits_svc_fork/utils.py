from __future__ import annotations

import json
import os
import re
import subprocess
import warnings
from itertools import groupby
from logging import getLogger
from pathlib import Path
from typing import Any, Literal, Sequence

import matplotlib
import matplotlib.pylab as plt
import numpy as np
import requests
import torch
import torch.backends.mps
import torch.nn as nn
import torchaudio
from cm_time import timer
from numpy import ndarray
from tqdm import tqdm
from transformers import HubertModel

from so_vits_svc_fork.hparams import HParams

LOG = getLogger(__name__)
HUBERT_SAMPLING_RATE = 16000
IS_COLAB = os.getenv("COLAB_RELEASE_TAG", False)


def get_optimal_device(index: int = 0) -> torch.device:
    if torch.cuda.is_available():
        return torch.device(f"cuda:{index % torch.cuda.device_count()}")
    elif torch.backends.mps.is_available():
        return torch.device("mps")
    else:
        try:
            import torch_xla.core.xla_model as xm  # noqa

            if xm.xrt_world_size() > 0:
                return torch.device("xla")
            # return xm.xla_device()
        except ImportError:
            pass
    return torch.device("cpu")


def download_file(
    url: str,
    filepath: Path | str,
    chunk_size: int = 64 * 1024,
    tqdm_cls: type = tqdm,
    skip_if_exists: bool = False,
    overwrite: bool = False,
    **tqdm_kwargs: Any,
):
    if skip_if_exists is True and overwrite is True:
        raise ValueError("skip_if_exists and overwrite cannot be both True")
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    temppath = filepath.parent / f"{filepath.name}.download"
    if filepath.exists():
        if skip_if_exists:
            return
        elif not overwrite:
            filepath.unlink()
        else:
            raise FileExistsError(f"{filepath} already exists")
    temppath.unlink(missing_ok=True)
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get("content-length", 0))
    kwargs = dict(
        total=total,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
        desc=f"Downloading {filepath.name}",
    )
    kwargs.update(tqdm_kwargs)
    with temppath.open("wb") as f, tqdm_cls(**kwargs) as pbar:
        for data in resp.iter_content(chunk_size=chunk_size):
            size = f.write(data)
            pbar.update(size)
    temppath.rename(filepath)


PRETRAINED_MODEL_URLS = {
    "hifi-gan": [
        [
            "https://huggingface.co/therealvul/so-vits-svc-4.0-init/resolve/main/D_0.pth",
            "https://huggingface.co/therealvul/so-vits-svc-4.0-init/resolve/main/G_0.pth",
        ],
        [
            "https://huggingface.co/Himawari00/so-vits-svc4.0-pretrain-models/resolve/main/D_0.pth",
            "https://huggingface.co/Himawari00/so-vits-svc4.0-pretrain-models/resolve/main/G_0.pth",
        ],
    ],
    "contentvec": [
        [
            "https://huggingface.co/therealvul/so-vits-svc-4.0-init/resolve/main/checkpoint_best_legacy_500.pt"
        ],
        [
            "https://huggingface.co/Himawari00/so-vits-svc4.0-pretrain-models/resolve/main/checkpoint_best_legacy_500.pt"
        ],
        [
            "http://obs.cstcloud.cn/share/obs/sankagenkeshi/checkpoint_best_legacy_500.pt"
        ],
    ],
}
from joblib import Parallel, delayed


def ensure_pretrained_model(
    folder_path: Path | str, type_: str | dict[str, str], **tqdm_kwargs: Any
) -> tuple[Path, ...] | None:
    folder_path = Path(folder_path)

    # new code
    if not isinstance(type_, str):
        try:
            Parallel(n_jobs=len(type_))(
                [
                    delayed(download_file)(
                        url,
                        folder_path / filename,
                        position=i,
                        skip_if_exists=True,
                        **tqdm_kwargs,
                    )
                    for i, (filename, url) in enumerate(type_.items())
                ]
            )
            return tuple(folder_path / filename for filename in type_.values())
        except Exception as e:
            LOG.error(f"Failed to download {type_}")
            LOG.exception(e)

    # old code
    models_candidates = PRETRAINED_MODEL_URLS.get(type_, None)
    if models_candidates is None:
        LOG.warning(f"Unknown pretrained model type: {type_}")
        return
    for model_urls in models_candidates:
        paths = [folder_path / model_url.split("/")[-1] for model_url in model_urls]
        try:
            Parallel(n_jobs=len(paths))(
                [
                    delayed(download_file)(
                        url, path, position=i, skip_if_exists=True, **tqdm_kwargs
                    )
                    for i, (url, path) in enumerate(zip(model_urls, paths))
                ]
            )
            return tuple(paths)
        except Exception as e:
            LOG.error(f"Failed to download {model_urls}")
            LOG.exception(e)


class HubertModelWithFinalProj(HubertModel):
    def __init__(self, config):
        super().__init__(config)

        # The final projection layer is only used for backward compatibility.
        # Following https://github.com/auspicious3000/contentvec/issues/6
        # Remove this layer is necessary to achieve the desired outcome.
        self.final_proj = nn.Linear(config.hidden_size, config.classifier_proj_size)


def remove_weight_norm_if_exists(module, name: str = "weight"):
    r"""Removes the weight normalization reparameterization from a module.

    Args:
        module (Module): containing module
        name (str, optional): name of weight parameter

    Example:
        >>> m = weight_norm(nn.Linear(20, 40))
        >>> remove_weight_norm(m)
    """
    from torch.nn.utils.weight_norm import WeightNorm

    for k, hook in module._forward_pre_hooks.items():
        if isinstance(hook, WeightNorm) and hook.name == name:
            hook.remove(module)
            del module._forward_pre_hooks[k]
            return module


def get_hubert_model(
    device: str | torch.device, final_proj: bool = True
) -> HubertModel:
    if final_proj:
        model = HubertModelWithFinalProj.from_pretrained("lengyue233/content-vec-best")
    else:
        model = HubertModel.from_pretrained("lengyue233/content-vec-best")
    # Hubert is always used in inference mode, we can safely remove weight-norms
    for m in model.modules():
        if isinstance(m, (nn.Conv2d, nn.Conv1d)):
            remove_weight_norm_if_exists(m)

    return model.to(device)


def get_content(
    cmodel: HubertModel,
    audio: torch.Tensor | ndarray[Any, Any],
    device: torch.device | str,
    sr: int,
    legacy_final_proj: bool = False,
) -> torch.Tensor:
    audio = torch.as_tensor(audio)
    if sr != HUBERT_SAMPLING_RATE:
        audio = (
            torchaudio.transforms.Resample(sr, HUBERT_SAMPLING_RATE)
            .to(audio.device)(audio)
            .to(device)
        )
    if audio.ndim == 1:
        audio = audio.unsqueeze(0)
    with torch.no_grad(), timer() as t:
        if legacy_final_proj:
            warnings.warn("legacy_final_proj is deprecated")
            if not hasattr(cmodel, "final_proj"):
                raise ValueError("HubertModel does not have final_proj")
            c = cmodel(audio, output_hidden_states=True)["hidden_states"][9]
            c = cmodel.final_proj(c)
        else:
            c = cmodel(audio)["last_hidden_state"]
        c = c.transpose(1, 2)
    wav_len = audio.shape[-1] / HUBERT_SAMPLING_RATE
    LOG.info(
        f"HuBERT inference time  : {t.elapsed:.3f}s, RTF: {t.elapsed / wav_len:.3f}"
    )
    return c


def _substitute_if_same_shape(to_: dict[str, Any], from_: dict[str, Any]) -> None:
    not_in_to = list(filter(lambda x: x not in to_, from_.keys()))
    not_in_from = list(filter(lambda x: x not in from_, to_.keys()))
    if not_in_to:
        warnings.warn(f"Keys not found in model state dict:" f"{not_in_to}")
    if not_in_from:
        warnings.warn(f"Keys not found in checkpoint state dict:" f"{not_in_from}")
    shape_missmatch = []
    for k, v in from_.items():
        if k not in to_:
            pass
        elif hasattr(v, "shape"):
            if not hasattr(to_[k], "shape"):
                raise ValueError(f"Key {k} is not a tensor")
            if to_[k].shape == v.shape:
                to_[k] = v
            else:
                shape_missmatch.append((k, to_[k].shape, v.shape))
        elif isinstance(v, dict):
            assert isinstance(to_[k], dict)
            _substitute_if_same_shape(to_[k], v)
        else:
            to_[k] = v
    if shape_missmatch:
        warnings.warn(
            f"Shape mismatch: {[f'{k}: {v1} -> {v2}' for k, v1, v2 in shape_missmatch]}"
        )


def safe_load(model: torch.nn.Module, state_dict: dict[str, Any]) -> None:
    model_state_dict = model.state_dict()
    _substitute_if_same_shape(model_state_dict, state_dict)
    model.load_state_dict(model_state_dict)


def load_checkpoint(
    checkpoint_path: Path | str,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    skip_optimizer: bool = False,
) -> tuple[torch.nn.Module, torch.optim.Optimizer | None, float, int]:
    if not Path(checkpoint_path).is_file():
        raise FileNotFoundError(f"File {checkpoint_path} not found")
    with Path(checkpoint_path).open("rb") as f:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore", category=UserWarning, message="TypedStorage is deprecated"
            )
            checkpoint_dict = torch.load(f, map_location="cpu", weights_only=True)
    iteration = checkpoint_dict["iteration"]
    learning_rate = checkpoint_dict["learning_rate"]

    # safe load module
    if hasattr(model, "module"):
        safe_load(model.module, checkpoint_dict["model"])
    else:
        safe_load(model, checkpoint_dict["model"])
    # safe load optim
    if (
        optimizer is not None
        and not skip_optimizer
        and checkpoint_dict["optimizer"] is not None
    ):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            safe_load(optimizer, checkpoint_dict["optimizer"])

    LOG.info(f"Loaded checkpoint '{checkpoint_path}' (epoch {iteration})")
    return model, optimizer, learning_rate, iteration


def save_checkpoint(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    learning_rate: float,
    iteration: int,
    checkpoint_path: Path | str,
) -> None:
    model = model.to("cpu")
    LOG.info(
        "Saving model and optimizer state at epoch {} to {}".format(
            iteration, checkpoint_path
        )
    )
    if hasattr(model, "module"):
        state_dict = model.module.state_dict()
    else:
        state_dict = model.state_dict()
    with Path(checkpoint_path).open("wb") as f:
        torch.save(
            {
                "model": state_dict,
                "iteration": iteration,
                "optimizer": optimizer.state_dict(),
                "learning_rate": learning_rate,
            },
            f,
        )


def clean_checkpoints(
    path_to_models: Path | str, n_ckpts_to_keep: int = 2, sort_by_time: bool = True
) -> None:
    """Freeing up space by deleting saved ckpts

    Arguments:
    path_to_models    --  Path to the model directory
    n_ckpts_to_keep   --  Number of ckpts to keep, excluding G_0.pth and D_0.pth
    sort_by_time      --  True -> chronologically delete ckpts
                          False -> lexicographically delete ckpts
    """
    LOG.info("Cleaning old checkpoints...")
    path_to_models = Path(path_to_models)

    # Define sort key functions
    name_key = lambda p: int(re.match(r"[GD]_(\d+)", p.stem).group(1))
    time_key = lambda p: p.stat().st_mtime
    path_key = lambda p: (p.stem[0], time_key(p) if sort_by_time else name_key(p))

    models = list(
        filter(
            lambda p: (
                p.is_file()
                and re.match(r"[GD]_\d+", p.stem)
                and not p.stem.endswith("_0")
            ),
            path_to_models.glob("*.pth"),
        )
    )

    models_sorted = sorted(models, key=path_key)

    models_sorted_grouped = groupby(models_sorted, lambda p: p.stem[0])

    for group_name, group_items in models_sorted_grouped:
        to_delete_list = list(group_items)[:-n_ckpts_to_keep]

        for to_delete in to_delete_list:
            if to_delete.exists():
                LOG.info(f"Removing {to_delete}")
                if IS_COLAB:
                    to_delete.write_text("")
                to_delete.unlink()


def latest_checkpoint_path(dir_path: Path | str, regex: str = "G_*.pth") -> Path | None:
    dir_path = Path(dir_path)
    name_key = lambda p: int(re.match(r"._(\d+)\.pth", p.name).group(1))
    paths = list(sorted(dir_path.glob(regex), key=name_key))
    if len(paths) == 0:
        return None
    return paths[-1]


def plot_spectrogram_to_numpy(spectrogram: ndarray) -> ndarray:
    matplotlib.use("Agg")
    fig, ax = plt.subplots(figsize=(10, 2))
    im = ax.imshow(spectrogram, aspect="auto", origin="lower", interpolation="none")
    plt.colorbar(im, ax=ax)
    plt.xlabel("Frames")
    plt.ylabel("Channels")
    plt.tight_layout()

    fig.canvas.draw()
    data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep="")
    data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    plt.close()
    return data


def get_backup_hparams(
    config_path: Path, model_path: Path, init: bool = True
) -> HParams:
    model_path.mkdir(parents=True, exist_ok=True)
    config_save_path = model_path / "config.json"
    if init:
        with config_path.open() as f:
            data = f.read()
        with config_save_path.open("w") as f:
            f.write(data)
    else:
        with config_save_path.open() as f:
            data = f.read()
    config = json.loads(data)

    hparams = HParams(**config)
    hparams.model_dir = model_path.as_posix()
    return hparams


def get_hparams(config_path: Path | str) -> HParams:
    config = json.loads(Path(config_path).read_text("utf-8"))
    hparams = HParams(**config)
    return hparams


def repeat_expand_2d(content: torch.Tensor, target_len: int) -> torch.Tensor:
    # content : [h, t]
    src_len = content.shape[-1]
    if target_len < src_len:
        return content[:, :target_len]
    else:
        return torch.nn.functional.interpolate(
            content.unsqueeze(0), size=target_len, mode="nearest"
        ).squeeze(0)


def plot_data_to_numpy(x: ndarray, y: ndarray) -> ndarray:
    matplotlib.use("Agg")
    fig, ax = plt.subplots(figsize=(10, 2))
    plt.plot(x)
    plt.plot(y)
    plt.tight_layout()

    fig.canvas.draw()
    data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep="")
    data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    plt.close()
    return data


def get_gpu_memory(type_: Literal["total", "free", "used"]) -> Sequence[int] | None:
    command = f"nvidia-smi --query-gpu=memory.{type_} --format=csv"
    try:
        memory_free_info = (
            subprocess.check_output(command.split())
            .decode("ascii")
            .split("\n")[:-1][1:]
        )
        memory_free_values = [int(x.split()[0]) for i, x in enumerate(memory_free_info)]
        return memory_free_values
    except Exception:
        return


def get_total_gpu_memory(type_: Literal["total", "free", "used"]) -> int | None:
    memories = get_gpu_memory(type_)
    if memories is None:
        return
    return sum(memories)
