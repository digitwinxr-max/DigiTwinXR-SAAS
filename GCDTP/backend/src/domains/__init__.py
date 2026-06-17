"""
Domains Module

Infrastructure domain plugins for electrical, water, and transport systems.
"""

from .base_domain import BaseDomainPlugin, DomainMetadata, GenericDomain
from .domain_registry import (
    DomainRegistry,
    get_domain_registry,
    get_domain,
    list_domains,
)

__all__ = [
    "BaseDomainPlugin",
    "DomainMetadata",
    "GenericDomain",
    "DomainRegistry",
    "get_domain_registry",
    "get_domain",
    "list_domains",
]
