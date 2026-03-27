from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/json",
        "Origin": "https://rankguruji.com",
        "Referer": "https://rankguruji.com/"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            raw_data = response.json()
            # Agar data 'data' key ke andar chhupa hai, toh use bahar nikal lo
            if isinstance(raw_data, dict) and "data" in raw_data:
                return raw_data["data"]
            return raw_data
        return None
    except Exception:
        return None

@app.route('/api/result', methods=['POST'])
def fetch_result():
    data = request.json
    roll_no = data.get('roll_no')
    year = data.get('year', '2026')
    std = data.get('class', '10')

    result = get_fast_result(roll_no, year, std)
    
    if result:
        # Terminal mein print karke dekho ki kya data ja raha hai
        print(f"Sending data for {roll_no}") 
        return jsonify(result)
    else:
        return jsonify({"error": "Result not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
