"""This is the main module of the transctipter tool.

The tool requeires an input and an ouput folder to be specified.
The input folder should contain mp3 files. 

There is a default model path provided that can be replaced."""

import os
import argparse
import logging
import shutil
import sys
import datetime

from pydub import AudioSegment  # type: ignore
from inaSpeechSegmenter import Segmenter  # type: ignore
from huggingsound import SpeechRecognitionModel  # type: ignore

# set up logger
LOGS_FOLDER = os.path.realpath(__file__ + "../../../logs")
if not os.path.isdir(LOGS_FOLDER):
    os.mkdir(LOGS_FOLDER)
now = datetime.datetime.now().strftime("%Y.%m.%d_%H:%M:%S")
log_name = os.path.join(LOGS_FOLDER, now + "_transcript_tool.log")

logging.basicConfig(
    filename=log_name,
    filemode="a",
    force=True,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)
numba_logger = logging.getLogger("numba")
numba_logger.setLevel(logging.WARNING)
pydub_logger = logging.getLogger("pydub")
pydub_logger.setLevel(logging.WARNING)

# show logs on the console as well (for now). this may get behind a -v flag
root = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root.addHandler(handler)

DEFAULT_MODEL = "../models/default_model/"

parser = argparse.ArgumentParser("Create transript for mp3 files.")
parser.add_argument(
    "-i",
    "--in_path",
    type=str,
    metavar="",
    required=True,
    help="Path to input file or directory",
)
parser.add_argument(
    "-o",
    "--out_path",
    type=str,
    metavar="",
    required=True,
    help="Path to output directory",
)
parser.add_argument(
    "-m",
    "--model_path",
    type=str,
    metavar="",
    default=DEFAULT_MODEL,
    required=False,
    help="Address to transcripter model",
)
args = parser.parse_args()


def main(in_path: str, out_path: str, model_path: str) -> None:
    """This is the entry point for the CLI of the radioship transcript tool."""

    if not os.path.isdir(out_path):
        print(f"Output dir [{out_path}] does not exist!")
        create_q = input("Would you like to create it? y/n: ")
        if create_q == "y":
            os.mkdir(out_path)
            print(f"Output dir [{out_path}] created!\n")
        else:
            return

    # fetch model
    model = SpeechRecognitionModel(model_path)
    logging.info("Model loaded from: %s", model_path)

    # create interim folders for processing slices & segments
    if not os.path.isdir("../data/interim/slices"):
        os.makedirs(os.path.abspath("../data/interim/slices"))
    if not os.path.isdir("../data/interim/segments"):
        os.makedirs(os.path.abspath("../data/interim/segments"))

    # get file_list
    logging.info("Loading input .mp3 files from: %s", in_path)
    full_paths = [
        os.path.abspath(os.path.join(in_path, f)) for f in os.listdir(in_path)
    ]
    mp3s = [e for e in full_paths if os.path.isfile(e) and e[-4:] == ".mp3"]

    for mp3 in mp3s:
        # check outpout to avoid reruns
        if is_processed(mp3, out_path):
            logging.info("%s already has a transcirpt in %s", mp3, out_path)
            continue
        # create transcript
        make_transcript(mp3, out_path, model)


def make_transcript(
    audio_file: str, out_path: str, model: SpeechRecognitionModel
) -> None:
    """Creates a transcirpt for a provided mp3 audio segment."""

    # do slicing for the audio_file
    slicing(audio_file)
    _, audio_file_name = separate_fileneme(audio_file)
    slices_folder = os.path.join("../data/interim/slices", audio_file_name)

    # do the segmenting:
    segmenting(slices_folder)
    segment_folder = os.path.join("../data/interim/segments", audio_file_name)
    segment_lst = [
        os.path.join(segment_folder, f) for f in sorted(os.listdir(segment_folder))
    ]
    segment_lst = [f for f in segment_lst if os.path.isfile(f)]

    transcriptions_without_decoder = model.transcribe(segment_lst)
    transcriptions_without_decoder = [
        e["transcription"] for e in transcriptions_without_decoder
    ]
    # send in the metadata, and zip it to the transcript lines, write them together.
    slice_meta = [e.split("_")[-1].strip(".mp3") for e in segment_lst]
    write_transcript(audio_file, out_path, transcriptions_without_decoder, slice_meta)
    logging.info("Transcipt created for: %s", audio_file)

    # DELETE THE INTERIM FOLDERS!
    shutil.rmtree(segment_folder)
    shutil.rmtree(slices_folder)


