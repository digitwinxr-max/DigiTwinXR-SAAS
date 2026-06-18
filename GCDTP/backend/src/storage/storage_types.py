"""
Storage Types

Defines storage-related types and enums.
"""

from enum import Enum


class BucketType(str, Enum):
    """Storage bucket types."""
    DOCUMENTS = "documents"
    ATTACHMENTS = "attachments"
    IMAGES = "images"
    CAD = "cad"
    BIM = "bim"
    POINTCLOUDS = "pointclouds"
    RASTERS = "rasters"
    DATASETS = "datasets"
    BACKUPS = "backups"
    TEMPORARY = "temporary"


class BucketStatus(str, Enum):
    """Bucket status."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class ObjectStatus(str, Enum):
    """Object status."""
    AVAILABLE = "available"
    DELETED = "deleted"
    ARCHIVED = "archived"
    LEGAL_HOLD = "legal_hold"


class RetentionMode(str, Enum):
    """Retention mode."""
    GOVERNANCE = "governance"
    COMPLIANCE = "compliance"


class RetentionStatus(str, Enum):
    """Retention status."""
    ACTIVE = "active"
    EXPIRED = "expired"
    RELEASED = "released"


class UploadStatus(str, Enum):
    """Upload status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class ReferenceType(str, Enum):
    """Storage reference types."""
    ASSET = "asset"
    DOCUMENT = "document"
    WORK_ORDER = "work_order"
    SIMULATION = "simulation"
    BACKUP = "backup"


class ChecksumAlgorithm(str, Enum):
    """Checksum algorithms."""
    MD5 = "MD5"
    SHA256 = "SHA256"
    SHA512 = "SHA512"
