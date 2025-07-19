"""
Secrets Management for EvolSynth API
Secure handling of sensitive configuration and credentials for production environments
"""

import os
import json
import base64
import hashlib
from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from api.utils.logging_config import get_logger

logger = get_logger("api.secrets")


class SecretNotFoundError(Exception):
    """Raised when a requested secret is not found"""
    pass


class SecretManagerError(Exception):
    """Raised when there's an error with secret management operations"""
    pass


class SecretBackend(ABC):
    """Abstract base class for secret backends"""

    @abstractmethod
    def get_secret(self, key: str) -> Optional[str]:
        """Retrieve a secret by key"""
        pass

    @abstractmethod
    def set_secret(self, key: str, value: str) -> bool:
        """Store a secret"""
        pass

    @abstractmethod
    def delete_secret(self, key: str) -> bool:
        """Delete a secret"""
        pass

    @abstractmethod
    def list_secrets(self) -> List[str]:
        """List all secret keys (without values)"""
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the secret backend"""
        pass


class EnvironmentSecretBackend(SecretBackend):
    """Environment variables secret backend"""

    def __init__(self, prefix: str = "EVOLSYNTH_SECRET_"):
        self.prefix = prefix
        logger.info(
            f"Initialized environment secret backend with prefix: {prefix}")

    def get_secret(self, key: str) -> Optional[str]:
        """Get secret from environment variables"""
        env_key = f"{self.prefix}{key.upper()}"
        value = os.environ.get(env_key)
        if value:
            logger.debug(f"Retrieved secret from environment: {key}")
        return value

    def set_secret(self, key: str, value: str) -> bool:
        """Set secret in environment (runtime only)"""
        env_key = f"{self.prefix}{key.upper()}"
        os.environ[env_key] = value
        logger.info(f"Set secret in environment: {key}")
        return True

    def delete_secret(self, key: str) -> bool:
        """Delete secret from environment"""
        env_key = f"{self.prefix}{key.upper()}"
        if env_key in os.environ:
            del os.environ[env_key]
            logger.info(f"Deleted secret from environment: {key}")
            return True
        return False

    def list_secrets(self) -> List[str]:
        """List all secret keys from environment"""
        keys = []
        for env_key in os.environ:
            if env_key.startswith(self.prefix):
                key = env_key[len(self.prefix):].lower()
                keys.append(key)
        return keys

    def health_check(self) -> Dict[str, Any]:
        """Check environment backend health"""
        secret_count = len(self.list_secrets())
        return {
            "backend": "environment",
            "healthy": True,
            "secret_count": secret_count,
            "prefix": self.prefix
        }


class FileSecretBackend(SecretBackend):
    """File-based encrypted secret backend"""

    def __init__(self, secrets_file: str, encryption_key: Optional[str] = None):
        self.secrets_file = Path(secrets_file)
        self.encryption_key = encryption_key or self._get_or_create_key()
        self.fernet = Fernet(self.encryption_key.encode() if isinstance(
            self.encryption_key, str) else self.encryption_key)

        # Ensure secrets directory exists
        self.secrets_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized file secret backend: {self.secrets_file}")

    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key"""
        key_file = self.secrets_file.parent / ".encryption_key"

        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            # Set restrictive permissions
            os.chmod(key_file, 0o600)
            logger.warning("Generated new encryption key for file backend")
            return key

    def _load_secrets(self) -> Dict[str, str]:
        """Load and decrypt secrets from file"""
        if not self.secrets_file.exists():
            return {}

        try:
            with open(self.secrets_file, 'rb') as f:
                encrypted_data = f.read()

            if not encrypted_data:
                return {}

            decrypted_data = self.fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())

        except Exception as e:
            logger.error(f"Failed to load secrets from file: {e}")
            raise SecretManagerError(f"Failed to load secrets: {e}")

    def _save_secrets(self, secrets: Dict[str, str]) -> None:
        """Encrypt and save secrets to file"""
        try:
            data = json.dumps(secrets, indent=2).encode()
            encrypted_data = self.fernet.encrypt(data)

            with open(self.secrets_file, 'wb') as f:
                f.write(encrypted_data)

            # Set restrictive permissions
            os.chmod(self.secrets_file, 0o600)

        except Exception as e:
            logger.error(f"Failed to save secrets to file: {e}")
            raise SecretManagerError(f"Failed to save secrets: {e}")

    def get_secret(self, key: str) -> Optional[str]:
        """Get secret from encrypted file"""
        secrets = self._load_secrets()
        value = secrets.get(key)
        if value:
            logger.debug(f"Retrieved secret from file: {key}")
        return value

    def set_secret(self, key: str, value: str) -> bool:
        """Set secret in encrypted file"""
        secrets = self._load_secrets()
        secrets[key] = value
        self._save_secrets(secrets)
        logger.info(f"Set secret in file: {key}")
        return True

    def delete_secret(self, key: str) -> bool:
        """Delete secret from encrypted file"""
        secrets = self._load_secrets()
        if key in secrets:
            del secrets[key]
            self._save_secrets(secrets)
            logger.info(f"Deleted secret from file: {key}")
            return True
        return False

    def list_secrets(self) -> List[str]:
        """List all secret keys from file"""
        secrets = self._load_secrets()
        return list(secrets.keys())

    def health_check(self) -> Dict[str, Any]:
        """Check file backend health"""
        try:
            secrets = self._load_secrets()
            file_exists = self.secrets_file.exists()
            readable = True
        except Exception as e:
             secrets = {}
             file_exists = self.secrets_file.exists()
             readable = False
             error_msg = str(e)

        return {
             "backend": "file",
             "healthy": readable,
             "file_exists": file_exists,
             "file_path": str(self.secrets_file),
             "secret_count": len(secrets),
             "error": None if readable else error_msg
         }


