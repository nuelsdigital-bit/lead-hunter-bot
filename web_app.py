import os
import time
from flask import Flask, render_template_string, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# Strict short prompt for fast, punchy responses
SYSTEM_PROMPT = (
    "You are Lead Hunter AI, an elite B2B sales strategist for Abuja, Nigeria. "
    "Keep responses extremely short and punchy. "
    "Provide max 3 short action bullet points and ONE short closing pitch script. "
    "No long introductions, no filler. Total response must be under 120 words."
)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lead Hunter AI - Abuja B2B Sales Intelligence</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #0b1120;
            color: #f8fafc;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .container {
            width: 100%;
            max-width: 650px;
            background: #1e293b;
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.6);
            margin-top: 10px;
            border: 1px solid #334155;
        }
        .header {
            display: flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 20px;
        }
        .logo-img {
            height: 40px;
            width: auto;
            object-fit: contain;
        }
        
        .briefing-box {
            background: #0f172a;
            border-left: 4px solid #38bdf8;
            padding: 14px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 16px;
        }
        .briefing-title { font-size: 0.75rem; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.5px; margin-bottom: 4px; }
        .briefing-heading { font-size: 1.1rem; font-weight: bold; color: #f8fafc; margin-bottom: 6px; }
        .briefing-desc { font-size: 0.9rem; color: #cbd5e1; line-height: 1.4; margin: 0; }

        .tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 20px;
        }
        .tag {
            background: rgba(56, 189, 248, 0.1);
            border: 1px solid rgba(56, 189, 248, 0.3);
            color: #38bdf8;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        .tag:hover { background: rgba(56, 189, 248, 0.25); }

        .input-group {
            position: relative;
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .input-group:focus-within { border-color: #38bdf8; }
        textarea {
            width: 100%;
            height: 80px;
            background: transparent;
            border: none;
            color: #fff;
            font-size: 0.95rem;
            resize: none;
            box-sizing: border-box;
            outline: none;
            font-family: inherit;
        }
        .input-actions {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid #1e293b;
            padding-top: 8px;
        }
        .mic-btn {
            background: #1e293b;
            border: 1px solid #334155;
            color: #94a3b8;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
        }
        .send-btn {
            background: #0284c7;
            color: white;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: background 0.2s;
        }
        .send-btn:hover { background: #0369a1; }
        .send-btn:disabled { background: #475569; cursor: not-allowed; }

        .response-container {
            margin-top: 20px;
            background: #0f172a;
            border: 1px solid #334155;
            padding: 16px;
            border-radius: 12px;
            display: none;
        }
        .response-header { font-size: 0.8rem; color: #38bdf8; text-transform: uppercase; margin-bottom: 8px; font-weight: bold; }
        .response-body { white-space: pre-wrap; line-height: 1.6; font-size: 0.95rem; color: #e2e8f0; }
        .loading { color: #38bdf8; font-style: italic; text-align: center; margin-top: 15px; display: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <!-- Exact custom user logo embedded -->
            <img src="https://raw.githubusercontent.com/nuelsdigital-bit/lead-hunter-bot/main/logo.png" alt="LeadHunter AI Logo" class="logo-img" onerror="this.src='https://i.ibb.co/3s8sX2c/logo.png'">
        </div>

        <div class="briefing-box">
            <div class="briefing-title">Briefing</div>
            <div class="briefing-heading">Every objection has a way in.</div>
            <p class="briefing-desc">Describe the deal, district, and blocker. Get a fast 3-step play and script built for Abuja.</p>
        </div>

        <div class="tags">
            <span class="tag" onclick="insertTag('Maitama')">MAITAMA</span>
            <span class="tag" onclick="insertTag('WUSE II')">WUSE II</span>
            <span class="tag" onclick="insertTag('GUZAPE')">GUZAPE</span>
            <span class="tag" onclick="insertTag('ASOKORO')">ASOKORO</span>
            <span class="tag" onclick="insertTag('UTAKO')">UTAKO</span>
            <span class="tag" onclick="insertTag('KUBWA')">KUBWA</span>
        </div>

        <form id="leadForm">
            <div class="input-group">
                <textarea id="userQuery" placeholder="e.g. Developer in Maitama says they have an in-house team..."></textarea>
                <div class="input-actions">
                    <button type="button" class="mic-btn" title="Voice input">🎙️</button>
                    <button type="submit" id="submitBtn" class="send-btn" title="Send query">🚀</button>
                </div>
            </div>
        </form>

        <div id="loading" class="loading">⚡ Generating fast tactical play...</div>
        
        <div id="responseContainer" class="response-container">
            <div class="response-header">Quick Tactical Output</div>
            <div id="responseBox" class="response-body"></div>
        </div>
    </div>

    <script>
        function insertTag(district) {
            const textarea = document.getElementById('userQuery');
            textarea.value = `Pitch strategy for ${district}: `;
            textarea.focus();
        }

        const form = document.getElementById('leadForm');
        const submitBtn = document.getElementById('submitBtn');
        const loading = document.getElementById('loading');
        const responseContainer = document.getElementById('responseContainer');
        const responseBox = document.getElementById('responseBox');
        const userQueryInput = document.getElementById('userQuery');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const query = userQueryInput.value.trim();
            if (!query) return;

            submitBtn.disabled = true;
            loading.style.display = 'block';
            responseContainer.style.display = 'none';
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
                    responseBox.innerText = '⚠️ ' + (data.error || 'Please wait a moment and try again.');
                }
            } catch (err) {
                responseBox.innerText = '⚠️ Network Error: ' + err.message;
            } finally {
                loading.style.display = 'none';
                responseContainer.style.display = 'block';
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

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=user_query,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.6,
                    max_output_tokens=250, # Forces short, lightning-fast replies
                )
            )
            return jsonify({"reply": response.text})
        except Exception as e:
            error_str = str(e)
            if "429" in error_str and attempt < 2:
                time.sleep(2)
                continue
            return jsonify({"error": error_str}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
