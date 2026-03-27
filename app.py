from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import json
import time

app = Flask(__name__)
CORS(app)

# RankGuruJi ka internal endpoint jo wo apni site (rankguruji.com/rbseresult/) par use karte hain
INTERNAL_API_URL = "https://rbse.rankguruji.com/api/result"
STREAM_API_URL = "https://rbse.rankguruji.com/api/stream"

def get_live_data(roll_no, year, std):
    payload = {
        "board": "rj",
        "year": str(year),
        "std": str(std),
        "roll_no": int(roll_no)
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://rankguruji.com",
        "Referer": "https://rankguruji.com/",
        "Content-Type": "application/json"
    }
    
    try:
        # Hum wahi headers bhej rahe hain jo unki website bhejti hai
        response = requests.post(INTERNAL_API_URL, json=payload, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data and "ROLL_NO" in data:
                return data
        return None
    except Exception as e:
        print(f"Scraping Error: {e}")
        return None

@app.route('/api/result', methods=['POST'])
def fetch_result():
    data = request.json
    roll_no = data.get('roll_no')
    year = data.get('year', '2026')
    std = data.get('class', '10')

    # Fast Fetch (1 sec goal)
    result = get_live_data(roll_no, year, std)
    
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "Result nahi mila ya site busy hai"}), 404

@app.route('/api/stream', methods=['POST'])
def fetch_stream():
    data = request.json
    def generate():
        try:
            headers = {"User-Agent": "Mozilla/5.0", "Origin": "https://rankguruji.com"}
            with requests.post(STREAM_API_URL, json=data, headers=headers, stream=True, timeout=60) as r:
                for line in r.iter_lines():
                    if line:
                        yield line.decode('utf-8') + "\n"
        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"

    return Response(generate(), mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
