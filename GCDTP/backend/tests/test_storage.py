"""
Tests for Storage Module

Tests bucket operations, object lifecycle, versioning, multipart uploads, retention policies, presigned URLs, and timeline integration.
"""

import pytest
from backend.src.storage import (
    StorageTypes,
    BucketType,
    BucketStatus,
    ObjectStatus,
    BucketManager,
    StorageBucket,
    ObjectManager,
    StoredObject,
    MetadataManager,
    MultipartUploadManager,
    RetentionManager,
    RetentionMode,
    VersionManager,
    PresignedURLManager,
    StorageValidator,
    StorageRegistry,
    ReferenceType,
)


class TestBucketManager:
    """Tests for BucketManager."""
    
    def test_get_bucket(self):
        """Test getting a bucket."""
        manager = BucketManager()
        bucket = manager.get_bucket_by_name("gcdtp-documents")
        assert bucket is not None
    
    def test_get_all_buckets(self):
        """Test getting all buckets."""
        manager = BucketManager()
        buckets = manager.get_all_buckets()
        assert len(buckets) >= 10
    
    def test_get_buckets_by_type(self):
        """Test getting buckets by type."""
        manager = BucketManager()
        buckets = manager.get_buckets_by_type(BucketType.DOCUMENTS)
        assert len(buckets) >= 1
    
    def test_suspend_bucket(self):
        """Test suspending a bucket."""
        manager = BucketManager()
        bucket = manager.get_bucket_by_name("gcdtp-documents")
        if bucket:
            result = manager.suspend_bucket(bucket.id)
            assert result is True


class TestObjectManager:
    """Tests for ObjectManager."""
    
    def test_create_object(self):
        """Test creating an object."""
        manager = ObjectManager()
        obj = manager.create_object(
            bucket_id="test-bucket",
            object_key="test/file.txt",
            content_type="text/plain",
            size_bytes=1024,
            checksum="abc123",
            owner_user_id="user-1",
            owner_organization_id="org-1"
        )
        assert obj.object_key == "test/file.txt"
    
    def test_get_object(self):
        """Test getting an object."""
        manager = ObjectManager()
        obj = manager.create_object(
            bucket_id="test-bucket",
            object_key="test/file.txt",
            content_type="text/plain",
            size_bytes=1024,
            checksum="abc123",
            owner_user_id="user-1",
            owner_organization_id="org-1"
        )
        retrieved = manager.get_object(obj.id)
        assert retrieved is not None
    
    def test_soft_delete(self):
        """Test soft deleting an object."""
        manager = ObjectManager()
        obj = manager.create_object(
            bucket_id="test-bucket",
            object_key="test/file.txt",
            content_type="text/plain",
            size_bytes=1024,
            checksum="abc123",
            owner_user_id="user-1",
            owner_organization_id="org-1"
        )
        result = manager.soft_delete(obj.id)
        assert result is True
    
    def test_restore(self):
        """Test restoring an object."""
        manager = ObjectManager()
        obj = manager.create_object(
            bucket_id="test-bucket",
            object_key="test/file.txt",
            content_type="text/plain",
            size_bytes=1024,
            checksum="abc123",
            owner_user_id="user-1",
            owner_organization_id="org-1"
        )
        manager.soft_delete(obj.id)
        result = manager.restore(obj.id)
        assert result is True
    
    def test_validate_checksum(self):
        """Test checksum validation."""
        manager = ObjectManager()
        obj = manager.create_object(
            bucket_id="test-bucket",
            object_key="test/file.txt",
            content_type="text/plain",
            size_bytes=1024,
            checksum="abc123",
            owner_user_id="user-1",
            owner_organization_id="org-1"
        )
        assert manager.validate_checksum(obj.id, "abc123") is True


