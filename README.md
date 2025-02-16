# SoftVC VITS Singing Voice Conversion Fork

[简体中文](README_zh_CN.md)

<p align="center">
  <a href="https://github.com/voicepaw/so-vits-svc-fork/actions/workflows/ci.yml?query=branch%3Amain">
    <img src="https://img.shields.io/github/actions/workflow/status/voicepaw/so-vits-svc-fork/ci.yml?branch=main&label=CI&logo=github&style=flat-square" alt="CI Status" >
  </a>
  <a href="https://so-vits-svc-fork.readthedocs.io">
    <img src="https://img.shields.io/readthedocs/so-vits-svc-fork.svg?logo=read-the-docs&logoColor=fff&style=flat-square" alt="Documentation Status">
  </a>
  <a href="https://codecov.io/gh/voicepaw/so-vits-svc-fork">
    <img src="https://img.shields.io/codecov/c/github/voicepaw/so-vits-svc-fork.svg?logo=codecov&logoColor=fff&style=flat-square" alt="Test coverage percentage">
  </a>
</p>
<p align="center">
  <a href="https://python-poetry.org/">
    <img src="https://img.shields.io/badge/packaging-poetry-299bd7?style=flat-square&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAASCAYAAABrXO8xAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAJJSURBVHgBfZLPa1NBEMe/s7tNXoxW1KJQKaUHkXhQvHgW6UHQQ09CBS/6V3hKc/AP8CqCrUcpmop3Cx48eDB4yEECjVQrlZb80CRN8t6OM/teagVxYZi38+Yz853dJbzoMV3MM8cJUcLMSUKIE8AzQ2PieZzFxEJOHMOgMQQ+dUgSAckNXhapU/NMhDSWLs1B24A8sO1xrN4NECkcAC9ASkiIJc6k5TRiUDPhnyMMdhKc+Zx19l6SgyeW76BEONY9exVQMzKExGKwwPsCzza7KGSSWRWEQhyEaDXp6ZHEr416ygbiKYOd7TEWvvcQIeusHYMJGhTwF9y7sGnSwaWyFAiyoxzqW0PM/RjghPxF2pWReAowTEXnDh0xgcLs8l2YQmOrj3N7ByiqEoH0cARs4u78WgAVkoEDIDoOi3AkcLOHU60RIg5wC4ZuTC7FaHKQm8Hq1fQuSOBvX/sodmNJSB5geaF5CPIkUeecdMxieoRO5jz9bheL6/tXjrwCyX/UYBUcjCaWHljx1xiX6z9xEjkYAzbGVnB8pvLmyXm9ep+W8CmsSHQQY77Zx1zboxAV0w7ybMhQmfqdmmw3nEp1I0Z+FGO6M8LZdoyZnuzzBdjISicKRnpxzI9fPb+0oYXsNdyi+d3h9bm9MWYHFtPeIZfLwzmFDKy1ai3p+PDls1Llz4yyFpferxjnyjJDSEy9CaCx5m2cJPerq6Xm34eTrZt3PqxYO1XOwDYZrFlH1fWnpU38Y9HRze3lj0vOujZcXKuuXm3jP+s3KbZVra7y2EAAAAAASUVORK5CYII=" alt="Poetry">
  </a>
  <a href="https://github.com/ambv/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square" alt="black">
  </a>
  <a href="https://github.com/pre-commit/pre-commit">
    <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=flat-square" alt="pre-commit">
  </a>
</p>
<p align="center">
  <a href="https://pypi.org/project/so-vits-svc-fork/">
    <img src="https://img.shields.io/pypi/v/so-vits-svc-fork.svg?logo=python&logoColor=fff&style=flat-square" alt="PyPI Version">
  </a>
  <img src="https://img.shields.io/pypi/pyversions/so-vits-svc-fork.svg?style=flat-square&logo=python&amp;logoColor=fff" alt="Supported Python versions">
  <img src="https://img.shields.io/pypi/l/so-vits-svc-fork.svg?style=flat-square" alt="License">
</p>

