from pathlib import Path
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

    private_key = RSA.generate(2048)

    initials = (first[0] + last[0]).upper()
    aes_key = get_random_bytes(32)
    aes = AES.new(aes_key, AES.MODE_GCM)
    aes.update(initials.encode("ascii"))
    encrypted, tag = aes.encrypt_and_digest(message.encode("utf-8"))

    rsa_cipher = PKCS1_OAEP.new(
          private_key.public_key(), hashAlgo=SHA256
    )
    protected_key = rsa_cipher.encrypt(aes_key)

    recovered_key = PKCS1_OAEP.new(
          private_key, hashAlgo=SHA256
    ).decrypt(protected_key)

    check = AES.new(recovered_key, AES.MODE_GCM, nonce=aes.nonce)
    check.update(initials.encode("ascii"))
    assert check.decrypt_and_verify(encrypted, tag).decode() == message

    (BASE / "key.txt").write_text(
    f"({private_key.e}, {private_key.n})",
    encoding="utf-8"
)

    data = {
        "initials": initials,
        "encrypted_key": protected_key.hex(),
        "nonce": aes.nonce.hex(),
        "tag": tag.hex(),
        "ciphertext": encrypted.hex()
    }
    (BASE / "cipher.txt").write_text(
    f"{int.from_bytes(protected_key, 'big')}\n"
    f"{initials}\n"
    + json.dumps(data),
    encoding="utf-8"
)

    (BASE/"private_key.pem").write_bytes(private_key.export_key())

    print("Created key.txt and cipher.txt.")
    print("Decryption check passed. Keep private_key.pem secret.")


try:
    main()
except ValueError as error:
    print("Error:", error)


