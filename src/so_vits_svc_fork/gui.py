from __future__ import annotations

import json
import multiprocessing
import os
from copy import copy
from logging import getLogger
from pathlib import Path

import PySimpleGUI as sg
import sounddevice as sd
import soundfile as sf
import torch
from pebble import ProcessFuture, ProcessPool

from . import __version__
from .utils import get_optimal_device

GUI_DEFAULT_PRESETS_PATH = Path(__file__).parent / "default_gui_presets.json"
GUI_PRESETS_PATH = Path("./user_gui_presets.json").absolute()

LOG = getLogger(__name__)


def play_audio(path: Path | str):
    if isinstance(path, Path):
        path = path.as_posix()
    data, sr = sf.read(path)
    sd.play(data, sr)


def load_presets() -> dict:
    defaults = json.loads(GUI_DEFAULT_PRESETS_PATH.read_text("utf-8"))
    users = (
        json.loads(GUI_PRESETS_PATH.read_text("utf-8"))
        if GUI_PRESETS_PATH.exists()
        else {}
    )
    # prioriy: defaults > users
    # order: defaults -> users
    return {**defaults, **users, **defaults}


def add_preset(name: str, preset: dict) -> dict:
    presets = load_presets()
    presets[name] = preset
    with GUI_PRESETS_PATH.open("w") as f:
        json.dump(presets, f, indent=2)
    return load_presets()


def delete_preset(name: str) -> dict:
    presets = load_presets()
    if name in presets:
        del presets[name]
    else:
        LOG.warning(f"Cannot delete preset {name} because it does not exist.")
    with GUI_PRESETS_PATH.open("w") as f:
        json.dump(presets, f, indent=2)
    return load_presets()


def get_output_path(input_path: Path) -> Path:
    # Default output path
    output_path = input_path.parent / f"{input_path.stem}.out{input_path.suffix}"

    # Increment file number in path if output file already exists
    file_num = 1
    while output_path.exists():
        output_path = (
            input_path.parent / f"{input_path.stem}.out_{file_num}{input_path.suffix}"
        )
        file_num += 1
    return output_path


def get_supported_file_types() -> tuple[tuple[str, str], ...]:
    res = tuple(
        [
            (extension, f".{extension.lower()}")
            for extension in sf.available_formats().keys()
        ]
    )

    # Sort by popularity
    common_file_types = ["WAV", "MP3", "FLAC", "OGG", "M4A", "WMA"]
    res = sorted(
        res,
        key=lambda x: (
            common_file_types.index(x[0])
            if x[0] in common_file_types
            else len(common_file_types)
        ),
    )
    return res


def get_supported_file_types_concat() -> tuple[tuple[str, str], ...]:
    return (("Audio", " ".join(sf.available_formats().keys())),)


def validate_output_file_type(output_path: Path) -> bool:
    supported_file_types = sorted(
        [f".{extension.lower()}" for extension in sf.available_formats().keys()]
    )
    if not output_path.suffix:
        sg.popup_ok(
            "Error: Output path missing file type extension, enter "
            + "one of the following manually:\n\n"
            + "\n".join(supported_file_types)
        )
        return False
    if output_path.suffix.lower() not in supported_file_types:
        sg.popup_ok(
            f"Error: {output_path.suffix.lower()} is not a supported "
            + "extension; use one of the following:\n\n"
            + "\n".join(supported_file_types)
        )
        return False
    return True


def get_devices(
    update: bool = True,
) -> tuple[list[str], list[str], list[int], list[int]]:
    if update:
        sd._terminate()
        sd._initialize()
    devices = sd.query_devices()
    hostapis = sd.query_hostapis()
    for hostapi in hostapis:
        for device_idx in hostapi["devices"]:
            devices[device_idx]["hostapi_name"] = hostapi["name"]
    input_devices = [
        f"{d['name']} ({d['hostapi_name']})"
        for d in devices
        if d["max_input_channels"] > 0
    ]
    output_devices = [
        f"{d['name']} ({d['hostapi_name']})"
        for d in devices
        if d["max_output_channels"] > 0
    ]
    input_devices_indices = [d["index"] for d in devices if d["max_input_channels"] > 0]
    output_devices_indices = [
        d["index"] for d in devices if d["max_output_channels"] > 0
    ]
    return input_devices, output_devices, input_devices_indices, output_devices_indices


