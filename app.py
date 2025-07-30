from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
import os

# Initialize Flask
app = Flask(__name__)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Check if API key is loaded correctly
if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found. Set it in .env or Render environment.")

# Configure Gemini API
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()
        topic = data.get("topic", "")
        num_questions = data.get("num_questions", 5)
        difficulty = data.get("difficulty", "easy")

        # Build prompt
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

        # Generate content using Gemini API
        response = model.generate_content(prompt)

        # Some versions return response.text; others may differ
        output = getattr(response, "text", None)
        if output:
            return jsonify({"quiz": output})
        else:
            return jsonify({"error": "Gemini API did not return text"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