A fork of [`so-vits-svc`](https://github.com/svc-develop-team/so-vits-svc) with **realtime support** and **greatly improved interface**. Based on branch `4.0` (v1) (or `4.1`) and the models are compatible. `4.1` models are not supported. Other models are also not supported.

## No Longer Maintained

### Reasons

- Within a year, the technology has evolved enormously and there are many better alternatives
- Was hoping to create a more Modular, easy-to-install repository, but didn't have the skills, time, money to do so
- PySimpleGUI is no longer LGPL
- Using Typer is getting more popular than directly using Click

### Alternatives

Always beware of the very few influencers who are **quite overly surprised** about any new project/technology. You need to take every social networking post with semi-doubt.

The voice changer boom that occurred in 2023 has come to an end, and many developers, not just those in this repository, have been not very active for a while.

There are too many alternatives to list here but:

- RVC family: [IAHispano/Applio](https://github.com/IAHispano/Applio) (MIT), [fumiama's RVC](https://github.com/fumiama/Retrieval-based-Voice-Conversion-WebUI) (AGPL) and [original RVC](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI) (MIT)
- [VCClient](https://github.com/w-okada/voice-changer) (MIT etc.) is quite actively maintained and offers web-based GUI for real-time conversion.
- [fish-diffusion](https://github.com/fishaudio/fish-diffusion/commits/main/) tried to be quite modular but not quite actively maintained.
- [yxlllc/DDSP\-SVC](https://github.com/yxlllc/DDSP-SVC) - new releases are issued occasionally. [yxlllc/ReFlow\-VAE\-SVC](https://github.com/yxlllc/ReFlow-VAE-SVC)
- [coqui\-ai/TTS](https://github.com/coqui-ai/TTS) was for TTS but was partially modular. However, it is not maintained anymore, unfortunately.

Elsewhere, several start-ups have improved and marketed voice changers (probably for profit).

> Updates to this repository have been limited to maintenance since Spring 2023.
> ~~It is difficult to narrow the list of alternatives here, but please consider trying other projects if you are looking for a voice changer with even better performance (especially in terms of latency other than quality).~~ > ~~However, this project may be ideal for those who want to try out voice conversion for the moment (because it is easy to install).~~

## Features not available in the original repo

- **Realtime voice conversion** (enhanced in v1.1.0)
- Partially integrates [`QuickVC`](https://github.com/quickvc/QuickVC-VoiceConversion)
- Fixed misuse of [`ContentVec`](https://github.com/auspicious3000/contentvec) in the original repository.[^c]
- More accurate pitch estimation using [`CREPE`](https://github.com/marl/crepe/).
- GUI and unified CLI available
- ~2x faster training
- Ready to use just by installing with `pip`.
- Automatically download pretrained models. No need to install `fairseq`.
- Code completely formatted with black, isort, autoflake etc.

[^c]: [#206](https://github.com/voicepaw/so-vits-svc-fork/issues/206)

## Installation

### Option 1. One click easy installation

<a href="https://github.com/voicepaw/so-vits-svc-fork/releases/download/v1.3.2/install.bat" download>
  <img src="https://img.shields.io/badge/.bat-download-blue?style=flat-square&logo=windows" alt="Download .bat">
</a>

This BAT file will automatically perform the steps described below.

### Option 2. Manual installation (using pipx, experimental)

#### 1. Installing pipx

Windows (development version required due to [pypa/pipx#940](https://github.com/pypa/pipx/issues/940)):

```shell
py -3 -m pip install --user git+https://github.com/pypa/pipx.git
py -3 -m pipx ensurepath
```

Linux/MacOS:

```shell
python -m pip install --user pipx
python -m pipx ensurepath
```

#### 2. Installing so-vits-svc-fork

```shell
pipx install so-vits-svc-fork --python=3.11
pipx inject so-vits-svc-fork torch torchaudio --pip-args="--upgrade" --index-url=https://download.pytorch.org/whl/cu121 # https://download.pytorch.org/whl/nightly/cu121
```

### Option 3. Manual installation

<details>
  <summary>Creating a virtual environment</summary>

Windows:

```shell
py -3.11 -m venv venv
venv\Scripts\activate
```

Linux/MacOS:

```shell
python3.11 -m venv venv
source venv/bin/activate
```

Anaconda:

```shell
conda create -n so-vits-svc-fork python=3.11 pip
conda activate so-vits-svc-fork
```

Installing without creating a virtual environment may cause a `PermissionError` if Python is installed in Program Files, etc.

</details>

Install this via pip (or your favourite package manager that uses pip):

```shell
python -m pip install -U pip setuptools wheel
pip install -U torch torchaudio --index-url https://download.pytorch.org/whl/cu121 # https://download.pytorch.org/whl/nightly/cu121
pip install -U so-vits-svc-fork
```

<details>
  <summary>Notes</summary>

- If no GPU is available or using MacOS, simply remove `pip install -U torch torchaudio --index-url https://download.pytorch.org/whl/cu121`. MPS is probably supported.
- If you are using an AMD GPU on Linux, replace `--index-url https://download.pytorch.org/whl/cu121` with `--index-url https://download.pytorch.org/whl/nightly/rocm5.7`. AMD GPUs are not supported on Windows ([#120](https://github.com/voicepaw/so-vits-svc-fork/issues/120)).
  </details>

### Update

Please update this package regularly to get the latest features and bug fixes.

```shell
pip install -U so-vits-svc-fork
# pipx upgrade so-vits-svc-fork
```

## Usage

### Inference

#### GUI

![GUI](https://raw.githubusercontent.com/voicepaw/so-vits-svc-fork/main/docs/_static/gui.png)

GUI launches with the following command:

```shell
svcg
```

#### CLI

- Realtime (from microphone)

```shell
svc vc
```

- File

```shell
svc infer source.wav
```

Pretrained models are available on [Hugging Face](https://huggingface.co/models?search=so-vits-svc) or [CIVITAI](https://civitai.com/tag/so-vits-svc-fork).

#### Notes

- If using WSL, please note that WSL requires additional setup to handle audio and the GUI will not work without finding an audio device.
- In real-time inference, if there is noise on the inputs, the HuBERT model will react to those as well. Consider using realtime noise reduction applications such as [RTX Voice](https://www.nvidia.com/en-us/geforce/guides/nvidia-rtx-voice-setup-guide/) in this case.
- Models other than for 4.0v1 or this repository are not supported.
- GPU inference requires at least 4 GB of VRAM. If it does not work, try CPU inference as it is fast enough. [^r-inference]

[^r-inference]: [#469](https://github.com/voicepaw/so-vits-svc-fork/issues/469)

### Training

#### Before training

- If your dataset has BGM, please remove the BGM using software such as [Ultimate Vocal Remover](https://ultimatevocalremover.com/). `3_HP-Vocal-UVR.pth` or `UVR-MDX-NET Main` is recommended. [^1]
- If your dataset is a long audio file with a single speaker, use `svc pre-split` to split the dataset into multiple files (using `librosa`).
- If your dataset is a long audio file with multiple speakers, use `svc pre-sd` to split the dataset into multiple files (using `pyannote.audio`). Further manual classification may be necessary due to accuracy issues. If speakers speak with a variety of speech styles, set --min-speakers larger than the actual number of speakers. Due to unresolved dependencies, please install `pyannote.audio` manually: `pip install pyannote-audio`.
- To manually classify audio files, `svc pre-classify` is available. Up and down arrow keys can be used to change the playback speed.

[^1]: https://ytpmv.info/how-to-use-uvr/

#### Cloud

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/voicepaw/so-vits-svc-fork/blob/main/notebooks/so-vits-svc-fork-4.0.ipynb)
[![Open In Paperspace](https://img.shields.io/badge/Open%20in-Paperspace-blue?style=flat-square&logo=paperspace)](https://console.paperspace.com/github/voicepaw/so-vits-svc-fork-paperspace/blob/main/so-vits-svc-fork-4.0-paperspace.ipynb)
[![Paperspace Referral](<https://img.shields.io/badge/Referral%20($10)-9VJN74I-blue?style=flat-square&logo=paperspace>)](https://www.paperspace.com/?r=9VJN74I)[^p]

If you do not have access to a GPU with more than 10 GB of VRAM, the free plan of Google Colab is recommended for light users and the Pro/Growth plan of Paperspace is recommended for heavy users. Conversely, if you have access to a high-end GPU, the use of cloud services is not recommended.

[^p]: If you register a referral code and then add a payment method, you may save about $5 on your first month's monthly billing. Note that both referral rewards are Paperspace credits and not cash. It was a tough decision but inserted because debugging and training the initial model requires a large amount of computing power and the developer is a student.

#### Local

Place your dataset like `dataset_raw/{speaker_id}/**/{wav_file}.{any_format}` (subfolders and non-ASCII filenames are acceptable) and run:

```shell
svc pre-resample
svc pre-config
svc pre-hubert
svc train -t
```

#### Notes

- Dataset audio duration per file should be <~ 10s.
- Need at least 4GB of VRAM. [^r-training]
- It is recommended to increase the `batch_size` as much as possible in `config.json` before the `train` command to match the VRAM capacity. Setting `batch_size` to `auto-{init_batch_size}-{max_n_trials}` (or simply `auto`) will automatically increase `batch_size` until OOM error occurs, but may not be useful in some cases.
- To use `CREPE`, replace `svc pre-hubert` with `svc pre-hubert -fm crepe`.
- To use `ContentVec` correctly, replace `svc pre-config` with `-t so-vits-svc-4.0v1`. Training may take slightly longer because some weights are reset due to reusing legacy initial generator weights.
- To use `MS-iSTFT Decoder`, replace `svc pre-config` with `svc pre-config -t quickvc`.
- Silence removal and volume normalization are automatically performed (as in the upstream repo) and are not required.
- If you have trained on a large, copyright-free dataset, consider releasing it as an initial model.
- For further details (e.g. parameters, etc.), you can see the [Wiki](https://github.com/voicepaw/so-vits-svc-fork/wiki) or [Discussions](https://github.com/voicepaw/so-vits-svc-fork/discussions).

[^r-training]: [#456](https://github.com/voicepaw/so-vits-svc-fork/issues/456)

### Further help

For more details, run `svc -h` or `svc <subcommand> -h`.

```shell
> svc -h
Usage: svc [OPTIONS] COMMAND [ARGS]...

  so-vits-svc allows any folder structure for training data.
  However, the following folder structure is recommended.
      When training: dataset_raw/{speaker_name}/**/{wav_name}.{any_format}
      When inference: configs/44k/config.json, logs/44k/G_XXXX.pth
  If the folder structure is followed, you DO NOT NEED TO SPECIFY model path, config path, etc.
  (The latest model will be automatically loaded.)
  To train a model, run pre-resample, pre-config, pre-hubert, train.
  To infer a model, run infer.

Options:
  -h, --help  Show this message and exit.

Commands:
  clean          Clean up files, only useful if you are using the default file structure
  infer          Inference
  onnx           Export model to onnx (currently not working)
  pre-classify   Classify multiple audio files into multiple files
  pre-config     Preprocessing part 2: config
  pre-hubert     Preprocessing part 3: hubert If the HuBERT model is not found, it will be...
  pre-resample   Preprocessing part 1: resample
  pre-sd         Speech diarization using pyannote.audio
  pre-split      Split audio files into multiple files
  train          Train model If D_0.pth or G_0.pth not found, automatically download from hub.
  train-cluster  Train k-means clustering
  vc             Realtime inference from microphone
```

#### External Links

[Video Tutorial](https://www.youtube.com/watch?v=tZn0lcGO5OQ)

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- prettier-ignore-start -->
<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/34j"><img src="https://avatars.githubusercontent.com/u/55338215?v=4?s=80" width="80px;" alt="34j"/><br /><sub><b>34j</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=34j" title="Code">💻</a> <a href="#ideas-34j" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=34j" title="Documentation">📖</a> <a href="#example-34j" title="Examples">💡</a> <a href="#infra-34j" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="#maintenance-34j" title="Maintenance">🚧</a> <a href="https://github.com/voicepaw/so-vits-svc-fork/pulls?q=is%3Apr+reviewed-by%3A34j" title="Reviewed Pull Requests">👀</a> <a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=34j" title="Tests">⚠️</a> <a href="#tutorial-34j" title="Tutorials">✅</a> <a href="#promotion-34j" title="Promotion">📣</a> <a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3A34j" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/GarrettConway"><img src="https://avatars.githubusercontent.com/u/22782004?v=4?s=80" width="80px;" alt="GarrettConway"/><br /><sub><b>GarrettConway</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=GarrettConway" title="Code">💻</a> <a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3AGarrettConway" title="Bug reports">🐛</a> <a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=GarrettConway" title="Documentation">📖</a> <a href="https://github.com/voicepaw/so-vits-svc-fork/pulls?q=is%3Apr+reviewed-by%3AGarrettConway" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/BlueAmulet"><img src="https://avatars.githubusercontent.com/u/43395286?v=4?s=80" width="80px;" alt="BlueAmulet"/><br /><sub><b>BlueAmulet</b></sub></a><br /><a href="#ideas-BlueAmulet" title="Ideas, Planning, & Feedback">🤔</a> <a href="#question-BlueAmulet" title="Answering Questions">💬</a> <a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=BlueAmulet" title="Code">💻</a> <a href="#maintenance-BlueAmulet" title="Maintenance">🚧</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/ThrowawayAccount01"><img src="https://avatars.githubusercontent.com/u/125531852?v=4?s=80" width="80px;" alt="ThrowawayAccount01"/><br /><sub><b>ThrowawayAccount01</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3AThrowawayAccount01" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/MashiroSA"><img src="https://avatars.githubusercontent.com/u/40637516?v=4?s=80" width="80px;" alt="緋"/><br /><sub><b>緋</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=MashiroSA" title="Documentation">📖</a> <a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3AMashiroSA" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Lordmau5"><img src="https://avatars.githubusercontent.com/u/1345036?v=4?s=80" width="80px;" alt="Lordmau5"/><br /><sub><b>Lordmau5</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3ALordmau5" title="Bug reports">🐛</a> <a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=Lordmau5" title="Code">💻</a> <a href="#ideas-Lordmau5" title="Ideas, Planning, & Feedback">🤔</a> <a href="#maintenance-Lordmau5" title="Maintenance">🚧</a> <a href="#question-Lordmau5" title="Answering Questions">💬</a> <a href="#userTesting-Lordmau5" title="User Testing">📓</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/DL909"><img src="https://avatars.githubusercontent.com/u/71912115?v=4?s=80" width="80px;" alt="DL909"/><br /><sub><b>DL909</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3ADL909" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Satisfy256"><img src="https://avatars.githubusercontent.com/u/101394399?v=4?s=80" width="80px;" alt="Satisfy256"/><br /><sub><b>Satisfy256</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3ASatisfy256" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/pierluigizagaria"><img src="https://avatars.githubusercontent.com/u/57801386?v=4?s=80" width="80px;" alt="Pierluigi Zagaria"/><br /><sub><b>Pierluigi Zagaria</b></sub></a><br /><a href="#userTesting-pierluigizagaria" title="User Testing">📓</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/ruckusmattster"><img src="https://avatars.githubusercontent.com/u/77196088?v=4?s=80" width="80px;" alt="ruckusmattster"/><br /><sub><b>ruckusmattster</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3Aruckusmattster" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Desuka-art"><img src="https://avatars.githubusercontent.com/u/111822082?v=4?s=80" width="80px;" alt="Desuka-art"/><br /><sub><b>Desuka-art</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3ADesuka-art" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/heyfixit"><img src="https://avatars.githubusercontent.com/u/41658450?v=4?s=80" width="80px;" alt="heyfixit"/><br /><sub><b>heyfixit</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=heyfixit" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.youtube.com/c/NerdyRodent"><img src="https://avatars.githubusercontent.com/u/74688049?v=4?s=80" width="80px;" alt="Nerdy Rodent"/><br /><sub><b>Nerdy Rodent</b></sub></a><br /><a href="#video-nerdyrodent" title="Videos">📹</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/xieyumc"><img src="https://avatars.githubusercontent.com/u/47858007?v=4?s=80" width="80px;" alt="谢宇"/><br /><sub><b>谢宇</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=xieyumc" title="Documentation">📖</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/ColdCawfee"><img src="https://avatars.githubusercontent.com/u/79474598?v=4?s=80" width="80px;" alt="ColdCawfee"/><br /><sub><b>ColdCawfee</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3AColdCawfee" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/sbersier"><img src="https://avatars.githubusercontent.com/u/34165937?v=4?s=80" width="80px;" alt="sbersier"/><br /><sub><b>sbersier</b></sub></a><br /><a href="#ideas-sbersier" title="Ideas, Planning, & Feedback">🤔</a> <a href="#userTesting-sbersier" title="User Testing">📓</a> <a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3Asbersier" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Meldoner"><img src="https://avatars.githubusercontent.com/u/43951115?v=4?s=80" width="80px;" alt="Meldoner"/><br /><sub><b>Meldoner</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3AMeldoner" title="Bug reports">🐛</a> <a href="#ideas-Meldoner" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=Meldoner" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/mmodeusher"><img src="https://avatars.githubusercontent.com/u/46575920?v=4?s=80" width="80px;" alt="mmodeusher"/><br /><sub><b>mmodeusher</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3Ammodeusher" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/AlonDan"><img src="https://avatars.githubusercontent.com/u/21152334?v=4?s=80" width="80px;" alt="AlonDan"/><br /><sub><b>AlonDan</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3AAlonDan" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Likkkez"><img src="https://avatars.githubusercontent.com/u/44336181?v=4?s=80" width="80px;" alt="Likkkez"/><br /><sub><b>Likkkez</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3ALikkkez" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/DuctTapeGames"><img src="https://avatars.githubusercontent.com/u/84365142?v=4?s=80" width="80px;" alt="Duct Tape Games"/><br /><sub><b>Duct Tape Games</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3ADuctTapeGames" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://tec.hxlxz.com/"><img src="https://avatars.githubusercontent.com/u/6624983?v=4?s=80" width="80px;" alt="Xianglong He"/><br /><sub><b>Xianglong He</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3Ahxl9654" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/75aosu"><img src="https://avatars.githubusercontent.com/u/79185331?v=4?s=80" width="80px;" alt="75aosu"/><br /><sub><b>75aosu</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3A75aosu" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/tonyco82"><img src="https://avatars.githubusercontent.com/u/56610534?v=4?s=80" width="80px;" alt="tonyco82"/><br /><sub><b>tonyco82</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3Atonyco82" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/yxlllc"><img src="https://avatars.githubusercontent.com/u/33565655?v=4?s=80" width="80px;" alt="yxlllc"/><br /><sub><b>yxlllc</b></sub></a><br /><a href="#ideas-yxlllc" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=yxlllc" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/outhipped"><img src="https://avatars.githubusercontent.com/u/116147475?v=4?s=80" width="80px;" alt="outhipped"/><br /><sub><b>outhipped</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3Aouthipped" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/escoolioinglesias"><img src="https://avatars.githubusercontent.com/u/73505402?v=4?s=80" width="80px;" alt="escoolioinglesias"/><br /><sub><b>escoolioinglesias</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3Aescoolioinglesias" title="Bug reports">🐛</a> <a href="#userTesting-escoolioinglesias" title="User Testing">📓</a> <a href="#video-escoolioinglesias" title="Videos">📹</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Blacksingh"><img src="https://avatars.githubusercontent.com/u/130872856?v=4?s=80" width="80px;" alt="Blacksingh"/><br /><sub><b>Blacksingh</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3ABlacksingh" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="http://tybantarnusa.com"><img src="https://avatars.githubusercontent.com/u/9532857?v=4?s=80" width="80px;" alt="Mgs. M. Thoyib Antarnusa"/><br /><sub><b>Mgs. M. Thoyib Antarnusa</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3Atybantarnusa" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/ZeroHackz"><img src="https://avatars.githubusercontent.com/u/15729496?v=4?s=80" width="80px;" alt="Exosfeer"/><br /><sub><b>Exosfeer</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3AZeroHackz" title="Bug reports">🐛</a> <a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=ZeroHackz" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/guranon"><img src="https://avatars.githubusercontent.com/u/130421189?v=4?s=80" width="80px;" alt="guranon"/><br /><sub><b>guranon</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3Aguranon" title="Bug reports">🐛</a> <a href="#ideas-guranon" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=guranon" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/alexanderkoumis"><img src="https://avatars.githubusercontent.com/u/5108856?v=4?s=80" width="80px;" alt="Alexander Koumis"/><br /><sub><b>Alexander Koumis</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=alexanderkoumis" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/acekagami"><img src="https://avatars.githubusercontent.com/u/127201056?v=4?s=80" width="80px;" alt="acekagami"/><br /><sub><b>acekagami</b></sub></a><br /><a href="#translation-acekagami" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Highupech"><img src="https://avatars.githubusercontent.com/u/114140670?v=4?s=80" width="80px;" alt="Highupech"/><br /><sub><b>Highupech</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3AHighupech" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Scorpi"><img src="https://avatars.githubusercontent.com/u/969654?v=4?s=80" width="80px;" alt="Scorpi"/><br /><sub><b>Scorpi</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=Scorpi" title="Code">💻</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="http://maximxlss.github.io"><img src="https://avatars.githubusercontent.com/u/29152154?v=4?s=80" width="80px;" alt="Maximxls"/><br /><sub><b>Maximxls</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=maximxlss" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Star3Lord"><img src="https://avatars.githubusercontent.com/u/57606931?v=4?s=80" width="80px;" alt="Star3Lord"/><br /><sub><b>Star3Lord</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3AStar3Lord" title="Bug reports">🐛</a> <a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=Star3Lord" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Ph0rk0z"><img src="https://avatars.githubusercontent.com/u/59298527?v=4?s=80" width="80px;" alt="Forkoz"/><br /><sub><b>Forkoz</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3APh0rk0z" title="Bug reports">🐛</a> <a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=Ph0rk0z" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Zerui18"><img src="https://avatars.githubusercontent.com/u/34794550?v=4?s=80" width="80px;" alt="Zerui Chen"/><br /><sub><b>Zerui Chen</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=Zerui18" title="Code">💻</a> <a href="#ideas-Zerui18" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.meimadix.com"><img src="https://avatars.githubusercontent.com/u/653972?v=4?s=80" width="80px;" alt="Roee Shenberg"/><br /><sub><b>Roee Shenberg</b></sub></a><br /><a href="#userTesting-shenberg" title="User Testing">📓</a> <a href="#ideas-shenberg" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=shenberg" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/ShinyJustyZ"><img src="https://avatars.githubusercontent.com/u/65282440?v=4?s=80" width="80px;" alt="Justas"/><br /><sub><b>Justas</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3AShinyJustyZ" title="Bug reports">🐛</a> <a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=ShinyJustyZ" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://onako2.github.io/"><img src="https://avatars.githubusercontent.com/u/79749977?v=4?s=80" width="80px;" alt="Onako2"/><br /><sub><b>Onako2</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=Onako2" title="Documentation">📖</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/4ll0w3v1l"><img src="https://avatars.githubusercontent.com/u/53517147?v=4?s=80" width="80px;" alt="4ll0w3v1l"/><br /><sub><b>4ll0w3v1l</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=4ll0w3v1l" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/SamuelSwartzberg"><img src="https://avatars.githubusercontent.com/u/16353439?v=4?s=80" width="80px;" alt="j5y0V6b"/><br /><sub><b>j5y0V6b</b></sub></a><br /><a href="#security-SamuelSwartzberg" title="Security">🛡️</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/marcellocirelli"><img src="https://avatars.githubusercontent.com/u/51972090?v=4?s=80" width="80px;" alt="marcellocirelli"/><br /><sub><b>marcellocirelli</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3Amarcellocirelli" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Priyanshu-hawk"><img src="https://avatars.githubusercontent.com/u/76026651?v=4?s=80" width="80px;" alt="Priyanshu Patel"/><br /><sub><b>Priyanshu Patel</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=Priyanshu-hawk" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/annagorshunova"><img src="https://avatars.githubusercontent.com/u/5199204?v=4?s=80" width="80px;" alt="Anna Gorshunova"/><br /><sub><b>Anna Gorshunova</b></sub></a><br /><a href="https://github.com/voicepaw/so-vits-svc-fork/issues?q=author%3Aannagorshunova" title="Bug reports">🐛</a> <a href="https://github.com/voicepaw/so-vits-svc-fork/commits?author=annagorshunova" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
<!-- prettier-ignore-end -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
