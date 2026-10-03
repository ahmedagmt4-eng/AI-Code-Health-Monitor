from flask import Flask, render_template, request
from analyzer import analyze_code
from ai_model import predict

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 512 * 1024

EXAMPLE_CODE = '''def calculate_total(items):\n    total = 0\n    for item in items:\n        if item["active"]:\n            if item["type"] == "A":\n                total += item["price"]\n            elif item["type"] == "B":\n                total += item["price"] * 0.9\n            else:\n                total += item["price"]\n    return total\n'''


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", example_code=EXAMPLE_CODE)


@app.route("/analyze", methods=["POST"])
def analyze():
    source = request.form.get("code", "")
    result = analyze_code(source)
    if result.get("valid"):
        try:
            result["ai"] = predict(result["features"])
        except Exception as exc:
            result["ai"] = {"label": "Unavailable", "confidence": None, "error": str(exc)}
    return render_template("results.html", result=result, source=source)


@app.errorhandler(413)
def too_large(_error):
    return render_template("index.html", example_code=EXAMPLE_CODE, error="The submitted code is too large. Please keep it below 512 KB."), 413


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
