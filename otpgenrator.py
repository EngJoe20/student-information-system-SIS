import pyotp

secret = "D2CE57PTLODYNBBYN4RRGFKXM636QH5X"
totp = pyotp.TOTP(secret)

print(totp.now())
