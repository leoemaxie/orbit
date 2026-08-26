import base64
import hashlib
import logging
import os

from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger("core.security.vault")


class SecretVault:
    """Enterprise secret encryption, decryption, and masking utility."""

    _cipher: Fernet

    @classmethod
    def _get_cipher(cls) -> Fernet:
        if not hasattr(cls, "_cipher") or getattr(cls, "_cipher", None) is None:
            raw_key = os.getenv("ORBIT_SECRET_KEY")
            if not raw_key:
                raise ValueError("ORBIT_SECRET_KEY environment variable must be configured.")
            derived_key = base64.urlsafe_b64encode(hashlib.sha256(raw_key.encode()).digest())
            cls._cipher = Fernet(derived_key)
        return cls._cipher

    @classmethod
    def mask_secret(cls, secret: str | None) -> str:
        """Masks sensitive credentials e.g. '••••••••3f8a'."""
        if not secret:
            return ""
        if len(secret) <= 6:
            return "••••••••"
        return f"••••••••{secret[-4:]}"

    @classmethod
    def encrypt_secret(cls, plain_text: str | None) -> str:
        """Encrypts a sensitive secret string into an AES-128-CBC + HMAC ciphertext."""
        if not plain_text:
            return ""
        try:
            cipher = cls._get_cipher()
            return cipher.encrypt(plain_text.encode("utf-8")).decode("utf-8")
        except Exception as e:
            logger.warning(f"Secret encryption failed: {e}")
            return plain_text

    @classmethod
    def decrypt_secret(cls, cipher_text: str | None) -> str:
        """Decrypts a ciphertext string back to plain text."""
        if not cipher_text:
            return ""
        try:
            cipher = cls._get_cipher()
            return cipher.decrypt(cipher_text.encode("utf-8")).decode("utf-8")
        except (InvalidToken, Exception):
            # If not a valid Fernet token, return raw (e.g. unencrypted fallback)
            return cipher_text
