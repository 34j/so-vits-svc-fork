import os
from logging import getLogger
from pathlib import Path
from random import shuffle
from typing import Iterable, Literal

import librosa
import numpy as np
import torch
from joblib import Parallel, cpu_count, delayed
from tqdm import tqdm

from . import utils

LOG = getLogger(__name__)
hps = utils.get_hparams_from_file("configs/config.json")
sampling_rate = hps.data.sampling_rate
hop_length = hps.data.hop_length


def _process_one(filepath: Path, hmodel, device: Literal["cuda", "cpu"] = "cuda"):
    wav, sr = librosa.load(filepath, sr=sampling_rate)
    soft_path = filepath.parent / (filepath.stem + ".soft.pt")
    if not os.path.exists(soft_path):
        wav16k = librosa.resample(wav, orig_sr=sampling_rate, target_sr=16000)
        wav16k = torch.from_numpy(wav16k).to(device)
        c = utils.get_hubert_content(hmodel, wav_16k_tensor=wav16k)
        torch.save(c.cpu(), soft_path)
    f0_path = filepath.parent / (filepath.stem + ".f0.npy")
    if not f0_path.exists():
        f0 = utils.compute_f0_dio(
            wav, sampling_rate=sampling_rate, hop_length=hop_length
        )
        np.save(f0_path, f0)


def _process_batch(filepaths: Iterable[Path]):
    LOG.info("Loading hubert model...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    hmodel = utils.get_hubert_model().to(device)
    LOG.info("Hubert model loaded.")
    for filepath in tqdm(filepaths):
        _process_one(filepath, hmodel, device)


def preprocess_hubert_f0(input_dir: Path):
    n_jobs = cpu_count()
    filepaths = list(input_dir.glob("**/*.wav"))
    shuffle(filepaths)
    filepath_chunks = np.array_split(filepaths, n_jobs)
    Parallel(n_jobs=n_jobs)(delayed(_process_batch)(chunk) for chunk in filepath_chunks)
