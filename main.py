import os
from uuid import uuid4

import boto3
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

# Initialize app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# S3 client
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "noticefiles")
s3_client = boto3.client("s3")

@app.post("/upload-to-s3")
async def upload_to_s3(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        return JSONResponse(
            status_code=400,
            content={"error": "Only PDF files are allowed"}
        )

    try:
        # Read file content
        contents = await file.read()

        # Generate unique filename
        unique_filename = f"{uuid4()}_{file.filename}"

        # Upload to S3
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=unique_filename,
            Body=contents,
            ContentType=file.content_type
        )

        return JSONResponse(
            status_code=200,
            content={"message": "File uploaded to S3", "s3_key": unique_filename}
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Upload failed", "details": str(e)}
        )

# Create handler for AWS Lambda
handler = Mangum(app)
