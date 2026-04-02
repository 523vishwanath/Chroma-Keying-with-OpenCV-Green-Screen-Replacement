"""
============================================================
  Chroma Keying (Green Screen Replacement) using OpenCV
============================================================
Author      : Vishwanath Reddy
Course      : OpenCV University — Computer Vision Project
Description : Replaces green screen backgrounds in videos
              with custom background images using HSV color
              masking and morphological operations.
============================================================
"""

import cv2
import numpy as np
import os
import sys


# ─────────────────────────────────────────────
#  CONFIGURATION — Edit paths here
# ─────────────────────────────────────────────

CONFIG = {
    # ── Video 1: Person / Subject on Green Screen ──
    "video1": {
        "input_video"  : "inputs/greenscreen-demo.mp4",
        "background"   : "inputs/zoomBg.jpeg",
        "output_video" : "outputs/greenScreenFinal.mp4",
        "fps"          : 30,
    },

    # ── Video 2: Asteroid on Green Screen ──
    "video2": {
        "input_video"  : "inputs/greenscreenAsteroid.mp4",
        "background"   : "inputs/universe.jpeg",
        "output_video" : "outputs/asteroidFinal.mp4",
        "fps"          : 25,
    },

    # ── Green Screen HSV Thresholds ──
    # Tune these if your green screen colour is slightly off
    "lower_green" : [36, 120,  70],
    "upper_green" : [80, 255, 255],

    # ── Morphology settings ──
    "morph_kernel_size" : 3,
    "dilate_iterations" : 2,
}


# ─────────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────

def load_video(path: str) -> cv2.VideoCapture:
    """Open a video file; exit with a clear message if it fails."""
    if not os.path.exists(path):
        print(f"[ERROR] Video file not found: {path}")
        sys.exit(1)
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        print(f"[ERROR] Could not open video: {path}")
        sys.exit(1)
    print(f"[INFO]  Loaded video  → {path}")
    return cap


def load_background(path: str, width: int, height: int) -> np.ndarray:
    """Load and resize a background image to match the video frame size."""
    if not os.path.exists(path):
        print(f"[ERROR] Background image not found: {path}")
        sys.exit(1)
    bg = cv2.imread(path)
    bg = cv2.resize(bg, (width, height))
    print(f"[INFO]  Loaded background → {path}  |  resized to ({width}x{height})")
    return bg


def create_writer(path: str, fps: int, width: int, height: int) -> cv2.VideoWriter:
    """Create an MP4 VideoWriter for the given output path."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(path, fourcc, fps, (width, height))
    print(f"[INFO]  Output video  → {path}")
    return writer


def build_green_mask(
    frame       : np.ndarray,
    lower_green : np.ndarray,
    upper_green : np.ndarray,
    kernel_size : int = 3,
    dilate_iter : int = 2,
) -> np.ndarray:
    """
    Convert a BGR frame to HSV, apply a green colour threshold,
    then clean up the mask with morphological operations.

    Returns
    -------
    mask : np.ndarray
        Binary mask where 255 = green screen pixel, 0 = foreground pixel.
    """
    # Step 1 — convert to HSV (green is easier to isolate here)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Step 2 — median blur to suppress noise before thresholding
    blurred = cv2.medianBlur(hsv, kernel_size)

    # Step 3 — threshold to isolate green pixels
    mask = cv2.inRange(blurred, lower_green, upper_green)

    # Step 4 — morphological opening: removes small isolated noise blobs
    kernel  = np.ones((kernel_size, kernel_size), np.uint8)
    mask    = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Step 5 — dilation: expands mask slightly to cover fringe/edge pixels
    mask    = cv2.dilate(mask, kernel, iterations=dilate_iter)

    return mask


def composite_frame(
    frame      : np.ndarray,
    background : np.ndarray,
    mask       : np.ndarray,
) -> np.ndarray:
    """
    Composite a foreground frame onto a background image using the green mask.

    Steps
    -----
    1. Extract background pixels where mask is active (green regions).
    2. Zero-out those same green regions in the foreground frame.
    3. Add the two layers together → final composite.

    Parameters
    ----------
    frame      : BGR video frame (foreground)
    background : BGR background image (same size as frame)
    mask       : Binary mask — 255 where green screen is detected

    Returns
    -------
    composite  : np.ndarray — final composited frame
    """
    # Background layer: visible only through green screen regions
    bg_layer = cv2.bitwise_and(background, background, mask=mask)

    # Foreground layer: black out the green pixels
    fg_layer = frame.copy()
    fg_layer[mask > 100] = (0, 0, 0)

    # Combine: background fills in exactly where foreground was zeroed
    composite = cv2.add(bg_layer, fg_layer)
    return composite


def process_video(cfg: dict, lower_green: np.ndarray, upper_green: np.ndarray) -> None:
    """
    Full pipeline for a single green screen video.

    Parameters
    ----------
    cfg         : dict with keys: input_video, background, output_video, fps
    lower_green : HSV lower bound for green
    upper_green : HSV upper bound for green
    """
    label = os.path.basename(cfg["input_video"])
    print(f"\n{'─'*55}")
    print(f"  Processing: {label}")
    print(f"{'─'*55}")

    # ── Open video ──────────────────────────────────────────
    cap         = load_video(cfg["input_video"])
    ret, frame  = cap.read()
    if not ret:
        print("[ERROR] Could not read the first frame. Check the video file.")
        cap.release()
        return

    h, w = frame.shape[:2]
    print(f"[INFO]  Frame size: {w}x{h}")

    # ── Load background ──────────────────────────────────────
    background  = load_background(cfg["background"], w, h)

    # ── Create output writer ─────────────────────────────────
    writer      = create_writer(cfg["output_video"], cfg["fps"], w, h)

    # ── Morphology config ────────────────────────────────────
    kernel_size = CONFIG["morph_kernel_size"]
    dilate_iter = CONFIG["dilate_iterations"]

    # ── Main processing loop ─────────────────────────────────
    frame_count = 0
    print("[INFO]  Processing frames…")

    while ret:
        mask      = build_green_mask(frame, lower_green, upper_green, kernel_size, dilate_iter)
        composite = composite_frame(frame, background, mask)
        writer.write(composite)

        frame_count += 1
        if frame_count % 100 == 0:
            print(f"          → {frame_count} frames written")

        ret, frame = cap.read()

    # ── Cleanup ──────────────────────────────────────────────
    cap.release()
    writer.release()
    print(f"[✓] Done!  {frame_count} frames saved → {cfg['output_video']}")


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main():
    # Build HSV numpy arrays from config
    lower_green = np.array(CONFIG["lower_green"], dtype=np.uint8)
    upper_green = np.array(CONFIG["upper_green"], dtype=np.uint8)

    print("=" * 55)
    print("  Chroma Keying — Green Screen Replacement")
    print("=" * 55)
    print(f"  Green HSV range:  {CONFIG['lower_green']}  →  {CONFIG['upper_green']}")

    # ── Process both videos ──────────────────────────────────
    process_video(CONFIG["video1"], lower_green, upper_green)
    process_video(CONFIG["video2"], lower_green, upper_green)

    print("\n" + "=" * 55)
    print("  All videos processed successfully! 🎬")
    print("=" * 55)


if __name__ == "__main__":
    main()
