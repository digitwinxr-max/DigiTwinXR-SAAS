"""Asset service for business logic."""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from ..models.asset import Asset, HAS_GEOMETRY
from ..schemas.asset import AssetCreate, AssetUpdate, GeoJSONFeature

# Try to import WKTElement from geoalchemy2
try:
    from geoalchemy2.elements import WKTElement
except ImportError:
    WKTElement = None


class AssetService:
    """Service class for asset operations."""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def create_point(longitude: float, latitude: float):
        """Create a PostGIS POINT geometry from coordinates.
        
        Args:
            longitude: X coordinate (longitude)
            latitude: Y coordinate (latitude)
            
        Returns:
            WKTElement representing the point in WGS84 (SRID 4326)
            or a dict with coordinates if PostGIS not available
        """
        if WKTElement is not None:
            point_wkt = f"POINT({longitude} {latitude})"
            return WKTElement(point_wkt, srid=4326)
        else:
            # Fallback for non-PostGIS databases
            return {"type": "Point", "coordinates": [longitude, latitude]}

    @staticmethod
    def update_point(asset: Asset) -> None:
        """Update an asset's geometry column from longitude/latitude.
        
        Args:
            asset: Asset instance to update
        """
        if asset.longitude is not None and asset.latitude is not None:
            asset.location = AssetService.create_point(
                asset.longitude, asset.latitude
            )
        else:
            asset.location = None

    def create_asset(self, asset_data: AssetCreate) -> Asset:
        """Create a new asset with spatial geometry."""
        asset = Asset(
            name=asset_data.name,
            asset_type=asset_data.asset_type,
            description=asset_data.description,
            longitude=asset_data.longitude,
            latitude=asset_data.latitude,
            status=asset_data.status,
        )
        # Auto-create geometry from coordinates
        self.update_point(asset)
        
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def get_asset(self, asset_id: UUID) -> Optional[Asset]:
        """Get an asset by ID."""
        return self.db.query(Asset).filter(Asset.id == asset_id).first()

    def get_assets(self, skip: int = 0, limit: int = 100) -> tuple[List[Asset], int]:
        """Get all assets with pagination."""
        total = self.db.query(Asset).count()
        assets = self.db.query(Asset).offset(skip).limit(limit).all()
        return assets, total

    def update_asset(self, asset_id: UUID, asset_data: AssetUpdate) -> Optional[Asset]:
        """Update an existing asset and its geometry."""
        asset = self.get_asset(asset_id)
        if not asset:
            return None
        
        update_data = asset_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(asset, field, value)
        
        # Auto-update geometry if coordinates changed
        self.update_point(asset)
        
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def delete_asset(self, asset_id: UUID) -> bool:
        """Delete an asset."""
        asset = self.get_asset(asset_id)
        if not asset:
            return False
        
        self.db.delete(asset)
        self.db.commit()
        return True

    def get_assets_geojson(self) -> List[GeoJSONFeature]:
        """Get all assets as GeoJSON features.
        
        Returns:
            List of GeoJSON Feature objects
        """
        assets = self.db.query(Asset).all()
        features = []
        
        for asset in assets:
            # Build geometry from coordinates (not raw WKB)
            if asset.longitude is not None and asset.latitude is not None:
                geometry = {
                    "type": "Point",
                    "coordinates": [asset.longitude, asset.latitude]
                }
            else:
                geometry = None
            
            properties = {
                "name": asset.name,
                "asset_type": asset.asset_type,
                "status": asset.status,
            }
            
            feature = GeoJSONFeature(
                id=str(asset.id),
                geometry=geometry,
                properties=properties
            )
            features.append(feature)
        
        return features
