from flask import Flask, request, Response
import requests
from random import choice

app = Flask(__name__)

# Rotating User-Agents to Avoid Blocking
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
]

@app.route("/")
def home():
    return "🚀 Proxy is Running! Use /proxy?url=YOUR_URL"

@app.route("/proxy")
def proxy():
    url = request.args.get("url")
    if not url:
        return "Usage: /proxy?url=http://example.com", 400
    
    try:
        headers = {
            "User-Agent": choice(USER_AGENTS),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
        }
        response = requests.get(url, headers=headers, stream=True)

        # Fix: Ensure content type is correct
        content_type = response.headers.get("Content-Type", "text/html")
        
        return Response(response.content, status=response.status_code, content_type=content_type)

    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
