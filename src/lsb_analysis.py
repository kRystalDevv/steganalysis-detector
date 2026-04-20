import numpy as np


def extract_lsb_plane(channel: np.ndarray) -> np.ndarray:
    """Return a binary array of the least significant bits of each pixel."""
    return (channel & 1).astype(np.uint8)


def compute_lsb_ratio(lsb_plane: np.ndarray) -> float:
    """Return the proportion of 1-bits in the LSB plane.

    After LSB embedding, random message data pushes this value toward 0.5.
    Natural images typically deviate from 0.5 by more than 2%.
    """
    return float(np.mean(lsb_plane))


def chi_square_pairs_test(channel: np.ndarray) -> float:
    """Compute a normalized chi-square statistic for adjacent pixel value pairs.

    In natural images, frequencies of pixel values 2k and 2k+1 differ.
    LSB embedding equalizes these pairs, driving the statistic toward 0.
    Returns a value in [0, ~1+]: near 0 is suspicious, higher is natural.
    """
    freq, _ = np.histogram(channel.flatten(), bins=256, range=(0, 256))

    chi_sum = 0.0
    total_expected = 0.0

    for i in range(128):
        f_even = float(freq[2 * i])
        f_odd = float(freq[2 * i + 1])
        expected = (f_even + f_odd) / 2.0

        if expected == 0:
            continue

        chi_sum += (f_even - expected) ** 2 / expected
        total_expected += expected

    if total_expected == 0:
        return 1.0

    return float(chi_sum / total_expected)


def analyze_lsb(image: np.ndarray) -> dict:
    """Run LSB-based analysis across all three channels of a BGR image."""
    channel_names = ["B", "G", "R"]
    per_channel = {}

    for idx, name in enumerate(channel_names):
        ch = image[:, :, idx]
        lsb_plane = extract_lsb_plane(ch)
        ratio = compute_lsb_ratio(lsb_plane)
        chi_stat = chi_square_pairs_test(ch)

        per_channel[name] = {
            "lsb_plane": lsb_plane,
            "ratio": ratio,
            "chi_stat": chi_stat,
        }

    avg_ratio = float(np.mean([per_channel[n]["ratio"] for n in channel_names]))
    avg_chi = float(np.mean([per_channel[n]["chi_stat"] for n in channel_names]))

    lsb_ratio_flag = abs(avg_ratio - 0.5) < 0.02
    chi_square_flag = avg_chi < 0.30

    return {
        "per_channel": per_channel,
        "avg_ratio": avg_ratio,
        "avg_chi_stat": avg_chi,
        "lsb_ratio_flag": lsb_ratio_flag,
        "chi_square_flag": chi_square_flag,
    }
