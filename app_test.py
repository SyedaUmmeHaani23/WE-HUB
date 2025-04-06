"""
Simple test application to verify web server accessibility.
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>Test Application</h1><p>This is a simple test to verify web server accessibility.</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)