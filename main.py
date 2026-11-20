#!/usr/bin/env python3
"""Entry point for the news-image-20261120 competition.

The front page was composed ahead of time by draw_frontpage.py and is
shipped in this repository as entry.png. This program only validates
that image against the competition's gate (a whole PNG, at most 1 MiB,
at most 1024 by 1024 pixels) and copies it byte for byte to the
output directory, so both grader runs produce identical bytes.

Standard library only. No network, no randomness, no timestamps.

Usage (as the grader runs it):
    MAKEFUN_OUTPUT_DIR=/output python3 main.py
"""

import os
import struct
import sys
import zlib

MAX_BYTES = 1_048_576
MAX_WIDTH = 1024
MAX_HEIGHT = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

SOURCE_NAME = "entry.png"
OUTPUT_NAME = "entry.png"


def fail(message):
    """Print an error to stderr and exit non-zero."""
    print("main.py: " + message, file=sys.stderr)
    sys.exit(1)


def read_png(path):
    """Read a PNG file and return (width, height, raw bytes).

    Checks the signature, walks every chunk verifying its CRC, and
    reads the dimensions from the IHDR chunk, so a truncated or
    corrupt file is rejected instead of copied.
    """
    with open(path, "rb") as handle:
        data = handle.read()

    if len(data) < 8 or data[:8] != PNG_SIGNATURE:
        fail("entry.png is not a PNG file (bad signature)")

    if len(data) > MAX_BYTES:
        fail("entry.png is %d bytes, over the 1 MiB limit" % len(data))

    offset = 8
    width = None
    height = None
    saw_iend = False
    while offset < len(data):
        if offset + 8 > len(data):
            fail("entry.png ends in the middle of a chunk header")
        chunk_len = struct.unpack(">I", data[offset:offset + 4])[0]
        chunk_type = data[offset + 4:offset + 8]
        chunk_end = offset + 8 + chunk_len + 4
        if chunk_end > len(data):
            fail("entry.png ends in the middle of a %s chunk"
                 % chunk_type.decode("ascii", "replace"))
        chunk_data = data[offset + 8:offset + 8 + chunk_len]
        stored_crc = struct.unpack(
            ">I", data[offset + 8 + chunk_len:chunk_end])[0]
        actual_crc = zlib.crc32(chunk_type + chunk_data) & 0xFFFFFFFF
        if stored_crc != actual_crc:
            fail("entry.png has a bad CRC in its %s chunk"
                 % chunk_type.decode("ascii", "replace"))
        if chunk_type == b"IHDR":
            if chunk_len != 13:
                fail("entry.png has a malformed IHDR chunk")
            width, height = struct.unpack(">II", chunk_data[:8])
            # Sanity-check the image format itself: 8-bit samples and a
            # colour type the PNG spec defines (0 grey, 2 RGB, 3 palette,
            # 4 grey+alpha, 6 RGBA). Anything else is not a normal image.
            bit_depth = chunk_data[8]
            colour_type = chunk_data[9]
            if bit_depth != 8 or colour_type not in (0, 2, 3, 4, 6):
                fail("entry.png has an unsupported bit depth or "
                     "colour type (%d/%d)" % (bit_depth, colour_type))
        if chunk_type == b"IEND":
            saw_iend = True
            if chunk_end != len(data):
                fail("entry.png has trailing bytes after IEND")
            break
        offset = chunk_end

    if not saw_iend:
        fail("entry.png has no IEND chunk (truncated file)")
    if width is None or height is None:
        fail("entry.png has no IHDR chunk")
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        fail("entry.png is %dx%d, over the 1024x1024 limit"
             % (width, height))
    return width, height, data


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(here, SOURCE_NAME)

    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    output_path = os.path.join(output_dir, OUTPUT_NAME)

    width, height, data = read_png(source_path)

    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "wb") as handle:
        handle.write(data)

    print("wrote %s (%dx%d, %d bytes)"
          % (output_path, width, height, len(data)))


if __name__ == "__main__":
    main()
