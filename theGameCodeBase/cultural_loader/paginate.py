from typing import Callable, Any, Dict, List, Iterator

FetchFn = Callable[[int,int], List[Dict[str, Any]]]

def page_through(
        fetch_fn: FetchFn,
        per_page: int,
        *,
        start_offset: int = 0,
        max_pages: int | None = None
        ) -> Iterator[List[Dict[str, Any]]]:
    """
    Yield pages of items using limit/offset until an incomplete page is returned.

    Args:
        fetch_fn: A function taking (limit, offset) that returns a list of items.
        per_page: Page size (must be >= 1).
        start_offset: Initial offset (default 0).
        max_pages: Optional safety cap on number of pages to emit.

    Yields:
        Lists of items (each list has length per_page, except possibly the last).

    Raises:
        ValueError: if per_page < 1 or start_offset < 0.
    """
    
    if per_page < 1:
        raise ValueError("per_page must be >= 1")
    if start_offset < 0:
        raise ValueError("start_offset must be >=0")

    offset = start_offset
    pages = 0
    while True:
        items = fetch_fn(per_page, offset)
        if not items:
            break
        
        yield items
        pages += 1

        if max_pages is not None and pages >= max_pages:
            break
        if len(items) <  per_page:
            break
        offset += per_page
