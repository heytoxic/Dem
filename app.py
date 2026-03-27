from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

# RankGuruJi ka main data endpoint
API_URL = "https://rbse.rankguruji.com/api/result"

def get_fast_result(roll_no):
    payload = {
        "board": "rj",
        "year": "2026",
        "std": "10",
        "roll_no": int(roll_no)
    }
    
    # Ye headers RankGuruJi ko lagne denge ki request unki site se hi aa rahi hai
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://rankguruji.com",
        "Referer": "https://rankguruji.com/",
        "Accept-Language": "en-US,en;q=0.9,hi;q=0.8"
    }

    try:
        # Timeout 5 second rakha hai taaki zyada wait na karna pade
        response = requests.post(API_URL, json=payload, headers=headers, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Server Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Fetch Error: {e}")
        return None

@app.route('/api/result', methods=['POST'])
def fetch_result():
    data = request.json
    roll_no = data.get('roll_no')
    
    if not roll_no:
        return jsonify({"error": "Roll number missing"}), 400

    # Fast process (Max 1-2 Seconds)
    result = get_fast_result(roll_no)
    
    if result:
        return jsonify(result)
    else:
        # Agar block ho gaya ho ya data na mile
        return jsonify({"error": "Result fetch failed: Server se invalid response."}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