class TestMetadataManager:
    """Tests for MetadataManager."""
    
    def test_add_metadata(self):
        """Test adding metadata."""
        manager = MetadataManager()
        metadata = manager.add_metadata("obj-1", "key1", "value1")
        assert metadata.key == "key1"
    
    def test_get_object_metadata(self):
        """Test getting object metadata."""
        manager = MetadataManager()
        manager.add_metadata("obj-1", "key1", "value1")
        manager.add_metadata("obj-1", "key2", "value2")
        metadata = manager.get_object_metadata("obj-1")
        assert len(metadata) == 2
    
    def test_add_asset_reference(self):
        """Test adding asset reference."""
        manager = MetadataManager()
        metadata = manager.add_asset_reference("obj-1", "asset-123")
        assert metadata.key == "asset_id"
    
    def test_add_tag(self):
        """Test adding tag."""
        manager = MetadataManager()
        manager.add_tag("obj-1", "important")
        tags = manager.get_tags("obj-1")
        assert "important" in tags


class TestMultipartUploadManager:
    """Tests for MultipartUploadManager."""
    
    def test_initiate_upload(self):
        """Test initiating multipart upload."""
        manager = MultipartUploadManager()
        upload = manager.initiate_upload(
            bucket_id="test-bucket",
            object_key="test/large-file.bin",
            content_type="application/octet-stream",
            total_size_bytes=1000000,
            chunk_size_bytes=100000,
            initiated_by="user-1"
        )
        assert upload.total_chunks == 10
    
    def test_get_upload(self):
        """Test getting an upload."""
        manager = MultipartUploadManager()
        upload = manager.initiate_upload(
            bucket_id="test-bucket",
            object_key="test/large-file.bin",
            content_type="application/octet-stream",
            total_size_bytes=1000000,
            chunk_size_bytes=100000,
            initiated_by="user-1"
        )
        retrieved = manager.get_upload(upload.upload_id)
        assert retrieved is not None
    
    def test_get_progress(self):
        """Test getting upload progress."""
        manager = MultipartUploadManager()
        upload = manager.initiate_upload(
            bucket_id="test-bucket",
            object_key="test/large-file.bin",
            content_type="application/octet-stream",
            total_size_bytes=1000000,
            chunk_size_bytes=100000,
            initiated_by="user-1"
        )
        manager.upload_part(upload.upload_id, 1, "etag1")
        progress = manager.get_progress(upload.upload_id)
        assert progress["uploaded_chunks"] == 1


class TestRetentionManager:
    """Tests for RetentionManager."""
    
    def test_create_policy(self):
        """Test creating a policy."""
        manager = RetentionManager()
        policy = manager.create_policy(
            name="30-day-retention",
            bucket_id="test-bucket",
            retention_days=30,
            retention_mode=RetentionMode.GOVERNANCE
        )
        assert policy.retention_days == 30
    
    def test_get_policies_by_bucket(self):
        """Test getting policies by bucket."""
        manager = RetentionManager()
        manager.create_policy("policy1", "bucket-1", 30, RetentionMode.GOVERNANCE)
        manager.create_policy("policy2", "bucket-1", 60, RetentionMode.COMPLIANCE)
        policies = manager.get_policies_by_bucket("bucket-1")
        assert len(policies) == 2
    
    def test_apply_legal_hold(self):
        """Test applying legal hold."""
        manager = RetentionManager()
        from datetime import datetime, timedelta
        result = manager.apply_legal_hold("obj-1", datetime.utcnow() + timedelta(days=30))
        assert result is True
        assert manager.is_legal_hold("obj-1") is True


class TestVersionManager:
    """Tests for VersionManager."""
    
    def test_create_version(self):
        """Test creating a version."""
        manager = VersionManager()
        version = manager.create_version(
            object_id="obj-1",
            version_id="v1",
            size_bytes=1024,
            checksum="abc123"
        )
        assert version.version_id == "v1"
    
    def test_get_versions(self):
        """Test getting versions."""
        manager = VersionManager()
        manager.create_version("obj-1", "v1", 1024, "abc")
        manager.create_version("obj-1", "v2", 2048, "def")
        versions = manager.get_versions("obj-1")
        assert len(versions) == 2
    
    def test_get_latest_version(self):
        """Test getting latest version."""
        manager = VersionManager()
        manager.create_version("obj-1", "v1", 1024, "abc")
        manager.create_version("obj-1", "v2", 2048, "def")
        latest = manager.get_latest_version("obj-1")
        assert latest.version_id == "v2"
    
    def test_rollback_to_version(self):
        """Test rolling back to a version."""
        manager = VersionManager()
        manager.create_version("obj-1", "v1", 1024, "abc")
        manager.create_version("obj-1", "v2", 2048, "def")
        result = manager.rollback_to_version("obj-1", "v1")
        assert result is True
        latest = manager.get_latest_version("obj-1")
        assert latest.version_id == "v1"


