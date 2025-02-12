from flask import Flask, request, Response
import requests
from urllib.parse import urlparse, urljoin
import re

app = Flask(__name__)

# Function to rewrite URLs inside HTML pages
def rewrite_html(html_content, base_url):
    html_content = re.sub(r'href="(/[^"]*)"', lambda m: f'href="/proxy?url={urljoin(base_url, m.group(1))}"', html_content)
    html_content = re.sub(r'src="(/[^"]*)"', lambda m: f'src="/proxy?url={urljoin(base_url, m.group(1))}"', html_content)
    return html_content

@app.route('/')
def home():
    return "🚀 Proxy is Running! Use /proxy?url=YOUR_URL"

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return "Usage: /proxy?url=http://example.com", 400
    
    try:
        # Forward user headers & cookies
        headers = {key: value for key, value in request.headers if key.lower() not in ['host']}
        response = requests.get(url, headers=headers, cookies=request.cookies, stream=True)

        # Detect content type
        content_type = response.headers.get('Content-Type', '')
        content = response.content

        # If it's an HTML page, rewrite the links
        if 'text/html' in content_type:
            content = content.decode('utf-8')
            content = rewrite_html(content, url)
            content = content.encode('utf-8')

        # Exclude problem headers
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for name, value in response.headers.items() if name.lower() not in excluded_headers]

        return Response(content, response.status_code, headers)
    
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

