#!/usr/bin/env python

"""Tests for `radioship_transcriber` package utils module."""

import pydub  # type: ignore
import os
import tempfile
import radioship_transcriber.src.utils as utils


def test_separate_filename():
    "Tests if separate_filename returns the correct path and filename."
    assert utils.separate_filename("/this/is/a_long/path/with/a_file.txt") == (
        "/this/is/a_long/path/with",
        "a_file",
    )


def test_separate_filename_no_extension():
    "Tests if separate_filename returns the correct path and filename when there is no extension."
    assert utils.separate_filename("/this/is/a_long/path/with/a_file") == (
        "/this/is/a_long/path/with",
        "a_file",
    )


def test_separate_filename_no_path():
    "Tests if separate_filename returns the correct path and filename when there is no path."
    assert utils.separate_filename("a_file.txt") == ("", "a_file")


def test_slicing_creates_files():
    "Tests if slicing creates files."
    # create test files
    test_mp3 = os.path.join(os.path.dirname(__file__), "test_input/test_vcv.mp3")
    with tempfile.TemporaryDirectory() as output_dir:
        utils.slicing(output_dir, test_mp3, pydub.AudioSegment)
        # check if files are created
        assert os.path.isfile(os.path.join(output_dir, "test_vcv_00000.0.mp3"))


def test_segmenting_creates_files():
    "Tests if segmenting creates files."
    test_slices_folder = os.path.join(
        os.path.dirname(__file__), "test_input/test_slices"
    )
    # run segmenting
    with tempfile.TemporaryDirectory() as output_dir:
        utils.segmenting(test_slices_folder, output_dir)
        # check if files are created
        assert os.path.isfile(os.path.join(output_dir, "test_vcv_0:00:01-0:00:15.mp3"))


# create test test_is_processed function
def test_is_processed():
    "Tests if is_processed returns True if the file is processed, and False if it is not."
    test_mp3 = os.path.join(os.path.dirname(__file__), "test_input/test_vcv.mp3")
    with tempfile.TemporaryDirectory() as output_dir:
        assert utils.is_processed(test_mp3, output_dir) is False
        # create processed file
        test_processed_file = os.path.join(output_dir, "test_vcv.txt")
        with open(test_processed_file, "w") as f:
            f.write("test")
        # run is_processed
        assert utils.is_processed(test_mp3, output_dir) is True
