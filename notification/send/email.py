import smtplib, os, json
from email.message import EmailMessage

def notification(message):
  try:
    message = json.loads(message)
    mp3_file_id = message["mp3_file_id"]
    sender_address = os.environ.get("GMAIL_ADDRESS")
    sender_password = os.environ.get("GMAIL_PASSWORD")
    receiver_address = message["username"]

    msg = EmailMessage()
    msg.set_content(f"MP3 file id: {mp3_file_id} has been created. You can download it from the app.")
    msg["Subject"] = "MP3 Download"
    msg["From"] = sender_address
    msg["To"] = receiver_address

    session = smtplib.SMTP("smtp.gmail.com")
    session.starttls() #Ensure connection to SMTP server is secure
    session.login(sender_address, sender_password)
    session.send_message(msg)
    session.quit()
    print("Email sent successfully")
  except Exception as e:
    print(f"Error sending email: {e}")
    return e #Return the error so the worker can nack the message

