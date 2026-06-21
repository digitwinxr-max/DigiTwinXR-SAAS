"""
Rasterio Adapter

Provides Rasterio-based raster reading, window operations, and band access.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
import hashlib
import numpy as np

try:
    import rasterio
    from rasterio.windows import Window
    from rasterio.warp import calculate_default_transform, reproject, Resampling
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class RasterWindow:
    """Rasterio window."""
    col_off: int
    row_off: int
    width: int
    height: int


@dataclass
class RasterProfile:
    """Raster profile."""
    driver: str
    width: int
    height: int
    crs: str
    transform: Any
    nodata: Optional[float]
    dtype: str
    count: int
    compress: Optional[str] = None


class RasterioAdapter:
    """
    Rasterio adapter for raster operations.

    Features:
    - Raster reading
    - Window operations
    - Band access
    """

    def __init__(self):
        self._crs_registry: Dict[str, str] = {}
        self._datasets: Dict[str, Any] = {}

    def open(self, file_path: str) -> Optional[RasterProfile]:
        """Open a raster dataset."""
        if not RASTERIO_AVAILABLE:
            logger.warning("RasterIO not available, returning mock profile")
            return RasterProfile(
                driver="GTiff",
                width=1024,
                height=1024,
                crs="EPSG:4326",
                transform=None,
                nodata=-9999,
                dtype="float32",
                count=3
            )
        
        try:
            with rasterio.open(file_path) as dataset:
                self._datasets[file_path] = dataset
                return RasterProfile(
                    driver=dataset.driver,
                    width=dataset.width,
                    height=dataset.height,
                    crs=str(dataset.crs) if dataset.crs else "EPSG:4326",
                    transform=dataset.transform,
                    nodata=dataset.nodata,
                    dtype=str(dataset.dtypes[0]),
                    count=dataset.count,
                    compress=dataset.compression.value if hasattr(dataset.compression, 'value') else None
                )
        except Exception as e:
            logger.error(f"Error opening raster {file_path}: {e}")
            return None

    def read_band(
        self,
        file_path: str,
        band_index: int = 1,
        window: Optional[RasterWindow] = None
    ) -> Optional[np.ndarray]:
        """Read raster band data."""
        if not RASTERIO_AVAILABLE:
            logger.warning("RasterIO not available")
            return None
        
        try:
            with rasterio.open(file_path) as dataset:
                if band_index < 1 or band_index > dataset.count:
                    logger.error(f"Band index {band_index} out of range")
                    return None
                
                if window:
                    win = Window(window.col_off, window.row_off, window.width, window.height)
                    data = dataset.read(band_index, window=win)
                else:
                    data = dataset.read(band_index)
                
                return data
            
        except Exception as e:
            logger.error(f"Error reading band {band_index} from {file_path}: {e}")
            return None

    def read_multi_band(
        self,
        file_path: str,
        band_indexes: List[int],
        window: Optional[RasterWindow] = None
    ) -> Optional[np.ndarray]:
        """Read multiple bands."""
        if not RASTERIO_AVAILABLE:
            logger.warning("RasterIO not available")
            return None
        
        try:
            with rasterio.open(file_path) as dataset:
                # Validate band indexes
                for idx in band_indexes:
                    if idx < 1 or idx > dataset.count:
                        logger.error(f"Band index {idx} out of range")
                        return None
                
                if window:
                    win = Window(window.col_off, window.row_off, window.width, window.height)
                    data = dataset.read(band_indexes, window=win)
                else:
                    data = dataset.read(band_indexes)
                
                return data
            
        except Exception as e:
            logger.error(f"Error reading bands from {file_path}: {e}")
            return None

    def write(
        self,
        file_path: str,
        data: np.ndarray,
        profile: RasterProfile
    ) -> bool:
        """Write raster data."""
        if not RASTERIO_AVAILABLE:
            logger.warning("RasterIO not available")
            return False
        
        try:
            with rasterio.open(
                file_path,
                'w',
                driver=profile.driver,
                width=profile.width,
                height=profile.height,
                count=profile.count,
                dtype=profile.dtype,
                crs=profile.crs,
                transform=profile.transform,
                nodata=profile.nodata,
                compress=profile.compress
            ) as dataset:
                dataset.write(data)
                return True
            
        except Exception as e:
            logger.error(f"Error writing raster to {file_path}: {e}")
            return False

    def get_window(
        self,
        file_path: str,
        col_off: int,
        row_off: int,
        width: int,
        height: int
    ) -> RasterWindow:
        """Create a window for reading."""
        return RasterWindow(col_off, row_off, width, height)

    def get_band_statistics(
        self,
        file_path: str,
        band_index: int = 1
    ) -> Dict[str, float]:
        """Get band statistics."""
        if not RASTERIO_AVAILABLE:
            logger.warning("RasterIO not available, returning mock stats")
            return {
                "min": 0.0,
                "max": 255.0,
                "mean": 127.5,
                "std": 50.0
            }
        
        try:
            with rasterio.open(file_path) as dataset:
                if band_index < 1 or band_index > dataset.count:
                    return {"min": 0.0, "max": 0.0, "mean": 0.0, "std": 0.0}
                
                data = dataset.read(band_index)
                return {
                    "min": float(np.min(data)),
                    "max": float(np.max(data)),
                    "mean": float(np.mean(data)),
                    "std": float(np.std(data))
                }
            
        except Exception as e:
            logger.error(f"Error getting statistics from {file_path}: {e}")
            return {"min": 0.0, "max": 0.0, "mean": 0.0, "std": 0.0}

    def get_histogram(
        self,
        file_path: str,
        band_index: int = 1,
        bins: int = 256
    ) -> Dict[str, Any]:
        """Get band histogram."""
        if not RASTERIO_AVAILABLE:
            logger.warning("RasterIO not available, returning mock histogram")
            return {
                "counts": [0] * bins,
                "bins": bins
            }
        
        try:
            with rasterio.open(file_path) as dataset:
                if band_index < 1 or band_index > dataset.count:
                    return {"counts": [], "bins": 0}
                
                data = dataset.read(band_index)
                hist, bin_edges = np.histogram(data.flatten(), bins=bins)
                
                return {
                    "counts": hist.tolist(),
                    "bin_edges": bin_edges.tolist()
                }
            
        except Exception as e:
            logger.error(f"Error getting histogram from {file_path}: {e}")
            return {"counts": [], "bins": 0}

    def compute_checksum(self, file_path: str, band_index: int = 1) -> str:
        """Compute MD5 checksum for band."""
        try:
            with rasterio.open(file_path) as dataset:
                if band_index < 1 or band_index > dataset.count:
                    return ""
                
                data = dataset.read(band_index)
                checksum = hashlib.md5(data.tobytes()).hexdigest()
                return checksum
            
        except Exception as e:
            logger.error(f"Error computing checksum for {file_path}: {e}")
            return ""

    def get_geotransform(self, file_path: str) -> Tuple:
        """Get geotransform."""
        if not RASTERIO_AVAILABLE:
            logger.warning("RasterIO not available, returning mock transform")
            return (0, 1, 0, 0, 0, 1)
        
        try:
            with rasterio.open(file_path) as dataset:
                return tuple(dataset.transform)
            
        except Exception as e:
            logger.error(f"Error getting geotransform from {file_path}: {e}")
            return (0, 1, 0, 0, 0, 1)

    def reproject(
        self,
        source_path: str,
        target_path: str,
        target_crs: str,
        resampling: str = "bilinear"
    ) -> bool:
        """Reproject raster."""
        if not RASTERIO_AVAILABLE:
            logger.warning("RasterIO not available")
            return False
        
        try:
            # Map resampling method
            resampling_map = {
                "nearest": Resampling.nearest,
                "bilinear": Resampling.bilinear,
                "cubic": Resampling.cubic,
                "lanczos": Resampling.lanczos,
                "average": Resampling.average
            }
            resample = resampling_map.get(resampling, Resampling.bilinear)
            
            with rasterio.open(source_path) as src:
                transform, width, height = calculate_default_transform(
                    src.crs, target_crs, src.width, src.height,
                    *src.bounds
                )
                
                kwargs = src.meta.copy()
                kwargs.update({
                    'crs': target_crs,
                    'transform': transform,
                    'width': width,
                    'height': height
                })
                
                with rasterio.open(target_path, 'w', **kwargs) as dst:
                    for i in range(1, src.count + 1):
                        reproject(
                            source=rasterio.band(src, i),
                            destination=rasterio.band(dst, i),
                            src_transform=src.transform,
                            src_crs=src.crs,
                            dst_transform=transform,
                            dst_crs=target_crs,
                            resampling=resample
                        )
                
                return True
            
        except Exception as e:
            logger.error(f"Error reprojecting {source_path} to {target_path}: {e}")
            return False
