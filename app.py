from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
import google.generativeai as genai
import logging
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# Load API Key from environment
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCCleVyIBEtjUsRxKz1_CPOhEaB0DzOG6U")

if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY is missing. Set it in .env or Render environment.")

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_quiz():
    try:
        data = request.get_json()

        topic = data.get("topic", "").strip()
        num_questions = int(data.get("num_questions", 5))
        difficulty = data.get("difficulty", "easy").lower()

        # Input Validation
        if not topic:
            return jsonify({"error": "❗ Topic is required"}), 400
        if not (1 <= num_questions <= 20):
            return jsonify({"error": "❗ Number of questions must be between 1 and 20"}), 400
        if difficulty not in ["easy", "medium", "hard"]:
            return jsonify({"error": "❗ Difficulty must be easy, medium, or hard"}), 400

        # Optimized fast prompt
        prompt = f"""
        Generate {num_questions} multiple choice questions on the topic "{topic}".
        Difficulty: {difficulty}.

        Each question should have:
        - A question
        - 4 options (A to D)
        - Correct answer at the end in the format: Answer: A

        Format:
        Q: What is...?
        A. Option A
        B. Option B
        C. Option C
        D. Option D
        Answer: A
        """

        response = model.generate_content(prompt)
        output = getattr(response, "text", "").strip()

        if output:
            return jsonify({"quiz": output})
        else:
            return jsonify({"error": "⚠️ Empty response from Gemini"}), 500

    except Exception as e:
        logging.exception("❌ Error generating quiz:")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.errorhandler(500)
def handle_server_error(error):
    return jsonify({"error": "🚨 Internal Server Error"}), 500

if __name__ == "__main__":
    app.run(debug=True)
