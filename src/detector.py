import os
import numpy as np
import matplotlib.pyplot as plt

from src.lsb_analysis import analyze_lsb
from src.histogram_analysis import analyze_histogram
from src.utils import save_plot


# Thresholds used by the rule-based classifier
LSB_RATIO_THRESHOLD = 0.02
CHI_SQUARE_THRESHOLD = 0.30
EVEN_ODD_THRESHOLD = 0.10


def classify(lsb_results: dict, hist_results: dict) -> dict:
    """Apply rule-based heuristics and return a verdict dict."""
    f1 = lsb_results["lsb_ratio_flag"]
    f2 = lsb_results["chi_square_flag"]
    f3 = hist_results["even_odd_flag"]

    flags_triggered = sum([f1, f2, f3])
    verdict = "SUSPICIOUS" if flags_triggered >= 2 else "LIKELY NORMAL"

    if flags_triggered == 3:
        confidence = "HIGH"
    elif flags_triggered == 2:
        confidence = "MEDIUM"
    elif flags_triggered == 1:
        confidence = "LOW"
    else:
        confidence = "NONE"

    return {
        "verdict": verdict,
        "confidence": confidence,
        "flags_triggered": flags_triggered,
        "lsb_ratio_flag": f1,
        "chi_square_flag": f2,
        "even_odd_flag": f3,
        "lsb_ratio_value": lsb_results["avg_ratio"],
        "chi_stat_value": lsb_results["avg_chi_stat"],
        "even_odd_value": hist_results["avg_even_odd_dev"],
        "correlation_value": hist_results["avg_correlation"],
    }


def generate_plots(
    image: np.ndarray,
    lsb_results: dict,
    hist_results: dict,
    image_name: str,
    output_dir: str,
    verdict: str,
) -> list:
    """Generate and save three analysis plots. Returns list of saved file paths."""
    saved_paths = []
    channel_names = ["B", "G", "R"]
    channel_colors = ["royalblue", "seagreen", "crimson"]

    # --- Plot 1: LSB Planes ---
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for idx, (name, color) in enumerate(zip(channel_names, channel_colors)):
        lsb_plane = lsb_results["per_channel"][name]["lsb_plane"]
        ratio = lsb_results["per_channel"][name]["ratio"]
        axes[idx].imshow(lsb_plane * 255, cmap="gray", vmin=0, vmax=255)
        axes[idx].set_title(f"{name} Channel LSB Plane\nratio={ratio:.4f}", fontsize=11)
        axes[idx].axis("off")

    fig.suptitle(f"LSB Plane Analysis — {image_name}", fontsize=14, fontweight="bold")
    plt.tight_layout()
    path = save_plot(fig, f"{image_name}_lsb_planes.png", output_dir)
    saved_paths.append(path)

    # --- Plot 2: Histogram Comparison ---
    fig, axes = plt.subplots(3, 2, figsize=(14, 12))
    x = np.arange(256)

    for row, (name, color) in enumerate(zip(channel_names, channel_colors)):
        ch_data = hist_results["per_channel"][name]
        hist_orig = ch_data["hist_orig"]
        hist_zero = ch_data["hist_zero"]
        corr = ch_data["correlation"]

        axes[row, 0].bar(x, hist_orig, color=color, alpha=0.7, width=1.0)
        axes[row, 0].set_title(f"{name} — Original Histogram", fontsize=10)
        axes[row, 0].set_xlabel("Pixel Value")
        axes[row, 0].set_ylabel("Frequency")

        axes[row, 1].bar(x, hist_zero, color=color, alpha=0.7, width=1.0)
        axes[row, 1].set_title(f"{name} — LSB-Zeroed  (corr={corr:.4f})", fontsize=10)
        axes[row, 1].set_xlabel("Pixel Value")
        axes[row, 1].set_ylabel("Frequency")

    fig.suptitle(
        f"Histogram Comparison — {image_name}", fontsize=14, fontweight="bold"
    )
    plt.tight_layout()
    path = save_plot(fig, f"{image_name}_histograms.png", output_dir)
    saved_paths.append(path)

    # --- Plot 3: Summary Bar Chart ---
    fig, ax = plt.subplots(figsize=(8, 5))

    labels = ["LSB Ratio\n|ratio-0.5|", "Chi-Square\nStat", "Even-Odd\nDeviation"]
    values = [
        abs(lsb_results["avg_ratio"] - 0.5),
        lsb_results["avg_chi_stat"],
        hist_results["avg_even_odd_dev"],
    ]
    thresholds = [LSB_RATIO_THRESHOLD, CHI_SQUARE_THRESHOLD, EVEN_ODD_THRESHOLD]
    bar_colors = ["crimson" if v < t else "seagreen" for v, t in zip(values, thresholds)]

    bars = ax.bar(labels, values, color=bar_colors, alpha=0.8, edgecolor="black", width=0.5)

    # Draw threshold reference lines per bar
    for i, t in enumerate(thresholds):
        ax.hlines(t, i - 0.3, i + 0.3, colors="black", linestyles="--", linewidth=1.5)
        ax.text(i + 0.32, t, f"threshold={t}", va="center", fontsize=8)

    # Value labels on top of bars
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.005,
            f"{val:.4f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax.set_title(
        f"Heuristic Scores — {image_name}\nVerdict: {verdict}",
        fontsize=13,
        fontweight="bold",
    )
    ax.set_ylabel("Score")
    ax.set_ylim(bottom=0)

    # Legend: red = suspicious, green = clean
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="crimson", alpha=0.8, label="Suspicious (below threshold)"),
        Patch(facecolor="seagreen", alpha=0.8, label="Normal (above threshold)"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=9)

    plt.tight_layout()
    path = save_plot(fig, f"{image_name}_summary.png", output_dir)
    saved_paths.append(path)

    return saved_paths


def analyze(image: np.ndarray, image_name: str, output_dir: str) -> dict:
    """Run the full steganalysis pipeline on a BGR image."""
    lsb_results = analyze_lsb(image)
    hist_results = analyze_histogram(image)
    result = classify(lsb_results, hist_results)

    plot_paths = generate_plots(
        image, lsb_results, hist_results, image_name, output_dir, result["verdict"]
    )
    result["plot_paths"] = plot_paths

    return result
