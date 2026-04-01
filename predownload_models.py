#!/usr/bin/env python3
import argparse
import logging
import os
from pathlib import Path

from PIL import Image
from rembg import new_session, remove

MODEL_SPEED_MAP = {
    "fastest": "u2netp",
    "balanced": "birefnet-general-lite",
    "best": "birefnet-general",
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("predownload-models")


def predownload_models(models_dir: Path) -> None:
    models_dir.mkdir(parents=True, exist_ok=True)
    os.environ["U2NET_HOME"] = str(models_dir.resolve())

    sample_image = Image.new("RGB", (1, 1), color=(255, 255, 255))

    logger.info("Downloading models into %s", models_dir.resolve())
    for speed_name, model_name in MODEL_SPEED_MAP.items():
        logger.info("Preparing model speed=%s model=%s", speed_name, model_name)
        session = new_session(model_name)
        remove(sample_image, session=session)
        logger.info("Model ready speed=%s model=%s", speed_name, model_name)

    logger.info("All models are downloaded and warmed up in %s", models_dir.resolve())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pre-download rembg models for Docker image builds")
    parser.add_argument(
        "--models-dir",
        default="./models",
        help="Local folder where downloaded models are stored (default: ./models)",
    )
    args = parser.parse_args()

    predownload_models(Path(args.models_dir))
