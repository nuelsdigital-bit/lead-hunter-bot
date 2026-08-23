import os
import asyncio
from flask import Flask, render_template_string, request, jsonify
from google import genai

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = (
    "You are Lead Hunter AI, an elite, high-end B2B sales strategist, corporate lead generator, "
    "and business consultant specializing in the Nigerian market (especially Abuja: Maitama, Wuse, Utako, Guzape, etc.). "
    "Your users are ambitious professionals, service providers, and real estate entrepreneurs. "
    "Never give generic answers. Provide deep, actionable business intelligence, precise target departments, "
    "culturally tailored Nigerian corporate pitch hooks, objection-handling scripts, and insider market advice "
    "that people would gladly pay a monthly subscription to access. Maintain a professional, sharp, and sharp-witted tone."
)

# HTML template with a clean frontend interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lead Hunter AI - Dashboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .container {
            width: 100%;
            max-width: 600px;
            background: #1e293b;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            margin-top: 20px;
        }
        h1 { font-size: 1.5rem; color: #38bdf8; margin-top: 0; text-align: center; }
        p.subtitle { text-align: center; color: #94a3b8; font-size: 0.9rem; margin-bottom: 20px; }
        textarea {
            width: 100%;
            height: 100px;
            background: #0f172a;
            border: 1px solid #334155;
            color: #fff;
            padding: 12px;
            border-radius: 8px;
            font-size: 1rem;
            resize: vertical;
            box-sizing: border-box;
            margin-bottom: 12px;
        }
        textarea:focus { outline: none; border-color: #38bdf8; }
        button {
            width: 100%;
            background: #0284c7;
            color: white;
            border: none;
            padding: 12px;
            font-size: 1rem;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s;
        }
        button:hover { background: #0369a1; }
        button:disabled { background: #475569; cursor: not-allowed; }
        .response-box {
            margin-top: 20px;
            background: #0f172a;
            border: 1px solid #334155;
            padding: 16px;
            border-radius: 8px;
            white-space: pre-wrap;
            line-height: 1.5;
            display: none;
        }
        .loading { color: #38bdf8; font-style: italic; text-align: center; margin-top: 15px; display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Lead Hunter AI</h1>
        <p class="subtitle">High-End B2B Sales & Real Estate Strategy Engine (Nigeria)</p>
        
        <form id="leadForm">
            <textarea id="userQuery" placeholder="e.g. Give me a strategy and script to pitch a real estate developer in Maitama..."></textarea>
            <button type="submit" id="submitBtn">Generate Strategy</button>
        </form>

        <div id="loading" class="loading">🗣️ Analyzing market data & formulating strategy...</div>
        <div id="responseBox" class="response-box"></div>
    </div>

    <script>
        const form = document.getElementById('leadForm');
        const submitBtn = document.getElementById('submitBtn');
        const loading = document.getElementById('loading');
        const responseBox = document.getElementById('responseBox');
        const userQueryInput = document.getElementById('userQuery');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const query = userQueryInput.value.trim();
            if (!query) return;

            submitBtn.disabled = true;
            loading.style.display = 'block';
            responseBox.style.display = 'none';
            responseBox.innerText = '';

            try {
                const res = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });
                const data = await res.json();
                
                if (data.reply) {
                    responseBox.innerText = data.reply;
                } else {
                    responseBox.innerText = '⚠️ Error: ' + (data.error || 'Unknown error occurred.');
                }
            } catch (err) {
                responseBox.innerText = '⚠️ Network Error: ' + err.message;
            } finally {
                loading.style.display = 'none';
                responseBox.style.display = 'block';
                submitBtn.disabled = false;
            }
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    user_query = data.get("query", "").strip()
    
    if not user_query:
        return jsonify({"error": "Query cannot be empty"}), 400

    try:
        # Generate content via Gemini synchronously for the web route handler
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"{SYSTEM_PROMPT}\n\nUser Request: {user_query}"
        )
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
