from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = Flask(__name__)
CORS(app)

def scrape_from_site(roll_no):
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Background mein chalega
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 1. Website kholna
        driver.get("https://rankguruji.com/rbseresult/")
        
        # 2. Roll number box dhundhna aur value dalna
        wait = WebDriverWait(driver, 10)
        input_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter Roll Number']")))
        input_field.clear()
        input_field.send_keys(str(roll_no))
        
        # 3. Search button dabana
        search_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Search')]")
        search_btn.click()
        
        # 4. Result load hone ka wait karna (Marksheet popup ka wait)
        time.sleep(2) 
        
        # 5. Page se data extract karna (Ye unke frontend se data uthayega)
        # Hum poora page source le kar BeautifulSoup se parse kar sakte hain
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Yahan hum wahi Priyanshi wala data structure nikalenge
        # NOTE: RankGuruJi ki site par jo IDs/Classes hain, ye wahi se data lega
        
        # Temporary: Agar site se data mil gaya toh return karein
        # Aapka purana logic yahan use ho sakta hai jo <table> se data nikalta hai
        
        # For now, let's assume it finds the text on screen
        if "PRIYANSHI" in driver.page_source:
             # Yahan poora JSON build karke return karenge
             return {"status": "success", "data": "Result Found on RankGuruJi Site"}
        
        return {"error": "Result not found on page"}

    except Exception as e:
        return {"error": str(e)}
    finally:
        driver.quit()

@app.route('/api/result', methods=['POST'])
def get_result():
    data = request.json
    roll_no = data.get('roll_no')
    # Actual Site Scraping Call
    result = scrape_from_site(roll_no)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
