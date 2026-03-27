from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json
import time

app = Flask(__name__)
CORS(app) 

# RBSE Actual Result URLs
# Note: Agar 2026 ka link active nahi hai, toh ye dummy error dega. 
# Testing ke liye aap 2024/2025 ke link use kar sakte hain.
TARGET_POST_URL = "https://rajeduboard.rajasthan.gov.in/RESULT2026/SEV/get_result.asp"
REFERER_URL = "https://rajeduboard.rajasthan.gov.in/RESULT2026/SEV/Roll_Input.htm"

def scrape_student(roll_no, board, year, std):
    session = requests.Session()
    # RBSE form aksar 'roll_no' aur 'B1' (Submit button) mangta hai
    payload = {'roll_no': roll_no, 'B1': 'Submit'}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': REFERER_URL
    }

    try:
        response = session.post(TARGET_POST_URL, data=payload, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Agar website par result nahi mila
        if "not found" in response.text.lower() or "invalid" in response.text.lower():
            return {"error": "Not found"}

        # --- Strict Extraction Logic ---
        def get_table_value(label):
            # Label dhundho (e.g., "Candidate's Name")
            tag = soup.find(string=lambda t: t and label.upper() in t.upper())
            if tag:
                # Label ke agle wale <td> mein value hoti hai
                td = tag.find_parent('td').find_next_sibling('td')
                return td.get_text(strip=True) if td else "N/A"
            return "N/A"

        # Aapke Frontend ke variables ke hisab se mapping
        student_data = {
            "ROLL_NO": str(roll_no),
            "YEAR": str(year),
            "CLASS": str(std),
            "CAN_NAME": get_table_value("Candidate's Name"),
            "FNAME": get_table_value("Father's Name"),
            "MNAME": get_table_value("Mother's Name"),
            "CENT_NAME": get_table_value("School/Centre's Name"),
            "RESULT": get_table_value("Result"),
            "TOT_MARKS": get_table_value("Total Marks"),
            "PER": get_table_value("Percentage"),
            "GROUP": get_table_value("Group") if std == '12' else ""
        }

        # --- Subjects Extraction ---
        # RBSE table mein marks rows dhundhna
        rows = soup.find_all('tr')
        sub_idx = 1
        for row in rows:
            cols = row.find_all('td')
            # Subject row mein usually 5 se zyada columns hote hain (Theory, Sessional, etc.)
            if len(cols) >= 5:
                sub_name = cols[0].get_text(strip=True)
                # Filter: Sirf wahi rows lein jo subjects hon (e.g., HINDI, MATHS)
                if any(x in sub_name.upper() for x in ["HINDI", "ENGLISH", "SCIENCE", "MATH", "SANSKRIT", "SOCIAL"]):
                    student_data[f"SC{sub_idx}"] = sub_name
                    student_data[f"SC{sub_idx}P1"] = cols[1].get_text(strip=True) # Theory
                    student_data[f"SC{sub_idx}P3"] = cols[2].get_text(strip=True) # Sessional
                    student_data[f"TOT{sub_idx}"] = cols[4].get_text(strip=True) # Total
                    sub_idx += 1

        # Error check: Agar naam hi nahi mila toh matlab scraping fail hui
        if student_data["CAN_NAME"] == "N/A":
             return {"error": "Not found"}

        return student_data

    except Exception as e:
        return {"error": str(e)}

@app.route('/api/result', methods=['POST'])
def fetch_single_result():
    data = request.json
    roll_no = data.get('roll_no')
    if not roll_no:
        return jsonify({"error": "Roll number missing"}), 400
    
    result = scrape_student(roll_no, data.get('board'), data.get('year'), data.get('class'))
    return jsonify(result)

@app.route('/api/stream', methods=['POST'])
def stream_school_results():
    data = request.json
    start_roll = int(data.get('roll_no'))
    board = data.get('board')
    year = data.get('year')
    std = data.get('class')
    
    def generate():
        # Stream 20 students (Testing ke liye kam rakha hai)
        for i in range(20):
            current_roll = start_roll + i
            result = scrape_student(current_roll, board, year, std)
            
            if "error" in result:
                break # Sequence break hone par ruk jaye
            
            yield json.dumps(result) + "\n"
            time.sleep(0.4) # Official site se ban hone se bachne ke liye delay

    return Response(generate(), mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
