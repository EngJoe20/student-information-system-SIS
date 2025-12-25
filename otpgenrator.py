import pyotp

secret = "Z6JCQEPQEU4HKU56VVK2NBNSNDU63LUU"
totp = pyotp.TOTP(secret)

print(totp.now())


