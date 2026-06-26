"""SQLAlchemy Base for all models."""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DeferredRelationshipRegistry:
    """Registry for deferred relationship setup.
    
    This class allows models to register relationships that will be
    configured after all models are loaded, avoiding circular import
    issues with SQLAlchemy mapper configuration.
    """
    
    _registry = []
    
    @classmethod
    def register(cls, target_model, relationship_name, relationship_def):
        """Register a relationship for deferred setup.
        
        Args:
            target_model: The model class to add the relationship to
            relationship_name: Name of the relationship attribute
            relationship_def: Tuple of (relationship_class, **kwargs)
        """
        cls._registry.append((target_model, relationship_name, relationship_def))
    
    @classmethod
    def setup_all(cls):
        """Set up all registered relationships.
        
        This should be called after all models are imported.
        """
        for target_model, relationship_name, (rel_class, kwargs) in cls._registry:
            from sqlalchemy.orm import relationship
            rel = relationship(rel_class, **kwargs)
            setattr(target_model, relationship_name, rel)
        
        cls._registry.clear()
    
    @classmethod
    def clear(cls):
        """Clear the registry."""
        cls._registry.clear()
