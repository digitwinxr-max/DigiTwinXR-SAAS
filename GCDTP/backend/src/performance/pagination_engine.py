"""
Pagination Engine

Provides pagination support for API endpoints.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PaginationParams:
    """Pagination parameters."""
    page: int = 1
    page_size: int = 20
    offset: Optional[int] = None
    cursor: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: str = "asc"  # asc or desc
    filters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.filters is None:
            self.filters = {}


@dataclass
class PageMetadata:
    """Page metadata."""
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool
    next_cursor: Optional[str] = None
    previous_cursor: Optional[str] = None


@dataclass
class PaginatedResult:
    """Paginated result."""
    items: List[Any]
    metadata: PageMetadata
    pagination_type: str  # "offset" or "cursor"


class PaginationEngine:
    """
    Provides pagination support.
    
    Supports:
    - Offset pagination
    - Cursor pagination
    - Sorting
    - Filtering
    - Page metadata
    """
    
    def __init__(self):
        self._max_page_size = 100
        self._default_page_size = 20
    
    def paginate_offset(
        self,
        items: List[Any],
        total_count: int,
        params: PaginationParams
    ) -> PaginatedResult:
        """
        Paginate using offset.
        
        Args:
            items: Items for current page
            total_count: Total item count
            params: Pagination parameters
            
        Returns:
            PaginatedResult
        """
        page = max(1, params.page)
        page_size = min(params.page_size, self._max_page_size)
        total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
        
        metadata = PageMetadata(
            page=page,
            page_size=page_size,
            total_items=total_count,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )
        
        return PaginatedResult(
            items=items,
            metadata=metadata,
            pagination_type="offset"
        )
    
    def paginate_cursor(
        self,
        items: List[Any],
        total_count: int,
        params: PaginationParams,
        cursor_field: str = "id"
    ) -> PaginatedResult:
        """
        Paginate using cursor.
        
        Args:
            items: Items for current page
            total_count: Total item count
            params: Pagination parameters
            cursor_field: Field to use for cursor
            
        Returns:
            PaginatedResult
        """
        page_size = min(params.page_size, self._max_page_size)
        
        # Calculate cursors
        next_cursor = None
        previous_cursor = None
        
        if items:
            if params.cursor:
                previous_cursor = self._encode_cursor(items[0], cursor_field)
            
            if len(items) == page_size:
                next_cursor = self._encode_cursor(items[-1], cursor_field)
        
        has_next = next_cursor is not None
        has_previous = params.cursor is not None
        
        metadata = PageMetadata(
            page=1,  # Cursor pagination doesn't use page numbers
            page_size=page_size,
            total_items=total_count,
            total_pages=0,  # Unknown for cursor pagination
            has_next=has_next,
            has_previous=has_previous,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor
        )
        
        return PaginatedResult(
            items=items,
            metadata=metadata,
            pagination_type="cursor"
        )
    
    def _encode_cursor(self, item: Any, field: str) -> str:
        """Encode cursor from item."""
        import base64
        value = getattr(item, field, None) or str(item.get(field, ""))
        return base64.b64encode(value.encode()).decode()
    
    def _decode_cursor(self, cursor: str) -> str:
        """Decode cursor to value."""
        import base64
        return base64.b64decode(cursor.encode()).decode()
    
    def sort_items(
        self,
        items: List[Any],
        sort_by: str,
        sort_order: str = "asc"
    ) -> List[Any]:
        """
        Sort items.
        
        Args:
            items: Items to sort
            sort_by: Field to sort by
            sort_order: Sort order
            
        Returns:
            Sorted items
        """
        reverse = sort_order.lower() == "desc"
        
        def get_value(item: Any) -> Any:
            if isinstance(item, dict):
                return item.get(sort_by, "")
            return getattr(item, sort_by, "")
        
        return sorted(items, key=get_value, reverse=reverse)
    
    def filter_items(
        self,
        items: List[Any],
        filters: Dict[str, Any]
    ) -> List[Any]:
        """
        Filter items.
        
        Args:
            items: Items to filter
            filters: Filter criteria
            
        Returns:
            Filtered items
        """
        result = items
        
        for field, value in filters.items():
            if value is None:
                continue
            
            if isinstance(value, str) and value.startswith("!"):
                # Negation
                result = [i for i in result if self._get_field(i, field) != value[1:]]
            elif isinstance(value, list):
                # IN clause
                result = [i for i in result if self._get_field(i, field) in value]
            elif isinstance(value, dict):
                # Operators
                field_val = self._get_field(i, field)
                for op, op_val in value.items():
                    if op == "gt" and not field_val > op_val:
                        result = [i for i in result if field_val > op_val]
                    elif op == "gte" and not field_val >= op_val:
                        result = [i for i in result if field_val >= op_val]
                    elif op == "lt" and not field_val < op_val:
                        result = [i for i in result if field_val < op_val]
                    elif op == "lte" and not field_val <= op_val:
                        result = [i for i in result if field_val <= op_val]
                    elif op == "contains" and op_val not in str(field_val):
                        result = [i for i in result if op_val in str(field_val)]
            else:
                # Exact match
                result = [i for i in result if self._get_field(i, field) == value]
        
        return result
    
    def _get_field(self, item: Any, field: str) -> Any:
        """Get field value from item."""
        if isinstance(item, dict):
            return item.get(field)
        return getattr(item, field, None)
    
    def get_page_slice(
        self,
        items: List[Any],
        page: int,
        page_size: int
    ) -> List[Any]:
        """
        Get slice of items for a page.
        
        Args:
            items: All items
            page: Page number (1-based)
            page_size: Items per page
            
        Returns:
            Items for the page
        """
        start = (page - 1) * page_size
        end = start + page_size
        return items[start:end]
