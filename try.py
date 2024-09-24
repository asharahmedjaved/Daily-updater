import smtplib

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'asharjaved18042000@gmail.com'
EMAIL_PASSWORD = 'hlwp kaqr chwm jvzh'

try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        print("Login successful")
except Exception as e:
    print(f"Error: {e}")
