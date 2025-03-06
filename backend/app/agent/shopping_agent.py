"""
AI Shopping Agent using OpenAI for conversational e-commerce.
This agent can understand user queries about products, search for them,
and make recommendations based on user preferences.
It also supports adding products to cart and checkout with minimal user interaction.
"""
import os
import json
import logging
import base64
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum

from openai import OpenAI
from dotenv import load_dotenv

# Local imports
from app.services.product_service import ProductService
from app.services.cart_service import CartService
from app.services.payment_service import PaymentService

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Tool definitions
def search_products(product_service, query: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Search for products based on query and filters.
    
    Args:
        product_service: Service for retrieving product data
        query: Search query
        filters: Optional filters to apply
        
    Returns:
        Search results
    """
    if not product_service:
        return {"error": "Product service not available", "products": []}
    
    try:
        products = product_service.search_products(query=query, filters=filters)
        return {
            "count": len(products),
            "products": [product.dict() for product in products]
        }
    except Exception as e:
        logger.error(f"Error searching products: {str(e)}")
        return {"error": str(e), "products": []}

def get_product_details(product_service, product_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific product.
    
    Args:
        product_service: Service for retrieving product data
        product_id: Product identifier
        
    Returns:
        Product details
    """
    if not product_service:
        return {"error": "Product service not available"}
    
    try:
        product = product_service.get_product_details(product_id)
        if product:
            return product.dict()
        return {"error": "Product not found"}
    except Exception as e:
        logger.error(f"Error getting product details: {str(e)}")
        return {"error": str(e)}

def get_related_products(product_service, product_id: str, limit: int = 3) -> Dict[str, Any]:
    """
    Get products related to a specific product.
    
    Args:
        product_service: Service for retrieving product data
        product_id: Product identifier
        limit: Maximum number of related products to return
        
    Returns:
        Related products
    """
    if not product_service:
        return {"error": "Product service not available", "products": []}
    
    try:
        products = product_service.get_related_products(product_id, limit)
        return {
            "count": len(products),
            "products": [product.dict() for product in products]
        }
    except Exception as e:
        logger.error(f"Error getting related products: {str(e)}")
        return {"error": str(e), "products": []}

def add_to_cart(cart_service, session_id: str, product_id: str, quantity: int = 1) -> Dict[str, Any]:
    """
    Add a product to the user's cart.
    
    Args:
        cart_service: Service for managing shopping carts
        session_id: Unique session identifier
        product_id: Product to add
        quantity: Quantity to add
        
    Returns:
        Updated cart information
    """
    if not cart_service:
        return {"error": "Cart service not available"}
    
    try:
        cart = cart_service.add_to_cart(
            session_id=session_id,
            product_id=product_id,
            quantity=quantity
        )
        return cart.dict()
    except Exception as e:
        logger.error(f"Error adding to cart: {str(e)}")
        return {"error": str(e)}

def get_cart(cart_service, session_id: str) -> Dict[str, Any]:
    """
    Get the current cart contents.
    
    Args:
        cart_service: Service for managing shopping carts
        session_id: Unique session identifier
        
    Returns:
        Cart information
    """
    if not cart_service:
        return {"error": "Cart service not available"}
    
    try:
        cart = cart_service.get_cart(session_id)
        return cart.dict()
    except Exception as e:
        logger.error(f"Error getting cart: {str(e)}")
        return {"error": str(e)}

def create_checkout(payment_service, cart_service, session_id: str, email: str, 
                   success_url: str, cancel_url: str) -> Dict[str, Any]:
    """
    Create a checkout session for payment.
    
    Args:
        payment_service: Service for payment processing
        cart_service: Service for managing shopping carts
        session_id: Unique session identifier
        email: Customer email
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect if payment is cancelled
        
    Returns:
        Checkout information
    """
    if not payment_service or not cart_service:
        return {"error": "Payment or cart service not available"}
    
    try:
        # Get current cart
        cart = cart_service.get_cart(session_id)
        
        # Create payment session
        checkout_session = payment_service.create_payment_session(
            cart=cart,
            customer_email=email,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        return {
            "checkout_url": checkout_session.url,
            "checkout_id": checkout_session.id,
            "session_id": session_id
        }
    except Exception as e:
        logger.error(f"Error creating checkout: {str(e)}")
        return {"error": str(e)}

class ShoppingAgent:
    """
    AI-powered shopping assistant using OpenAI.
    This agent can understand natural language queries about products,
    search for matching items, and make recommendations.
    It also supports adding products to cart and checkout with minimal user interaction.
    """
    
    def __init__(self, product_service: ProductService, cart_service: CartService, payment_service: PaymentService):
        """
        Initialize the shopping agent.
        
        Args:
            product_service: Service for retrieving product data
            cart_service: Service for managing shopping carts
            payment_service: Service for payment processing
        """
        self.product_service = product_service
        self.cart_service = cart_service
        self.payment_service = payment_service
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Define the tools available to the agent
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_products",
                    "description": "Search for products based on query and filters",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query text"
                            },
                            "filters": {
                                "type": "object",
                                "description": "Optional filters (price range, category, etc.)",
                                "properties": {
                                    "min_price": {"type": "number"},
                                    "max_price": {"type": "number"},
                                    "category": {"type": "string"},
                                    "brand": {"type": "string"}
                                }
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_product_details",
                    "description": "Get detailed information about a specific product",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_id": {
                                "type": "string",
                                "description": "Unique product identifier"
                            }
                        },
                        "required": ["product_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_related_products",
                    "description": "Get products related to a specific product",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_id": {
                                "type": "string",
                                "description": "Product identifier"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of related products to return"
                            }
                        },
                        "required": ["product_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_to_cart",
                    "description": "Add a product to the user's cart",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_id": {
                                "type": "string",
                                "description": "Product identifier"
                            },
                            "quantity": {
                                "type": "integer",
                                "description": "Quantity to add"
                            }
                        },
                        "required": ["product_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_cart",
                    "description": "Get the current cart contents",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_checkout",
                    "description": "Create a checkout session for payment",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "email": {
                                "type": "string",
                                "description": "Customer email"
                            },
                            "success_url": {
                                "type": "string",
                                "description": "URL to redirect after successful payment"
                            },
                            "cancel_url": {
                                "type": "string",
                                "description": "URL to redirect if payment is cancelled"
                            }
                        },
                        "required": ["email", "success_url", "cancel_url"]
                    }
                }
            }
        ]
        
        logger.info("Initialized ShoppingAgent")
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the shopping assistant."""
        return """You are an AI shopping assistant that helps users find products they're looking for.
