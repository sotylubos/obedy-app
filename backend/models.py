from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MenuItem:
    name: str
    price: Optional[str] = None


@dataclass
class RestaurantMenu:
    id: str
    name: str
    url: Optional[str]
    address: Optional[str]
    items: List[MenuItem] = field(default_factory=list)
    error: Optional[str] = None  # vyplní se, pokud se menu nepodařilo stáhnout/rozpoznat
