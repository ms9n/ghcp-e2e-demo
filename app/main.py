import os
import threading

from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from error_reporter import report_error_sync

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify(
        {
            "app": "ghcp-e2e-demo",
            "status": "running",
            "endpoints": {
                "/": "This page",
                "/health": "Health check",
                "/calculate": "Calculate division (params: a, b)",
            },
        }
    )


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/calculate")
def calculate():
    a = request.args.get("a", type=float)
    b = request.args.get("b", type=float)

    if a is None or b is None:
        return jsonify({"error": "Both 'a' and 'b' query parameters are required"}), 400

    # BUG: No zero-division guard — this will crash when b=0
    result = a / b

    return jsonify({"a": a, "b": b, "result": result})


@app.errorhandler(Exception)
def handle_exception(error):
    context = {
        "url": request.url,
        "method": request.method,
        "args": dict(request.args),
        "endpoint": request.endpoint,
    }

    threading.Thread(
        target=report_error_sync, args=(error, context), daemon=True
    ).start()

    return (
        jsonify(
            {
                "error": type(error).__name__,
                "message": str(error),
                "detail": "This error has been automatically reported.",
            }
        ),
        500,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
