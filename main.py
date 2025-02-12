import logging
import time
import random
import requests
import redis
from flask import Flask, request, jsonify, Response
from requests_html import HTMLSession
from flask_cors import CORS
from aiohttp import ClientSession, ClientTimeout, ClientError
import asyncio
import hashlib
import os

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing (CORS)

# Redis Configuration for Persistent Caching
cache = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# Proxy Pool Configuration (example IPs)
PROXY_POOL = [
    "http://user:pass@proxy1.com:8080",
    "http://user:pass@proxy2.com:8080",
    "http://user:pass@proxy3.com:8080"
]

# Rate limiting setup
user_requests = {}

# Time interval for rate limiting (in seconds)
RATE_LIMIT_INTERVAL = 60  # 1 minute
MAX_REQUESTS = 10  # max requests per minute

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function for rate limiting
def check_rate_limit(ip):
    current_time = time.time()
    if ip not in user_requests:
        user_requests[ip] = [current_time]
        return True

    user_requests[ip] = [timestamp for timestamp in user_requests[ip] if current_time - timestamp < RATE_LIMIT_INTERVAL]

    if len(user_requests[ip]) < MAX_REQUESTS:
        user_requests[ip].append(current_time)
        return True
    return False

# Asynchronous request handler for speed
async def fetch_url(session, url, proxy=None):
    try:
        headers = {
            "User-Agent": random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0"
            ]),
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://google.com"
        }
        timeout = ClientTimeout(total=10)
        proxy = random.choice(PROXY_POOL) if proxy is None else proxy
        async with session.get(url, headers=headers, proxy=proxy, timeout=timeout) as resp:
            return await resp.text()
    except ClientError as e:
        logger.error(f"Error fetching URL: {str(e)}")
        return None

@app.route('/')
def proxy():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Usage: /?url=http://example.com"}), 400

    # Cache check
    cached_response = cache.get(url)
    if cached_response:
        logger.info(f"Cache hit for {url}")
        return Response(cached_response, content_type='text/html')

    # Rate limiting
    ip = request.remote_addr
    if not check_rate_limit(ip):
        return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429

    # Fetch the URL asynchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async with ClientSession() as session:
        response_text = loop.run_until_complete(fetch_url(session, url))

    if response_text:
        # Cache the response
        cache.setex(url, 3600, response_text)  # Cache for 1 hour
        return Response(response_text, content_type='text/html')
    else:
        return jsonify({"error": "Failed to fetch URL, please try again."}), 500

@app.route('/clear_cache', methods=['POST'])
def clear_cache():
    cache.flushdb()  # Clears all cache
    logger.info("Cache cleared")
    return jsonify({"message": "Cache cleared successfully!"})

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Error: {str(e)}")
    return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
