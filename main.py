from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
import httpx
import base64

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """トップページ（匿名ビューUI）"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/proxy/")
async def proxy(encoded_url: str = Query(..., description="Base64エンコードされたURL")):
    """Base64デコードしてプロキシ経由で取得"""
    try:
        decoded_bytes = base64.urlsafe_b64decode(encoded_url.encode())
        decoded_url = decoded_bytes.decode()

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": ""
        }
        async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
            resp = await client.get(decoded_url)
        
        return Response(
            content=resp.content,
            media_type=resp.headers.get("content-type", "text/html"),
            headers={"X-Frame-Options": "ALLOWALL"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {e}")
