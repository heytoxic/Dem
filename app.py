from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import json
import time

app = Flask(__name__)
CORS(app)

# Rank Guru Ji ke Actual Endpoints
RANK_GURU_RESULT_API = "https://rbse.rankguruji.com/api/result"
RANK_GURU_STREAM_API = "https://rbse.rankguruji.com/api/stream"

def fetch_data(payload, url):
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        # Unka API JSON format mangta hai
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/api/result', methods=['POST'])
def get_result():
    data = request.json
    # Rank Guru Ji ke API parameters match kar rahe hain
    payload = {
        "board": data.get('board', 'rj'),
        "year": data.get('year', '2026'),
        "std": data.get('class', '10'),
        "roll_no": int(data.get('roll_no'))
    }
    
    result = fetch_data(payload, RANK_GURU_RESULT_API)
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "Result nahi mila"}), 404

@app.route('/api/stream', methods=['POST'])
def stream_results():
    data = request.json
    payload = {
        "board": data.get('board', 'rj'),
        "year": data.get('year', '2026'),
        "std": data.get('class', '10'),
        "roll_no": int(data.get('roll_no'))
    }

    def generate():
        try:
            # Stream mode mein data forward karna
            with requests.post(RANK_GURU_STREAM_API, json=payload, stream=True, timeout=60) as r:
                for line in r.iter_lines():
                    if line:
                        yield line.decode('utf-8') + "\n"
        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"

    return Response(generate(), mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