class TestPresignedURLManager:
    """Tests for PresignedURLManager."""
    
    def test_create_download_url(self):
        """Test creating download URL."""
        manager = PresignedURLManager()
        url = manager.create_download_url("test/file.txt", "test-bucket")
        assert url.object_key == "test/file.txt"
    
    def test_create_upload_url(self):
        """Test creating upload URL."""
        manager = PresignedURLManager()
        url = manager.create_upload_url("test/file.txt", "test-bucket")
        assert "upload" in url.url
    
    def test_is_valid(self):
        """Test URL validity check."""
        manager = PresignedURLManager()
        url = manager.create_download_url("test/file.txt", "test-bucket")
        assert manager.is_valid(url.id) is True
    
    def test_revoke_url(self):
        """Test revoking URL."""
        manager = PresignedURLManager()
        url = manager.create_download_url("test/file.txt", "test-bucket")
        result = manager.revoke_url(url.id)
        assert result is True


class TestStorageValidator:
    """Tests for StorageValidator."""
    
    def test_validate_bucket_name(self):
        """Test validating bucket name."""
        validator = StorageValidator()
        issues = validator.validate_bucket_name("valid-bucket")
        assert len(issues) == 0
    
    def test_validate_bucket_name_invalid(self):
        """Test validating invalid bucket name."""
        validator = StorageValidator()
        issues = validator.validate_bucket_name("ab")
        assert len(issues) > 0
    
    def test_validate_object_key(self):
        """Test validating object key."""
        validator = StorageValidator()
        issues = validator.validate_object_key("valid/key.txt")
        assert len(issues) == 0
    
    def test_validate_upload_size(self):
        """Test validating upload size."""
        validator = StorageValidator()
        issues = validator.validate_upload_size(1024)
        assert len(issues) == 0
    
    def test_validate_content_type(self):
        """Test validating content type."""
        validator = StorageValidator()
        issues = validator.validate_content_type("text/plain")
        assert len(issues) == 0


class TestStorageRegistry:
    """Tests for StorageRegistry."""
    
    def test_register_reference(self):
        """Test registering reference."""
        registry = StorageRegistry()
        ref = registry.register_reference(
            object_id="obj-1",
            reference_type=ReferenceType.ASSET,
            reference_id="asset-123",
            owner_organization_id="org-1"
        )
        assert ref.reference_type == ReferenceType.ASSET
    
    def test_get_object_references(self):
        """Test getting object references."""
        registry = StorageRegistry()
        registry.register_reference("obj-1", ReferenceType.ASSET, "asset-1", "org-1")
        registry.register_reference("obj-1", ReferenceType.DOCUMENT, "doc-1", "org-1")
        refs = registry.get_object_references("obj-1")
        assert len(refs) == 2
    
    def test_get_references_by_type(self):
        """Test getting references by type."""
        registry = StorageRegistry()
        registry.register_reference("obj-1", ReferenceType.ASSET, "asset-1", "org-1")
        refs = registry.get_references_by_type(ReferenceType.ASSET)
        assert len(refs) >= 1


class TestBucketType:
    """Tests for BucketType."""
    
    def test_bucket_types(self):
        """Test bucket type values."""
        assert BucketType.DOCUMENTS.value == "documents"
        assert BucketType.IMAGES.value == "images"


class TestObjectStatus:
    """Tests for ObjectStatus."""
    
    def test_object_statuses(self):
        """Test object status values."""
        assert ObjectStatus.AVAILABLE.value == "available"
        assert ObjectStatus.DELETED.value == "deleted"


class TestRetentionMode:
    """Tests for RetentionMode."""
    
    def test_retention_modes(self):
        """Test retention mode values."""
        assert RetentionMode.GOVERNANCE.value == "governance"
        assert RetentionMode.COMPLIANCE.value == "compliance"


class TestReferenceType:
    """Tests for ReferenceType."""
    
    def test_reference_types(self):
        """Test reference type values."""
        assert ReferenceType.ASSET.value == "asset"
        assert ReferenceType.DOCUMENT.value == "document"
