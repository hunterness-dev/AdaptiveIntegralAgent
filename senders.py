import requests
import smtplib
from email.message import EmailMessage
import os

def send_telegram(file_bytes, chat_id, bot_token):
    if not chat_id or not bot_token:
        raise ValueError("Telegram Chat ID and Bot Token are required")
    bot_token = bot_token.strip().replace(" ", "")
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    files = {"document": ("integral_report.pdf", file_bytes, "application/pdf")}
    data = {"chat_id": chat_id}
    try:
        r = requests.post(url, files=files, data=data, timeout=15)
        r.raise_for_status()
        return True
    except Exception as e:
        raise RuntimeError(f"Telegram error: {str(e)}")

def send_gmail(to_email, subject, body, file_bytes, filename, gmail_user, app_password):
    if not all([to_email, gmail_user, app_password]):
        raise ValueError("Gmail: missing email or app password")
    try:
        msg = EmailMessage()
        msg['From'] = gmail_user
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.set_content(body)
        msg.add_attachment(file_bytes, maintype='application', subtype='pdf', filename=filename)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15) as smtp:
            smtp.login(gmail_user, app_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        raise RuntimeError(f"Gmail error: {str(e)}")

def upload_to_drive(file_bytes, filename, service_account_file='service_account.json'):
    # Optional: disable if you don't use Drive
    if not os.path.exists(service_account_file):
        raise RuntimeError("Google Drive: service_account.json not found")
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseUpload
        from google.oauth2.service_account import Credentials
        import io
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        creds = Credentials.from_service_account_file(service_account_file, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': filename}
        media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype='application/pdf')
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')
    except Exception as e:
        raise RuntimeError(f"Drive error: {str(e)}")