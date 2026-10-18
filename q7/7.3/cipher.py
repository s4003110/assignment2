from pathlib import Path
from math import gcd
import json

from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Util.number import isPrime


BASE = Path(__file__).resolve().parent


def main():
    first = input("First name: ").strip()
    last = input("Last name: ").strip()
    p = int(input("First prime: "))
    q = int(input("Second prime: "))
    message = input("Plaintext: ")



    for name in(first, last):
        if not name.isascii() or not name.isalpha():
            raise ValueError("Names must contain English letters only.")

    if len(message) < 3 or not message.isascii() or not message.isalpha():
            raise ValueError("Plaintext needs at least 3 English letters")

    if min(p,q) <= 1_000_000 or p == q:
            raise ValueError("Use different primers greater than 1,000,000")

    if not isPrime(p) or not isPrime(q):
            raise ValueError("Both numbers must be prime.")

    if min(p.bit_length(), q.bit_length()) < 1024:
            raise ValueError("Use primers of at least 1024 bits each")

    e = 65537
    phi = (p-1) * (q-1)

    if gcd(e, phi) != 1:
          raise ValueError("These primers are unsuitable for exponent 65537")   

    d = pow(e,-1,phi)
    private_key = RSA.construct((p*q, e, d, p, q))