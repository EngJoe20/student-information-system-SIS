import pyotp

<<<<<<< HEAD
secret = "D2CE57PTLODYNBBYN4RRGFKXM636QH5X"
=======
secret = "EVPJIWANQJCHA65UKIQKOY47BUHFFUVM"
>>>>>>> f7eaa727e3e450043429d8bf7d885af3011062e1
totp = pyotp.TOTP(secret)

print(totp.now())
