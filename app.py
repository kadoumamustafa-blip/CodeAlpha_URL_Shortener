from flask import Flask, request, redirect, render_template_string
import sqlite3
import string
import random

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urls
                 (short_code TEXT PRIMARY KEY, original_url TEXT)''')
    conn.commit()
    conn.close()

def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

@app.route('/')
def home():
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CodeAlpha URL Shortener</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
            
            body {
                margin: 0;
                padding: 0;
                font-family: 'Cairo', sans-serif;
                background: linear-gradient(-45deg, #0a0a0a, #1a1a2e, #16213e, #0f0f1f);
                background-size: 400% 400%;
                animation: gradient 15s ease infinite;
                color: white;
                height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
            }

            @keyframes gradient {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            .container { text-align: center; z-index: 10; }

            h1 {
                font-size: 3.5rem;
                margin-bottom: 8px;
                text-shadow: 0 0 30px rgba(0, 255, 255, 0.6);
            }

            .subtitle {
                font-size: 1.4rem;
                margin-bottom: 50px;
                opacity: 0.9;
            }

            .form-box {
                background: rgba(255,255,255,0.08);
                padding: 40px 30px;
                border-radius: 20px;
                backdrop-filter: blur(12px);
                box-shadow: 0 15px 35px rgba(0,0,0,0.6);
                max-width: 560px;
                margin: 0 auto;
                width: 100%;
            }

            input {
                width: 100%;
                padding: 18px;
                font-size: 1.2rem;
                border: none;
                border-radius: 12px;
                margin-bottom: 20px;
                background: rgba(255,255,255,0.15);
                color: white;
                box-sizing: border-box;
            }

            input::placeholder { color: #bbbbbb; }

            button {
                width: 100%;
                padding: 18px;
                font-size: 1.4rem;
                background: #00ffcc;
                color: #000;
                border: none;
                border-radius: 12px;
                cursor: pointer;
                font-weight: bold;
                transition: 0.3s;
            }

            button:hover {
                background: #00ccaa;
                transform: scale(1.03);
            }

            /*زرار اللغة  ل */
            .lang-toggle {
                position: absolute;
                top: 30px;
                left: 30px;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: rgba(255,255,255,0.12);
                border: 3px solid #00ffcc;
                color: white;
                font-size: 0.95rem;
                font-weight: bold;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                backdrop-filter: blur(10px);
                box-shadow: 0 0 15px rgba(0, 255, 204, 0.6);
                transition: all 0.4s ease;
            }

            .lang-toggle:hover {
                background: #00ffcc;
                color: black;
                transform: scale(1.1);
            }
        </style>
    </head>
    <body>
        <button class="lang-toggle" id="langBtn" onclick="toggleLang()">عربي</button>

        <div class="container">
            <h1 id="title">CodeAlpha_URLShortener</h1>
            <p class="subtitle" id="subtitle">Shorten your long links instantly!</p>
            
            <div class="form-box">
                <form action="/shorten" method="post">
                    <input type="text" id="urlInput" name="url" placeholder="Paste your long URL here..." required>
                    <button type="submit" id="shortenBtn">Shorten URL</button>
                </form>
            </div>
        </div>

        <script>
            let currentLang = "en";

            function toggleLang() {
                currentLang = currentLang === "en" ? "ar" : "en";
                const btn = document.getElementById("langBtn");
                const title = document.getElementById("title");
                const subtitle = document.getElementById("subtitle");
                const input = document.getElementById("urlInput");
                const shortenBtn = document.getElementById("shortenBtn");

                if (currentLang === "ar") {
                    btn.textContent = "English";
                    title.textContent = "CodeAlpha_URLShortener";
                    subtitle.textContent = "اختصر روابطك الطويلة في ثانية واحدة!";
                    input.placeholder = "الرابط الطويل هنا...";
                    shortenBtn.textContent = "اختصر الرابط";
                } else {
                    btn.textContent = "عربي";
                    title.textContent = "CodeAlpha_URLShortener";
                    subtitle.textContent = "Shorten your long links instantly!";
                    input.placeholder = "Paste your long URL here...";
                    shortenBtn.textContent = "Shorten URL";
                }
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/shorten', methods=['POST'])
def shorten():
    original_url = request.form.get('url')
    short_code = generate_short_code()

    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute("INSERT INTO urls (short_code, original_url) VALUES (?, ?)", 
              (short_code, original_url))
    conn.commit()
    conn.close()

    short_url = f"http://127.0.0.1:5000/{short_code}"
    return f'''
    <h2 style="color:#00ffcc; text-align:center; margin-top:80px;">✅ Link shortened successfully!</h2>
    <p style="text-align:center; font-size:28px; margin:30px 0;">
        <a href="{short_url}" target="_blank" style="color:#00ffcc;">{short_url}</a>
    </p>
    <a href="/" style="color:white; text-align:center; display:block; font-size:18px;">← Back to home</a>
    '''

@app.route('/<short_code>')
def redirect_url(short_code):
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute("SELECT original_url FROM urls WHERE short_code = ?", (short_code,))
    result = c.fetchone()
    conn.close()

    if result:
        return redirect(result[0])
    return "❌ Short URL not found!", 404

if __name__ == '__main__':
    init_db()
    print("🚀 Server running at: http://127.0.0.1:5000")
    app.run(debug=True)