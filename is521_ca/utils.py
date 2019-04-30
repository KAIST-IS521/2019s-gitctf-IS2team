# install PyCrypto using `pip3 install pycryptodome`
import os

from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import binascii
from hashlib import sha1

from is521_ca import settings
from is521_ca.models import User


def sha1digest(plaintext):
    s = sha1()
    s.update(plaintext)
    return s.hexdigest()

# generate key
def key_gen():
    key = RSA.generate(2048)
    f = open('Keys/privatekey.pri', 'wb')
    f.write(key.export_key('PEM', passphrase = 'mypass'))
    f.close()
    
    f = open('Keys/publickey.pub', 'wb')
    f.write(key.publickey().export_key('PEM'))
    f.close()
    return None

# return a binary signed data
def cert_sign(message):
    f = open('Keys/privatekey.pri', 'r')
    key = RSA.import_key(f.read(), passphrase = 'mypass')
    f.close()

    h = SHA256.new(message.encode('utf-8'))
    signature = pkcs1_15.new(key).sign(h)

    return (message, signature)

# return a boolean
def cert_verify(message, signature):
    f = open('Keys/publickey.pub', 'r')
    key = RSA.import_key(f.read())
    f.close()

    h = SHA256.new(message.encode('utf-8'))
    try:
        pkcs1_15.new(key).verify(h, signature)
        return True
    except (ValueError, TypeError):
        return False

def temp_filename(uid):
    user = User.objects.filter(uid=uid)[0]
    tempdir = os.path.join(settings.BASE_DIR, "Keys/Temp")
    tempfile = os.path.join(tempdir, user.firstname + user.lastname + ".pub")

    return tempfile
