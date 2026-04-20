# Steganalysis Detector for Hidden Data in Images

A Python-based steganalysis tool that detects LSB-based steganography in images using rule-based heuristics, histogram analysis, and visual reporting.

---

## Overview

Steganography is the practice of hiding secret data inside ordinary-looking files. Images are a common carrier — by modifying the **Least Significant Bit (LSB)** of each pixel value, an attacker can embed hidden text or data with almost no visible change to the image.

This project implements **steganalysis**: the forensic process of detecting whether an image has been tampered with to conceal hidden data. It uses three statistical heuristics to classify an image as **LIKELY NORMAL** or **SUSPICIOUS**, and generates visual analysis plots to support the result.

Designed as a university course project — clean, readable, and easy to explain in a presentation.

---

## Features

- Detect LSB-based steganography using three independent heuristics
- Analyze each color channel (B, G, R) independently
- Classify images as **LIKELY NORMAL** or **SUSPICIOUS** with a confidence level
- Generate three saved analysis plots per image:
  - LSB plane visualization
  - Histogram comparison (original vs. LSB-zeroed)
  - Summary bar chart with threshold markers
- Built-in LSB embedder to generate stego-images for testing
- Clean terminal output with flag indicators

---

## Tech Stack

| Tool | Version |
|---|---|
| Python | 3.8+ |
| OpenCV (`opencv-python`) | >= 4.5.0 |
| NumPy | >= 1.21.0 |
| Matplotlib | >= 3.4.0 |

No machine learning. No web framework. No scipy. All statistical tests are implemented from scratch.

---

## Project Structure

```
steganalysis-detector/
├── main.py                  # Main entry point (analyze or embed)
├── requirements.txt
├── .gitignore
├── README.md
├── src/
│   ├── __init__.py
│   ├── detector.py          # Orchestrates analysis, classification, and plotting
│   ├── lsb_analysis.py      # LSB extraction, ratio test, chi-square pairs test
│   ├── histogram_analysis.py# Histogram comparison and even-odd deviation test
│   ├── utils.py             # Image loading, plot saving, result printing
│   └── embedder.py          # LSB steganography tool for creating test images
├── images/
│   ├── clean/               # Place original unmodified images here
│   └── stego/               # Stego images go here
└── output/                  # Analysis plots are saved here
```

---

## Setup

```bash
git clone https://github.com/krystaldevv/steganalysis-detector.git
cd steganalysis-detector
pip install -r requirements.txt
```

Python 3.8 or higher is required. A virtual environment is recommended:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## Usage

### Analyze an image for hidden data

```bash
python main.py --analyze images/stego/photo_stego.png
```

With a custom output directory for plots:

```bash
python main.py --analyze images/clean/photo.png --output-dir output/
```

### Embed a secret message (create a stego-image)

```bash
python main.py --embed images/clean/photo.png --message "this is a secret" --output images/stego/photo_stego.png
```

> **Important:** Always save the stego image as PNG. JPEG compression destroys LSB data.

### Extract a hidden message (standalone embedder)

```bash
python src/embedder.py --input images/stego/photo_stego.png --extract
```

---

## Sample Workflow

**Step 1 — Add a clean image**

Place any PNG image in `images/clean/`. For example, download a sample photo and save it as `images/clean/photo.png`.

**Step 2 — Generate a stego-image**

```bash
python main.py --embed images/clean/photo.png --message "meet me at midnight" --output images/stego/photo_stego.png
```

Output:
```
[*] Input image : images/clean/photo.png
[*] Message     : 20 characters (160 bits)
[*] Stego image saved to: images/stego/photo_stego.png
```

**Step 3 — Analyze the clean image**

```bash
python main.py --analyze images/clean/photo.png
```

Expected output:
```
================================================
  VERDICT: LIKELY NORMAL        [CONFIDENCE: NONE]
================================================
  Flags triggered: 0/3

  Heuristic Results:
    [ ] LSB Ratio Test        ratio=0.4731  (suspicious: |ratio - 0.5| < 0.02)
    [ ] Chi-Square Pairs Test stat=0.8214   (suspicious: stat < 0.30)
    [ ] Even-Odd Deviation    dev=0.3102    (suspicious: dev < 0.10)
================================================
```

