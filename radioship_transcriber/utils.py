"""This is a utility module for the transctipter tool.
It contains various utility functions."""

import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # suppress tensorflow warnings.
import logging
import datetime
import shutil

from pydub import AudioSegment  # type: ignore
from inaSpeechSegmenter import Segmenter  # type: ignore
from huggingsound import SpeechRecognitionModel  # type: ignore

import warnings

warnings.filterwarnings(
    "ignore", message=r"arrays to stack must be", category=FutureWarning
)


def make_transcript(
    audio_file_path: str, out_path: str, model: SpeechRecognitionModel, timestamps: bool
) -> None:
    """Creates a transcirpt for a provided mp3 audio segment."""

    # prepare subfolders in slicing and segmenting
    # _, audio_file_name = separate_filename(audio_file_path)
    # segment_folder = os.path.join(out_path, "interim_data/segments", audio_file_name)

    # # do slicing for the audio_file
    # slicing(slices_folder, audio_file_path, AudioSegment)

    # # do the segmenting:
    # segmenting(slices_folder, segment_folder)
    # segment_lst = [
    #     os.path.join(segment_folder, f) for f in sorted(os.listdir(segment_folder))
    # ]
    segment_lst = [os.path.join(audio_file_path, f) for f in os.listdir(audio_file_path)
                    if os.path.isfile(os.path.join(audio_file_path, f))
                    and f.endswith(".mp3")]
    print("audio path", audio_file_path)
    print("segment list:", segment_lst)

    transcriptions_without_decoder = model.transcribe(segment_lst)
    transcriptions_without_decoder = [
        e["transcription"] for e in transcriptions_without_decoder
    ]
    # send in the metadata, and zip it to the transcript lines, write them together.
    slice_meta = [e.split("_")[-1].strip(".mp3") for e in segment_lst]
    write_transcript(
        audio_file_path,
        out_path,
        transcriptions_without_decoder,
        slice_meta,
        timestamps,
    )
    logging.info("Transcipt created for: %s", audio_file_path)

    # I sould have a switch for deleting the inputs.
    # # DELETE THE INTERIM FOLDERS!
    # shutil.rmtree(segment_folder)  # should these be temporary folders instead?
    # shutil.rmtree(slices_folder)


def slicing(slices_folder: str, audio_file_path: str, slicer: AudioSegment) -> None:
    "Slice up an audio file to smaller parts that can be fed to the segmenter"
    minute = 2 * 60 * 1000
    programme = slicer.from_mp3(audio_file_path)
    _, audio_file_name = separate_filename(audio_file_path)

    for i in range(0, len(programme), minute):
        slice_mp3 = programme[i : i + minute]
        start_second = i / 1000
        slice_name = os.path.join(
            slices_folder, audio_file_name + f"_{start_second:07}.mp3"
        )
        slice_mp3.export(slice_name, format="mp3")
        logging.info("Just saved slice: %s", slice_name)


def segmenting(slices_folder: str, segments_folder: str) -> None:
    "Segment the slices further, while filering out noise and music"
    seg = Segmenter()
    slice_list = [
        os.path.join(slices_folder, f) for f in sorted(os.listdir(slices_folder))
    ]
    slice_list = [f for f in slice_list if os.path.isfile(f)]

    for slice_mp3 in slice_list:
        segmentation = seg(slice_mp3)
        programme = AudioSegment.from_mp3(slice_mp3)
        _, outfile = separate_filename(slice_mp3)
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
                outfile = os.path.join(segments_folder, outfile)

                onset = segment[1] * 1000
                offset = segment[2] * 1000
                speech = programme[onset:offset]
                speech.export(outfile, format="mp3")
                logging.info("Saved segment: %s", outfile)


def write_transcript(
    file_path: str,
    out_path: str,
    transcript: list[str],
    slice_meta: list[str],
    timestamps: bool,
) -> None:
    "Handle paths and file names, write output to .txt file."
    _, base_name = separate_filename(file_path)
    file_name = os.path.join(out_path, base_name + ".txt")
    if timestamps:
        transcript = [l[0] + "\t" + l[1] for l in zip(slice_meta, transcript)]
    with open(file_name, "w", encoding="utf-8") as file:
        file.write("\n".join(transcript))


def separate_filename(verbose_filename: str) -> tuple[str, str]:
    """Separate the path to a file and the filename without extension.
    return (path_to_file, filename_without_extension)"""
    print(verbose_filename)
    out = os.path.split(os.path.splitext(verbose_filename)[0])
    print (out)
    return out

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
    _, base_name = separate_filename(mp3)
    file_name = os.path.join(out_path, base_name + ".txt")
    return os.path.isfile(file_name)
