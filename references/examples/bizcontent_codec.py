#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import sys
from pathlib import Path

from Crypto.Cipher import AES

KEY = b"d9XBpRQPivd3l51E"
BLOCK_SIZE = 16


def pkcs7_pad(data: bytes) -> bytes:
    pad_len = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + bytes([pad_len]) * pad_len


def pkcs7_unpad(data: bytes) -> bytes:
    if not data:
        raise ValueError("empty ciphertext")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > BLOCK_SIZE:
        raise ValueError("invalid pkcs7 padding")
    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("broken pkcs7 padding")
    return data[:-pad_len]


def encrypt_biz_content(raw: str) -> str:
    cipher = AES.new(KEY, AES.MODE_ECB)
    import base64
    return base64.b64encode(cipher.encrypt(pkcs7_pad(raw.encode("utf-8")))).decode("ascii")


def decrypt_biz_content(raw: str) -> str:
    raw = raw.strip()
    import base64
    try:
        data = base64.b64decode(raw)
    except Exception:
        raise ValueError("ciphertext is not valid base64")
    cipher = AES.new(KEY, AES.MODE_ECB)
    return pkcs7_unpad(cipher.decrypt(data)).decode("utf-8")


def read_text_from_args(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    if args.file is not None:
        return Path(args.file).read_text(encoding="utf-8")
    return sys.stdin.read()


def main() -> int:
    parser = argparse.ArgumentParser(description="Encode / decode bizContent for 宜兴陶瓷博物馆 miniapp")
    sub = parser.add_subparsers(dest="action", required=True)

    enc = sub.add_parser("enc", help="encrypt plaintext json/text to bizContent")
    enc.add_argument("-t", "--text", help="plaintext content")
    enc.add_argument("-f", "--file", help="plaintext file path")
    enc.add_argument("--json", action="store_true", help="normalize plaintext as compact JSON before encrypting")

    dec = sub.add_parser("dec", help="decrypt bizContent ciphertext")
    dec.add_argument("-t", "--text", help="ciphertext hex")
    dec.add_argument("-f", "--file", help="ciphertext file path")
    dec.add_argument("--pretty", action="store_true", help="pretty-print decrypted json when possible")

    args = parser.parse_args()
    raw = read_text_from_args(args).strip()

    if args.action == "enc":
        if args.json:
            raw = json.dumps(json.loads(raw), ensure_ascii=False, separators=(",", ":"))
        print(encrypt_biz_content(raw))
        return 0

    plain = decrypt_biz_content(raw)
    if args.pretty:
        try:
            print(json.dumps(json.loads(plain), ensure_ascii=False, indent=2))
            return 0
        except Exception:
            pass
    print(plain)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
