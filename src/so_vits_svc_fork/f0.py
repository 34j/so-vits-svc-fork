from __future__ import annotations

from logging import getLogger
from typing import Any, Literal

import numpy as np
import torch
import torchcrepe
from cm_time import timer
from numpy import dtype, float32, ndarray
from torch import FloatTensor, Tensor

from so_vits_svc_fork.utils import get_optimal_device

LOG = getLogger(__name__)


def normalize_f0(
    f0: FloatTensor, x_mask: FloatTensor, uv: FloatTensor, random_scale=True
) -> FloatTensor:
    # calculate means based on x_mask
    uv_sum = torch.sum(uv, dim=1, keepdim=True)
    uv_sum[uv_sum == 0] = 9999
    means = torch.sum(f0[:, 0, :] * uv, dim=1, keepdim=True) / uv_sum

    if random_scale:
        factor = torch.Tensor(f0.shape[0], 1).uniform_(0.8, 1.2).to(f0.device)
    else:
        factor = torch.ones(f0.shape[0], 1).to(f0.device)
    # normalize f0 based on means and factor
    f0_norm = (f0 - means.unsqueeze(-1)) * factor.unsqueeze(-1)
    if torch.isnan(f0_norm).any():
        exit(0)
    return f0_norm * x_mask


def interpolate_f0(
    f0: ndarray[Any, dtype[float32]],
) -> tuple[ndarray[Any, dtype[float32]], ndarray[Any, dtype[float32]]]:
    data = np.reshape(f0, (f0.size, 1))

    vuv_vector = np.zeros((data.size, 1), dtype=np.float32)
    vuv_vector[data > 0.0] = 1.0
    vuv_vector[data <= 0.0] = 0.0

    ip_data = data

    frame_number = data.size
    last_value = 0.0
    for i in range(frame_number):
        if data[i] <= 0.0:
            j = i + 1
            for j in range(i + 1, frame_number):
                if data[j] > 0.0:
                    break
            if j < frame_number - 1:
                if last_value > 0.0:
                    step = (data[j] - data[i - 1]) / float(j - i)
                    for k in range(i, j):
                        ip_data[k] = data[i - 1] + step * (k - i + 1)
                else:
                    for k in range(i, j):
                        ip_data[k] = data[j]
            else:
                for k in range(i, frame_number):
                    ip_data[k] = last_value
        else:
            ip_data[i] = data[i]
            last_value = data[i]

    return ip_data[:, 0], vuv_vector[:, 0]


