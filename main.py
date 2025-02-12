from flask import Flask, request, Response
import aiohttp
import asyncio
import random
import re
import os

app = Flask(__name__)

# ✅ Rotating User-Agents to Avoid Blocks
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
]

# ✅ Rewrite links so they stay inside the proxy
def rewrite_links(content, target_url):
    try:
        base_url = "/proxy?url="
        # Convert absolute URLs (like https://en.wikipedia.org/page) into proxied links
        content = re.sub(
            r'href="https?://([^"]+)"', 
            lambda match: f'href="{base_url}https://{match.group(1)}"',
            content
        )
        # Convert relative URLs (like /wiki/Example) into proxied links
        content = re.sub(
            r'href="(/[^"]*)"', 
            lambda match: f'href="{base_url}{target_url.rstrip("/")}{match.group(1)}"',
            content
        )
        return content
    except:
        return content

async def fetch_url(url):
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            
            async with session.get(url, headers=headers) as response:
                content = await response.text()
                content_type = response.headers.get("Content-Type", "text/html")
                
                # Rewrite links so they stay inside the proxy
                if "text/html" in content_type:
                    content = rewrite_links(content, url)

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
