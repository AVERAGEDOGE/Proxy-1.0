from flask import Flask, request, Response
import requests
from urllib.parse import urlparse, urljoin

app = Flask(__name__)

@app.route('/')
def home():
    return "🚀 Railway Proxy is Running! Use /proxy?url=YOUR_URL"

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return "Usage: /proxy?url=http://example.com", 400
    
    try:
        # Forward request with headers and cookies
        headers = {key: value for key, value in request.headers if key.lower() not in ['host']}
        response = requests.get(url, headers=headers, cookies=request.cookies, stream=True)

        # Rewrite HTML to fix links (so images, CSS, and JS load correctly)
        content_type = response.headers.get('Content-Type', '')
        content = response.content

        if 'text/html' in content_type:
            content = content.decode('utf-8')
            content = content.replace('href="/', f'href="/proxy?url={urljoin(url, "/")}')
            content = content.replace('src="/', f'src="/proxy?url={urljoin(url, "/")}')
            content = content.encode('utf-8')

        # Remove certain headers that can cause issues
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for name, value in response.headers.items() if name.lower() not in excluded_headers]

        return Response(content, response.status_code, headers)
    
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