class HashiCorpVaultBackend(SecretBackend):
    """HashiCorp Vault secret backend (requires hvac library)"""
    
    def __init__(self, vault_url: str, vault_token: str, mount_point: str = "secret"):
        try:
            import hvac
        except ImportError:
            raise SecretManagerError("hvac library required for Vault backend: pip install hvac")
        
        self.client = hvac.Client(url=vault_url, token=vault_token)
        self.mount_point = mount_point
        
        if not self.client.is_authenticated():
            raise SecretManagerError("Failed to authenticate with Vault")
        
        logger.info(f"Initialized Vault backend: {vault_url}")
    
    def get_secret(self, key: str) -> Optional[str]:
        """Get secret from Vault"""
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=key,
                mount_point=self.mount_point
            )
            value = response['data']['data'].get('value')
            if value:
                logger.debug(f"Retrieved secret from Vault: {key}")
            return value
        except Exception as e:
            logger.warning(f"Failed to get secret from Vault: {key} - {e}")
            return None
    
    def set_secret(self, key: str, value: str) -> bool:
        """Set secret in Vault"""
        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=key,
                secret={'value': value},
                mount_point=self.mount_point
            )
            logger.info(f"Set secret in Vault: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to set secret in Vault: {key} - {e}")
            return False
    
    def delete_secret(self, key: str) -> bool:
        """Delete secret from Vault"""
        try:
            self.client.secrets.kv.v2.delete_metadata_and_all_versions(
                path=key,
                mount_point=self.mount_point
            )
            logger.info(f"Deleted secret from Vault: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete secret from Vault: {key} - {e}")
            return False
    
    def list_secrets(self) -> List[str]:
        """List all secret keys from Vault"""
        try:
            response = self.client.secrets.kv.v2.list_secrets(
                path="",
                mount_point=self.mount_point
            )
            return response['data']['keys']
        except Exception as e:
            logger.error(f"Failed to list secrets from Vault: {e}")
            return []
    
    def health_check(self) -> Dict[str, Any]:
        """Check Vault backend health"""
        try:
            is_authenticated = self.client.is_authenticated()
            seal_status = self.client.sys.read_seal_status()
            
            return {
                "backend": "vault",
                "healthy": is_authenticated and not seal_status['sealed'],
                "authenticated": is_authenticated,
                "sealed": seal_status['sealed'],
                "vault_version": seal_status.get('version', 'unknown')
            }
        except Exception as e:
            return {
                "backend": "vault",
                "healthy": False,
                "error": str(e)
            }


