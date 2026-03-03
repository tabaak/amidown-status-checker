import httpx
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()
handler = Mangum(app)

@app.get("/check")
async def check_url(url: str = None):
    return {"url": url, "is_up": True}
    
