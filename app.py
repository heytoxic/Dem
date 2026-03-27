from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import json
import time

app = Flask(__name__)
CORS(app) # Frontend block hone se bachane ke liye

# Rank Guru Ji ke official API endpoints
RANK_GURU_RESULT_API = "https://rbse.rankguruji.com/api/result"
RANK_GURU_STREAM_API = "https://rbse.rankguruji.com/api/stream"

def fetch_from_rank_guru(roll_no, board, year, std):
    """Rank Guru Ji ke API se single student ka data laane ke liye"""
    payload = {
        "board": board,
        "year": year,
        "std": std,
        "roll_no": int(roll_no)
    }
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }
    
    try:
        response = requests.post(RANK_GURU_RESULT_API, json=payload, headers=headers, timeout=10)
        if response.status_status == 200:
            return response.json()
        return {"error": "API se data nahi mila"}
    except Exception as e:
        return {"error": str(e)}

# 1. Single Result Endpoint
@app.route('/api/result', methods=['POST'])
def get_result():
    data = request.json
    res = fetch_from_rank_guru(
        data.get('roll_no'), 
        data.get('board', 'rj'), 
        data.get('year', '2026'), 
        data.get('class', '10')
    )
    return jsonify(res)

# 2. School Wise Stream Endpoint
@app.route('/api/stream', methods=['POST'])
def stream_results():
    data = request.json
    # Hum Rank Guru Ji ke stream API ko direct forward karenge
    def generate():
        try:
            # Rank Guru Ji ke API ko hit karte hain
            with requests.post(RANK_GURU_STREAM_API, json=data, stream=True, timeout=30) as r:
                for line in r.iter_lines():
                    if line:
                        # Har ek bache ka data live yield karega
                        yield line.decode('utf-8') + "\n"
        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"

    return Response(generate(), mimetype='application/json')

if __name__ == '__main__':
    # 0.0.0.0 par run karein taaki internet par access ho sake
    app.run(host='0.0.0.0', port=5000)
    
