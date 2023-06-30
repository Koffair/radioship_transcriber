#!/usr/bin/env python

"""Tests for `radioship_transcripter` package."""

import shutil
import pytest
from unittest.mock import MagicMock
import pydub
import os

import radioship_transcripter.src.utils as utils


@pytest.fixture
def set_up_slicing_for_side_effect_checks():
    mock_slicer = MagicMock(spec=pydub.AudioSegment)
    mock_slicer.from_mp3.return_value = pydub.AudioSegment([1,0,1,0,0,1,0,0,1,0,0,1,0,0,1],
                                                            frame_rate=3,
                                                            sample_width=3, 
                                                            channels=1)
    utils.slicing('fake_mp3_flie.mp3', mock_slicer)
    current_dir = os.path.dirname(os.path.abspath("__main__.py"))  # or whatever the eintry point will be
    yield current_dir
    # Teardown - Remove the temporary folder
    if os.path.exists(os.path.join(current_dir, 'transcripter_interim_data/')):
        shutil.rmtree(os.path.join(current_dir, 'transcripter_interim_data/'))
    # this is not right. test should not be able to remove real dir.
    # functions should not create paths for themselves. but be provided with as argument.
    # then they will be fake-able -> testable.


def test_slicing_creates_folder(set_up_slicing_for_side_effect_checks) -> None:
    current_dir = set_up_slicing_for_side_effect_checks
    folder_path = os.path.join(current_dir, 'transcripter_interim_data/slices/fake_mp3_flie')
    assert os.path.isdir(folder_path)


def test_slicing_creates_slices(set_up_slicing_for_side_effect_checks) -> None:
    current_dir = set_up_slicing_for_side_effect_checks
    file_path = os.path.join(current_dir, 'transcripter_interim_data/slices/fake_mp3_flie/fake_mp3_flie_00000.0.mp3')
    assert os.path.isfile(file_path)


def test_separate_filename()-> None: 
    result = utils.separate_filename("/this/is/a_long/path/with/a_file.txt")
    assert result == ("/this/is/a_long/path/with", "a_file")
