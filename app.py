from flask import Flask, render_template, request, jsonify
from process_command import processCommand

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message.strip():
        return jsonify({"reply": "Please type something."})

    try:
        reply = processCommand(user_message)
    except Exception as e:
        reply = f"⚠️ Error: {str(e)}"

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