def write_transcript(
    file_path: str, out_path: str, transcript: list[str], slice_meta: list[str]
) -> None:
    "Handle paths and file names, write output to .txt file."
    _, base_name = separate_fileneme(file_path)
    file_name = os.path.join(out_path, base_name + ".txt")
    lines = [l[0] + "\t" + l[1] for l in zip(slice_meta, transcript)]
    with open(file_name, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))


def slicing(audio_file: str) -> None:
    "Slice up an audio file to smaller parts that can be fed to the segmenter"
    minute = 2 * 60 * 1000
    _, base_name = separate_fileneme(audio_file)
    audio_file_slice_folder = os.path.join(
        os.path.abspath("../data/interim/slices"), base_name
    )
    os.makedirs(audio_file_slice_folder, exist_ok=True)
    programme = AudioSegment.from_mp3(audio_file)

    for i in range(0, len(programme), minute):
        slice_mp3 = programme[i : i + minute]
        start_second = i / 1000
        slice_name = os.path.join(
            audio_file_slice_folder, base_name + f"_{start_second:07}.mp3"
        )
        slice_mp3.export(slice_name, format="mp3")
        logging.info("Just saved slice: %s", slice_name)


def segmenting(slices_folder: str) -> None:
    "Segment the slices further, while filering out noise and music"
    seg = Segmenter()
    slice_list = [
        os.path.join(slices_folder, f) for f in sorted(os.listdir(slices_folder))
    ]
    slice_list = [f for f in slice_list if os.path.isfile(f)]

    _, folder_name = separate_fileneme(slices_folder)
    audio_file_segment_folder = os.path.join(
        os.path.abspath("../data/interim/segments"), folder_name
    )
    os.makedirs(audio_file_segment_folder, exist_ok=True)

    for slice_mp3 in slice_list:
        segmentation = seg(slice_mp3)
        programme = AudioSegment.from_mp3(slice_mp3)
        _, outfile = separate_fileneme(slice_mp3)
        # avoid fails on '_' in filenames
        outfile_parts = outfile.split("_")
        slice_base = "_".join(outfile_parts[:-1])
        slice_start_sec = outfile_parts[-1]

        for segment in segmentation:
            if segment[0] == "male" or segment[0] == "female":
                start, end = timestamp_segment(
                    float(slice_start_sec), segment[1], segment[2]
                )
                outfile = f"{slice_base}_{start}-{end}.mp3"
                outfile = os.path.join(audio_file_segment_folder, outfile)

                onset = segment[1] * 1000
                offset = segment[2] * 1000
                speech = programme[onset:offset]
                speech.export(outfile, format="mp3")
                logging.info("Saved segment: %s", outfile)


def separate_fileneme(verbose_filename: str) -> tuple[str, str]:
    """Separate the path to a file and the filename without extension.
    return (path_to_file, filename_without_extension)"""
    return os.path.split(os.path.splitext(verbose_filename)[0])


def timestamp_segment(offset: float, seg_start: int, seg_end: int) -> tuple[str, str]:
    "Create timestamp from offset and time inteval start/end times. All inputs should be in seconds."
    start_stamp = str(datetime.timedelta(seconds=offset + seg_start)).split(
        ".", maxsplit=1
    )[0]
    end_stamp = str(datetime.timedelta(seconds=offset + seg_end)).split(
        ".", maxsplit=1
    )[0]
    return (start_stamp, end_stamp)


def is_processed(mp3: str, out_path: str) -> bool:
    "Check wether the given audio file already has a transcript."
    _, base_name = separate_fileneme(mp3)
    file_name = os.path.join(out_path, base_name + ".txt")
    return os.path.isfile(file_name)


if __name__ == "__main__":
    main(args.in_path, args.out_path, args.model_path)
