"""
LSB Steganography Embedder — generate stego-images for testing the detector.

Usage:
  Embed:   python src/embedder.py --input images/clean/photo.png --message "secret" --output images/stego/photo_stego.png
  Extract: python src/embedder.py --input images/stego/photo_stego.png --extract
"""

import argparse
import os
import sys

import cv2
import numpy as np


def text_to_bits(text: str) -> list:
    """Convert a UTF-8 string to a list of bits (MSB-first)."""
    bits = []
    for byte in text.encode("utf-8"):
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


def bits_to_text(bits: list) -> str:
    """Convert a list of bits back to a UTF-8 string."""
    chars = []
    for i in range(0, len(bits) - 7, 8):
        byte_val = sum(bits[i + j] << (7 - j) for j in range(8))
        chars.append(chr(byte_val))
    return "".join(chars)


def embed_lsb(image: np.ndarray, message: str) -> np.ndarray:
    """Embed a text message into the LSBs of an image.

    Prepends a 32-bit header storing the message bit-length so extraction
    does not need to know the message size in advance.
    """
    message_bits = text_to_bits(message)
    num_bits = len(message_bits)

    # 32-bit big-endian length header
    header_bits = [(num_bits >> (31 - i)) & 1 for i in range(32)]
    all_bits = header_bits + message_bits

    flat = image.flatten().copy()

    if len(all_bits) > len(flat):
        raise ValueError(
            f"Message too large: need {len(all_bits)} bits, "
            f"but image only has {len(flat)} pixels available."
        )

    for i, bit in enumerate(all_bits):
        flat[i] = (flat[i] & 0xFE) | bit

    return flat.reshape(image.shape).astype(np.uint8)


def extract_lsb(image: np.ndarray, num_bits: int = None) -> str:
    """Extract a hidden message from an image's LSBs.

    If num_bits is None, reads the 32-bit header first to determine length.
    """
    flat = image.flatten()

    if num_bits is None:
        # Read 32-bit header to get message bit-length
        header_bits = [int(flat[i]) & 1 for i in range(32)]
        msg_length = sum(bit << (31 - i) for i, bit in enumerate(header_bits))
        start, end = 32, 32 + msg_length
    else:
        start, end = 0, num_bits

    msg_bits = [int(flat[i]) & 1 for i in range(start, min(end, len(flat)))]
    return bits_to_text(msg_bits)


def main():
    parser = argparse.ArgumentParser(
        description="LSB Steganography Tool — embed or extract hidden messages in images"
    )
    parser.add_argument("--input", required=True, help="Input image path")
    parser.add_argument("--output", help="Output path for the stego image (PNG recommended)")
    parser.add_argument("--message", help="Text message to embed")
    parser.add_argument("--extract", action="store_true", help="Extract a hidden message")
    parser.add_argument(
        "--length", type=int, default=None,
        help="Number of bits to extract (skips header; optional)"
    )
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"[ERROR] Input file not found: {args.input}")
        sys.exit(1)

    image = cv2.imread(args.input)
    if image is None:
        print(f"[ERROR] Cannot read image: {args.input}")
        sys.exit(1)

    if args.extract:
        print(f"[*] Extracting message from: {args.input}")
        try:
            message = extract_lsb(image, args.length)
            print(f"[*] Extracted message:\n\n    {message}\n")
        except Exception as e:
            print(f"[ERROR] Extraction failed: {e}")
            sys.exit(1)

    elif args.message:
        if not args.output:
            print("[ERROR] --output is required when embedding a message.")
            sys.exit(1)

        if args.output.lower().endswith((".jpg", ".jpeg")):
            print(
                "[WARNING] JPEG compression will destroy the embedded data. "
                "Use a lossless format like PNG."
            )

        print(f"[*] Embedding message into: {args.input}")
        print(f"[*] Message length: {len(args.message)} characters")

        try:
            stego = embed_lsb(image, args.message)
        except ValueError as e:
            print(f"[ERROR] {e}")
            sys.exit(1)

        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        cv2.imwrite(args.output, stego)
        print(f"[*] Stego image saved to: {args.output}")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
