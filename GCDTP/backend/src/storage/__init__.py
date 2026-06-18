"""
Storage Module

Provides object storage capabilities using MinIO:
- Bucket management
- Object management
- Metadata tracking
- Multipart uploads
- Retention policies
- Version management
- Presigned URLs
- Storage registry

Components:
- StorageTypes
- MinIOClient
- BucketManager
- ObjectManager
- MetadataManager
- MultipartUploadManager
- RetentionManager
- VersionManager
- PresignedURLManager
- StorageValidator
- StorageRegistry
"""

from .storage_types import (
    BucketType,
    BucketStatus,
    ObjectStatus,
    RetentionMode,
    RetentionStatus,
    UploadStatus,
    ReferenceType,
    ChecksumAlgorithm,
)
from .minio_client import MinIOClient, MinIOConfig, MinIOObject
from .bucket_manager import BucketManager, StorageBucket
from .object_manager import ObjectManager, StoredObject
from .metadata_manager import MetadataManager, ObjectMetadata
from .multipart_upload_manager import MultipartUploadManager, MultipartUpload
from .retention_manager import RetentionManager, RetentionPolicy
from .version_manager import VersionManager, ObjectVersion
from .presigned_url_manager import PresignedURLManager, PresignedURL
from .storage_validator import StorageValidator
from .storage_registry import StorageRegistry, StorageReference


__all__ = [
    # Types
    "BucketType",
    "BucketStatus",
    "ObjectStatus",
    "RetentionMode",
    "RetentionStatus",
    "UploadStatus",
    "ReferenceType",
    "ChecksumAlgorithm",
    # MinIO Client
    "MinIOClient",
    "MinIOConfig",
    "MinIOObject",
    # Bucket Manager
    "BucketManager",
    "StorageBucket",
    # Object Manager
    "ObjectManager",
    "StoredObject",
    # Metadata Manager
    "MetadataManager",
    "ObjectMetadata",
    # Multipart Upload Manager
    "MultipartUploadManager",
    "MultipartUpload",
    # Retention Manager
    "RetentionManager",
    "RetentionPolicy",
    # Version Manager
    "VersionManager",
    "ObjectVersion",
    # Presigned URL Manager
    "PresignedURLManager",
    "PresignedURL",
    # Validator
    "StorageValidator",
    # Registry
    "StorageRegistry",
    "StorageReference",
]