**Step 4 — Analyze the stego-image**

```bash
python main.py --analyze images/stego/photo_stego.png
```

Expected output:
```
================================================
  VERDICT: SUSPICIOUS           [CONFIDENCE: HIGH]
================================================
  Flags triggered: 3/3

  Heuristic Results:
    [X] LSB Ratio Test        ratio=0.5003  (suspicious: |ratio - 0.5| < 0.02)
    [X] Chi-Square Pairs Test stat=0.0041   (suspicious: stat < 0.30)
    [X] Even-Odd Deviation    dev=0.0088    (suspicious: dev < 0.10)
================================================

[*] Plots saved:
    output/photo_stego_lsb_planes.png
    output/photo_stego_histograms.png
    output/photo_stego_summary.png
```

**Step 5 — Verify extraction**

```bash
python src/embedder.py --input images/stego/photo_stego.png --extract
```

Output:
```
[*] Extracted message:

    meet me at midnight
```

---

## Detection Methodology

The detector applies three independent heuristics and flags the image as **SUSPICIOUS** if **2 or more** tests trigger.

### 1. LSB Ratio Test

Each pixel's least significant bit is extracted. In a natural image, the proportion of 1-bits tends to deviate from 50% because of natural patterns in image data (smooth gradients, camera noise, compression artifacts). After LSB embedding, the ratio is replaced by the statistical distribution of the message data, which is typically closer to 50%.

- **Suspicious condition:** `|ratio − 0.5| < 0.02`

### 2. Chi-Square Pairs Test

For each pair of adjacent pixel values `(2k, 2k+1)`, the detector compares their frequencies in the image histogram. In natural images, these pairs have unequal counts. When LSB embedding occurs, the `(2k, 2k+1)` pair frequencies equalize, because changing bit 0 of `2k` gives `2k+1` and vice versa — the embedding redistributes counts between each pair.

The chi-square statistic is computed as:

```
chi = sum( (f_even - expected)^2 / expected )  for each pair
normalized = chi / total_expected
```

A value near 0 means pairs are equalized (suspicious). Higher values indicate natural unevenness.

- **Suspicious condition:** `normalized_chi < 0.30`

### 3. Even-Odd Deviation Test

Similar in spirit to the chi-square test, this measures the mean absolute difference between even-indexed and odd-indexed histogram bins, normalized by the mean frequency. It captures the same equalization effect from a different angle.

- **Suspicious condition:** `avg_even_odd_dev < 0.10`

### Classification Table

| Flags Triggered | Verdict | Confidence |
|---|---|---|
| 3 | SUSPICIOUS | HIGH |
| 2 | SUSPICIOUS | MEDIUM |
| 1 | LIKELY NORMAL | LOW |
| 0 | LIKELY NORMAL | NONE |

---

## Limitations

- **Lossless formats only.** JPEG compression rewrites pixel values and destroys LSB data. Use PNG or BMP images.
- **No ML.** Rule-based thresholds may produce false positives on synthetically generated or highly uniform images.
- **Sequential embedding only.** The embedder writes message bits starting at pixel 0. Spread-spectrum or randomized embedding would not be detected by these heuristics.
- **No payload recovery from unknown images.** The extractor requires either the 32-bit header (written by this tool) or a known bit length.
- **Single LSB only.** Embedding into the 2nd or 3rd LSB is not detected.

---

## Future Improvements

- Batch processing: analyze all images in a folder and produce a summary report
- JPEG steganalysis using DCT coefficient analysis
- Detection of F5, StegHide, or other common stego tools
- Support for 2-LSB and 3-LSB embedding detection
- Statistical significance testing (p-values) using scipy
- ML-based classifier trained on a labeled stego dataset (e.g., BOSS Base)
- Command-line report export to JSON or CSV

---

## License

This project is for academic and educational purposes.
