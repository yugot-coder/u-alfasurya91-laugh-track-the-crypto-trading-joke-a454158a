"""One-line crypto trading joke entry for make.fun.

Writes the chosen joke to ``entry.txt`` next to this file (and to
``/output/entry.txt`` when that directory exists, which is where the
competition harness reads it from).

Standard library only; fully deterministic: the same input always
produces the same bytes. Every write is verified by reading the file
back and comparing it byte-for-byte with the expected bytes, so a
truncated or altered write can never pass silently.
"""

import hashlib
import os

JOKE = (
    "I bought the dip. Turns out the dip had a basement, "
    "a sub-basement, and a parking garage."
)


def validate_entry(text):
    """Check the entry against the competition gate.

    The gate requires /output/entry.txt to be UTF-8 text of 1 to 200
    characters, not only white space. The joke must also be a single
    line (no newline characters).
    """
    if not isinstance(text, str):
        return False, "entry is not a string"
    if not text.strip():
        return False, "entry is empty or only white space"
    if not 1 <= len(text) <= 200:
        return False, "entry is %d characters, must be 1-200" % len(text)
    if "\n" in text or "\r" in text:
        return False, "entry must be a single line"
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        return False, "entry is not valid UTF-8 text"
    return True, "valid (%d characters)" % len(text)


def verify_written_bytes(path, expected):
    """Read *path* back and check it against *expected* bytes.

    The read-back must have the same byte length as the expected data
    (no trailing newline may sneak in), be byte-identical to it, and
    hash to the same sha256 digest. Returns the digest on success.
    """
    with open(path, "rb") as fh:
        back = fh.read()
    if len(back) != len(expected):
        raise IOError("read-back byte length mismatch for %s" % path)
    if back != expected:
        raise IOError("read-back mismatch for %s" % path)
    digest = hashlib.sha256(back).hexdigest()
    if digest != hashlib.sha256(expected).hexdigest():
        raise IOError("read-back digest mismatch for %s" % path)
    return digest


def write_entry(path):
    """Write the joke to *path* and verify the write byte-for-byte."""
    ok, reason = validate_entry(JOKE)
    if not ok:
        raise ValueError("invalid entry: %s" % reason)
    data = JOKE.encode("utf-8")
    with open(path, "wb") as fh:
        fh.write(data)
    return verify_written_bytes(path, data)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    paths = [os.path.join(here, "entry.txt")]
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env_dir:
        os.makedirs(env_dir, exist_ok=True)
        paths.append(os.path.join(env_dir, "entry.txt"))
    output_dir = "/output"
    if os.path.isdir(output_dir):
        paths.append(os.path.join(output_dir, "entry.txt"))
    for path in paths:
        digest = write_entry(path)
        print("wrote %s (sha256 %s)" % (path, digest))
    print("entry: %s" % JOKE)


if __name__ == "__main__":
    main()
