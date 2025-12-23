import pyotp

secret = "EVPJIWANQJCHA65UKIQKOY47BUHFFUVM"
totp = pyotp.TOTP(secret)

print(totp.now())
