from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "Railway Proxy Server is Running!"

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return "Usage: /proxy?url=http://example.com", 400
    
    try:
        response = requests.get(url)
        return response.content, response.status_code, response.headers.items()
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
