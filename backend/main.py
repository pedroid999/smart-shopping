"""
Main entry point for the AI Shopping Assistant backend.
Implements a FastAPI application exposing the shopping assistant API.
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Local modules
from app.agent.shopping_agent import ShoppingAgent
from app.models.request_models import ChatRequest, SearchRequest, ProductRequest, CartAction, CheckoutRequest
from app.models.response_models import ChatResponse, SearchResponse, ProductDetails, CartResponse, CheckoutResponse
from app.services.product_service import ProductService
from app.services.cart_service import CartService
from app.services.payment_service import PaymentService

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Shopping Assistant API",
    description="Backend API for the AI-powered e-commerce shopping assistant",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
product_service = ProductService()
cart_service = CartService()
payment_service = PaymentService()

# WebSocket connections store
active_connections: Dict[str, WebSocket] = {}

# Agent instance cache (in a real app, this would use Redis or similar)
agent_instances: Dict[str, ShoppingAgent] = {}

@app.get("/")
async def root():
    """Root endpoint to verify API is working."""
    return {"message": "AI Shopping Assistant API is running"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message from the user."""
    try:
        # Get or create an agent for this session
        if request.session_id not in agent_instances:
            agent_instances[request.session_id] = ShoppingAgent(
                product_service=product_service
            )
        
        agent = agent_instances[request.session_id]
        
        # Process the message with the agent
        response = agent.process_message(request.message, request.session_id)
        
        return ChatResponse(
            session_id=request.session_id,
            response=response,
            requires_action=False  # In MVP, we'll handle actions separately
        )
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search", response_model=SearchResponse)
async def search_products(request: SearchRequest):
    """Search for products based on a query."""
    try:
        products = product_service.search_products(
            query=request.query,
            filters=request.filters,
            page=request.page,
            page_size=request.page_size
        )
        
        return SearchResponse(
            products=products,
            total=len(products),  # In a real app, get actual total
            page=request.page,
            page_size=request.page_size
        )
    except Exception as e:
        logger.error(f"Error searching products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{product_id}", response_model=ProductDetails)
async def get_product(product_id: str):
    """Get detailed information about a product."""
    try:
        product = product_service.get_product_details(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cart/{session_id}", response_model=CartResponse)
async def update_cart(session_id: str, action: CartAction):
    """Update the shopping cart (add, remove, update quantity)."""
    try:
        if action.action_type == "add":
            cart = cart_service.add_to_cart(
                session_id=session_id,
                product_id=action.product_id,
                quantity=action.quantity or 1
            )
        elif action.action_type == "remove":
            cart = cart_service.remove_from_cart(
                session_id=session_id,
                product_id=action.product_id
            )
        elif action.action_type == "update":
            cart = cart_service.update_quantity(
                session_id=session_id,
                product_id=action.product_id,
                quantity=action.quantity or 1
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid action type")
            
        return cart
    except Exception as e:
        logger.error(f"Error updating cart: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cart/{session_id}", response_model=CartResponse)
async def get_cart(session_id: str):
    """Get the current shopping cart contents."""
    try:
        cart = cart_service.get_cart(session_id)
        return cart
    except Exception as e:
        logger.error(f"Error getting cart: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/checkout/{session_id}", response_model=CheckoutResponse)
async def create_checkout(session_id: str, checkout_request: CheckoutRequest):
    """Create a checkout session for payment."""
    try:
        # Get current cart
        cart = cart_service.get_cart(session_id)
        
        # Create payment session with Stripe
        checkout_session = payment_service.create_payment_session(
            cart=cart,
            customer_email=checkout_request.email,
            success_url=checkout_request.success_url,
            cancel_url=checkout_request.cancel_url
        )
        
        return CheckoutResponse(
            session_id=session_id,
            checkout_url=checkout_session.url,
            checkout_id=checkout_session.id
        )
    except Exception as e:
        logger.error(f"Error creating checkout: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()
    active_connections[session_id] = websocket
    
    # Create agent for this session if it doesn't exist
    if session_id not in agent_instances:
        agent_instances[session_id] = ShoppingAgent(
            product_service=product_service
        )
    
    agent = agent_instances[session_id]
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "")
            
            # Process with the agent
            response = agent.process_message(user_message, session_id)
            
            # Send response back to client
            await websocket.send_json({
                "type": "message",
                "content": response,
                "requires_action": False
            })
            
    except WebSocketDisconnect:
        # Clean up on disconnect
        if session_id in active_connections:
            del active_connections[session_id]
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close(code=1011, reason=str(e))

if __name__ == "__main__":
    # Run the FastAPI app with uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    uvicorn.run("main:app", host=host, port=port, reload=debug) 