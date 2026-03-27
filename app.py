from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json
import time

app = Flask(__name__)
# CORS allow karna zaroori hai taaki aapki website block na ho
CORS(app) 

# Official RBSE Result Target URL (Isko network tab se check karke confirm kar lena)
TARGET_POST_URL = "https://rajeduboard.rajasthan.gov.in/RESULT2026/SEV/get_result.asp"

def scrape_student(roll_no, board, year, std):
    """Ye function official site se ek bache ka result nikalega"""
    session = requests.Session()
    payload = {'roll_no': roll_no, 'submit': 'Submit'}
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://rajeduboard.rajasthan.gov.in/RESULT2026/SEV/Roll_Input.htm'
    }

    try:
        response = session.post(TARGET_POST_URL, data=payload, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        if "not found" in response.text.lower():
            return {"error": "Not found"}

        # DUMMY EXTRACTION LOGIC (Aapko site ke HTML ke hisaab se isko set karna hoga)
        # Pichli baar ki tarah, 'Name' aur 'Father Name' ko strict labels se extract karein
        student_data = {
            "ROLL_NO": str(roll_no),
            "YEAR": str(year),
            "CLASS": str(std),
            "CAN_NAME": "Student Name Extra", # Replace with soup.find() logic
            "FNAME": "Father Name Extra",     # Replace with soup.find() logic
            "MNAME": "Mother Name Extra",
            "CENT_NAME": "Govt School Jaipur",
            "GROUP": "Science",
            "RESULT": "FIRST DIVISION",
            "TOT_MARKS": "450",
            "PER": "75.00"
        }
        
        # Adding dummy subjects for testing
        student_data.update({
            "SC1": "Hindi", "SC1P1": "80", "TOT1": "80",
            "SC2": "English", "SC2P1": "85", "TOT2": "85"
        })

        # Agar aap chahein toh yahan MongoDB ka insert code laga sakte hain caching ke liye

        return student_data

    except Exception as e:
        return {"error": str(e)}

# 1. API_RESULT URL yahan ban raha hai
@app.route('/api/result', methods=['POST'])
def fetch_single_result():
    data = request.json
    roll_no = data.get('roll_no')
    if not roll_no:
        return jsonify({"error": "Roll number missing"}), 400
    
    result = scrape_student(roll_no, data.get('board'), data.get('year'), data.get('class'))
    return jsonify(result)

# 2. API_STREAM URL yahan ban raha hai
@app.route('/api/stream', methods=['POST'])
def stream_school_results():
    data = request.json
    start_roll = int(data.get('roll_no'))
    
    def generate():
        # Stream 15 students live (aap isko 50 ya 100 kar sakte hain school size ke hisaab se)
        for i in range(15):
            current_roll = start_roll + i
            result = scrape_student(current_roll, data.get('board'), data.get('year'), data.get('class'))
            
            if "error" in result:
                break # Roll numbers khatam hone par ruk jayega
            
            # JSON ko string banakar yield karte hain, yahi "streaming" hoti hai
            yield json.dumps(result) + "\n"
            time.sleep(0.3) # Official server ko block karne se rokne ke liye delay

    return Response(generate(), mimetype='application/json')

if __name__ == '__main__':
    # 0.0.0.0 ka matlab hai API internet par available hogi
    app.run(host='0.0.0.0', port=5000)