Your goal is to understand what the user wants and provide helpful recommendations.

Follow these guidelines:
1. Be conversational and friendly, but efficient and helpful.
2. Ask clarifying questions if the user's request is vague or missing important details, EXCEPT for image uploads.
3. When suggesting products, provide key information like price, features, and why it matches their needs.
4. If you can't find exactly what they're looking for, suggest alternatives.
5. Never make up products or details - only use information from the search results.
6. Use the search_products tool to find products based on user queries.
7. Use the get_product_details tool to get detailed information about a specific product.
8. Use the get_related_products tool to find similar products.
9. When a user expresses interest in a product, suggest adding it to their cart using the add_to_cart tool.
10. Use the get_cart tool to check what's in the user's cart.
11. When the user is ready to checkout, use the create_checkout tool to create a payment session.
12. Always wait for user confirmation before adding items to cart or proceeding to checkout.
13. When a user uploads an image, IMMEDIATELY analyze it and search for similar products without asking additional questions. Use the search_products tool with keywords from the image analysis to find matching products. List at least 3-5 products that match what's in the image.
14. For image uploads, focus on identifying the object, its category, color, style, and other visible attributes, then directly search for similar items in our catalog.
15. After listing products from an image search, ask if the user would like to see more options or details about any specific product."""
    
    def process_message(self, message: str, session_id: str, image_data: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user message and generate a response.
        
        Args:
            message: User's message text
            session_id: Unique session identifier
            image_data: Optional base64-encoded image data
            
        Returns:
            Dictionary containing the assistant's response and any suggested products
        """
        # Initialize conversation if this is the first message
        if not hasattr(self, f"conversation_{session_id}"):
            # Create a new conversation state
            setattr(self, f"conversation_{session_id}", {
                "messages": [
                    {"role": "system", "content": self._create_system_prompt()},
                ],
                "session_id": session_id,
                "has_image": False  # Track if the conversation has image data
            })
        
        # Get the conversation state
        conversation = getattr(self, f"conversation_{session_id}")
        
        # Add the user message
        user_message = {"role": "user", "content": message}
        
        # If image is provided, add it to the message
        model = "gpt-4o"  # Always use gpt-4o
        is_image_upload = False
        
        if image_data:
            is_image_upload = True
            try:
                # Validate the image data
                if not isinstance(image_data, str) or not image_data:
                    raise ValueError("Invalid image data format")
                
                # For the first message with an image, use the image_url format
                if not conversation.get("has_image", False):
                    # Add special instruction for image processing
                    if not message or message.strip() == "":
                        message = "Analyze this image and find similar products in the catalog."
                    
                    user_message["content"] = [
                        {"type": "text", "text": message},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                    # Mark that this conversation has image data
                    conversation["has_image"] = True
                else:
                    # For subsequent messages, just use the text
                    user_message["content"] = message
                
                # Log successful image processing
                logger.info(f"Processing image for session {session_id}")
            except Exception as e:
                # Log the error and continue without the image
                logger.error(f"Error processing image data: {str(e)}")
        
        # Add the message to the conversation
        conversation["messages"].append(user_message)
        
        try:
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=model,
                messages=conversation["messages"],
                tools=self.tools,
                tool_choice="auto"
            )
            
            assistant_message = response.choices[0].message
            
            # Add the assistant's message to the conversation
            conversation["messages"].append(assistant_message.model_dump())
            
            # Initialize suggested products list
            suggested_products = []
            requires_action = False
            action_data = None
            
            # For image uploads, ensure we search for products if the model didn't do it
            if is_image_upload and not assistant_message.tool_calls:
                # Add a system message to force product search
                conversation["messages"].append({
                    "role": "system",
                    "content": "The user has uploaded an image. Please use the search_products tool to find similar products based on what you see in the image."
                })
                
                # Call the API again to get product recommendations
                second_response = self.client.chat.completions.create(
                    model=model,
                    messages=conversation["messages"],
                    tools=self.tools,
                    tool_choice={"type": "function", "function": {"name": "search_products"}}
                )
                
                # Replace the assistant message with the new one
                assistant_message = second_response.choices[0].message
                conversation["messages"][-1] = assistant_message.model_dump()
            
            # Check if the model wants to use a tool
            if assistant_message.tool_calls:
                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    # Dispatch to the right tool
                    if function_name == "search_products":
                        result = search_products(self.product_service, **arguments)
                        # Extract products for the carousel
                        if "products" in result and result["products"]:
                            suggested_products = result["products"]
                    elif function_name == "get_product_details":
                        result = get_product_details(self.product_service, **arguments)
                        # Add single product to suggested products
                        if "id" in result:
                            suggested_products = [result]
                    elif function_name == "get_related_products":
                        result = get_related_products(self.product_service, **arguments)
                        # Extract related products for the carousel
                        if "products" in result and result["products"]:
                            suggested_products = result["products"]
                    elif function_name == "add_to_cart":
                        # For add_to_cart, we need user confirmation (man-in-the-loop)
                        product_id = arguments.get("product_id")
                        quantity = arguments.get("quantity", 1)
                        
                        # Get product details for confirmation
                        product = get_product_details(self.product_service, product_id)
                        
                        # Set up the action that requires user confirmation
                        requires_action = True
                        action_data = {
                            "type": "add_to_cart",
                            "product": product,
                            "quantity": quantity,
                            "session_id": session_id
                        }
                        
                        # Don't execute the action yet, wait for user confirmation
                        result = {"status": "waiting_for_confirmation", "product": product}
                    elif function_name == "get_cart":
                        result = get_cart(self.cart_service, session_id)
                    elif function_name == "create_checkout":
                        # For checkout, we need user confirmation (man-in-the-loop)
                        email = arguments.get("email")
                        success_url = arguments.get("success_url")
                        cancel_url = arguments.get("cancel_url")
                        
                        # Get cart for confirmation
                        cart = get_cart(self.cart_service, session_id)
                        
                        # Set up the action that requires user confirmation
                        requires_action = True
                        action_data = {
                            "type": "checkout",
                            "cart": cart,
                            "email": email,
                            "success_url": success_url,
                            "cancel_url": cancel_url,
                            "session_id": session_id
                        }
                        
                        # Don't execute the action yet, wait for user confirmation
                        result = {"status": "waiting_for_confirmation", "cart": cart}
                    else:
                        result = {"error": f"Unknown tool: {function_name}"}
                    
                    # Add the tool result to the conversation
                    conversation["messages"].append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": json.dumps(result)
                    })
                
                # Call the API again to get the final response
                second_response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=conversation["messages"]
                )
                
                final_message = second_response.choices[0].message
                conversation["messages"].append(final_message.model_dump())
                
                response_text = final_message.content
            else:
                # If no tool calls, just return the assistant's response
                response_text = assistant_message.content or "I'll help you find what you're looking for."
            
            # Return the response along with any suggested products and action data
            return {
                "response": response_text,
                "suggested_products": suggested_products,
                "requires_action": requires_action,
                "action_data": action_data
            }
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "response": f"I'm sorry, I encountered an error processing your request. {str(e)}",
                "suggested_products": [],
                "requires_action": False,
                "action_data": None
            }
    
    def execute_action(self, action_type: str, action_data: Dict[str, Any], confirmed: bool) -> Dict[str, Any]:
        """
        Execute an action after user confirmation.
        
        Args:
            action_type: Type of action to execute
            action_data: Data needed for the action
            confirmed: Whether the user confirmed the action
            
        Returns:
            Result of the action
        """
        if not confirmed:
            return {"status": "cancelled", "message": "Action cancelled by user"}
        
        try:
            if action_type == "add_to_cart":
                session_id = action_data.get("session_id")
                product_id = action_data.get("product", {}).get("id")
                quantity = action_data.get("quantity", 1)
                
                if not session_id or not product_id:
                    return {"status": "error", "message": "Missing required data for add_to_cart"}
                
                result = add_to_cart(self.cart_service, session_id, product_id, quantity)
                return {
                    "status": "success",
                    "message": f"Added {quantity} item(s) to cart",
                    "cart": result
                }
            
            elif action_type == "checkout":
                session_id = action_data.get("session_id")
                email = action_data.get("email")
                success_url = action_data.get("success_url")
                cancel_url = action_data.get("cancel_url")
                
                if not session_id or not email or not success_url or not cancel_url:
                    return {"status": "error", "message": "Missing required data for checkout"}
                
                result = create_checkout(
                    self.payment_service,
                    self.cart_service,
                    session_id,
                    email,
                    success_url,
                    cancel_url
                )
                
                return {
                    "status": "success",
                    "message": "Checkout created successfully",
                    "checkout": result
                }
            
            else:
                return {"status": "error", "message": f"Unknown action type: {action_type}"}
        
        except Exception as e:
            logger.error(f"Error executing action: {str(e)}")
            return {"status": "error", "message": str(e)} 