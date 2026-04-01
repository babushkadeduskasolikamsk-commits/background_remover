#!/usr/bin/env python3
import argparse
from pathlib import Path
from PIL import Image
from rembg import remove, new_session
import time

SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}

# Available models: u2netp (fastest), birefnet-general-lite (balanced), birefnet-general (slowest/best)
MODEL_SPEED_MAP = {
    "fastest": "u2netp",
    "balanced": "birefnet-general-lite", 
    "best": "birefnet-general"
}

def process_folder(input_folder: str, output_folder: str, model_name: str):
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    image_files = [f for f in input_path.iterdir() if f.suffix.lower() in SUPPORTED_EXTENSIONS]
    
    if not image_files:
        print(f"No supported images found in {input_folder}")
        return
    
    print(f"Found {len(image_files)} images. Loading model: {model_name}...")
    session = new_session(model_name)
    
    for i, img_file in enumerate(image_files, 1):
        print(f"[{i}/{len(image_files)}] Processing: {img_file.name}")
        try:
            input_img = Image.open(img_file)
            start = time.time()
            output_img = remove(input_img, session=session)
            elapsed = time.time() - start
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
    parser.add_argument("--model", "-m", default="balanced", 
                        choices=["fastest", "balanced", "best"],
                        help="Model speed: fastest (u2netp), balanced (birefnet-general-lite), best (birefnet-general)")
    args = parser.parse_args()
    
    model_name = MODEL_SPEED_MAP[args.model]
    process_folder(args.input, args.output, model_name)