def after_inference(window: sg.Window, path: Path, auto_play: bool, output_path: Path):
    try:
        LOG.info(f"Finished inference for {path.stem}{path.suffix}")
        window["infer"].update(disabled=False)

        if auto_play:
            play_audio(output_path)
    except Exception as e:
        LOG.exception(e)


def main():
    LOG.info(f"version: {__version__}")

    # sg.theme("Dark")
    sg.theme_add_new(
        "Very Dark",
        {
            "BACKGROUND": "#111111",
            "TEXT": "#FFFFFF",
            "INPUT": "#444444",
            "TEXT_INPUT": "#FFFFFF",
            "SCROLL": "#333333",
            "BUTTON": ("white", "#112233"),
            "PROGRESS": ("#111111", "#333333"),
            "BORDER": 2,
            "SLIDER_DEPTH": 2,
            "PROGRESS_DEPTH": 2,
        },
    )
    sg.theme("Very Dark")

    model_candidates = list(sorted(Path("./logs/44k/").glob("G_*.pth")))

    frame_contents = {
        "Paths": [
            [
                sg.Text("Model path"),
                sg.Push(),
                sg.InputText(
                    key="model_path",
                    default_text=(
                        model_candidates[-1].absolute().as_posix()
                        if model_candidates
                        else ""
                    ),
                    enable_events=True,
                ),
                sg.FileBrowse(
                    initial_folder=(
                        Path("./logs/44k/").absolute
                        if Path("./logs/44k/").exists()
                        else Path(".").absolute().as_posix()
                    ),
                    key="model_path_browse",
                    file_types=(
                        ("PyTorch", "G_*.pth G_*.pt"),
                        ("Pytorch", "*.pth *.pt"),
                    ),
                ),
            ],
            [
                sg.Text("Config path"),
                sg.Push(),
                sg.InputText(
                    key="config_path",
                    default_text=(
                        Path("./configs/44k/config.json").absolute().as_posix()
                        if Path("./configs/44k/config.json").exists()
                        else ""
                    ),
                    enable_events=True,
                ),
                sg.FileBrowse(
                    initial_folder=(
                        Path("./configs/44k/").as_posix()
                        if Path("./configs/44k/").exists()
                        else Path(".").absolute().as_posix()
                    ),
                    key="config_path_browse",
                    file_types=(("JSON", "*.json"),),
                ),
            ],
            [
                sg.Text("Cluster model path (Optional)"),
                sg.Push(),
                sg.InputText(
                    key="cluster_model_path",
                    default_text=(
                        Path("./logs/44k/kmeans.pt").absolute().as_posix()
                        if Path("./logs/44k/kmeans.pt").exists()
                        else ""
                    ),
                    enable_events=True,
                ),
                sg.FileBrowse(
                    initial_folder=(
                        "./logs/44k/" if Path("./logs/44k/").exists() else "."
                    ),
                    key="cluster_model_path_browse",
                    file_types=(("PyTorch", "*.pt"), ("Pickle", "*.pt *.pth *.pkl")),
                ),
            ],
        ],
        "Common": [
            [
                sg.Text("Speaker"),
                sg.Push(),
                sg.Combo(values=[], key="speaker", size=(20, 1)),
            ],
            [
                sg.Text("Silence threshold"),
                sg.Push(),
                sg.Slider(
                    range=(-60.0, 0),
                    orientation="h",
                    key="silence_threshold",
                    resolution=0.1,
                ),
            ],
            [
                sg.Text(
                    "Pitch (12 = 1 octave)\n"
                    "ADJUST THIS based on your voice\n"
                    "when Auto predict F0 is turned off.",
                    size=(None, 4),
                ),
                sg.Push(),
                sg.Slider(
                    range=(-36, 36),
                    orientation="h",
                    key="transpose",
                    tick_interval=12,
                ),
            ],
            [
                sg.Checkbox(
                    key="auto_predict_f0",
                    text="Auto predict F0 (Pitch may become unstable when turned on in real-time inference.)",
                )
            ],
            [
                sg.Text("F0 prediction method"),
                sg.Push(),
                sg.Combo(
                    ["crepe", "crepe-tiny", "parselmouth", "dio", "harvest"],
                    key="f0_method",
                ),
            ],
            [
                sg.Text("Cluster infer ratio"),
                sg.Push(),
                sg.Slider(
                    range=(0, 1.0),
                    orientation="h",
                    key="cluster_infer_ratio",
                    resolution=0.01,
                ),
            ],
            [
                sg.Text("Noise scale"),
                sg.Push(),
                sg.Slider(
                    range=(0.0, 1.0),
                    orientation="h",
                    key="noise_scale",
                    resolution=0.01,
                ),
            ],
            [
                sg.Text("Pad seconds"),
                sg.Push(),
                sg.Slider(
                    range=(0.0, 1.0),
                    orientation="h",
                    key="pad_seconds",
                    resolution=0.01,
                ),
            ],
            [
                sg.Text("Chunk seconds"),
                sg.Push(),
                sg.Slider(
                    range=(0.0, 3.0),
                    orientation="h",
                    key="chunk_seconds",
                    resolution=0.01,
                ),
            ],
            [
                sg.Text("Max chunk seconds (set lower if Out Of Memory, 0 to disable)"),
                sg.Push(),
                sg.Slider(
                    range=(0.0, 240.0),
                    orientation="h",
                    key="max_chunk_seconds",
                    resolution=1.0,
                ),
            ],
            [
                sg.Checkbox(
                    key="absolute_thresh",
                    text="Absolute threshold (ignored (True) in realtime inference)",
                )
            ],
        ],
        "File": [
            [
                sg.Text("Input audio path"),
                sg.Push(),
                sg.InputText(key="input_path", enable_events=True),
                sg.FileBrowse(
                    initial_folder=".",
                    key="input_path_browse",
                    file_types=(
                        get_supported_file_types_concat()
                        if os.name == "nt"
                        else get_supported_file_types()
                    ),
                ),
                sg.FolderBrowse(
                    button_text="Browse(Folder)",
                    initial_folder=".",
                    key="input_path_folder_browse",
                    target="input_path",
                ),
                sg.Button("Play", key="play_input"),
            ],
            [
                sg.Text("Output audio path"),
                sg.Push(),
                sg.InputText(key="output_path"),
                sg.FileSaveAs(
                    initial_folder=".",
                    key="output_path_browse",
                    file_types=get_supported_file_types(),
                ),
            ],
            [sg.Checkbox(key="auto_play", text="Auto play", default=True)],
        ],
        "Realtime": [
            [
                sg.Text("Crossfade seconds"),
                sg.Push(),
                sg.Slider(
                    range=(0, 0.6),
                    orientation="h",
                    key="crossfade_seconds",
                    resolution=0.001,
                ),
            ],
            [
                sg.Text(
                    "Block seconds",  # \n(big -> more robust, slower, (the same) latency)"
                    tooltip="Big -> more robust, slower, (the same) latency",
                ),
                sg.Push(),
                sg.Slider(
                    range=(0, 3.0),
                    orientation="h",
                    key="block_seconds",
                    resolution=0.001,
                ),
            ],
            [
                sg.Text(
                    "Additional Infer seconds (before)",  # \n(big -> more robust, slower)"
                    tooltip="Big -> more robust, slower, additional latency",
                ),
                sg.Push(),
                sg.Slider(
                    range=(0, 2.0),
                    orientation="h",
                    key="additional_infer_before_seconds",
                    resolution=0.001,
                ),
            ],
            [
                sg.Text(
                    "Additional Infer seconds (after)",  # \n(big -> more robust, slower, additional latency)"
                    tooltip="Big -> more robust, slower, additional latency",
                ),
                sg.Push(),
                sg.Slider(
                    range=(0, 2.0),
                    orientation="h",
                    key="additional_infer_after_seconds",
                    resolution=0.001,
                ),
            ],
            [
                sg.Text("Realtime algorithm"),
                sg.Push(),
                sg.Combo(
                    ["2 (Divide by speech)", "1 (Divide constantly)"],
                    default_value="1 (Divide constantly)",
                    key="realtime_algorithm",
                ),
            ],
            [
                sg.Text("Input device"),
                sg.Push(),
                sg.Combo(
                    key="input_device",
                    values=[],
                    size=(60, 1),
                ),
            ],
            [
                sg.Text("Output device"),
                sg.Push(),
                sg.Combo(
                    key="output_device",
                    values=[],
                    size=(60, 1),
                ),
            ],
            [
                sg.Checkbox(
                    "Passthrough original audio (for latency check)",
                    key="passthrough_original",
                    default=False,
                ),
                sg.Push(),
                sg.Button("Refresh devices", key="refresh_devices"),
            ],
            [
                sg.Frame(
                    "Notes",
                    [
                        [
                            sg.Text(
                                "In Realtime Inference:\n"
                                "    - Setting F0 prediction method to 'crepe` may cause performance degradation.\n"
                                "    - Auto Predict F0 must be turned off.\n"
                                "If the audio sounds mumbly and choppy:\n"
                                "    Case: The inference has not been made in time (Increase Block seconds)\n"
                                "    Case: Mic input is low (Decrease Silence threshold)\n"
                            )
                        ]
                    ],
                ),
            ],
        ],
        "Presets": [
            [
                sg.Text("Presets"),
                sg.Push(),
                sg.Combo(
                    key="presets",
                    values=list(load_presets().keys()),
                    size=(40, 1),
                    enable_events=True,
                ),
                sg.Button("Delete preset", key="delete_preset"),
            ],
            [
                sg.Text("Preset name"),
                sg.Stretch(),
                sg.InputText(key="preset_name", size=(26, 1)),
                sg.Button("Add current settings as a preset", key="add_preset"),
            ],
        ],
    }

    # frames
    frames = {}
    for name, items in frame_contents.items():
        frame = sg.Frame(name, items)
        frame.expand_x = True
        frames[name] = [frame]

    bottoms = [
        [
            sg.Checkbox(
                key="use_gpu",
                default=get_optimal_device() != torch.device("cpu"),
                text="Use GPU"
                + (
                    " (not available; if your device has GPU, make sure you installed PyTorch with CUDA support)"
                    if get_optimal_device() == torch.device("cpu")
                    else ""
                ),
                disabled=get_optimal_device() == torch.device("cpu"),
            )
        ],
        [
            sg.Button("Infer", key="infer"),
            sg.Button("(Re)Start Voice Changer", key="start_vc"),
            sg.Button("Stop Voice Changer", key="stop_vc"),
            sg.Push(),
            # sg.Button("ONNX Export", key="onnx_export"),
        ],
    ]
    column1 = sg.Column(
        [
            frames["Paths"],
            frames["Common"],
        ],
        vertical_alignment="top",
    )
    column2 = sg.Column(
        [
            frames["File"],
            frames["Realtime"],
            frames["Presets"],
        ]
        + bottoms
    )
    # columns
    layout = [[column1, column2]]
    # get screen size
    screen_width, screen_height = sg.Window.get_screen_size()
    if screen_height < 720:
        layout = [
            [
                sg.Column(
                    layout,
                    vertical_alignment="top",
                    scrollable=False,
                    expand_x=True,
                    expand_y=True,
                    vertical_scroll_only=True,
                    key="main_column",
                )
            ]
        ]
    window = sg.Window(
        f"{__name__.split('.')[0].replace('_', '-')} v{__version__}",
        layout,
        grab_anywhere=True,
        finalize=True,
        scaling=1,
        font=("Yu Gothic UI", 11) if os.name == "nt" else None,
        # resizable=True,
        # size=(1280, 720),
        # Below disables taskbar, which may be not useful for some users
        # use_custom_titlebar=True, no_titlebar=False
        # Keep on top
        # keep_on_top=True
    )

    # event, values = window.read(timeout=0.01)
    # window["main_column"].Scrollable = True

    # make slider height smaller
    try:
        for v in window.element_list():
            if isinstance(v, sg.Slider):
                v.Widget.configure(sliderrelief="flat", width=10, sliderlength=20)
    except Exception as e:
        LOG.exception(e)

    # for n in ["input_device", "output_device"]:
    #     window[n].Widget.configure(justify="right")
    event, values = window.read(timeout=0.01)

    def update_speaker() -> None:
        from . import utils

        config_path = Path(values["config_path"])
        if config_path.exists() and config_path.is_file():
            hp = utils.get_hparams(values["config_path"])
            LOG.debug(f"Loaded config from {values['config_path']}")
            window["speaker"].update(
                values=list(hp.__dict__["spk"].keys()), set_to_index=0
            )

    def update_devices() -> None:
        (
            input_devices,
            output_devices,
            input_device_indices,
            output_device_indices,
        ) = get_devices()
        input_device_indices_reversed = {
            v: k for k, v in enumerate(input_device_indices)
        }
        output_device_indices_reversed = {
            v: k for k, v in enumerate(output_device_indices)
        }
        window["input_device"].update(
            values=input_devices, value=values["input_device"]
        )
        window["output_device"].update(
            values=output_devices, value=values["output_device"]
        )
        input_default, output_default = sd.default.device
        if values["input_device"] not in input_devices:
            window["input_device"].update(
                values=input_devices,
                set_to_index=input_device_indices_reversed.get(input_default, 0),
            )
        if values["output_device"] not in output_devices:
            window["output_device"].update(
                values=output_devices,
                set_to_index=output_device_indices_reversed.get(output_default, 0),
            )

    PRESET_KEYS = [
        key
        for key in values.keys()
        if not any(exclude in key for exclude in ["preset", "browse"])
    ]

    def apply_preset(name: str) -> None:
        for key, value in load_presets()[name].items():
            if key in PRESET_KEYS:
                window[key].update(value)
                values[key] = value

    default_name = list(load_presets().keys())[0]
    apply_preset(default_name)
    window["presets"].update(default_name)
    del default_name
    update_speaker()
    update_devices()
    # with ProcessPool(max_workers=1) as pool:
    # to support Linux
    with ProcessPool(
        max_workers=min(2, multiprocessing.cpu_count()),
        context=multiprocessing.get_context("spawn"),
    ) as pool:
        future: None | ProcessFuture = None
        infer_futures: set[ProcessFuture] = set()
        while True:
            event, values = window.read(200)
            if event == sg.WIN_CLOSED:
                break
            if not event == sg.EVENT_TIMEOUT:
                LOG.info(f"Event {event}, values {values}")
            if event.endswith("_path"):
                for name in window.AllKeysDict:
                    if str(name).endswith("_browse"):
                        browser = window[name]
                        if isinstance(browser, sg.Button):
                            LOG.info(
                                f"Updating browser {browser} to {Path(values[event]).parent}"
                            )
                            browser.InitialFolder = Path(values[event]).parent
                            browser.update()
                        else:
                            LOG.warning(f"Browser {browser} is not a FileBrowse")
            window["transpose"].update(
                disabled=values["auto_predict_f0"],
                visible=not values["auto_predict_f0"],
            )

            input_path = Path(values["input_path"])
            output_path = Path(values["output_path"])

            if event == "add_preset":
                presets = add_preset(
                    values["preset_name"], {key: values[key] for key in PRESET_KEYS}
                )
                window["presets"].update(values=list(presets.keys()))
            elif event == "delete_preset":
                presets = delete_preset(values["presets"])
                window["presets"].update(values=list(presets.keys()))
            elif event == "presets":
                apply_preset(values["presets"])
                update_speaker()
            elif event == "refresh_devices":
                update_devices()
            elif event == "config_path":
                update_speaker()
            elif event == "input_path":
                # Don't change the output path if it's already set
                # if values["output_path"]:
                #     continue
                # Set a sensible default output path
                window.Element("output_path").Update(str(get_output_path(input_path)))
            elif event == "infer":
                if "Default VC" in values["presets"]:
                    window["presets"].update(
                        set_to_index=list(load_presets().keys()).index("Default File")
                    )
                    apply_preset("Default File")
                if values["input_path"] == "":
                    LOG.warning("Input path is empty.")
                    continue
                if not input_path.exists():
                    LOG.warning(f"Input path {input_path} does not exist.")
                    continue
                # if not validate_output_file_type(output_path):
                #     continue

                try:
                    from so_vits_svc_fork.inference.main import infer

                    LOG.info("Starting inference...")
                    window["infer"].update(disabled=True)
                    infer_future = pool.schedule(
                        infer,
                        kwargs=dict(
                            # paths
                            model_path=Path(values["model_path"]),
                            output_path=output_path,
                            input_path=input_path,
                            config_path=Path(values["config_path"]),
                            recursive=True,
                            # svc config
                            speaker=values["speaker"],
                            cluster_model_path=(
                                Path(values["cluster_model_path"])
                                if values["cluster_model_path"]
                                else None
                            ),
                            transpose=values["transpose"],
                            auto_predict_f0=values["auto_predict_f0"],
                            cluster_infer_ratio=values["cluster_infer_ratio"],
                            noise_scale=values["noise_scale"],
                            f0_method=values["f0_method"],
                            # slice config
                            db_thresh=values["silence_threshold"],
                            pad_seconds=values["pad_seconds"],
                            chunk_seconds=values["chunk_seconds"],
                            absolute_thresh=values["absolute_thresh"],
                            max_chunk_seconds=values["max_chunk_seconds"],
                            device=(
                                "cpu" if not values["use_gpu"] else get_optimal_device()
                            ),
                        ),
                    )
                    infer_future.add_done_callback(
                        lambda _future: after_inference(
                            window, input_path, values["auto_play"], output_path
                        )
                    )
                    infer_futures.add(infer_future)
                except Exception as e:
                    LOG.exception(e)
            elif event == "play_input":
                if Path(values["input_path"]).exists():
                    pool.schedule(play_audio, args=[Path(values["input_path"])])
            elif event == "start_vc":
                _, _, input_device_indices, output_device_indices = get_devices(
                    update=False
                )
                from so_vits_svc_fork.inference.main import realtime

                if future:
                    LOG.info("Canceling previous task")
                    future.cancel()
                future = pool.schedule(
                    realtime,
                    kwargs=dict(
                        # paths
                        model_path=Path(values["model_path"]),
                        config_path=Path(values["config_path"]),
                        speaker=values["speaker"],
                        # svc config
                        cluster_model_path=(
                            Path(values["cluster_model_path"])
                            if values["cluster_model_path"]
                            else None
                        ),
                        transpose=values["transpose"],
                        auto_predict_f0=values["auto_predict_f0"],
                        cluster_infer_ratio=values["cluster_infer_ratio"],
                        noise_scale=values["noise_scale"],
                        f0_method=values["f0_method"],
                        # slice config
                        db_thresh=values["silence_threshold"],
                        pad_seconds=values["pad_seconds"],
                        chunk_seconds=values["chunk_seconds"],
                        # realtime config
                        crossfade_seconds=values["crossfade_seconds"],
                        additional_infer_before_seconds=values[
                            "additional_infer_before_seconds"
                        ],
                        additional_infer_after_seconds=values[
                            "additional_infer_after_seconds"
                        ],
                        block_seconds=values["block_seconds"],
                        version=int(values["realtime_algorithm"][0]),
                        input_device=input_device_indices[
                            window["input_device"].widget.current()
                        ],
                        output_device=output_device_indices[
                            window["output_device"].widget.current()
                        ],
                        device=get_optimal_device() if values["use_gpu"] else "cpu",
                        passthrough_original=values["passthrough_original"],
                    ),
                )
            elif event == "stop_vc":
                if future:
                    future.cancel()
                    future = None
            elif event == "onnx_export":
                try:
                    raise NotImplementedError("ONNX export is not implemented yet.")
                    from so_vits_svc_fork.modules.onnx._export import onnx_export

                    onnx_export(
                        input_path=Path(values["model_path"]),
                        output_path=Path(values["model_path"]).with_suffix(".onnx"),
                        config_path=Path(values["config_path"]),
                        device="cpu",
                    )
                except Exception as e:
                    LOG.exception(e)
            if future is not None and future.done():
                try:
                    future.result()
                except Exception as e:
                    LOG.error("Error in realtime: ")
                    LOG.exception(e)
                future = None
            for future in copy(infer_futures):
                if future.done():
                    try:
                        future.result()
                    except Exception as e:
                        LOG.error("Error in inference: ")
                        LOG.exception(e)
                    infer_futures.remove(future)
        if future:
            future.cancel()
    window.close()
