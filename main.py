import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import time
from datetime import datetime



# --- CONFIG ---
URL = "https://mhicareers.com/search/?createNewAlert=false&q=&locationsearch=Mississauga&optionsFacetsDD_title=&optionsFacetsDD_facility=MHI%20Canada%20Aerospace%2C%20Inc.&optionsFacetsDD_customfield5=&optionsFacetsDD_brand="  # what I'm trying to target
KEYWORDS = ["Aerospace structural assembler 1", "Aerospace structural assembler",]  # Role patterns 
EMAIL_TO = "immanueljoy107@gmail.com"
EMAIL_FROM = "immanueljoy107@gmail.com"  # Gmail works with app passwords
##check intervel is every 24 hours
CHECK_INTERVAL = 86400   

def scrape_jobs():
    """Extract job listings from the page"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # This selector varies by site—you'll inspect the target page
    job_elements = soup.find_all('div', class_='job-listing')  # Adjust selector
    
    jobs = []
    for job in job_elements:
        title = job.find('h2').text.strip() if job.find('h2') else ''
        link = job.find('a')['href'] if job.find('a') else URL
        if any(kw.lower() in title.lower() for kw in KEYWORDS):
            jobs.append({'title': title, 'url': link})
    
    return jobs

def send_email(subject, body):
    """Fire off the notification"""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_FROM, 'your-app-password')  # Use Gmail App Password
        server.send_message(msg)

def main():
    seen_jobs = set()
    
    while True:
        print(f"[{datetime.now()}] Checking for new roles...")
        
        try:
            current_jobs = scrape_jobs()
            new_jobs = [j for j in current_jobs if j['title'] not in seen_jobs]
            
            if new_jobs:
                body = "\n\n".join([f"{j['title']}\n{j['url']}" for j in new_jobs])
                send_email(f" {len(new_jobs)} New Job(s) Found", body)
                print(f"Alert sent for: {[j['title'] for j in new_jobs]}")
                seen_jobs.update(j['title'] for j in new_jobs)
            else:
                print("No new matches.")
                
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()