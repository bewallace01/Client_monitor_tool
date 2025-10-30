"""
API Configuration Service
Handles CRUD operations, encryption, and file management for API configurations
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
from uuid import UUID

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import and_
from sqlalchemy.orm import Session
import logging

from app.core.config import settings
from app.models.api_config import APIConfig
from app.schemas.api_config import (
    APIConfigCreate,
    APIConfigUpdate,
    APIConfigResponse,
    APIUsageStats,
)


class EncryptionService:
    """Handles encryption/decryption of sensitive API data"""

    def __init__(self, encryption_key: Optional[str] = None):
        """Initialize with encryption key from settings or generate new one"""
        if encryption_key:
            self.cipher = Fernet(encryption_key.encode())
        else:
            # Use SECRET_KEY from settings as basis for encryption
            # Derive a consistent Fernet key from SECRET_KEY
            import hashlib
            import base64
            from app.core.config import settings
            # Derive a 32-byte key from SECRET_KEY
            key_bytes = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
            # Fernet requires base64-encoded 32-byte key
            fernet_key = base64.urlsafe_b64encode(key_bytes)
            self.cipher = Fernet(fernet_key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string"""
        if not plaintext:
            return ""
        encrypted = self.cipher.encrypt(plaintext.encode())
        return encrypted.decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a string"""
        if not ciphertext:
            return ""
        try:
            decrypted = self.cipher.decrypt(ciphertext.encode())
            return decrypted.decode()
        except InvalidToken:
            logging.error(f"Failed to decrypt: Invalid encryption key. The ENCRYPTION_KEY may have changed.")
            raise ValueError("Failed to decrypt API credentials. The encryption key may have changed. Please re-enter your API key.")


# Initialize encryption service (in production, use secure key management)
encryption_service = EncryptionService()


class APIConfigService:
    """Service for managing API configurations"""

    @staticmethod
    def get_config_file_path(business_id: UUID) -> Path:
        """Get the file path for a business's API configuration"""
        config_dir = Path("api_configs")
        config_dir.mkdir(exist_ok=True)
        return config_dir / f"{business_id}.json"

    @staticmethod
    def create_config_file(business_id: UUID, configs: List[APIConfig]) -> str:
        """Create or update the API configuration file for a business"""
        file_path = APIConfigService.get_config_file_path(business_id)

        config_data = {
            "business_id": str(business_id),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "configs": []
        }

        for config in configs:
            config_data["configs"].append({
                "id": str(config.id),
                "provider": config.provider,
                "provider_name": config.provider_name,
                "is_active": config.is_active,
                "max_tokens_per_month": config.max_tokens_per_month,
                "rate_limit_per_hour": config.rate_limit_per_hour,
                # Note: Encrypted values stored in DB, not in file for double security
            })

        with open(file_path, 'w') as f:
            json.dump(config_data, f, indent=2)

        return str(file_path)

    @staticmethod
    def get_api_configs(
        db: Session,
        business_id: UUID,
        skip: int = 0,
        limit: int = 50,
        provider: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[APIConfig], int]:
        """Get API configurations for a business"""
        query = db.query(APIConfig).filter(APIConfig.business_id == business_id)

        if provider:
            query = query.filter(APIConfig.provider == provider)

        if is_active is not None:
            query = query.filter(APIConfig.is_active == is_active)

        total = query.count()
        configs = query.offset(skip).limit(limit).all()

        return configs, total

    @staticmethod
    def get_api_config_by_id(
        db: Session,
        config_id: UUID,
        business_id: UUID
    ) -> Optional[APIConfig]:
        """Get a specific API configuration"""
        return db.query(APIConfig).filter(
            and_(
                APIConfig.id == config_id,
                APIConfig.business_id == business_id
            )
        ).first()

    @staticmethod
    def get_api_config_by_provider(
        db: Session,
        business_id: UUID,
        provider: str
    ) -> Optional[APIConfig]:
        """Get API configuration by provider for a business"""
        return db.query(APIConfig).filter(
            and_(
                APIConfig.business_id == business_id,
                APIConfig.provider == provider
            )
        ).first()

    @staticmethod
    def create_api_config(
        db: Session,
        config_create: APIConfigCreate,
        user_id: Optional[int] = None
    ) -> APIConfig:
        """Create a new API configuration"""
        # Check if config already exists for this provider
        existing = APIConfigService.get_api_config_by_provider(
            db,
            config_create.business_id,
            config_create.provider
        )
        if existing:
            raise ValueError(f"API configuration for {config_create.provider} already exists")

        # Encrypt sensitive data
        encrypted_data = {}
        if config_create.api_key:
            encrypted_data['api_key'] = encryption_service.encrypt(config_create.api_key)
        if config_create.api_secret:
            encrypted_data['api_secret'] = encryption_service.encrypt(config_create.api_secret)
        if config_create.access_token:
            encrypted_data['access_token'] = encryption_service.encrypt(config_create.access_token)
        if config_create.refresh_token:
            encrypted_data['refresh_token'] = encryption_service.encrypt(config_create.refresh_token)

        # Create config
        db_config = APIConfig(
            business_id=config_create.business_id,
            provider=config_create.provider,
            provider_name=config_create.provider_name,
            max_tokens_per_month=config_create.max_tokens_per_month,
            rate_limit_per_hour=config_create.rate_limit_per_hour,
            cost_per_1k_tokens=config_create.cost_per_1k_tokens,
            is_active=config_create.is_active,
            config_data=config_create.config_data,
            created_by_user_id=user_id,
            updated_by_user_id=user_id,
            **encrypted_data
        )

        db.add(db_config)
        db.commit()
        db.refresh(db_config)

        # Update config file
        configs, _ = APIConfigService.get_api_configs(db, config_create.business_id)
        file_path = APIConfigService.create_config_file(config_create.business_id, configs)

        db_config.config_file_path = file_path
        db.commit()
        db.refresh(db_config)

        return db_config

    @staticmethod
    def update_api_config(
        db: Session,
        config_id: UUID,
        business_id: UUID,
        config_update: APIConfigUpdate,
        user_id: Optional[int] = None
    ) -> Optional[APIConfig]:
        """Update an existing API configuration"""
        db_config = APIConfigService.get_api_config_by_id(db, config_id, business_id)
        if not db_config:
            return None

        # Update encrypted fields
        if config_update.api_key is not None:
            db_config.api_key = encryption_service.encrypt(config_update.api_key)
        if config_update.api_secret is not None:
            db_config.api_secret = encryption_service.encrypt(config_update.api_secret)
        if config_update.access_token is not None:
            db_config.access_token = encryption_service.encrypt(config_update.access_token)
        if config_update.refresh_token is not None:
            db_config.refresh_token = encryption_service.encrypt(config_update.refresh_token)

        # Update non-encrypted fields
        update_data = config_update.dict(exclude_unset=True, exclude={'api_key', 'api_secret', 'access_token', 'refresh_token'})
        for field, value in update_data.items():
            setattr(db_config, field, value)

        db_config.updated_by_user_id = user_id
        db_config.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(db_config)

        # Update config file
        configs, _ = APIConfigService.get_api_configs(db, business_id)
        APIConfigService.create_config_file(business_id, configs)

        return db_config

    @staticmethod
    def delete_api_config(
        db: Session,
        config_id: UUID,
        business_id: UUID
    ) -> bool:
        """Delete an API configuration"""
        db_config = APIConfigService.get_api_config_by_id(db, config_id, business_id)
        if not db_config:
            return False

        db.delete(db_config)
        db.commit()

        # Update config file
        configs, _ = APIConfigService.get_api_configs(db, business_id)
        if configs:
            APIConfigService.create_config_file(business_id, configs)
        else:
            # Remove file if no configs left
            file_path = APIConfigService.get_config_file_path(business_id)
            if file_path.exists():
                file_path.unlink()

        return True

    @staticmethod
    def get_decrypted_api_key(db: Session, config_id: UUID, business_id: UUID) -> Optional[str]:
        """Get decrypted API key for a configuration"""
        db_config = APIConfigService.get_api_config_by_id(db, config_id, business_id)
        if not db_config or not db_config.api_key:
            return None

        return encryption_service.decrypt(db_config.api_key)

    @staticmethod
    def get_usage_stats(db: Session, business_id: UUID) -> List[APIUsageStats]:
        """Get usage statistics for all API configurations"""
        configs, _ = APIConfigService.get_api_configs(db, business_id)

        stats = []
        for config in configs:
            usage_stat = APIUsageStats(
                config_id=config.id,
                provider=config.provider,
                tokens_used_current_month=config.tokens_used_current_month or 0,
                max_tokens_per_month=config.max_tokens_per_month,
                requests_this_hour=config.requests_this_hour or 0,
                rate_limit_per_hour=config.rate_limit_per_hour,
                estimated_monthly_cost=config.estimated_monthly_cost,
            )
            stats.append(usage_stat)

        return stats

    @staticmethod
    def record_api_usage(
        db: Session,
        config_id: UUID,
        business_id: UUID,
        tokens_used: int = 1
    ) -> Optional[APIConfig]:
        """Record API usage (increment counters)"""
        db_config = APIConfigService.get_api_config_by_id(db, config_id, business_id)
        if not db_config:
            return None

        # Update usage counters
        db_config.tokens_used_current_month = (db_config.tokens_used_current_month or 0) + tokens_used
        db_config.requests_this_hour = (db_config.requests_this_hour or 0) + 1
        db_config.last_request_time = datetime.utcnow()

        # Update estimated cost
        if db_config.cost_per_1k_tokens:
            db_config.estimated_monthly_cost = (
                (db_config.tokens_used_current_month / 1000) * db_config.cost_per_1k_tokens
            )

        db.commit()
        db.refresh(db_config)

        return db_config

    @staticmethod
    def reset_monthly_usage(db: Session, business_id: UUID) -> int:
        """Reset monthly usage counters (called by scheduler on month start)"""
        configs, _ = APIConfigService.get_api_configs(db, business_id)

        count = 0
        for config in configs:
            config.tokens_used_current_month = 0
            config.estimated_monthly_cost = 0.0
            config.last_reset_date = datetime.utcnow()
            count += 1

        db.commit()
        return count

    @staticmethod
    def reset_hourly_usage(db: Session, business_id: UUID) -> int:
        """Reset hourly usage counters (called by scheduler every hour)"""
        configs, _ = APIConfigService.get_api_configs(db, business_id)

        count = 0
        for config in configs:
            config.requests_this_hour = 0
            count += 1

        db.commit()
        return count
