"""This is the main module of the transctipter tool.

The tool requeires an input and an ouput folder to be specified.
The input folder should contain mp3 files. 

There is a default model path provided that can be replaced."""

import os
import argparse

from huggingsound import SpeechRecognitionModel  # type: ignore


# --- Notes ----
# check check if hooks are working - DONE. yes.
# do not forget typehints - DONE: mypy working.

# do not forget logging
# docstrings
# tests
# feature-branch
# --------------


DEFAULT_MODEL = "../models/final_model-20230516T143657Z-001/final_model/"

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

    print(f"Creating transcript for files in {in_path}. \nOutput dir: {out_path}")
    # get file_list
    input_files = os.listdir(in_path)
    for audio_file in input_files:
        if os.path.isfile(audio_file):
            # create transcript
            make_transcript(audio_file, out_path, model)
            print(f"transcipt created for {audio_file}")


def make_transcript(audio_file: str, out_path: str, model) -> None: # what is the model type?
    """Creates a transcirpt for a provided mp3 audio segment."""

    # model. valami predict
    # see transcription part in Zoli script


if __name__ == "__main__":
    main(
        args.in_path, args.out_path, args.model_path
    )  # pylint: disable=no-value-for-parameter
