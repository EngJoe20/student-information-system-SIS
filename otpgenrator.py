import pyotp

secret = "EGUV423NUWV7QJMSQQKD7CVGYWQ37P52"
totp = pyotp.TOTP(secret)

print(totp.now())
