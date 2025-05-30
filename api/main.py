from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import boto3
import os

app = FastAPI()

s3_bucket_name = os.environ.get("S3_BUCKET_NAME")
s3_client = boto3.client("s3")

dynamodb_table_name = os.environ.get("DYNAMODB_TABLE_NAME")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(dynamodb_table_name) if dynamodb_table_name else None

@app.get("/")
async def read_root():
  return HTMLResponse("<h1>Hello from FastAPI on Fargate!</h1>")

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
  if not s3_bucket_name:
    return {"message": "S3 Bucket Name is not configured."}
  try:
    s3_client.upload_fileobj(file.file, s3_bucket_name, file.filename)
    return {"filename": file.filename, "message": "File uploaded successfully!"}
  except Exception as e:
    return {"message": f"File upload failed: {e}"}

@app.get("/items/{item_id}")
async def read_item(item_id: str):
  if not table:
    return {"message": "DynamoDB Table Name is not configured."}
  try:
    response = table.get_item(Key={'id': item_id})
    item = response.get('Item')
    if item:
      return item
    else:
      return {"message": "Item not found"}
  except Exception as e:
    return {"message": f"Error retrieving item: {e}"}

@app.post("/items/")
async def create_item(item: dict):
  if not table:
    return {"message": "DynamoDB Table Name is not configured."}
  try:
    table.put_item(Item=item)
    return {"message": "Item created successfully!", "item": item}
  except Exception as e:
    return {"message": f"Error creating item: {e}"}
