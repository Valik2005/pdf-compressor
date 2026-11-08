"""Make an ABI-preserving PE resource change to a copy of a Qt DLL.

Windows CI fixture only. Adds an inert RCDATA marker; does not rebuild Qt
machine code and is not evidence that a source-modified Qt build is compatible.
"""
from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import hashlib
import os
from pathlib import Path
import shutil

MARKER = b"PDFCompressor Qt onefile relinking integration test - changed RCDATA resource\x00"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_resource(source: Path, output: Path) -> dict:
    if os.name != "nt":
        raise RuntimeError("Only Windows PE DLLs support this test")
    source = source.resolve(strict=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    if source == output.resolve():
        raise ValueError("Never modify the installed stock Qt DLL in place")
    shutil.copy2(source, output)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    begin = kernel32.BeginUpdateResourceW
    begin.argtypes = [wintypes.LPCWSTR, wintypes.BOOL]
    begin.restype = wintypes.HANDLE
    update = kernel32.UpdateResourceW
    update.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p,
                       wintypes.WORD, ctypes.c_void_p, wintypes.DWORD]
    update.restype = wintypes.BOOL
    end = kernel32.EndUpdateResourceW
    end.argtypes = [wintypes.HANDLE, wintypes.BOOL]
    end.restype = wintypes.BOOL
    handle = begin(str(output), False)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    resource = ctypes.create_string_buffer(MARKER)
    ok = update(handle, ctypes.c_void_p(10), ctypes.c_void_p(16101),
                0, ctypes.cast(resource, ctypes.c_void_p), len(MARKER))
    if not ok:
        err = ctypes.get_last_error()
        end(handle, True)
        raise ctypes.WinError(err)
    if not end(handle, False):
        raise ctypes.WinError(ctypes.get_last_error())
    original, modified = digest(source), digest(output)
    if original == modified:
        raise ValueError("PE resource update did not change Qt DLL")
    return {"original_sha256": original, "modified_sha256": modified,
            "modified_path": str(output), "type": "inert PE RCDATA resource"}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    print(add_resource(args.original, args.out))


if __name__ == "__main__":
    main()
