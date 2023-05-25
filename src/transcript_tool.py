"""This is the main module of the transctipter tool.

The tool requeires an input and an ouput folder to be specified.
The input folder should contain mp3 files. 

There is a default model path provided that can be replaced."""

import os
import argparse
import logging
import sys
import datetime

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

# show logs on the console as well (for now). this may get behind a -v flag
root = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root.addHandler(handler)

NAME = "Senki"
logging.debug("%s raised an error", NAME)

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
    print(f"\nModel: {model_path} fetched\n")

    # get file_list
    print(f"Creating transcript for files in {in_path} \nOutput dir: {out_path}")
    full_paths = [
        os.path.abspath(os.path.join(in_path, f)) for f in os.listdir(in_path)
    ]
    mp3s = [e for e in full_paths if os.path.isfile(e) and e[-4:] == ".mp3"]

    for mp3 in mp3s:
        # create transcript
        make_transcript(mp3, out_path, model)


def make_transcript(
    audio_file: str, out_path: str, model: SpeechRecognitionModel
) -> None:
    """Creates a transcirpt for a provided mp3 audio segment."""
    transcriptions_without_decoder = model.transcribe([audio_file])
    transcriptions_without_decoder = [
        e["transcription"] for e in transcriptions_without_decoder
    ]
    print(transcriptions_without_decoder)
    write_transcript(audio_file, out_path, transcriptions_without_decoder)
    print(f"Transcipt created for {audio_file}")  # log this


def write_transcript(file_path: str, out_path: str, transcript: list[str]) -> None:
    "Handle paths and file names, write output to .txt file."
    _, base_name = os.path.split(os.path.splitext(file_path)[0])
    file_name = os.path.join(out_path, base_name + ".txt")
    with open(file_name, "w", encoding="utf-8") as file:
        file.write("\n".join(transcript))


if __name__ == "__main__":
    main(args.in_path, args.out_path, args.model_path)
