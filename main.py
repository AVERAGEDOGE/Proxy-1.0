from flask import Flask, request, Response
import aiohttp
import asyncio
import random

app = Flask(__name__)

# ✅ Rotating User-Agents to Avoid Blocking
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
]

# ✅ Proxy IPs (Optional: Use if you want multiple IPs)
PROXY_LIST = [
    "http://your-proxy-ip:port",
    "http://another-proxy-ip:port"
]

async def fetch_url(url):
    async with aiohttp.ClientSession() as session:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        
        proxy = random.choice(PROXY_LIST) if PROXY_LIST else None  # Use a proxy if available
        
        async with session.get(url, headers=headers, proxy=proxy) as response:
            content = await response.read()
            return Response(content, status=response.status, headers=dict(response.headers))

@app.route("/")
def home():
    return "🚀 Advanced Proxy is Running! Use /proxy?url=YOUR_URL"

@app.route("/proxy")
async def proxy():
    url = request.args.get("url")
    if not url:
        return "Usage: /proxy?url=http://example.com", 400
    return await fetch_url(url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
