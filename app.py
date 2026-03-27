from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

API_URL = "https://rbse.rankguruji.com/api/result"

@app.route('/api/result', methods=['POST'])
def fetch_result():
    data = request.json
    roll_no = data.get('roll_no')
    year = data.get('year', '2026')
    std = data.get('class', '10')

    # Standardizing class for 12th
    std_lower = str(std).lower()
    clean_std = "10"
    if "12" in std_lower:
        if "sci" in std_lower: clean_std = "12s"
        elif "com" in std_lower: clean_std = "12c"
        elif "arts" in std_lower: clean_std = "12a"
        else: clean_std = "12"

    payload = {
        "board": "rj",
        "year": str(year),
        "std": clean_std,
        "roll_no": int(roll_no)
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json",
        "Origin": "https://rankguruji.com",
        "Referer": "https://rankguruji.com/"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return jsonify(response.json())
        return jsonify({"error": "Result not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

app_export = app 

if __name__ == '__main__':
    app.run()
