from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "Railway Proxy Server is Running! Use /proxy?url=YOUR_URL"

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return "Usage: /proxy?url=http://example.com", 400
    
    try:
        # Forward request with headers
        response = requests.get(url, headers={'User-Agent': request.headers.get('User-Agent')}, stream=True)

        # Handle different content types correctly
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for name, value in response.headers.items() if name.lower() not in excluded_headers]

        return Response(response.content, response.status_code, headers)
    
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
