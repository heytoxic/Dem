from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json
import time

app = Flask(__name__)
CORS(app) 

# Official RBSE URLs (2026 ke liye update kiya gaya hai)
TARGET_POST_URL = "https://rajeduboard.rajasthan.gov.in/RESULT2026/SEV/get_result.asp"
REFERER_URL = "https://rajeduboard.rajasthan.gov.in/RESULT2026/SEV/Roll_Input.htm"

def scrape_student(roll_no, board, year, std):
    # --- 1. TESTING MODE (Priyanshi's Data from Screenshot) ---
    if str(roll_no) == "1800953":
        return {
            "ROLL_NO": "1800953",
            "YEAR": "2026",
            "CLASS": "10th",
            "CAN_NAME": "PRIYANSHI",
            "FNAME": "SITA RAM",
            "MNAME": "SUNITA DEVI",
            "CENT_NAME": "(1220056) SHEKHAWATI PUB SR SEC SCH, LOSAL",
            "RESULT": "First Division",
            "TOT_MARKS": "599",
            "PER": "99.83",
            "Subjects": {
                "HINDI": "100D",
                "ENGLISH": "099D",
                "SCIENCE": "100D",
                "SOC.SCIENCE": "100D",
                "MATHEMATICS": "100D",
                "SANSKRIT": "100D"
            },
            # Frontend table formats ke liye duplicate keys
            "SC1": "HINDI", "TOT1": "100D", "SC1P1": "080", "SC1P3": "020",
            "SC2": "ENGLISH", "TOT2": "099D", "SC2P1": "079", "SC2P3": "020",
            "SC3": "SCIENCE", "TOT3": "100D", "SC3P1": "080", "SC3P3": "020",
            "SC4": "SOC.SCIENCE", "TOT4": "100D", "SC4P1": "080", "SC4P3": "020",
            "SC5": "MATHEMATICS", "TOT5": "100D", "SC5P1": "080", "SC5P3": "020",
            "SC6": "SANSKRIT", "TOT6": "100D", "SC6P1": "080", "SC6P3": "020"
        }

    # --- 2. ACTUAL SCRAPING LOGIC ---
    session = requests.Session()
    payload = {'roll_no': roll_no, 'B1': 'Submit'} # RBSE 'B1' use karta hai button ke liye
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': REFERER_URL
    }

    try:
        response = session.post(TARGET_POST_URL, data=payload, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        if "not found" in response.text.lower() or "invalid" in response.text.lower():
            return {"error": "Not found"}

        # Extraction Logic using Labels
        def get_val(label):
            tag = soup.find(string=lambda t: t and label.upper() in t.upper())
            if tag:
                td = tag.find_parent('td').find_next_sibling('td')
                return td.get_text(strip=True) if td else "N/A"
            return "N/A"

        student_data = {
            "ROLL_NO": str(roll_no),
            "YEAR": str(year),
            "CLASS": str(std),
            "CAN_NAME": get_val("NAME"),
            "FNAME": get_val("FATHER'S NAME"),
            "MNAME": get_val("MOTHER'S NAME"),
            "CENT_NAME": get_val("SCHOOL"),
            "RESULT": get_val("RESULT"),
            "TOT_MARKS": get_val("TOTAL"),
            "PER": get_val("PERCENTAGE")
        }

        # Subject extraction logic (RBSE table structure)
        rows = soup.find_all('tr')
        idx = 1
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 5:
                sub_name = cols[0].text.strip().upper()
                if any(s in sub_name for s in ["HINDI", "ENGLISH", "SCIENCE", "MATH", "SANSKRIT", "SOCIAL"]):
                    student_data[f"SC{idx}"] = sub_name
                    student_data[f"SC{idx}P1"] = cols[1].text.strip() # Theory
                    student_data[f"SC{idx}P3"] = cols[2].text.strip() # Sessional
                    student_data[f"TOT{idx}"] = cols[4].text.strip() # Total
                    idx += 1

        if student_data["CAN_NAME"] == "N/A":
            return {"error": "Result processing..."}

        return student_data

    except Exception as e:
        return {"error": str(e)}

# --- ENDPOINTS ---

@app.route('/api/result', methods=['POST'])
def fetch_result():
    data = request.json
    roll_no = data.get('roll_no')
    res = scrape_student(roll_no, data.get('board'), data.get('year'), data.get('class'))
    return jsonify(res)

@app.route('/api/stream', methods=['POST'])
def stream_results():
    data = request.json
    start_roll = int(data.get('roll_no'))
    
    def generate():
        for i in range(20): # Stream 20 students
            res = scrape_student(start_roll + i, data.get('board'), data.get('year'), data.get('class'))
            if "error" in res: break
            yield json.dumps(res) + "\n"
            time.sleep(0.4)

    return Response(generate(), mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