def compute_f0_parselmouth(
    wav_numpy: ndarray[Any, dtype[float32]],
    p_len: None | int = None,
    sampling_rate: int = 44100,
    hop_length: int = 512,
):
    import parselmouth

    x = wav_numpy
    if p_len is None:
        p_len = x.shape[0] // hop_length
    else:
        assert abs(p_len - x.shape[0] // hop_length) < 4, "pad length error"
    time_step = hop_length / sampling_rate * 1000
    f0_min = 50
    f0_max = 1100
    f0 = (
        parselmouth.Sound(x, sampling_rate)
        .to_pitch_ac(
            time_step=time_step / 1000,
            voicing_threshold=0.6,
            pitch_floor=f0_min,
            pitch_ceiling=f0_max,
        )
        .selected_array["frequency"]
    )

    pad_size = (p_len - len(f0) + 1) // 2
    if pad_size > 0 or p_len - len(f0) - pad_size > 0:
        f0 = np.pad(f0, [[pad_size, p_len - len(f0) - pad_size]], mode="constant")
    return f0


def _resize_f0(
    x: ndarray[Any, dtype[float32]], target_len: int
) -> ndarray[Any, dtype[float32]]:
    source = np.array(x)
    source[source < 0.001] = np.nan
    target = np.interp(
        np.arange(0, len(source) * target_len, len(source)) / target_len,
        np.arange(0, len(source)),
        source,
    )
    res = np.nan_to_num(target)
    return res


def compute_f0_pyworld(
    wav_numpy: ndarray[Any, dtype[float32]],
    p_len: None | int = None,
    sampling_rate: int = 44100,
    hop_length: int = 512,
    type_: Literal["dio", "harvest"] = "dio",
):
    import pyworld

    if p_len is None:
        p_len = wav_numpy.shape[0] // hop_length
    if type_ == "dio":
        f0, t = pyworld.dio(
            wav_numpy.astype(np.double),
            fs=sampling_rate,
            f0_ceil=f0_max,
            f0_floor=f0_min,
            frame_period=1000 * hop_length / sampling_rate,
        )
    elif type_ == "harvest":
        f0, t = pyworld.harvest(
            wav_numpy.astype(np.double),
            fs=sampling_rate,
            f0_ceil=f0_max,
            f0_floor=f0_min,
            frame_period=1000 * hop_length / sampling_rate,
        )
    f0 = pyworld.stonemask(wav_numpy.astype(np.double), f0, t, sampling_rate)
    for index, pitch in enumerate(f0):
        f0[index] = round(pitch, 1)
    return _resize_f0(f0, p_len)


def compute_f0_crepe(
    wav_numpy: ndarray[Any, dtype[float32]],
    p_len: None | int = None,
    sampling_rate: int = 44100,
    hop_length: int = 512,
    device: str | torch.device = get_optimal_device(),
    model: Literal["full", "tiny"] = "full",
):
    audio = torch.from_numpy(wav_numpy).to(device, copy=True)
    audio = torch.unsqueeze(audio, dim=0)

    if audio.ndim == 2 and audio.shape[0] > 1:
        audio = torch.mean(audio, dim=0, keepdim=True).detach()
    # (T) -> (1, T)
    audio = audio.detach()

    pitch: Tensor = torchcrepe.predict(
        audio,
        sampling_rate,
        hop_length,
        f0_min,
        f0_max,
        model,
        batch_size=hop_length * 2,
        device=device,
        pad=True,
    )

    f0 = pitch.squeeze(0).cpu().float().numpy()
    p_len = p_len or wav_numpy.shape[0] // hop_length
    f0 = _resize_f0(f0, p_len)
    return f0


def compute_f0(
    wav_numpy: ndarray[Any, dtype[float32]],
    p_len: None | int = None,
    sampling_rate: int = 44100,
    hop_length: int = 512,
    method: Literal["crepe", "crepe-tiny", "parselmouth", "dio", "harvest"] = "dio",
    **kwargs,
):
    with timer() as t:
        wav_numpy = wav_numpy.astype(np.float32)
        wav_numpy /= np.quantile(np.abs(wav_numpy), 0.999)
        if method in ["dio", "harvest"]:
            f0 = compute_f0_pyworld(wav_numpy, p_len, sampling_rate, hop_length, method)
        elif method == "crepe":
            f0 = compute_f0_crepe(wav_numpy, p_len, sampling_rate, hop_length, **kwargs)
        elif method == "crepe-tiny":
            f0 = compute_f0_crepe(
                wav_numpy, p_len, sampling_rate, hop_length, model="tiny", **kwargs
            )
        elif method == "parselmouth":
            f0 = compute_f0_parselmouth(wav_numpy, p_len, sampling_rate, hop_length)
        else:
            raise ValueError(
                "type must be dio, crepe, crepe-tiny, harvest or parselmouth"
            )
    rtf = t.elapsed / (len(wav_numpy) / sampling_rate)
    LOG.info(f"F0 inference time:       {t.elapsed:.3f}s, RTF: {rtf:.3f}")
    return f0


def f0_to_coarse(f0: torch.Tensor | float):
    is_torch = isinstance(f0, torch.Tensor)
    f0_mel = 1127 * (1 + f0 / 700).log() if is_torch else 1127 * np.log(1 + f0 / 700)
    f0_mel[f0_mel > 0] = (f0_mel[f0_mel > 0] - f0_mel_min) * (f0_bin - 2) / (
        f0_mel_max - f0_mel_min
    ) + 1

    f0_mel[f0_mel <= 1] = 1
    f0_mel[f0_mel > f0_bin - 1] = f0_bin - 1
    f0_coarse = (f0_mel + 0.5).long() if is_torch else np.rint(f0_mel).astype(np.int)
    assert f0_coarse.max() <= 255 and f0_coarse.min() >= 1, (
        f0_coarse.max(),
        f0_coarse.min(),
    )
    return f0_coarse


f0_bin = 256
f0_max = 1100.0
f0_min = 50.0
f0_mel_min = 1127 * np.log(1 + f0_min / 700)
f0_mel_max = 1127 * np.log(1 + f0_max / 700)
