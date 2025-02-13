from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "Proxy is running! Use /proxy?url=your_url to access."

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return "Error: No URL provided", 400
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        return response.content, response.status_code, response.headers.items()
    except requests.RequestException as e:
        return f"Request failed: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
