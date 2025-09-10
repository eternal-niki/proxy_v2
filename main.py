from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
import httpx
from urllib.parse import unquote

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """トップページ（匿名ビューUI）"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/proxy/")
async def proxy(url: str = Query(..., description="エンコードされたURL")):
    """URLをデコードしてプロキシ経由で取得"""
    try:
        decoded_url = unquote(url)
        headers = {
            "User-Agent": "Mozilla/5.0",  # 匿名ビュー風
            "Referer": ""
        }
        async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
            resp = await client.get(decoded_url)
        
        # iframe対応 & content-type維持
        return Response(
            content=resp.content,
            media_type=resp.headers.get("content-type", "text/html"),
            headers={"X-Frame-Options": "ALLOWALL"}
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {e}")
