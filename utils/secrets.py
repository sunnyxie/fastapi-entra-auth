from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os

VAULT_URL = os.getenv("AZURE_KEYVAULT_URL", "https://key-vault-2026-test3.vault.azure.net/")

def get_secret_azure(secret_name):
    try:
            credential = DefaultAzureCredential()
            with SecretClient(vault_url=VAULT_URL, credential=credential) as client:
                #  Retrieve the secret
                retrieved_secret = client.get_secret(secret_name)
                
                return retrieved_secret.value
    except Exception as e:
        print(f"Failed to retrieve secret: {e}")
        return None