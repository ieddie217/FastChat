import logging
import os
from urllib.request import Request
import time, uuid, logging
from fastapi import FastAPI
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()
# LOAD FROM ENV
AZURE_ENDPOINT  = os.getenv("ENDPOINT")
AZURE_KEY  = os.getenv("KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
DEPLOYMENT  = os.getenv("DEPLOYMENT")
API_VERSION  = os.getenv("API_VERSION")

# LOGGING
logger = logging.getLogger("app")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
handler.setFormatter(formatter)
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(handler)

app = FastAPI(title="AI Chat API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
client = AsyncAzureOpenAI(
    api_version=API_VERSION ,
    azure_endpoint=AZURE_ENDPOINT ,
    api_key=AZURE_KEY ,
)
# Middle ware that runs for every request, so good for logging
@app.middleware("http")
async def add_logging(request: Request, call_next):
    cid = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    logger.info(f"Request ID: {cid} - {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Request ID: {cid} - Response status: {response.status_code}")
    return response

@app.get("/ask")
async def ask_question(question: str):
    response = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": question,
            }
        ],
        max_tokens=16384,
        temperature=1.0,
        top_p=1.0,
        model=MODEL_NAME
    )
    return {"response": response.choices[0].message.content
    }