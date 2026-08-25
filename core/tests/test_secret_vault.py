from core.security.vault import SecretVault


def test_secret_masking():
    assert SecretVault.mask_secret("") == ""
    assert SecretVault.mask_secret(None) == ""
    assert SecretVault.mask_secret("short") == "••••••••"
    assert SecretVault.mask_secret("sk-live-abcdef123456") == "••••••••3456"
    assert SecretVault.mask_secret("https://hooks.slack.com/services/T00/B00/X12345678") == "••••••••5678"


def test_secret_encryption_and_decryption():
    raw_secret = "my-secret-aws-token-998877"
    encrypted = SecretVault.encrypt_secret(raw_secret)
    assert encrypted != raw_secret
    assert len(encrypted) > len(raw_secret)

    decrypted = SecretVault.decrypt_secret(encrypted)
    assert decrypted == raw_secret


def test_secret_vault_handles_empty():
    assert SecretVault.encrypt_secret("") == ""
    assert SecretVault.decrypt_secret("") == ""
    assert SecretVault.encrypt_secret(None) == ""
