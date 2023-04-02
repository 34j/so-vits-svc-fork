from __future__ import annotations

import json
import re
from itertools import groupby
from logging import getLogger
from pathlib import Path
from typing import Any

import matplotlib
import matplotlib.pylab as plt
import numpy as np
import requests
import torch
from cm_time import timer
from fairseq import checkpoint_utils
from fairseq.models.hubert.hubert import HubertModel
from numpy import ndarray
from scipy.io.wavfile import read
from tqdm import tqdm

from so_vits_svc_fork.hparams import HParams

LOG = getLogger(__name__)
HUBERT_SAMPLING_RATE = 16000


def download_file(
    url: str,
    filepath: Path | str,
    chunk_size: int = 4 * 1024,
    tqdm_cls: type = tqdm,
    **tqdm_kwargs: Any,
):
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    temppath = filepath.parent / f"{filepath.name}.download"
    if filepath.exists():
        raise FileExistsError(f"{filepath} already exists")
    temppath.unlink(missing_ok=True)
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get("content-length", 0))
    with temppath.open("wb") as f, tqdm_cls(
        total=total,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
        **tqdm_kwargs,
    ) as pbar:
        for data in resp.iter_content(chunk_size=chunk_size):
            size = f.write(data)
            pbar.update(size)
    temppath.rename(filepath)


def ensure_pretrained_model(folder_path: Path, **tqdm_kwargs: Any) -> None:
    model_urls = [
        # "https://huggingface.co/innnky/sovits_pretrained/resolve/main/sovits4/G_0.pth",
        "https://huggingface.co/therealvul/so-vits-svc-4.0-init/resolve/main/D_0.pth",
        # "https://huggingface.co/innnky/sovits_pretrained/resolve/main/sovits4/D_0.pth",
        "https://huggingface.co/therealvul/so-vits-svc-4.0-init/resolve/main/G_0.pth",
    ]
    for model_url in model_urls:
        model_path = folder_path / model_url.split("/")[-1]
        if not model_path.exists():
            download_file(
                model_url,
                model_path,
                desc=f"Downloading {model_path.name}",
                **tqdm_kwargs,
            )


def ensure_hubert_model(**tqdm_kwargs: Any) -> Path:
    vec_path = Path("checkpoint_best_legacy_500.pt")
    vec_path.parent.mkdir(parents=True, exist_ok=True)
    if not vec_path.exists():
        # url = "http://obs.cstcloud.cn/share/obs/sankagenkeshi/checkpoint_best_legacy_500.pt"
        # url = "https://huggingface.co/innnky/contentvec/resolve/main/checkpoint_best_legacy_500.pt"
        url = "https://huggingface.co/therealvul/so-vits-svc-4.0-init/resolve/main/checkpoint_best_legacy_500.pt"
        download_file(url, vec_path, desc="Downloading Hubert model", **tqdm_kwargs)
    return vec_path


def get_hubert_model() -> HubertModel:
    vec_path = ensure_hubert_model()

    models, saved_cfg, task = checkpoint_utils.load_model_ensemble_and_task(
        [vec_path.as_posix()],
        suffix="",
    )
    model = models[0]
    model.eval()
    return model


def get_content(
    cmodel: HubertModel, audio: torch.Tensor, wrong_legacy_proj: bool = False
) -> ndarray:
    with torch.no_grad(), timer() as t:
        c = cmodel.extract_features(
            audio.squeeze(1),
            padding_mask=torch.BoolTensor(audio.shape).fill_(False),
            output_layer=9,
        )
        if wrong_legacy_proj:
            assert hasattr(cmodel, "final_proj")
            c = cmodel.final_proj(c[0])
    c = c.transpose(1, 2)
    wav_len = audio.shape[-1] / 16000
    LOG.info(
        f"HuBERT inference time  : {t.elapsed:.3f}s, RTF: {t.elapsed / wav_len:.3f}"
    )
    return c


