from __future__ import annotations

import warnings
from logging import getLogger
from pathlib import Path
from typing import Iterable

import librosa
import soundfile
from joblib import Parallel, delayed
from tqdm_joblib import tqdm_joblib

from .preprocess_utils import check_hubert_min_duration

LOG = getLogger(__name__)

# input_dir and output_dir exists.
# write code to convert input dir audio files to output dir audio files,
# without changing folder structure. Use joblib to parallelize.
# Converting audio files includes:
# - resampling to specified sampling rate
# - trim silence
# - adjust volume in a smart way
# - save as 16-bit wav file


def _get_unique_filename(path: Path, existing_paths: Iterable[Path]) -> Path:
    """Return a unique path by appending a number to the original path."""
    if path not in existing_paths:
        return path
    i = 1
    while True:
        new_path = path.parent / f"{path.stem}_{i}{path.suffix}"
        if new_path not in existing_paths:
            return new_path
        i += 1


def is_relative_to(path: Path, *other):
    """Return True if the path is relative to another path or False.
    Python 3.9+ has Path.is_relative_to() method, but we need to support Python 3.8.
    """
    try:
        path.relative_to(*other)
        return True
    except ValueError:
        return False


def _preprocess_one(
    input_path: Path,
    output_path: Path,
    sr: int,
    *,
    top_db: int,
    frame_seconds: float,
    hop_seconds: float,
) -> None:
    """Preprocess one audio file."""

    try:
        audio, sr = librosa.load(input_path, sr=sr, mono=True)

    # Audioread is the last backend it will attempt, so this is the exception thrown on failure
    except Exception as e:
        # Failure due to attempting to load a file that is not audio, so return early
        LOG.warning(f"Failed to load {input_path} due to {e}")
        return

    if not check_hubert_min_duration(audio, sr):
        LOG.info(f"Skip {input_path} because it is too short.")
        return

    # Adjust volume
    audio /= max(audio.max(), -audio.min())

    # Trim silence
    audio, _ = librosa.effects.trim(
        audio,
        top_db=top_db,
        frame_length=int(frame_seconds * sr),
        hop_length=int(hop_seconds * sr),
    )

    if not check_hubert_min_duration(audio, sr):
        LOG.info(f"Skip {input_path} because it is too short.")
        return

    soundfile.write(output_path, audio, samplerate=sr, subtype="PCM_16")


def preprocess_resample(
    input_dir: Path | str,
    output_dir: Path | str,
    sampling_rate: int,
    n_jobs: int = -1,
    *,
    top_db: int = 30,
    frame_seconds: float = 0.1,
    hop_seconds: float = 0.05,
) -> None:
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    """Preprocess audio files in input_dir and save them to output_dir."""

    out_paths = []
    in_paths = list(input_dir.rglob("*.*"))
    if not in_paths:
        raise ValueError(f"No audio files found in {input_dir}")
    for in_path in in_paths:
        in_path_relative = in_path.relative_to(input_dir)
        if not in_path.is_absolute() and is_relative_to(
            in_path, Path("dataset_raw") / "44k"
        ):
            new_in_path_relative = in_path_relative.relative_to("44k")
            warnings.warn(
                f"Recommended folder structure has changed since v1.0.0. "
                "Please move your dataset directly under dataset_raw folder. "
                f"Recognized {in_path_relative} as {new_in_path_relative}"
            )
            in_path_relative = new_in_path_relative

        if len(in_path_relative.parts) < 2:
            continue
        speaker_name = in_path_relative.parts[0]
        file_name = in_path_relative.with_suffix(".wav").name
        out_path = output_dir / speaker_name / file_name
        out_path = _get_unique_filename(out_path, out_paths)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_paths.append(out_path)

    in_and_out_paths = list(zip(in_paths, out_paths))

    with tqdm_joblib(desc="Preprocessing", total=len(in_and_out_paths)):
        Parallel(n_jobs=n_jobs)(
            delayed(_preprocess_one)(
                *args,
                sr=sampling_rate,
                top_db=top_db,
                frame_seconds=frame_seconds,
                hop_seconds=hop_seconds,
            )
            for args in in_and_out_paths
        )
