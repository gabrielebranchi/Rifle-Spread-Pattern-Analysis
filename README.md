# Rifle Spread Pattern Analysis

## Description
This software allows analyzing a target image and detecting the fired shots. Additionally, it calculates and draws the minimum diameter circumference that contains a specified percentage of the closest shots, excluding those nearest to the center.

## Features
- Upload target images.
- Automatic shot detection through image processing.
- Calculation of the optimal circumference containing the set percentage of shots.
- Visualization of results with highlighted shots and circumference.
- Export of the processed image.

## Requirements
- Python 3.x
- Required libraries:
  - `opencv-python`
  - `numpy`
  - `Pillow`
  - `tkinter`
  - `math`
  - `threading`
  - `random`

You can install the dependencies with the following command:
```sh
pip install requirements.txt
```

Tkinter, math, threading, and random are included in every Python installation,
so if a missing dependencies error appears, try reinstalling Python.

## Instructions

1. **Program Start**
   ```sh
   python main.py
   ```

2. **Upload an Image**
   - Click on "Select Image" and choose an image file.

3. **Set the parameters**
   - `Threshold`: Threshold value for image processing.
   - `Area Minima`: Minimum size of a shot to be considered.
   - `Percentuale`: Percentage of the closest shots to include in the circumference calculation.

4. **Analyze the Image**
   - Click on "Analyze Shots" to start the process.

5. **View the Results**
   - The software will display the detected shots and the calculated circumference.

6. **Export the image**
   - Click on "Export Image" to save the processed image.

## Contact
To report issues or suggest improvements, open an issue on the GitHub repository or contact the developer.

---
© 2024 - Rifle Spread Analysis Pattern - RSPA
