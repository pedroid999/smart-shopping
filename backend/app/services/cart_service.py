"""
Shopping cart service for managing cart operations.
In the MVP, this uses in-memory storage.
In a production environment, this would use Redis or a database.
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Local imports
from app.models.response_models import CartResponse, CartItem, Product
from app.services.product_service import ProductService

logger = logging.getLogger(__name__)

class CartService:
    """Service for managing shopping carts."""
    
    def __init__(self):
        """Initialize the cart service with in-memory storage for MVP."""
        self.carts: Dict[str, CartResponse] = {}
        self.product_service = ProductService()
        logger.info("Initialized CartService")
        
    def get_cart(self, session_id: str) -> CartResponse:
        """
        Get the current cart for a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            CartResponse object (empty cart if none exists)
        """
        if session_id not in self.carts:
            # Create a new empty cart for this session
            self.carts[session_id] = CartResponse(
                session_id=session_id,
                items=[],
                subtotal=0.0,
                total=0.0,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        
        return self.carts[session_id]
    
    def add_to_cart(self, session_id: str, product_id: str, quantity: int = 1) -> CartResponse:
        """
        Add a product to the cart.
        
        Args:
            session_id: Unique session identifier
            product_id: Product to add
            quantity: Quantity to add
            
        Returns:
            Updated CartResponse
        """
        # Get the current cart
        cart = self.get_cart(session_id)
        
        # Check if the product exists
        product_details = self.product_service.get_product_details(product_id)
        if not product_details:
            raise ValueError(f"Product with ID {product_id} not found")
        
        # Check if already in cart
        for item in cart.items:
            if item.product.id == product_id:
                # Update quantity if already in cart
                item.quantity += quantity
                item.item_total = item.quantity * item.product.price
                cart.updated_at = datetime.now()
                break
        else:
            # Add new item to cart
            cart.items.append(CartItem(
                product=product_details,
                quantity=quantity,
                item_total=product_details.price * quantity
            ))
            cart.updated_at = datetime.now()
        
        # Recalculate totals
        self._update_cart_totals(cart)
        
        return cart
    
    def remove_from_cart(self, session_id: str, product_id: str) -> CartResponse:
        """
        Remove a product from the cart.
        
        Args:
            session_id: Unique session identifier
            product_id: Product to remove
            
        Returns:
            Updated CartResponse
        """
        # Get the current cart
        cart = self.get_cart(session_id)
        
        # Remove the item if it exists
        cart.items = [item for item in cart.items if item.product.id != product_id]
        cart.updated_at = datetime.now()
        
        # Recalculate totals
        self._update_cart_totals(cart)
        
        return cart
    
    def update_quantity(self, session_id: str, product_id: str, quantity: int) -> CartResponse:
        """
        Update the quantity of a product in the cart.
        
        Args:
            session_id: Unique session identifier
            product_id: Product to update
            quantity: New quantity
            
        Returns:
            Updated CartResponse
        """
        # Get the current cart
        cart = self.get_cart(session_id)
        
        # Find the item and update quantity
        item_found = False
        for item in cart.items:
            if item.product.id == product_id:
                if quantity <= 0:
                    # Remove if quantity is zero or negative
                    return self.remove_from_cart(session_id, product_id)
                
                item.quantity = quantity
                item.item_total = item.quantity * item.product.price
                item_found = True
                break
        
        if not item_found:
            # If item not in cart and trying to add
            if quantity > 0:
                return self.add_to_cart(session_id, product_id, quantity)
            # If item not in cart and trying to remove, just return current cart
        
        cart.updated_at = datetime.now()
        
        # Recalculate totals
        self._update_cart_totals(cart)
        
        return cart
    
    def clear_cart(self, session_id: str) -> CartResponse:
        """
        Clear all items from the cart.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Empty CartResponse
        """
        # Create a new empty cart
        self.carts[session_id] = CartResponse(
            session_id=session_id,
            items=[],
            subtotal=0.0,
            total=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return self.carts[session_id]
    
    def _update_cart_totals(self, cart: CartResponse) -> None:
        """
        Recalculate subtotal and total for a cart.
        
        Args:
            cart: CartResponse to update
        """
        subtotal = sum(item.item_total for item in cart.items)
        
        # In MVP, we'll keep tax and shipping simple
        # In a real app, these would be calculated based on location, etc.
        tax = subtotal * 0.1 if subtotal > 0 else 0.0  # 10% tax
        shipping = 5.99 if subtotal > 0 else 0.0  # Flat shipping fee
        
        cart.subtotal = subtotal
        cart.tax = tax
        cart.shipping = shipping
        cart.total = subtotal + tax + shipping 