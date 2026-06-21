"""Video Intelligence Layer"""
from .frigate import frigate_router
from .opencv import opencv_router
from .yolo import yolo_router
from .deepstream import deepstream_router

__all__ = [
    "frigate_router",
    "opencv_router",
    "yolo_router",
    "deepstream_router",
]
