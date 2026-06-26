"""
YOLO Detection Models

Detection metadata and model registry.
NO automatic actions, work orders, events, or agent execution.
Human approval required for all detections.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ModelSize(str, Enum):
    """YOLO model sizes."""
    NANO = "n"  # nano (fastest)
    SMALL = "s"  # small
    MEDIUM = "m"  # medium
    LARGE = "l"  # large
    EXTRA_LARGE = "x"  # extra large


class ModelType(str, Enum):
    """YOLO model types."""
    YOLOV8 = "yolov8"
    YOLOV9 = "yolov9"
    YOLOV10 = "yolov10"
    YOLOV11 = "yolov11"


@dataclass
class DetectionClass:
    """Detection class definition."""
    class_id: int
    name: str
    description: str
    category: str
    severity_levels: List[str] = field(default_factory=list)


@dataclass
class ConfidenceThreshold:
    """Confidence threshold configuration."""
    class_id: int
    min_confidence: float
    max_confidence: float = 1.0


@dataclass
class ModelMetadata:
    """YOLO model metadata."""
    model_id: str
    name: str
    model_type: ModelType
    model_size: ModelSize
    classes: List[DetectionClass]
    input_size: int
    confidence_default: float
    confidence_thresholds: List[ConfidenceThreshold]
    version: str
    trained_on: datetime
    accuracy_map: Optional[float] = None
    inference_time_ms: Optional[float] = None
    gpu_required: bool = False


@dataclass
class DetectionMetadata:
    """Detection result metadata (no actual detection)."""
    detection_id: str
    model_id: str
    frame_id: str
    timestamp: datetime
    class_id: int
    class_name: str
    confidence: float
    bbox_x: int
    bbox_y: int
    bbox_width: int
    bbox_height: int
    requires_review: bool = True
    approved: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None


class YOLORegistry:
    """
    YOLO model registry.
    
    ALLOWED:
    - Model metadata storage
    - Class registry
    - Confidence threshold configuration
    - Detection metadata storage
    
    FORBIDDEN:
    - Automatic actions
    - Work order creation
    - Event triggering
    - Agent execution
    """
    
    # Default COCO classes subset
    DEFAULT_CLASSES = [
        DetectionClass(0, "person", "Human person", "safety"),
        DetectionClass(1, "bicycle", "Bicycle", "vehicle"),
        DetectionClass(2, "car", "Car", "vehicle"),
        DetectionClass(3, "motorcycle", "Motorcycle", "vehicle"),
        DetectionClass(4, "airplane", "Airplane", "vehicle"),
        DetectionClass(5, "bus", "Bus", "vehicle"),
        DetectionClass(6, "train", "Train", "vehicle"),
        DetectionClass(7, "truck", "Truck", "vehicle"),
        DetectionClass(8, "boat", "Boat", "vehicle"),
        DetectionClass(15, "cat", "Cat", "animal"),
        DetectionClass(16, "dog", "Dog", "animal"),
        DetectionClass(17, "horse", "Horse", "animal"),
        DetectionClass(18, "sheep", "Sheep", "animal"),
        DetectionClass(19, "cow", "Cow", "animal"),
        DetectionClass(39, "backpack", "Backpack", "object"),
        DetectionClass(41, "umbrella", "Umbrella", "object"),
    ]
    
    def __init__(self):
        self._models: Dict[str, ModelMetadata] = {}
        self._classes: Dict[int, DetectionClass] = {c.class_id: c for c in self.DEFAULT_CLASSES}
        self._detections: Dict[str, DetectionMetadata] = {}
    
    def register_model(self, model: ModelMetadata) -> ModelMetadata:
        """Register a YOLO model."""
        self._models[model.model_id] = model
        return model
    
    def get_model(self, model_id: str) -> Optional[ModelMetadata]:
        """Get model by ID."""
        return self._models.get(model_id)
    
    def list_models(self) -> List[ModelMetadata]:
        """List all registered models."""
        return list(self._models.values())
    
    def register_class(self, detection_class: DetectionClass) -> DetectionClass:
        """Register a detection class."""
        self._classes[detection_class.class_id] = detection_class
        return detection_class
    
    def get_class(self, class_id: int) -> Optional[DetectionClass]:
        """Get class by ID."""
        return self._classes.get(class_id)
    
    def list_classes(self) -> List[DetectionClass]:
        """List all detection classes."""
        return list(self._classes.values())
    
    def add_detection(self, detection: DetectionMetadata) -> DetectionMetadata:
        """Add detection metadata."""
        self._detections[detection.detection_id] = detection
        return detection
    
    def get_detection(self, detection_id: str) -> Optional[DetectionMetadata]:
        """Get detection by ID."""
        return self._detections.get(detection_id)
    
    def approve_detection(
        self,
        detection_id: str,
        approved_by: str
    ) -> Optional[DetectionMetadata]:
        """Approve a detection (requires human action)."""
        detection = self._detections.get(detection_id)
        if detection:
            detection.approved = True
            detection.approved_by = approved_by
            detection.approved_at = datetime.now()
        return detection
    
    def list_detections(
        self,
        model_id: Optional[str] = None,
        approved_only: bool = False
    ) -> List[DetectionMetadata]:
        """List detections with filters."""
        detections = list(self._detections.values())
        
        if model_id:
            detections = [d for d in detections if d.model_id == model_id]
        if approved_only:
            detections = [d for d in detections if d.approved]
        
        return sorted(detections, key=lambda d: d.timestamp, reverse=True)
    
    def get_pending_approvals(self) -> List[DetectionMetadata]:
        """Get detections pending approval."""
        return [d for d in self._detections.values() if not d.approved]


# Singleton instance
_registry: Optional[YOLORegistry] = None


def get_yolo_registry() -> YOLORegistry:
    """Get or create YOLO registry singleton."""
    global _registry
    if _registry is None:
        _registry = YOLORegistry()
    return _registry
