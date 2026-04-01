#!/usr/bin/env python3
import io
import logging
from typing import Dict

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from PIL import Image
from rembg import new_session, remove

MODEL_SPEED_MAP: Dict[str, str] = {
    "fastest": "u2netp",
    "balanced": "birefnet-general-lite",
    "best": "birefnet-general",
}

logger = logging.getLogger("background-remover-api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(title="Background Remover API", version="1.0.0")


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.post("/remove-background")
async def remove_background(
    requestId: str = Form(...),
    model: str = Form("balanced"),
    image: UploadFile = File(...),
):
    logger.info("started requestId=%s model=%s filename=%s", requestId, model, image.filename)

    try:
        model_name = MODEL_SPEED_MAP.get(model)
        if not model_name:
            allowed = ", ".join(MODEL_SPEED_MAP.keys())
            raise HTTPException(status_code=400, detail=f"Invalid model '{model}'. Allowed: {allowed}")

        image_bytes = await image.read()
        input_image = Image.open(io.BytesIO(image_bytes))

        session = new_session(model_name)
        output_image = remove(input_image, session=session)

        output_buffer = io.BytesIO()
        output_image.save(output_buffer, format="PNG")
        output_buffer.seek(0)

        logger.info("finished requestId=%s", requestId)
        return StreamingResponse(output_buffer, media_type="image/png")

    except HTTPException as err:
        logger.exception("error requestId=%s detail=%s", requestId, err.detail)
        raise
    except Exception:
        logger.exception("error requestId=%s", requestId)
        raise HTTPException(status_code=500, detail="Failed to remove background")
