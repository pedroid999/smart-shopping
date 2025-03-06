"""
Pydantic models for API responses.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Product(BaseModel):
    """Basic product information."""
    id: str = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Product name")
    description: str = Field(..., description="Short product description")
    price: float = Field(..., description="Product price")
    image_url: Optional[str] = Field(default=None, description="URL to product image")
    category: str = Field(..., description="Product category")
    brand: Optional[str] = Field(default=None, description="Product brand")
    rating: Optional[float] = Field(default=None, description="Average product rating")
    in_stock: bool = Field(default=True, description="Whether the product is in stock")
    
class ProductDetails(Product):
    """Detailed product information."""
    long_description: Optional[str] = Field(default=None, description="Detailed product description")
    specifications: Optional[Dict[str, Any]] = Field(default=None, description="Product specifications")
    reviews: Optional[List[Dict[str, Any]]] = Field(default=None, description="Product reviews")
    related_products: Optional[List[str]] = Field(default=None, description="Related product IDs")
    tags: Optional[List[str]] = Field(default=None, description="Product tags")

class SearchResponse(BaseModel):
    """Response for product search."""
    products: List[Product] = Field(..., description="List of matching products")
    total: int = Field(..., description="Total number of matching products")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of results per page")

class CartItem(BaseModel):
    """Item in a shopping cart."""
    product: Product = Field(..., description="Product information")
    quantity: int = Field(..., description="Quantity in cart")
    item_total: float = Field(..., description="Total price for this item")

class CartResponse(BaseModel):
    """Shopping cart contents."""
    session_id: str = Field(..., description="Unique session identifier")
    items: List[CartItem] = Field(default_factory=list, description="Items in the cart")
    subtotal: float = Field(..., description="Subtotal of all items")
    tax: Optional[float] = Field(default=None, description="Tax amount")
    shipping: Optional[float] = Field(default=None, description="Shipping cost")
    total: float = Field(..., description="Total cost including tax and shipping")
    created_at: datetime = Field(default_factory=datetime.now, description="Cart creation time")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update time")

class ChatResponse(BaseModel):
    """Response to a chat message."""
    session_id: str = Field(..., description="Unique session identifier")
    response: str = Field(..., description="AI assistant's response")
    requires_action: bool = Field(default=False, description="Whether the response requires user action")
    action_data: Optional[Dict[str, Any]] = Field(default=None, description="Data for required action")
    suggested_products: Optional[List[Product]] = Field(default=None, description="Suggested products")
    
class CheckoutResponse(BaseModel):
    """Response for checkout creation."""
    session_id: str = Field(..., description="Unique session identifier")
    checkout_url: str = Field(..., description="URL to complete checkout")
    checkout_id: str = Field(..., description="Unique checkout identifier") 