def load_checkpoint(
    checkpoint_path: Path | str,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    skip_optimizer: bool = False,
) -> tuple[torch.nn.Module, torch.optim.Optimizer | None, float, int]:
    if not Path(checkpoint_path).is_file():
        raise FileNotFoundError(f"File {checkpoint_path} not found")
    checkpoint_dict = torch.load(checkpoint_path, map_location="cpu")
    iteration = checkpoint_dict["iteration"]
    learning_rate = checkpoint_dict["learning_rate"]
    if (
        optimizer is not None
        and not skip_optimizer
        and checkpoint_dict["optimizer"] is not None
    ):
        optimizer.load_state_dict(checkpoint_dict["optimizer"])
    saved_state_dict = checkpoint_dict["model"]
    if hasattr(model, "module"):
        state_dict = model.module.state_dict()
    else:
        state_dict = model.state_dict()
    new_state_dict = {}
    for k, v in state_dict.items():
        try:
            new_state_dict[k] = saved_state_dict[k]
            assert saved_state_dict[k].shape == v.shape, (
                saved_state_dict[k].shape,
                v.shape,
            )
        except Exception as e:
            LOG.exception(e)
            LOG.error("%s is not in the checkpoint" % k)
            new_state_dict[k] = v
    if hasattr(model, "module"):
        model.module.load_state_dict(new_state_dict)
    else:
        model.load_state_dict(new_state_dict)
    LOG.info(f"Loaded checkpoint '{checkpoint_path}' (iteration {iteration})")
    return model, optimizer, learning_rate, iteration


def save_checkpoint(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    learning_rate: float,
    iteration: int,
    checkpoint_path: Path | str,
) -> None:
    LOG.info(
        "Saving model and optimizer state at iteration {} to {}".format(
            iteration, checkpoint_path
        )
    )
    if hasattr(model, "module"):
        state_dict = model.module.state_dict()
    else:
        state_dict = model.state_dict()
    torch.save(
        {
            "model": state_dict,
            "iteration": iteration,
            "optimizer": optimizer.state_dict(),
            "learning_rate": learning_rate,
        },
        checkpoint_path,
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
            LOG.info(f"Removing {to_delete}")
            to_delete.unlink()


from torch.utils.tensorboard.writer import SummaryWriter


def summarize(
    writer: SummaryWriter,
    global_step: int,
    scalars: dict[str, float] = {},
    histograms: dict[str, ndarray] = {},
    images: dict[str, ndarray] = {},
    audios: dict[str, ndarray] = {},
    audio_sampling_rate: int = 22050,
) -> None:
    for k, v in scalars.items():
        writer.add_scalar(k, v, global_step)
    for k, v in histograms.items():
        writer.add_histogram(k, v, global_step)
    for k, v in images.items():
        writer.add_image(k, v, global_step, dataformats="HWC")
    for k, v in audios.items():
        writer.add_audio(k, v, global_step, audio_sampling_rate)


def latest_checkpoint_path(dir_path: Path | str, regex: str = "G_*.pth") -> Path:
    dir_path = Path(dir_path)
    name_key = lambda p: int(re.match(r"._(\d+)\.pth", p.name).group(1))
    return list(sorted(dir_path.glob(regex), key=name_key))[-1]


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


def load_wav_to_torch(full_path: Path | str) -> tuple[torch.Tensor, int]:
    sampling_rate, data = read(full_path)
    return torch.FloatTensor(data.astype(np.float32)), sampling_rate


def load_filepaths_and_text(filename: Path | str, split="|"):
    with open(filename, encoding="utf-8") as f:
        filepaths_and_text = [line.strip().split(split) for line in f]
    return filepaths_and_text


def get_hparams(config_path: Path, model_path: Path, init: bool = True) -> HParams:
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


def get_hparams_from_file(config_path: Path | str) -> HParams:
    config = json.loads(Path(config_path).read_text())
    hparams = HParams(**config)
    return hparams


def repeat_expand_2d(content: ndarray, target_len: int) -> ndarray:
    # content : [h, t]
    src_len = content.shape[-1]
    target = torch.zeros([content.shape[0], target_len], dtype=torch.float).to(
        content.device
    )
    temp = torch.arange(src_len + 1) * target_len / src_len
    current_pos = 0
    for i in range(target_len):
        if i < temp[current_pos + 1]:
            target[:, i] = content[:, current_pos]
        else:
            current_pos += 1
            target[:, i] = content[:, current_pos]

    return target


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
