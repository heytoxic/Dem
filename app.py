from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

API_URL = "https://rbse.rankguruji.com/api/result"

def get_fast_result(roll_no, year, std):
    # Class mapping logic for 12th
    std_lower = str(std).lower()
    if "12" in std_lower:
        if "science" in std_lower or "sci" in std_lower:
            clean_std = "12s"
        elif "commerce" in std_lower or "com" in std_lower:
            clean_std = "12c"
        elif "arts" in std_lower:
            clean_std = "12a"
        else:
            clean_std = "12" # Default 12th
    else:
        clean_std = "10" # Default 10th

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
        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
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
    std = data.get('class') or "10"

    result = get_fast_result(roll_no, year, std)
    
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "Result not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
