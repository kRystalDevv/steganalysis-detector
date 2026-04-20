import os
import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt


BANNER = """
+------------------------------------------+
|   STEGANALYSIS DETECTOR v1.0             |
|   LSB Hidden Data Detection Tool         |
+------------------------------------------+
"""


def print_banner():
    print(BANNER)


def load_image(path: str) -> np.ndarray:
    if not os.path.exists(path):
        print(f"[ERROR] File not found: {path}")
        sys.exit(1)

    image = cv2.imread(path)

    if image is None:
        print(f"[ERROR] Cannot read image (unsupported format or corrupt): {path}")
        sys.exit(1)

    return image


def save_plot(fig: plt.Figure, filename: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    fig.savefig(filepath, dpi=100, bbox_inches="tight")
    plt.close(fig)
    return filepath


def print_result(result: dict) -> None:
    verdict = result["verdict"]
    confidence = result["confidence"]
    flags = result["flags_triggered"]

    sep = "=" * 48

    print(f"\n{sep}")
    print(f"  VERDICT: {verdict:<20} [CONFIDENCE: {confidence}]")
    print(f"{sep}")
    print(f"  Flags triggered: {flags}/3")
    print()
    print("  Heuristic Results:")

    def flag_str(flag):
        return "[X]" if flag else "[ ]"

    ratio_val = result["lsb_ratio_value"]
    chi_val = result["chi_stat_value"]
    dev_val = result["even_odd_value"]

    print(
        f"    {flag_str(result['lsb_ratio_flag'])} LSB Ratio Test        "
        f"ratio={ratio_val:.4f}  (suspicious: |ratio - 0.5| < 0.02)"
    )
    print(
        f"    {flag_str(result['chi_square_flag'])} Chi-Square Pairs Test "
        f"stat={chi_val:.4f}   (suspicious: stat < 0.30)"
    )
    print(
        f"    {flag_str(result['even_odd_flag'])} Even-Odd Deviation    "
        f"dev={dev_val:.4f}    (suspicious: dev < 0.10)"
    )
    print(f"{sep}\n")
