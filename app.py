from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
import os

app = Flask(__name__)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/")
def home():
    return render_template("index.html")
    
@app.route('/ads.txt')
def ads():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'ads.txt')
    
@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    topic = data.get("topic", "")
    num_questions = data.get("num_questions", 5)
    difficulty = data.get("difficulty", "easy")

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

    try:
        response = model.generate_content(prompt)
        return jsonify({"quiz": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
