"""
Geospatial Validator

Validates geospatial operations and data.
"""

from typing import Dict, List, Any


class GeospatialValidator:
    """
    Validates geospatial operations and data.
    """
    
    def __init__(self):
        self.issues: List[str] = []
    
    def validate_raster_format(self, format_name: str) -> List[str]:
        """Validate raster format."""
        issues = []
        supported_formats = ["GTiff", "HFA", "JPEG", "PNG", "GIF", "BMP", "ENVI", "GPKG"]
        
        if format_name not in supported_formats:
            issues.append(f"Unsupported raster format: {format_name}")
        
        return issues
    
    def validate_vector_format(self, format_name: str) -> List[str]:
        """Validate vector format."""
        issues = []
        supported_formats = ["ESRI Shapefile", "GeoJSON", "GPKG", "GML", "KML"]
        
        if format_name not in supported_formats:
            issues.append(f"Unsupported vector format: {format_name}")
        
        return issues
    
    def validate_crs(self, crs_string: str) -> List[str]:
        """Validate CRS string."""
        issues = []
        
        if not crs_string:
            issues.append("CRS is required")
        elif not crs_string.startswith(("EPSG:", "PROJ:", "+proj=")):
            issues.append("CRS must be in EPSG, PROJ, or proj4 format")
        
        return issues
    
    def validate_extent(
        self,
        min_x: float,
        min_y: float,
        max_x: float,
        max_y: float
    ) -> List[str]:
        """Validate spatial extent."""
        issues = []
        
        if min_x >= max_x:
            issues.append("min_x must be less than max_x")
        
        if min_y >= max_y:
            issues.append("min_y must be less than max_y")
        
        if min_x < -180 or max_x > 180:
            issues.append("X coordinates out of valid longitude range")
        
        if min_y < -90 or max_y > 90:
            issues.append("Y coordinates out of valid latitude range")
        
        return issues
    
    def validate_resolution(self, resolution: float) -> List[str]:
        """Validate raster resolution."""
        issues = []
        
        if resolution <= 0:
            issues.append("Resolution must be positive")
        elif resolution > 360:
            issues.append("Resolution too large for geographic data")
        
        return issues
    
    def validate_buffer_distance(self, distance: float) -> List[str]:
        """Validate buffer distance."""
        issues = []
        
        if distance < 0:
            issues.append("Buffer distance cannot be negative")
        
        return issues
    
    def validate_band_index(self, band_index: int, max_bands: int) -> List[str]:
        """Validate band index."""
        issues = []
        
        if band_index < 1:
            issues.append("Band index must be at least 1")
        elif band_index > max_bands:
            issues.append(f"Band index exceeds number of bands ({max_bands})")
        
        return issues
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary."""
        return {
            "issues": self.issues,
            "issue_count": len(self.issues),
            "has_critical": any("required" in i.lower() for i in self.issues)
        }
