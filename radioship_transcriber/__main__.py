"""This is the CLI of the transctipter tool.

The tool requeires an input and an ouput folder to be specified.
The input folder should contain mp3 files. 

There is a default model path provided that can be replaced."""

import radioship_transcriber.utils as utils

import os
import argparse
import logging
import sys
import datetime
import torch

from huggingsound import SpeechRecognitionModel  # type: ignore


def transcribe(in_path: str, out_path: str, model_path: str, timestamps: bool) -> None:
    """Set up logger and interim folders, create transcriptions."""

    if not os.path.isdir(out_path):
        print(f"Output dir [{out_path}] does not exist!")
        create_q = input("Would you like to create it? y/n: ")
        if create_q == "y":
            os.mkdir(out_path)
            print(f"Output dir [{out_path}] created!\n")
        else:
            return

    # test if the output folder is writable
    if not os.access(out_path, os.W_OK):
        raise PermissionError(
            f"""Output dir [{out_path}] is not writable!

                              
You do not have the necessary permissions to access or modify the specified folders. To resolve this issue:

- On Unix (Linux/Mac):
  - Use the 'chmod' command to change permissions on the folders. For example:

  chmod +rw /path/to/folder

- On Windows:
  - Right-click on the folder, choose 'Properties.'
  - Go to the 'Security' tab and click 'Edit' to change permissions.
  - Add your user account and grant 'Read' and 'Write' permissions.
  
If you're not sure how to do this, consider seeking assistance from your system administrator or referring to your operating system's documentation.
"""
        )

    # test if the input folder is readable
    if not os.access(in_path, os.R_OK):
        raise PermissionError(
            f"""Input dir [{in_path}] is not readable!

                              
You do not have the necessary permissions to access or modify the specified folders. To resolve this issue:

- On Unix (Linux/Mac):
  - Use the 'chmod' command to change permissions on the folders. For example:

  chmod +rw /path/to/folder

- On Windows:
  - Right-click on the folder, choose 'Properties.'
  - Go to the 'Security' tab and click 'Edit' to change permissions.
  - Add your user account and grant 'Read' and 'Write' permissions.
  
If you're not sure how to do this, consider seeking assistance from your system administrator or referring to your operating system's documentation.
"""
        )

    # set up logger
    LOGS_FOLDER = os.path.join(out_path, "logs")
    if not os.path.isdir(LOGS_FOLDER):
        os.mkdir(LOGS_FOLDER)
    now = datetime.datetime.now().strftime("%Y.%m.%d_%H:%M:%S")
    log_name = os.path.join(LOGS_FOLDER, now + "_transcriber_tool.log")

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
    urllib3_logger = logging.getLogger("urllib3")
    urllib3_logger.setLevel(logging.WARNING)

    # show logs on the console as well (for now). this may get behind a -v flag
    root = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)

    logging.info("Timstamp is set to: %i", timestamps)

    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    print("DEVICE:", device_str, device)
    batch_size = 1
    # model = SpeechRecognitionModel("radioship/wav2vec2-large-xlsr-53-hu", device=device_str)
    # model.to(device)


    # fetch model
    model = SpeechRecognitionModel(model_path, device=device_str)
    logging.info("Model %s loaded.", model_path)

    # create interim folders for processing slices & segments
    segments_path = os.path.join(out_path, "interim_data/segments")

    # get file_list
    logging.info("Looking for segment folders in: %s", in_path)
    full_paths = [
        os.path.abspath(os.path.join(in_path, f)) for f in os.listdir(in_path)
    ]
    mp3_folders = [e for e in full_paths if os.path.isdir(e)] # we take folders now

    for mp3_folder in mp3_folders:
        # create transcript
        utils.make_transcript(mp3_folder, out_path, model, timestamps)


def main():
    """This is the entry point for the CLI of the radioship transcript tool."""
    DEFAULT_MODEL = "radioship/wav2vec2-large-xlsr-53-hu"

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

    parser.add_argument("--timestamp", action="store_true", required=False)
    parser.add_argument(
        "--no-timestamp", dest="timestamp", action="store_false", required=False
    )
    parser.set_defaults(timestamp=True)
    args = parser.parse_args()

    transcribe(args.in_path, args.out_path, args.model_path, args.timestamp)


if __name__ == "__main__":
    main()
