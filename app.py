from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

API_URL = "https://rbse.rankguruji.com/api/result"

def get_fast_result(roll_no, year, std):
    # Agar 12th hai toh '12' jayega, varna '10'
    clean_std = str(std) if std else "10"
    
    payload = {
        "board": "rj",
        "year": str(year) if year else "2026",
        "std": clean_std,
        "roll_no": int(roll_no)
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/json",
        "Origin": "https://rankguruji.com",
        "Referer": "https://rankguruji.com/"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=8)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

@app.route('/api/result', methods=['POST'])
def fetch_result():
    data = request.json
    if not data or 'roll_no' not in data:
        return jsonify({"error": "Roll number missing"}), 400

    roll_no = data.get('roll_no')
    year = data.get('year') or "2026"
    # Frontend se 'class' uthayega (e.g., 10 or 12)
    std = data.get('class') or "10"

    result = get_fast_result(roll_no, year, std)
    
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "Result fetch failed"}), 404

# Baaki saara code wahi rahega...

app_export = app # Ye Vercel ke liye hai

if __name__ == '__main__':
    app.run()

