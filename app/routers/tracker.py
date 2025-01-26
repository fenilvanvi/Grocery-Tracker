import base64
import datetime
from typing import Annotated

from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Body

from app.config import logger
from app.controllers.tracker import process_image_with_gpt4o, get_results_from_query
from app.dao.mongo import get_mongo_connection
from app.models.tracker import UploadResponse, QueryRequest

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_image(user_id: str = Form(...), file: UploadFile = File(...)):
    try:
        # Read image file
        image_bytes = await file.read()
        base64_encoded_image = base64.b64encode(image_bytes).decode("utf-8")

        # Process the image with GPT-4o
        data = await process_image_with_gpt4o(base64_encoded_image)

        mongo_db = get_mongo_connection()
        collection = mongo_db["groceries"]
        document = {
            "user_id": int(user_id),
            "bill_date": data["bill_date"],
            "bill_total": data["bill_total"],
            "items": data["items"],
            "timestamp": datetime.datetime.now(datetime.timezone.utc),
        }

        # Insert the document into the groceries collection
        collection.insert_one(document)

        return UploadResponse(
            message="Data extracted and stored successfully.",
            data=data,
        )
    except Exception as e:
        logger.error(f"Internal Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
async def execute_query(req_body: QueryRequest):
    try:
        results = await get_results_from_query(req_body.query, req_body.user_id)

        return {
            "message": "Query executed successfully.",
            "results": results,
        }

    except Exception as e:
        logger.error(f"Internal Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
