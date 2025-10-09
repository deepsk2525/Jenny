from flask import Flask, render_template, request, jsonify
from process_command import processCommand

app = Flask(__name__)


@app.route("/")
def home():
    """Render the main chat interface."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def handle_chat():
    """Receive user message and return Jenny's reply."""
    payload = request.get_json(silent=True) or {}
    message = payload.get("message", "").strip()

    if not message:
        return jsonify({"reply": "Please enter a message before sending."})

    try:
        response_text = processCommand(message)
    except Exception as error:
        # Log or handle unexpected errors gracefully
        response_text = f"Something went wrong: {error}"

    return jsonify({"reply": response_text})


if __name__ == "__main__":
    # Run in debug mode for development only
    app.run(host="0.0.0.0", port=5000, debug=True)
