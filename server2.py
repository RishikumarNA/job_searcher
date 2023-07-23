from flask import Flask, render_template, request
from twilio.rest import Client
import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
import ssl
import csv

app = Flask(__name__)


TWILIO_ACCOUNT_SID = 'ACf7959623a4275162a5679d91dcb06643'
TWILIO_AUTH_TOKEN = '59bf9757a4ebc5bb75a697f4fcce9ec6'
TWILIO_PHONE_NUMBER = '+12343322418'
SENDER_EMAIL = 'rishikumarashokan@gmail.com'
SENDER_EMAIL_PASSWORD = 'hrnrahelxepqhyet'
HACKER_NEWS_URL = 'https://news.ycombinator.com/jobs'



def send_sms(job_data, phone_number):
    account_sid = TWILIO_ACCOUNT_SID
    auth_token = TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_=TWILIO_PHONE_NUMBER,
        body=f"Job: {job_data['title']}\nAppliction Link: {job_data['link']}\nPosted: {job_data['days']}",
        to=phone_number
    )

    print(f"SMS sent: {message.sid}")

def email_sender(job_data, email_address):  
    email_sender = SENDER_EMAIL
    email_password = SENDER_EMAIL_PASSWORD

    email_receiver = email_address

    subject = "Job Seeker"
    body = f"Job: {job_data['title']}\nAppliction Link: {job_data['link']}\nPosted: {job_data['days']}"

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

@app.route('/')
def my_page():
    return render_template('final.html')

@app.route('/submit_form', methods=['POST'])
def my_page2():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']    
    
    write_to_csv(name,email,phone)
    # Process the form data as needed

    # Call the send_sms() and email_sender() functions
    get_latest_job(phone, email)

    return render_template('submit.html')

def write_to_csv(name,email,phone):
    with open('database.csv', mode='a', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow([name,email,phone])

def get_latest_job(phone_number, email_address):
    response = requests.get(HACKER_NEWS_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.select('.titleline')
    subtexts = soup.select('.subtext')

    # Load the previously stored latest job data
    with open('latest_job.txt', 'r') as file:
        previous_job_data = file.read().strip()

    latest_job_data = []
    for idx, item in enumerate(links):
        title = links[idx].getText()
        href = links[idx].find('a')['href']  # Extract the 'href' attribute from the 'a' tag
        day = subtexts[idx].select('.age')
        if day:
            days = day[0].getText()
            job_data = {'title': title, 'link': href,'days': days}
            latest_job_data.append(job_data)

            # Check if the current job data is different from the previously stored one
            if previous_job_data != str(job_data):
                #send_sms(job_data, phone_number)
                #email_sender(job_data, email_address)
                continue

    # Save the latest job data to compare with next time
    with open('latest_job.txt', 'w') as file:
        file.write(str(latest_job_data))

if __name__ == "__main__":
    app.run()
