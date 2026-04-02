# 🎬 Chroma Keying with OpenCV — Green Screen Replacement

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?logo=opencv&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1.x-orange?logo=numpy&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

A computer vision project that implements **Chroma Keying (Green Screen Matting)** from scratch using OpenCV and NumPy. This technique — routinely used in the film and television industry — removes a solid-color background (green screen) from a video and replaces it with any custom image or video of your choice.

> 🚀 **Demo Result:** Asteroids originally shot against a green screen are composited onto a deep-space universe background, producing a seamless space scene!

---

## 📸 Sample Output

| Input — Green Screen | Output — Universe Background |
|:---:|:---:|
| Asteroid on green screen | Asteroid flying through space 🌌 |

---

## 📖 Table of Contents

- [Background](#-background)
- [How It Works](#-how-it-works)
- [Project Structure](#-project-structure)
- [Requirements](#-requirements)
- [Setup & Installation](#-setup--installation)
- [Usage](#-usage)
- [Algorithm Details](#-algorithm-details)
- [Controls & Interface](#-controls--interface)
- [Results](#-results)
- [References](#-references)
- [Contributors & Acknowledgements](#-contributors--acknowledgements)
- [License](#-license)

---

## 🧠 Background

**Chroma Keying** is a visual effects technique that has been used since the mid-1960s. The idea is simple but powerful:

- A subject (actor, object, etc.) is filmed in front of a **solid-colored background** — historically blue, but now almost universally **green**.
- In post-production (or in real time), the background color is detected and **replaced** with any image or video.
- Green was chosen over blue because green clothing is far less common than blue, reducing accidental subject removal.

This project implements chroma keying entirely using OpenCV, without relying on any external compositing software.

---

## ⚙️ How It Works

The core pipeline for each frame:

```
Input Frame (BGR)
      │
      ▼
Convert to HSV Color Space
      │
      ▼
Apply Median Blur (noise reduction)
      │
      ▼
Threshold Green Color Range → Binary Mask
      │
      ▼
Morphological Opening (remove small noise)
      │
      ▼
Dilation (smooth mask edges)
      │
      ▼
Apply Mask to Background Image
      │
      ▼
Zero-out Green Regions in Foreground Frame
      │
      ▼
Add Background + Foreground → Final Composite Frame
      │
      ▼
Write to Output Video
```

---

## 📁 Project Structure

```
chroma-keying-opencv/
│
├── chroma_key.py             # Main script
├── README.md                 # Project documentation
│
├── inputs/                   # (Not included — add your own)
│   ├── greenscreen-demo.mp4      # Person/object on green screen
│   ├── greenscreenAsteroid.mp4   # Asteroid on green screen
│   ├── zoomBg.jpeg               # Replacement background (Video 1)
│   └── universe.jpeg             # Replacement background (Video 2)
│
└── outputs/                  # Generated output videos
    ├── greenScreenSathyaFinal.mp4
    └── asteroidFinal.mp4
```

---

## 🛠️ Requirements

- Python 3.x
- OpenCV (`cv2`)
- NumPy

Install dependencies:

```bash
pip install opencv-python numpy
```

---

## 🚀 Setup & Installation

1. **Clone the repository:**

```bash
git clone https://github.com/your-username/chroma-keying-opencv.git
cd chroma-keying-opencv
```

2. **Install dependencies:**

```bash
pip install opencv-python numpy
```

3. **Add your input files** to the `inputs/` directory:
   - A video with a subject on a green screen
   - A background image (JPEG/PNG) for replacement

4. **Update the file paths** in `chroma_key.py` to point to your files.

5. **Run the script:**

```bash
python chroma_key.py
```

---

## 🎮 Usage

### Basic Example

```python
import cv2
import numpy as np

# Load video and background
cap = cv2.VideoCapture("inputs/greenscreenAsteroid.mp4")
bg = cv2.imread("inputs/universe.jpeg")

# Define green color range in HSV
lower_green = np.array([36, 120, 70])
upper_green = np.array([80, 255, 255])
```

### Tuning the Green Range

The HSV thresholds control what counts as "green screen." Adjust these values if your results are poor:

| Parameter | Meaning | Default |
|---|---|---|
| `lower_green` | Lower HSV bound for green | `[36, 120, 70]` |
| `upper_green` | Upper HSV bound for green | `[80, 255, 255]` |

> **Tip:** Use a tool like `cv2.inRange` visualizations to fine-tune these bounds for your specific footage.

---

## 🔬 Algorithm Details

### 1. Color Space Conversion — BGR → HSV

Green is much easier to isolate in **HSV (Hue, Saturation, Value)** space than in raw BGR, because hue is separated from brightness. This makes the detection robust to lighting variations.

```python
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
```

### 2. Noise Reduction — Median Blur

A median blur is applied before thresholding to reduce pixel-level noise without smearing edges.

```python
blur = cv2.medianBlur(hsv, 3)
```

### 3. Green Mask — `cv2.inRange`

Pixels within the defined green HSV range become white (255); everything else becomes black (0).

```python
mask = cv2.inRange(blur, lower_green, upper_green)
```

### 4. Mask Refinement — Morphological Operations

- **Opening** (`MORPH_OPEN`): Removes small isolated noise pixels from the mask.
- **Dilation**: Slightly expands the mask to smooth edges and cover fringe pixels.

```python
morphed = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
morphed = cv2.dilate(morphed, np.ones((3,3), np.uint8), iterations=2)
```

### 5. Compositing

- The background image is **masked** to only show through green regions.
- The foreground frame's green pixels are **zeroed out**.
- Both layers are **added** together to produce the final composite.

```python
bg_layer  = cv2.bitwise_and(background, background, mask=morphed)
frame[morphed > 100] = (0, 0, 0)
final = bg_layer + frame
```

---

## 🎛️ Controls & Interface

> As specified in the project brief, this implementation supports the following controls (extendable via OpenCV HighGUI trackbars):

| Control | Description |
|---|---|
| **Color Patch Selector** | Allows the user to select a rectangular patch of the green screen from a frame to sample the target color |
| **Tolerance Slider** | Controls how broadly the color threshold is applied around the sampled green mean |
| **Softness Slider** *(optional)* | Controls edge softness of the foreground mask using blur kernel size |
| **Color Cast Removal** *(optional)* | Reduces green color spill cast onto the subject |

> These controls are defined in the project specification and can be wired to OpenCV `cv2.createTrackbar()` for an interactive real-time interface.

---

## ✅ Results

### Video 1 — Person on Green Screen + Zoom Background
- **Input:** `greenscreen-demo.mp4` (subject in front of green screen)
- **Background:** `zoomBg.jpeg`
- **Output:** `greenScreenSathyaFinal.mp4`

### Video 2 — Asteroid on Green Screen + Universe Background
- **Input:** `greenscreenAsteroid.mp4`
- **Background:** `universe.jpeg`
- **Output:** `asteroidFinal.mp4` 🌌

The asteroid footage, originally shot against a flat green background, is seamlessly composited onto a deep-space image — giving the appearance of an asteroid hurtling through the universe.

---

## 📚 References

1. **[Blue Screen Matting](https://graphics.pixar.com/library/Compositing/)** — A. Ray Smith & J. Blinn. Pioneering paper on chroma matting. Alvy Ray Smith is a co-founder of Pixar and two-time Technical Oscar winner.

2. **[A C Language Implementation of Chroma Keying](http://www.cs.utah.edu/~michael/chroma/)** — Practical implementation reference.

3. **[Robust Chroma Keying System based on Human Visual Perception and Statistical Color Models](https://ieeexplore.ieee.org/)** — Academic reference for statistical modeling approaches.

4. **[State-of-the-Art Matting by Disney Research](https://www.disneyresearch.com/)** — Non-real-time high quality compositing. See also their [demo video](https://www.youtube.com/results?search_query=disney+research+matting).

5. **[OpenCV Documentation — Color Spaces](https://docs.opencv.org/4.x/df/d9d/tutorial_py_colorspaces.html)**

6. **[OpenCV Documentation — Morphological Transformations](https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html)**

---

## 🤝 Contributors & Acknowledgements

- **Author:** [Vishwanath Reddy](https://github.com/your-username)

- **Course Project:** This project was completed as part of a computer vision curriculum. Special thanks to **[OpenCV University](https://opencv.org/university/)** for providing the project specification, course materials, and reference resources that guided this implementation.

> *"Chroma keying is one of the most elegant demonstrations of color space mathematics in real-world use."*

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">Made with ❤️ and lots of green pixels</p>
