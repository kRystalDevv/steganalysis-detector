# Steganalysis Detector for Hidden Data in Images

A Python-based steganalysis project that detects suspicious images by analyzing LSB patterns, histograms, and pixel behavior.

## Overview
Steganography is the practice of hiding secret data inside ordinary-looking files such as images. This project focuses on steganalysis, the process of detecting whether an image may contain concealed information.

The detector is designed primarily for basic LSB-based image steganography and uses simple forensic indicators to classify an image as normal or suspicious.

## Features
- Detects possible LSB-based hidden data in images
- Analyzes image histograms and pixel behavior
- Performs basic least significant bit inspection
- Classifies images as normal or suspicious
- Visualizes analysis results for interpretation

## Tech Stack
- Python
- OpenCV
- NumPy
- Matplotlib

## Project Goals
- Build a simple and practical steganalysis detector
- Understand the difference between normal and stego-images
- Apply image processing concepts to information security
- Demonstrate a digital forensics use case

## How It Works
1. A set of normal images is collected
2. Stego-images are generated using simple LSB embedding
3. The system analyzes:
   - LSB distribution
   - histogram irregularities
   - pixel-level behavior
4. The image is flagged as either normal or suspicious

## Expected Output
The system takes an image as input and produces:
- a suspicion result
- simple supporting analysis
- optional visual graphs for comparison

## License
This project is for academic and educational purposes.
