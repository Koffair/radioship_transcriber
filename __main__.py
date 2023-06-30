"""This is the CLI of the transctipter tool.

The tool requeires an input and an ouput folder to be specified.
The input folder should contain mp3 files. 

There is a default model path provided that can be replaced."""

import radioship_transcripter.src.utils as utils

import os
import argparse
import logging
import sys
import datetime

from huggingsound import SpeechRecognitionModel  # type: ignore

# set up logger
LOGS_FOLDER = os.path.realpath(__file__ + "../../logs")
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

DEFAULT_MODEL = os.path.abspath("radioship_transcripter/models/default_model/")
# default model can't be local. this is just a placeholder.

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

    # create interim folders for processing slices & segments - relative to __main__.py?
    if not os.path.isdir("transcripter_interim_data/slices"):
        os.makedirs(os.path.abspath("transcripter_interim_data/slices"))
    if not os.path.isdir("transcripter_interim_data/segments"):
        os.makedirs(os.path.abspath("transcripter_interim_data/segments"))

    # get file_list
    logging.info("Loading input .mp3 files from: %s", in_path)
    full_paths = [
        os.path.abspath(os.path.join(in_path, f)) for f in os.listdir(in_path)
    ]
    mp3s = [e for e in full_paths if os.path.isfile(e) and e[-4:] == ".mp3"]

    for mp3 in mp3s:
        # check outpout to avoid reruns
        if utils.is_processed(mp3, out_path):
            logging.info("%s already has a transcirpt in %s", mp3, out_path)
            continue
        # create transcript
        utils.make_transcript(mp3, out_path, model)



if __name__ == "__main__":
    main(args.in_path, args.out_path, args.model_path)

