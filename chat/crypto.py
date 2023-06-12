from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey


def generate_key_pair() -> RSAPrivateKey:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key


def encrypt_message(message_bytes: bytes, public_key: RSAPublicKey) -> bytes:
    encrypted_message_bytes = public_key.encrypt(
        message_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        ))
    return encrypted_message_bytes


def decrypt_message(encrypted_message_bytes: bytes, private_key: RSAPrivateKey) -> bytes:
    decrypted_message_bytes = private_key.decrypt(
        encrypted_message_bytes,
        padding.OAEP(mgf=padding.MGF1(
            algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        ))
    return decrypted_message_bytes

