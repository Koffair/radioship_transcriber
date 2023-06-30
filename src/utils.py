"""This is a utility module for the transctipter tool.
It contains various utility functions."""

import os
import logging
import datetime
import shutil

from pydub import AudioSegment  # type: ignore
from inaSpeechSegmenter import Segmenter  # type: ignore
from huggingsound import SpeechRecognitionModel  # type: ignore


def make_transcript(
    audio_file: str, out_path: str, model: SpeechRecognitionModel
) -> None:
    """Creates a transcirpt for a provided mp3 audio segment."""

    # do slicing for the audio_file
    slicing(audio_file, AudioSegment)
    _, audio_file_name = separate_filename(audio_file)
    slices_folder = os.path.join("transcripter_interim_data/slices", audio_file_name)

    # do the segmenting:
    segmenting(slices_folder)
    segment_folder = os.path.join("transcripter_interim_data/segments", audio_file_name)
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
    _, base_name = separate_filename(file_path)
    file_name = os.path.join(out_path, base_name + ".txt")
    lines = [l[0] + "\t" + l[1] for l in zip(slice_meta, transcript)]
    with open(file_name, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))


def slicing(audio_file: str, slicer: AudioSegment) -> None:
    "Slice up an audio file to smaller parts that can be fed to the segmenter"
    minute = 2 * 60 * 1000
    _, base_name = separate_filename(audio_file)
    audio_file_slice_folder = os.path.join(
        os.path.abspath("transcripter_interim_data/slices"), base_name
    )

    os.makedirs(audio_file_slice_folder, exist_ok=True)
    programme = slicer.from_mp3(audio_file)

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

    _, folder_name = separate_filename(slices_folder)
    audio_file_segment_folder = os.path.join(
        os.path.abspath("transcripter_interim_data/segments"), folder_name
    )
    os.makedirs(audio_file_segment_folder, exist_ok=True)

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
                outfile = os.path.join(audio_file_segment_folder, outfile)

                onset = segment[1] * 1000
                offset = segment[2] * 1000
                speech = programme[onset:offset]
                speech.export(outfile, format="mp3")
                logging.info("Saved segment: %s", outfile)


def separate_filename(verbose_filename: str) -> tuple[str, str]:
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
    _, base_name = separate_filename(mp3)
    file_name = os.path.join(out_path, base_name + ".txt")
    return os.path.isfile(file_name)
