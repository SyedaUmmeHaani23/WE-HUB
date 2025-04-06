"""
Simple test application for web feedback tool testing.
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simple Test</title>
    </head>
    <body>
        <h1>Simple Test Page</h1>
        <p>This is a simple test page to verify that the web feedback tool can access the application.</p>
    </body>
    </html>
    """

if __name__ == "__main__":
    print("Starting simple test app on port 8080...")
    app.run(host="0.0.0.0", port=8080, debug=True)