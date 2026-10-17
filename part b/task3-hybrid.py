from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from base64 import b64encode
import os
from os import urandom

BASE = os.path.dirname(os.path.abspath(__file__))
input_path   = os.path.join(BASE, 'input', 'task3.txt')
encrypt_path = os.path.join(BASE, 'output', 'task3encrypted.txt')
keys_path    = os.path.join(BASE, 'keys', 'keys.txt')
decrypt_path = os.path.join(BASE, 'output', 'task3decrypted.txt')

os.makedirs(os.path.dirname(encrypt_path), exist_ok=True)
os.makedirs(os.path.dirname(keys_path), exist_ok=True)

def get_oaep():
    return asym_padding.OAEP(
        mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )

def generate_rsa_keys():
    priv_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    return priv_key, priv_key.public_key()

def encrypt_file_data(data, public_key):
    symmetric_key = urandom(32)   # AES-256
    iv = urandom(16)

    cipher = Cipher(algorithms.AES(symmetric_key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = sym_padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    encrypted_key = public_key.encrypt(symmetric_key, get_oaep())
    return encrypted_data, iv, encrypted_key

def decrypt_file_data(encrypted_data, iv, encrypted_key, private_key):
    symmetric_key = private_key.decrypt(encrypted_key, get_oaep())

    cipher = Cipher(algorithms.AES(symmetric_key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    unpadder = sym_padding.PKCS7(algorithms.AES.block_size).unpadder()
    return unpadder.update(padded_data) + unpadder.finalize()

# --- main program ---
private_key, public_key = generate_rsa_keys()

with open(input_path, 'rb') as f:
    original = f.read()

encrypted_data, iv, encrypted_key = encrypt_file_data(original, public_key)

with open(encrypt_path, 'wb') as f:
    f.write(iv + encrypted_data)
with open(keys_path, 'wb') as f:
    f.write(encrypted_key)

with open(encrypt_path, 'rb') as f:
    data = f.read()
iv_from_file = data[:16]
ciphertext_from_file = data[16:]
with open(keys_path, 'rb') as f:
    encrypted_key_from_file = f.read()

decrypted = decrypt_file_data(ciphertext_from_file, iv_from_file, encrypted_key_from_file, private_key)

with open(decrypt_path, 'wb') as f:
    f.write(decrypted)

print("Original:", original.decode())
print("Encrypted Message:", b64encode(encrypted_data).decode())
print("IV (Initialization Vector):", b64encode(iv).decode())
print("Encrypted Symmetric Key:", b64encode(encrypted_key).decode())
print("Decrypted:", decrypted.decode())
print("Files match:", decrypted == original)