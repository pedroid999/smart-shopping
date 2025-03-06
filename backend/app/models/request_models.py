"""
Pydantic models for API requests.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, EmailStr

class ChatRequest(BaseModel):
    """Chat message request from a user."""
    session_id: str = Field(..., description="Unique session identifier")
    message: str = Field(..., description="User's message text")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context for the agent")
    image_data: Optional[str] = Field(default=None, description="Base64-encoded image data")

class SearchRequest(BaseModel):
    """Product search request."""
    query: str = Field(..., description="Search query text")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Filter parameters (price range, category, etc.)")
    page: int = Field(default=1, description="Page number for pagination")
    page_size: int = Field(default=10, description="Number of results per page")

class ProductRequest(BaseModel):
    """Request for product details."""
    product_id: str = Field(..., description="Unique product identifier")

class CartAction(BaseModel):
    """Action to perform on a shopping cart."""
    action_type: str = Field(..., description="Action type: add, remove, update")
    product_id: str = Field(..., description="Product identifier")
    quantity: Optional[int] = Field(default=None, description="Quantity for add/update actions")

class CheckoutRequest(BaseModel):
    """Request to create a checkout session."""
    email: str = Field(..., description="Customer email")
    success_url: str = Field(..., description="URL to redirect after successful payment")
    cancel_url: str = Field(..., description="URL to redirect if payment is cancelled")
    shipping_address: Optional[Dict[str, str]] = Field(default=None, description="Shipping address information")
    billing_address: Optional[Dict[str, str]] = Field(default=None, description="Billing address information")

class ActionConfirmation(BaseModel):
    """Confirmation for an action that requires user approval."""
    session_id: str = Field(..., description="Unique session identifier")
    action_type: str = Field(..., description="Type of action to confirm (add_to_cart, checkout)")
    action_data: Dict[str, Any] = Field(..., description="Data needed for the action")
    confirmed: bool = Field(..., description="Whether the user confirmed the action") 