class SecretManager:
    """Main secret manager with multiple backend support"""
    
    def __init__(self, primary_backend: SecretBackend, fallback_backends: Optional[List[SecretBackend]] = None):
        self.primary_backend = primary_backend
        self.fallback_backends = fallback_backends or []
        self.all_backends = [primary_backend] + self.fallback_backends
        
        logger.info(f"Initialized SecretManager with {len(self.all_backends)} backends")
    
    def get_secret(self, key: str, fallback_value: Optional[str] = None) -> Optional[str]:
        """
        Get secret with fallback support
        
        Args:
            key: Secret key to retrieve
            fallback_value: Default value if secret not found
            
        Returns:
            Secret value or fallback value
        """
        for backend in self.all_backends:
            try:
                value = backend.get_secret(key)
                if value is not None:
                    return value
            except Exception as e:
                logger.warning(f"Backend {backend.__class__.__name__} failed for key {key}: {e}")
                continue
        
        if fallback_value is not None:
            logger.debug(f"Using fallback value for secret: {key}")
            return fallback_value
        
        logger.warning(f"Secret not found in any backend: {key}")
        return None
    
    def get_secret_or_raise(self, key: str) -> str:
        """Get secret or raise SecretNotFoundError"""
        value = self.get_secret(key)
        if value is None:
            raise SecretNotFoundError(f"Secret not found: {key}")
        return value
    
    def set_secret(self, key: str, value: str, backends: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Set secret in specified backends
        
        Args:
            key: Secret key
            value: Secret value
            backends: List of backend names to use (default: all)
            
        Returns:
            Dict mapping backend names to success status
        """
        results = {}
        target_backends = self.all_backends
        
        if backends:
            target_backends = [
                b for b in self.all_backends 
                if b.__class__.__name__.replace('SecretBackend', '').lower() in [name.lower() for name in backends]
            ]
        
        for backend in target_backends:
            try:
                success = backend.set_secret(key, value)
                results[backend.__class__.__name__] = success
            except Exception as e:
                logger.error(f"Failed to set secret in {backend.__class__.__name__}: {e}")
                results[backend.__class__.__name__] = False
        
        return results
    
    def delete_secret(self, key: str) -> Dict[str, bool]:
        """Delete secret from all backends"""
        results = {}
        
        for backend in self.all_backends:
            try:
                success = backend.delete_secret(key)
                results[backend.__class__.__name__] = success
            except Exception as e:
                logger.error(f"Failed to delete secret from {backend.__class__.__name__}: {e}")
                results[backend.__class__.__name__] = False
        
        return results
    
    def list_all_secrets(self) -> Dict[str, List[str]]:
        """List secrets from all backends"""
        results = {}
        
        for backend in self.all_backends:
            try:
                secrets = backend.list_secrets()
                results[backend.__class__.__name__] = secrets
            except Exception as e:
                logger.error(f"Failed to list secrets from {backend.__class__.__name__}: {e}")
                results[backend.__class__.__name__] = []
        
        return results
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all backends"""
        backend_health = {}
        overall_healthy = True
        
        for backend in self.all_backends:
            try:
                health = backend.health_check()
                backend_health[backend.__class__.__name__] = health
                if not health.get('healthy', False):
                    overall_healthy = False
            except Exception as e:
                backend_health[backend.__class__.__name__] = {
                    "healthy": False,
                    "error": str(e)
                }
                overall_healthy = False
        
        return {
            "overall_healthy": overall_healthy,
            "backends": backend_health,
            "primary_backend": self.primary_backend.__class__.__name__,
            "fallback_count": len(self.fallback_backends)
        }
    
    def rotate_secret(self, key: str, new_value: str, verify_callback: Optional[callable] = None) -> bool:
        """
        Rotate a secret with optional verification
        
        Args:
            key: Secret key to rotate
            new_value: New secret value
            verify_callback: Function to verify the new secret works
            
        Returns:
            True if rotation successful
        """
        # Store old value for rollback
        old_value = self.get_secret(key)
        
        try:
            # Set new value
            results = self.set_secret(key, new_value)
            
            # Verify if callback provided
            if verify_callback:
                if not verify_callback(new_value):
                    # Rollback on verification failure
                    if old_value:
                        self.set_secret(key, old_value)
                    raise SecretManagerError("Secret verification failed")
            
            logger.info(f"Successfully rotated secret: {key}")
            return all(results.values())
            
        except Exception as e:
            # Rollback on error
            if old_value:
                self.set_secret(key, old_value)
            logger.error(f"Failed to rotate secret {key}: {e}")
            raise


def create_secret_manager(config: Dict[str, Any]) -> SecretManager:
    """
    Factory function to create SecretManager from configuration
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured SecretManager instance
    """
    backend_type = config.get('backend', 'environment').lower()
    backends = []
    
    # Create primary backend
    if backend_type == 'environment':
        primary = EnvironmentSecretBackend(
            prefix=config.get('prefix', 'EVOLSYNTH_SECRET_')
        )
    elif backend_type == 'file':
        primary = FileSecretBackend(
            secrets_file=config.get('file_path', '/etc/evolsynth/secrets.enc'),
            encryption_key=config.get('encryption_key')
        )
    elif backend_type == 'vault':
        primary = HashiCorpVaultBackend(
            vault_url=config['vault_url'],
            vault_token=config['vault_token'],
            mount_point=config.get('mount_point', 'secret')
        )
    else:
        raise SecretManagerError(f"Unknown backend type: {backend_type}")
    
    # Create fallback backends
    fallback_configs = config.get('fallbacks', [])
    for fallback_config in fallback_configs:
        fallback_type = fallback_config.get('backend', '').lower()
        
        if fallback_type == 'environment':
            backends.append(EnvironmentSecretBackend(
                prefix=fallback_config.get('prefix', 'EVOLSYNTH_SECRET_')
            ))
        elif fallback_type == 'file':
            backends.append(FileSecretBackend(
                secrets_file=fallback_config.get('file_path', '/etc/evolsynth/secrets_fallback.enc'),
                encryption_key=fallback_config.get('encryption_key')
            ))
    
    return SecretManager(primary, backends)


# Utility functions for common secret operations
def mask_secret(value: str, visible_chars: int = 4) -> str:
    """Mask a secret value for logging"""
    if not value or len(value) <= visible_chars:
        return "*" * len(value) if value else ""
    
    return value[:visible_chars] + "*" * (len(value) - visible_chars)


def generate_secret_key(length: int = 32) -> str:
    """Generate a random secret key"""
    import secrets
    return secrets.token_urlsafe(length)


def hash_secret(value: str, salt: Optional[bytes] = None) -> str:
    """Hash a secret value (for verification, not storage)"""
    if salt is None:
        salt = os.urandom(32)
    
    key = hashlib.pbkdf2_hmac('sha256', value.encode(), salt, 100000)
    return base64.b64encode(salt + key).decode()


def verify_secret_hash(value: str, hashed: str) -> bool:
    """Verify a secret against its hash"""
    try:
        decoded = base64.b64decode(hashed.encode())
        salt = decoded[:32]
        key = decoded[32:]
        
        new_key = hashlib.pbkdf2_hmac('sha256', value.encode(), salt, 100000)
        return key == new_key
    except:
        return False


# Global secret manager instance (initialized by configuration)
_secret_manager: Optional[SecretManager] = None


def get_secret_manager() -> SecretManager:
    """Get the global secret manager instance"""
    global _secret_manager
    if _secret_manager is None:
        raise SecretManagerError("Secret manager not initialized. Call initialize_secret_manager() first.")
    return _secret_manager


def initialize_secret_manager(config: Optional[Dict[str, Any]] = None) -> SecretManager:
    """Initialize the global secret manager"""
    global _secret_manager
    
    if config is None:
        # Default configuration - environment with file fallback
        config = {
            'backend': 'environment',
            'prefix': 'EVOLSYNTH_SECRET_',
            'fallbacks': [
                {
                    'backend': 'file',
                    'file_path': '/tmp/evolsynth_secrets.enc'
                }
            ]
        }
    
    _secret_manager = create_secret_manager(config)
    logger.info("Global secret manager initialized")
    return _secret_manager


# Convenience functions using global manager
def get_secret(key: str, fallback: Optional[str] = None) -> Optional[str]:
    """Get secret using global manager"""
    return get_secret_manager().get_secret(key, fallback)


def set_secret(key: str, value: str) -> Dict[str, bool]:
    """Set secret using global manager"""
    return get_secret_manager().set_secret(key, value) 