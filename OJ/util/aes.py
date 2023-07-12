from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import os

from OJ.app.settings import AES_KEY


class AESTool:

    @staticmethod
    def encrypt_data(plaintext):
        plaintext = str(plaintext)
        iv = os.urandom(AES.block_size)
        cipher = AES.new(AES_KEY.encode(), AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
        encrypted_data = base64.b64encode(iv + ciphertext).decode()
        encrypted_data = encrypted_data.replace('/', '~')
        return encrypted_data

    @staticmethod
    def decrypt_data(encrypted_data):
        encrypted_data = encrypted_data.replace('~', '/')
        ciphertext = base64.b64decode(encrypted_data)
        iv = ciphertext[:AES.block_size]
        ciphertext = ciphertext[AES.block_size:]
        cipher = AES.new(AES_KEY.encode(), AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return decrypted_data.decode()
