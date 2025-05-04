import ctypes
import os

LIB_PATH = os.path.join(os.path.dirname(__file__), "libsecret.so")

def save_secret(secret: str, filename: str) -> str:
    lib = ctypes.CDLL(LIB_PATH)
    lib.write_secret.argtypes = [ctypes.c_char_p, ctypes.c_char_p]

    output_path = os.path.join("/tmp", filename)
    lib.write_secret(secret.encode("utf-8"), output_path.encode("utf-8"))
    return output_path
