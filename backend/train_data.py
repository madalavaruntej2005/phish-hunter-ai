"""
Sample training data for Phish Hunter AI.
Contains phishing/scam examples and safe/legitimate examples.
"""

PHISHING_TEXTS = [
    # SMS Phishing
    "URGENT: Your bank account has been suspended. Click here immediately to restore access: http://bank-secure-login.xyz/verify",
    "Congratulations! You've won $1000 Amazon gift card. Claim now: bit.ly/win-prize-now",
    "Dear customer, your PayPal account is limited. Verify your identity: http://paypa1-secure.com/login",
    "Your OTP for SBI NetBanking is 847291. NEVER share this OTP with anyone. SBI never asks for OTP.",
    "FREE MSG: You have been selected for a $500 Walmart voucher. Tap to claim: http://walmart-deals.cc/free",
    "Alert: Unusual activity on your account. Login immediately to secure: http://secure-hdfc-bank.ml",
    "Your Netflix account will be cancelled. Update payment info: https://netf1ix-billing.com/update",
    "Hi, I'm from the IRS. You owe $3,200 in back taxes. Pay now to avoid arrest: 1-800-fake-irs",
    "WINNER! You have been selected in our lucky draw. Send your details to claim $5000 prize!",
    "Your FedEx package is on hold. Pay $2.99 to release: http://fedex-delivery-fee.net/pay",
    "Verify your Aadhaar card immediately or your mobile service will be suspended: aadhaar-verify.ml",
    "You have a pending refund of Rs.8500 from Income Tax Dept. Click: incometax-refund.xyz/claim",
    "Your WhatsApp will expire in 24 hours! Renew now for FREE: http://whatsapp-renew.tk",
    "Dear user, we detected login from unknown device. Verify now: http://google-security-alert.ml",
    "Congratulations! Your mobile number won Rs.25 Lakh in KBC lottery. Call: 9876543210",
    "HDFC Bank: Your account will be blocked tomorrow. Update KYC now: http://hdfc-kyc-update.xyz",
    "You have UNCLAIMED insurance money worth Rs.12,000. Claim before it expires!",
    "Your Amazon order #4829 is delayed. Verify address to get refund: amzn-help.cc/verify",
    "Click here to get FREE 2GB data from Airtel! Limited time offer: airtel-free-data.ml/claim",
    "Security Notice: Someone tried accessing your Gmail. Reset password now: google-reset.xyz/secure",
    # Email Phishing
    "Dear valued customer, your account has been compromised. Please verify your credentials at: http://secure-login-verify.com",
    "You have inherited $4,500,000 from a deceased relative. Contact our lawyer at: inheritance@legitlaw.tk",
    "Your credit card has been charged $499. If this wasn't you, click: http://dispute-charge-now.cc",
    "Action Required: Your Apple ID has been locked due to too many failed attempts. Unlock: apple-id-help.ml",
    "FINAL NOTICE: Your domain name expires in 24 hours. Renew instantly: domain-renew-urgent.xyz",
]

SAFE_TEXTS = [
    # Legitimate SMS
    "Your OTP for logging in to SBI account is 123456. Valid for 10 minutes. Do not share with anyone.",
    "Hi John, your appointment with Dr. Smith is confirmed for tomorrow at 10:00 AM.",
    "Your Uber ride is arriving in 3 minutes. Driver: Raju, Car: MH-02-AB-1234",
    "Amazon: Your order #123-456-789 has been shipped and will arrive by Friday.",
    "Zomato: Your order from Pizza Hut is on the way! Estimated delivery: 30 mins.",
    "HDFC Bank: Rs.500 debited from account XX1234 on 04-Mar. Available balance: Rs.25,000.",
    "Your Flipkart order has been placed successfully. Order ID: OD-123456789.",
    "Hi, this is a reminder that your credit card bill of Rs.3,450 is due on March 10.",
    "Your blood test report is ready. Please visit the lab to collect your report.",
    "Thank you for subscribing to our newsletter. You can unsubscribe anytime.",
    # Legitimate Email
    "Dear John, thank you for your recent purchase. Your receipt is attached to this email.",
    "Meeting reminder: Sprint planning is scheduled for tomorrow at 9:00 AM in Conference Room B.",
    "Your monthly bank statement for February 2026 is now available in your account portal.",
    "Welcome to GitHub! Please verify your email address by clicking the link below.",
    "Your flight booking is confirmed. PNR: ABC123. Depart on March 10, 2026 at 14:30.",
    "Hi, I'm reaching out regarding the job application you submitted last week.",
    "Your subscription to Adobe Creative Cloud has been renewed for another year.",
    "Your tax return has been submitted successfully. Reference number: ITR-2026-XXXXX.",
    "Happy Birthday! As a special gift, enjoy 20% off your next purchase with code: BDAY20",
    "Your package has cleared customs and is out for delivery today between 2-6 PM.",
    # URL/QR Code safe
    "Visit our store at https://www.amazon.com for the best deals this season.",
    "Check your account statement at https://www.hdfcbank.com",
    "Download the official Aadhaar app from the Play Store: UIDAI mAadhaar",
    "For assistance, visit our help center at https://support.google.com",
    "Your meeting link: https://meet.google.com/abc-defg-hij — Join at 3 PM today!",
]


def get_training_data():
    """Returns lists of (text, label) tuples. Label 1 = phishing, 0 = safe."""
    data = [(text, 1) for text in PHISHING_TEXTS] + \
           [(text, 0) for text in SAFE_TEXTS]
    return data
