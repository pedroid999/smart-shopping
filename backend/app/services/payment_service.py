"""
Payment service for handling payment processing with Stripe.
"""
import os
import logging
from typing import Dict, Any, Optional, List

import stripe
from dotenv import load_dotenv

# Local imports
from app.models.response_models import CartResponse

# Load environment variables for Stripe keys
load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

logger = logging.getLogger(__name__)

class PaymentService:
    """Service for handling payment processing with Stripe."""
    
    def __init__(self):
        """Initialize the payment service."""
        # Verify Stripe keys are available
        if not stripe.api_key:
            logger.warning("Stripe API key not set. Payment processing will not work.")
        logger.info("Initialized PaymentService")
    
    def create_payment_session(
        self,
        cart: CartResponse,
        customer_email: str,
        success_url: str,
        cancel_url: str
    ) -> Any:
        """
        Create a Stripe checkout session for payment.
        
        Args:
            cart: Cart containing items to purchase
            customer_email: Customer's email address
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if payment is cancelled
            
        Returns:
            Stripe checkout session object
        """
        try:
            # Convert cart items to Stripe line items
            line_items = []
            
            for item in cart.items:
                line_items.append({
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": item.product.name,
                            "description": item.product.description,
                            "images": [item.product.image_url] if item.product.image_url else [],
                            "metadata": {
                                "product_id": item.product.id
                            }
                        },
                        "unit_amount": int(item.product.price * 100),  # Convert to cents
                    },
                    "quantity": item.quantity,
                })
            
            # Add tax and shipping if applicable
            if cart.tax and cart.tax > 0:
                line_items.append({
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Tax",
                            "description": "Sales tax"
                        },
                        "unit_amount": int(cart.tax * 100),  # Convert to cents
                    },
                    "quantity": 1,
                })
                
            if cart.shipping and cart.shipping > 0:
                line_items.append({
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Shipping",
                            "description": "Shipping fee"
                        },
                        "unit_amount": int(cart.shipping * 100),  # Convert to cents
                    },
                    "quantity": 1,
                })
            
            # Create Stripe session
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                customer_email=customer_email,
                line_items=line_items,
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "session_id": cart.session_id
                }
            )
            
            logger.info(f"Created Stripe checkout session: {session.id}")
            return session
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            raise ValueError(f"Payment processing error: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating payment session: {str(e)}")
            raise
    
    def verify_payment(self, checkout_session_id: str) -> bool:
        """
        Verify that a payment was successful.
        
        Args:
            checkout_session_id: Stripe checkout session ID
            
        Returns:
            True if payment was successful, False otherwise
        """
        try:
            session = stripe.checkout.Session.retrieve(checkout_session_id)
            return session.payment_status == "paid"
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error verifying payment: {str(e)}")
            return False 