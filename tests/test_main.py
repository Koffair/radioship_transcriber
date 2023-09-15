"""Tests for main() of `radioship_transcriber` package."""

import pytest
import os
import tempfile
from radioship_transcripter import __main__ as main


def test_main_read_permission_error():
    "Tests if main raises a PermissionError if the input folder is not readable."
    with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
        # make the input directory not readable
        os.chmod(input_dir, 0o000)

        # Test if the permission exception is raised when input is not readable
        with pytest.raises(PermissionError, match="is not readable"):
            main.main(input_dir, output_dir, "no_model")


def test_main_write_permission_error():
    "Tests if main raises a PermissionError if the output folder is not writable."
    with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
        # Make the output directory not writable
        os.chmod(output_dir, 0o400)

        # Test if the permission exception is raised when output is not writable
        with pytest.raises(PermissionError, match="is not writable"):
            main.main(input_dir, output_dir, "no_model")
