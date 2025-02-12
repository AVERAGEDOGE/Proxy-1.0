from flask import Flask, request, Response
import aiohttp
import asyncio
import random
import os

app = Flask(__name__)

# ✅ Rotating User-Agents to Avoid Blocks
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
]

async def fetch_url(url):
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            
            async with session.get(url, headers=headers) as response:
                content = await response.read()
                content_type = response.headers.get("Content-Type", "text/html")
                return Response(content, status=response.status, headers={"Content-Type": content_type})
    
    except Exception as e:
        return Response(f"Error: {str(e)}", status=500)

@app.route("/")
def home():
    return "🚀 Proxy is Running! Use /proxy?url=YOUR_URL"

@app.route("/proxy")
def proxy():
    url = request.args.get("url")
    if not url:
        return "Usage: /proxy?url=http://example.com", 400
    return asyncio.run(fetch_url(url))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
