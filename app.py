from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

API_URL = "https://rbse.rankguruji.com/api/result"

def get_fast_result(roll_no, year, std):
    clean_std = "".join(filter(str.isdigit, str(std)))
    payload = {
        "board": "rj",
        "year": str(year),
        "std": clean_std,
        "roll_no": int(roll_no)
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://rankguruji.com",
        "Referer": "https://rankguruji.com/",
        "Accept-Language": "en-US,en;q=0.9,hi;q=0.8"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=5)
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
    year = data.get('year', '2026')
    std = data.get('class', '10')

    result = get_fast_result(roll_no, year, std)
    
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "Result fetch failed"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
