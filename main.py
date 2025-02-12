import logging
import random
from flask import Flask, request, jsonify, Response
import requests

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Proxy pool (example proxies)
PROXY_POOL = [
    "http://user:pass@proxy1.com:8080",
    "http://user:pass@proxy2.com:8080",
    "http://user:pass@proxy3.com:8080"
]

@app.route('/')
def proxy():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Usage: /?url=http://example.com"}), 400

    # Randomly pick a proxy from the pool (for better anonymity)
    proxy = random.choice(PROXY_POOL)

    try:
        response = requests.get(url, proxies={"http": proxy, "https": proxy})
        response.raise_for_status()  # Check if the request was successful

        return Response(response.content, content_type='text/html')

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching URL: {str(e)}")
        return jsonify({"error": "Failed to fetch URL, please try again."}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Error: {str(e)}")
    return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
