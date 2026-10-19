from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
from os import urandom
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
image_path   = os.path.join(BASE, 'input', 'kitty.jpg')
output_path  = os.path.join(BASE, 'output', 'kitty_tampered.png')

def inputbin(data):
    return [format(byte, '08b') for byte in data]

def modifyimage(pix, data):
    datalist = inputbin(data)
    lendata = len(datalist)
    imdata = iter(pix)
    
    for x in range(lendata):
        pixels = [value for value in next(imdata)[:3] + next(imdata)[:3] + next(imdata)[:3]]
        
        for y in range(8):
            if datalist[x][y] == '0' and pixels[y] % 2 != 0:
                pixels[y] -= 1
            elif datalist[x][y] == '1' and pixels[y] % 2 == 0:
                pixels[y] = pixels[y] - 1 if pixels[y] != 0 else pixels[y] + 1
        
        if x == lendata - 1:
            pixels[-1] |= 1
        else:
            pixels[-1] &= ~1
        
        yield tuple(pixels[:3])
        yield tuple(pixels[3:6])
        yield tuple(pixels[6:9])

def addencode(tamperedimage, data):
    w = tamperedimage.size[0]
    (x, y) = (0, 0)
    
    for pixel in modifyimage(tamperedimage.getdata(), data):
        tamperedimage.putpixel((x, y), pixel)
        x = 0 if x == w - 1 else x + 1
        y += 1 if x == 0 else 0

def encrypt_message(message):
    symmetric_key = urandom(32)  
    iv = urandom(16)
    cipher = Cipher(algorithms.AES(symmetric_key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = sym_padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(message.encode()) + padder.finalize()
    enc_message = encryptor.update(padded_data) + encryptor.finalize()

    return enc_message, iv, symmetric_key
 
def decode(tampimage, iv, symmetric_key) -> str:
    image = Image.open(tampimage, 'r')
    imgdata = iter(image.getdata())
    data = bytearray()
    
    while True:
        pixels = [value for value in next(imgdata)[:3] + next(imgdata)[:3] + next(imgdata)[:3]]
        binstr = ''.join(['1' if i % 2 else '0' for i in pixels[:8]])
        data += bytes([int(binstr, 2)])
        
        if pixels[-1] % 2 != 0:
            break

    data = bytes(data)
    cipher = Cipher(algorithms.AES(symmetric_key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(data) + decryptor.finalize()
    unpadder = sym_padding.PKCS7(algorithms.AES.block_size).unpadder()
    plaintext = unpadder.update(padded_data) + unpadder.finalize()
    return plaintext.decode('utf-8')

# --- main program ---
message = "This is a secret message."
print("Original Message:", message)
enc_message, iv, symmetric_key = encrypt_message(message)
print("Encrypted Message:", enc_message)

with open(image_path, 'rb') as f:
    image = Image.open(f)
    tampered_image = image.copy()

addencode(tampered_image, enc_message)
tampered_image.save(output_path)
print (f"The message : {message} has been hidden in the image : {image_path} and is now {tampered_image}.")

decoded_message = decode(output_path, iv, symmetric_key)
print(f"Decoded Message: {decoded_message}")