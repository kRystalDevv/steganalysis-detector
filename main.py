"""
Steganalysis Detector — main entry point.

Analyze mode:
  python main.py --analyze <image_path> [--output-dir output/]

Embed mode:
  python main.py --embed <input_image> --message <text> --output <output_path>
"""

import argparse
import os
import sys

import cv2

from src.utils import load_image, print_banner, print_result
from src.detector import analyze
from src.embedder import embed_lsb


def parse_args():
    parser = argparse.ArgumentParser(
        description="Steganalysis Detector — detect LSB-based hidden data in images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Analyze an image:
    python main.py --analyze images/stego/photo.png

  Embed a secret message:
    python main.py --embed images/clean/photo.png --message "hidden text" --output images/stego/photo_stego.png
        """,
    )

    parser.add_argument(
        "--analyze",
        metavar="IMAGE_PATH",
        help="Path to the image to analyze for hidden data",
    )
    parser.add_argument(
        "--output-dir",
        default="output/",
        metavar="DIR",
        help="Directory where analysis plots are saved (default: output/)",
    )
    parser.add_argument(
        "--embed",
        metavar="INPUT_IMAGE",
        help="Input image to embed a secret message into",
    )
    parser.add_argument(
        "--message",
        help="Text message to embed (required with --embed)",
    )
    parser.add_argument(
        "--output",
        metavar="OUTPUT_PATH",
        help="Output path for the stego image (required with --embed)",
    )

    return parser, parser.parse_args()


def run_analyze(image_path: str, output_dir: str) -> None:
    print_banner()

    image = load_image(image_path)
    image_name = (
        os.path.splitext(os.path.basename(image_path))[0].replace(" ", "_")
    )

    print(f"[*] Analyzing : {image_path}")
    print(f"[*] Image size: {image.shape[1]} x {image.shape[0]} pixels  ({image.shape[2]} channels)")
    print(f"[*] Output dir: {output_dir}")

    result = analyze(image, image_name, output_dir)

    print_result(result)

    print("[*] Plots saved:")
    for path in result["plot_paths"]:
        print(f"    {path}")
    print()


def run_embed(input_path: str, message: str, output_path: str) -> None:
    print_banner()

    if output_path.lower().endswith((".jpg", ".jpeg")):
        print(
            "[WARNING] JPEG compression destroys LSB data. "
            "Use a lossless format like PNG for the output."
        )

    image = load_image(input_path)

    print(f"[*] Input image : {input_path}")
    print(f"[*] Message     : {len(message)} characters ({len(message.encode('utf-8')) * 8} bits)")

    try:
        stego = embed_lsb(image, message)
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    cv2.imwrite(output_path, stego)
    print(f"[*] Stego image saved to: {output_path}")
    print("[*] Done. Use --analyze on the stego image to verify detection.\n")


def main():
    parser, args = parse_args()

    if args.analyze:
        run_analyze(args.analyze, args.output_dir)

    elif args.embed:
        if not args.message:
            print("[ERROR] --message is required when using --embed.")
            sys.exit(1)
        if not args.output:
            print("[ERROR] --output is required when using --embed.")
            sys.exit(1)
        run_embed(args.embed, args.message, args.output)

    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
