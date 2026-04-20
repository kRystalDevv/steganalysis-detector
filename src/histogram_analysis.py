import numpy as np


def compute_histogram(channel: np.ndarray, bins: int = 256) -> np.ndarray:
    """Return raw pixel frequency counts as float64."""
    hist, _ = np.histogram(channel.flatten(), bins=bins, range=(0, 256))
    return hist.astype(np.float64)


def histogram_correlation(hist1: np.ndarray, hist2: np.ndarray) -> float:
    """Compute Pearson correlation between two histograms.

    Values close to 1.0 mean the histograms are nearly identical.
    """
    h1 = hist1 - np.mean(hist1)
    h2 = hist2 - np.mean(hist2)
    numerator = np.dot(h1, h2)
    denominator = np.sqrt(np.dot(h1, h1) * np.dot(h2, h2))

    if denominator == 0:
        return 1.0

    return float(numerator / denominator)


def lsb_zeroed_image(image: np.ndarray) -> np.ndarray:
    """Return a copy of the image with all LSBs set to zero."""
    return (image & np.uint8(0xFE)).astype(np.uint8)


def even_odd_deviation(channel: np.ndarray) -> float:
    """Measure how equalized adjacent histogram bins (even/odd pairs) are.

    After LSB embedding, even and odd bin counts equalize (deviation → 0).
    Natural images have higher deviation between adjacent bins.
    Normalized by mean frequency to be scale-independent.
    """
    freq, _ = np.histogram(channel.flatten(), bins=256, range=(0, 256))
    freq = freq.astype(np.float64)

    even_bins = freq[0::2]  # pixel values 0, 2, 4, ..., 254
    odd_bins = freq[1::2]   # pixel values 1, 3, 5, ..., 255

    mean_dev = float(np.mean(np.abs(even_bins - odd_bins)))
    mean_freq = float(np.mean(freq))

    if mean_freq == 0:
        return 0.0

    return mean_dev / mean_freq


def analyze_histogram(image: np.ndarray) -> dict:
    """Run histogram-based analysis across all three channels of a BGR image."""
    channel_names = ["B", "G", "R"]
    zeroed = lsb_zeroed_image(image)
    per_channel = {}

    for idx, name in enumerate(channel_names):
        ch_orig = image[:, :, idx]
        ch_zero = zeroed[:, :, idx]

        hist_orig = compute_histogram(ch_orig)
        hist_zero = compute_histogram(ch_zero)
        corr = histogram_correlation(hist_orig, hist_zero)
        dev = even_odd_deviation(ch_orig)

        per_channel[name] = {
            "hist_orig": hist_orig,
            "hist_zero": hist_zero,
            "correlation": corr,
            "even_odd_dev": dev,
        }

    avg_corr = float(np.mean([per_channel[n]["correlation"] for n in channel_names]))
    avg_dev = float(np.mean([per_channel[n]["even_odd_dev"] for n in channel_names]))

    even_odd_flag = avg_dev < 0.10

    return {
        "per_channel": per_channel,
        "avg_correlation": avg_corr,
        "avg_even_odd_dev": avg_dev,
        "even_odd_flag": even_odd_flag,
    }
