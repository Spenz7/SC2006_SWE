import random
from twilio.rest import Client

class OTPStrategy:
    def send(self, phone_number, otp):
        raise NotImplementedError

class TwilioOTPStrategy(OTPStrategy):
    def __init__(self, sid, token, twilio_number):
        self.client = Client(sid, token)
        self.twilio_number = twilio_number

    def send(self, phone_number, otp):
        message = self.client.messages.create(
            body=f'Your OTP is {otp}',
            from_=self.twilio_number,
            to=phone_number
        )
        return message.sid

class MockOTPStrategy(OTPStrategy):
    def send(self, phone_number, otp):
        print(f"[MOCK] Your OTP is {otp} sent to {phone_number}")
        return "mocked_sid"
        
def send_otp_sms(phone_number, strategy):
    from flask import session  #Include this inside the function to avoid circular import issues
    otp = generate_otp()
    session['otp'] = otp
    print("DEBUG: OTP stored in session:", session.get('otp'))
    message_sid = strategy.send(phone_number, otp)
    return message_sid

def generate_otp():
    return random.randint(100000, 999999)