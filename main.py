from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
import httpx
import base64
from urllib.parse import urljoin
from bs4 import BeautifulSoup  # pip install beautifulsoup4

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """トップページ（匿名ビューUI）"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/proxy/")
async def proxy(encoded_url: str = Query(..., description="Base64エンコードされたURL")):
    """Base64デコードしてプロキシ経由で取得、相対パスを絶対URL化"""
    try:
        # Base64デコード
        decoded_bytes = base64.urlsafe_b64decode(encoded_url.encode())
        decoded_url = decoded_bytes.decode()

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": ""
        }
        async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
            resp = await client.get(decoded_url)

        content_type = resp.headers.get("content-type", "text/html", "")
        html_content = resp.text

        # HTMLの場合は相対パスを絶対URLに変換
        if "text/html" in content_type:
            soup = BeautifulSoup(html_content, "html.parser")

            # img, script, link の src/href を絶対URL化
            for tag in soup.find_all(["img", "script"]):
                if tag.has_attr("src"):
                    tag["src"] = urljoin(decoded_url, tag["src"])
            for tag in soup.find_all("link"):
                if tag.has_attr("href"):
                    tag["href"] = urljoin(decoded_url, tag["href"])

            html_content = str(soup)

        return Response(
            content=html_content,
            media_type=content_type,
            headers={"X-Frame-Options": "ALLOWALL"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {e}")
