"""
YOLO Registry Service

Registry service for YOLO models.
NO automatic actions, work orders, events, or agent execution.
"""

import logging
from typing import Dict, List, Optional, Any

from .models import (
    YOLORegistry,
    get_yolo_registry,
    ModelMetadata,
    ModelType,
    ModelSize,
    DetectionClass,
    ConfidenceThreshold,
    DetectionMetadata,
)


logger = logging.getLogger(__name__)


class YOLORegistryService:
    """
    YOLO model registry service.
    
    Features:
    - Model metadata registration
    - Class registry management
    - Confidence threshold configuration
    - Detection metadata storage
    - Human approval workflow
    
    LIMITATIONS:
    - NO automatic actions
    - NO work order creation
    - NO event triggering
    - NO agent execution
    """
    
    def __init__(self, registry: Optional[YOLORegistry] = None):
        self.registry = registry or get_yolo_registry()
    
    def register_model(
        self,
        model_id: str,
        name: str,
        model_type: ModelType,
        model_size: ModelSize,
        classes: List[DetectionClass],
        version: str = "latest"
    ) -> ModelMetadata:
        """
        Register a YOLO model.
        
        Args:
            model_id: Unique model ID
            name: Model name
            model_type: YOLO version
            model_size: Model size (n/s/m/l/x)
            classes: List of detection classes
            version: Model version
        
        Returns:
            ModelMetadata for the registered model
        """
        # Calculate default input size based on model size
        input_sizes = {
            ModelSize.NANO: 320,
            ModelSize.SMALL: 640,
            ModelSize.MEDIUM: 640,
            ModelSize.LARGE: 640,
            ModelSize.EXTRA_LARGE: 1280,
        }
        
        # Calculate default confidence
        confidences = {
            ModelSize.NANO: 0.4,
            ModelSize.SMALL: 0.35,
            ModelSize.MEDIUM: 0.3,
            ModelSize.LARGE: 0.25,
            ModelSize.EXTRA_LARGE: 0.2,
        }
        
        # Create confidence thresholds
        thresholds = [
            ConfidenceThreshold(
                class_id=c.class_id,
                min_confidence=confidences.get(model_size, 0.3)
            )
            for c in classes
        ]
        
        metadata = ModelMetadata(
            model_id=model_id,
            name=name,
            model_type=model_type,
            model_size=model_size,
            classes=classes,
            input_size=input_sizes.get(model_size, 640),
            confidence_default=confidences.get(model_size, 0.3),
            confidence_thresholds=thresholds,
            version=version,
            trained_on=None,
            gpu_required=model_size in (ModelSize.LARGE, ModelSize.EXTRA_LARGE)
        )
        
        return self.registry.register_model(metadata)
    
    def register_class(
        self,
        class_id: int,
        name: str,
        description: str,
        category: str
    ) -> DetectionClass:
        """
        Register a detection class.
        
        Args:
            class_id: Class ID (COCO convention)
            name: Class name
            description: Class description
            category: Category (safety, vehicle, animal, object)
        
        Returns:
            DetectionClass
        """
        detection_class = DetectionClass(
            class_id=class_id,
            name=name,
            description=description,
            category=category
        )
        return self.registry.register_class(detection_class)
    
    def record_detection(
        self,
        detection_id: str,
        model_id: str,
        frame_id: str,
        class_id: int,
        confidence: float,
        bbox: tuple
    ) -> DetectionMetadata:
        """
        Record detection metadata.
        
        All detections require human review.
        
        Args:
            detection_id: Unique detection ID
            model_id: Model used
            frame_id: Frame ID
            class_id: Detected class ID
            confidence: Detection confidence
            bbox: Bounding box (x, y, width, height)
        
        Returns:
            DetectionMetadata
        """
        # Get class name
        detection_class = self.registry.get_class(class_id)
        class_name = detection_class.name if detection_class else f"class_{class_id}"
        
        detection = DetectionMetadata(
            detection_id=detection_id,
            model_id=model_id,
            frame_id=frame_id,
            timestamp=None,
            class_id=class_id,
            class_name=class_name,
            confidence=confidence,
            bbox_x=bbox[0],
            bbox_y=bbox[1],
            bbox_width=bbox[2],
            bbox_height=bbox[3],
            requires_review=True,
            approved=False
        )
        
        return self.registry.add_detection(detection)
    
    def approve_detection(
        self,
        detection_id: str,
        approved_by: str
    ) -> Optional[DetectionMetadata]:
        """
        Approve a detection.
        
        Human approval required for all detections.
        
        Args:
            detection_id: Detection to approve
            approved_by: Approver identifier
        
        Returns:
            Updated DetectionMetadata
        """
        return self.registry.approve_detection(detection_id, approved_by)
    
    def get_model_by_type(
        self,
        model_type: ModelType,
        model_size: Optional[ModelSize] = None
    ) -> List[ModelMetadata]:
        """
        Get models by type.
        
        Args:
            model_type: YOLO version
            model_size: Optional size filter
        
        Returns:
            List of matching models
        """
        models = self.registry.list_models()
        models = [m for m in models if m.model_type == model_type]
        
        if model_size:
            models = [m for m in models if m.model_size == model_size]
        
        return models


# Singleton instance
_service: Optional[YOLORegistryService] = None


def get_yolo_service() -> YOLORegistryService:
    """Get or create YOLO service singleton."""
    global _service
    if _service is None:
        _service = YOLORegistryService()
    return _service
