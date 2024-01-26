from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles 
from pydantic import BaseModel
from typing import Optional

from image_search import *

app = FastAPI()
# Mount a static directory to serve images from
app.mount("/images", StaticFiles(directory="image_data"), name="images")

class SearchRequest(BaseModel):
    text: str
    k: Optional[int] = None


# Ingest endpoint
@app.get("/api/ingest")
async def ingest():
    # Your logic for the ingest endpoint goes here
    return {"message": "Ingest successful"}


# Search endpoint
@app.post("/api/search")
async def search(request: SearchRequest):
    # Your logic for the search endpoint goes here
    # You can access the search text and k using request.text and request.k
    return {"message": "Search successful", "text": request.text, "k": request.k}


# Run the server using Uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
