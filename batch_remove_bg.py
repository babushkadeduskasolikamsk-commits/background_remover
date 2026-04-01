#!/usr/bin/env python3
"""
Batch background removal using rembg with BiRefNet model.
Usage: python batch_remove_bg.py --input ./input_images --output ./output_images
"""

import argparse
from pathlib import Path
from PIL import Image
from rembg import remove, new_session
import time

SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}

def process_folder(input_folder: str, output_folder: str):
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    
    # Create output folder if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all image files
    image_files = [f for f in input_path.iterdir() if f.suffix.lower() in SUPPORTED_EXTENSIONS]
    
    if not image_files:
        print(f"No supported images found in {input_folder}")
        return
    
    print(f"Found {len(image_files)} images. Loading BiRefNet model...")
    
    # Initialize BiRefNet session (downloads model on first run)
    session = new_session("birefnet-general")
    
    for i, img_file in enumerate(image_files, 1):
        print(f"[{i}/{len(image_files)}] Processing: {img_file.name}")
        try:
            # Open image
            input_img = Image.open(img_file)
            # Remove background
            start = time.time()
            output_img = remove(input_img, session=session)
            elapsed = time.time() - start
            # Save as PNG (supports transparency)
            output_file = output_path / f"{img_file.stem}_nobg.png"
            output_img.save(output_file, "PNG")
            print(f"    Saved to {output_file} ({elapsed:.2f}s)")
        except Exception as e:
            print(f"    Error processing {img_file.name}: {e}")
    
    print("Batch processing complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch remove background from images")
    parser.add_argument("--input", "-i", required=True, help="Input folder containing images")
    parser.add_argument("--output", "-o", required=True, help="Output folder for transparent PNGs")
    args = parser.parse_args()
    
    process_folder(args.input, args.output)