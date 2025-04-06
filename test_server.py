"""
Minimal server for testing connectivity.
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World! This is a test server."

@app.route('/health')
def health():
    return '{"status": "ok"}'

if __name__ == '__main__':
    print("Starting minimal test server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)