from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
import os
import logging
from flask_cors import CORS

# Initialize Flask
app = Flask(__name__)
CORS(app)  # Optional: Allow JS frontend to talk to this API

# Logging setup
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Safety check
if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found. Set it in .env or Render environment.")

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()

        topic = data.get("topic", "").strip()
        num_questions = int(data.get("num_questions", 5))
        difficulty = data.get("difficulty", "easy").lower()

        # Simple validation
        if not topic:
            return jsonify({"error": "Topic is required"}), 400
        if num_questions < 1 or num_questions > 20:
            return jsonify({"error": "Choose between 1 and 20 questions"}), 400
        if difficulty not in ["easy", "medium", "hard"]:
            return jsonify({"error": "Difficulty must be easy, medium, or hard"}), 400

        prompt = f"""
        Generate {num_questions} multiple-choice questions on the topic: "{topic}".
        Difficulty level: {difficulty}.

        Each question must have 4 options (A–D) and clearly indicate the correct answer.

        Format:
        1. Question?
           A) Option A
           B) Option B
           C) Option C
           D) Option D
           ✅ Answer: Option C
        """

        response = model.generate_content(prompt)
        output = getattr(response, "text", None)

        if output:
            return jsonify({"quiz": output})
        else:
            return jsonify({"error": "Empty response from Gemini"}), 500

    except Exception as e:
        logging.exception("❌ Error generating quiz:")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(500)
def handle_500(error):
    return jsonify({"error": "Something went wrong on the server"}), 500

if __name__ == "__main__":
    app.run(debug=True)
