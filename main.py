from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    target_url = f"https://{path}" if "http" not in path else path
    try:
        resp = requests.get(target_url, headers=request.headers, stream=True)
        response = Response(resp.content, resp.status_code)
        for key, value in resp.headers.items():
            response.headers[key] = value
        return response
    except requests.exceptions.RequestException:
        return "Error: Could not connect to target site.", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
