"""
AI Shopping Agent using LangGraph for conversational e-commerce.
This agent can understand user queries about products, search for them,
and make recommendations based on user preferences.
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum

from openai import OpenAI
from dotenv import load_dotenv
import langgraph.graph as lg
from langgraph.prebuilt import ToolNode
from langgraph.graph import START, END, StateGraph

# Local imports
from app.services.product_service import ProductService

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Define state schema
class AgentState(dict):
    """State maintained throughout the agent's execution."""
    messages: List[Dict[str, str]]
    session_id: str
    context: Dict[str, Any]

# Tool definitions
def search_products(state: AgentState, query: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Search for products based on query and filters.
    
    Args:
        state: Current agent state
        query: Search query
        filters: Optional filters to apply
        
    Returns:
        Search results
    """
    product_service = state.get("context", {}).get("product_service")
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

def get_product_details(state: AgentState, product_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific product.
    
    Args:
        state: Current agent state
        product_id: Product identifier
        
    Returns:
        Product details
    """
    product_service = state.get("context", {}).get("product_service")
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

def get_related_products(state: AgentState, product_id: str, limit: int = 3) -> Dict[str, Any]:
    """
    Get products related to a specific product.
    
    Args:
        state: Current agent state
        product_id: Product identifier
        limit: Maximum number of related products to return
        
    Returns:
        Related products
    """
    product_service = state.get("context", {}).get("product_service")
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

class ShoppingAgent:
    """
    AI-powered shopping assistant using LangGraph.
    This agent can understand natural language queries about products,
    search for matching items, and make recommendations.
    """
    
    def __init__(self, product_service: ProductService):
        """
        Initialize the shopping agent.
        
        Args:
            product_service: Service for retrieving product data
        """
        self.product_service = product_service
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
            }
        ]
        
        # Build the agent graph
        self._build_graph()
        
        logger.info("Initialized ShoppingAgent")
    
    def _build_graph(self):
        """Build the LangGraph for the shopping agent."""
        # Define the nodes in the graph
        
        # This node processes user input and determines next actions
        def llm_node(state: AgentState) -> Dict[str, Any]:
            """Process user input and determine next actions."""
            messages = state["messages"]
            
            # Call the LLM
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use 3.5 for MVP; can upgrade to GPT-4 later
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )
            
            assistant_message = response.choices[0].message
            
            # Add the assistant's message to the state
            state["messages"].append(assistant_message.model_dump())
            
            # Check if the model wants to use a tool
            if assistant_message.tool_calls:
                return {"next": "tool_executor"}
            else:
                # No tool calls, just return the response
                return {"next": "end"}
        
        # This node executes tools requested by the LLM
        def tool_executor(state: AgentState) -> Dict[str, Any]:
            """Execute tools requested by the LLM."""
            # Get the last assistant message with tool calls
            last_message = state["messages"][-1]
            tool_calls = last_message.get("tool_calls", [])
            
            if not tool_calls:
                return {"next": "end"}
            
            # Execute each tool call
            for tool_call in tool_calls:
                function_name = tool_call["function"]["name"]
                arguments = json.loads(tool_call["function"]["arguments"])
                
                # Dispatch to the right tool
                if function_name == "search_products":
                    result = search_products(state, **arguments)
                elif function_name == "get_product_details":
                    result = get_product_details(state, **arguments)
                elif function_name == "get_related_products":
                    result = get_related_products(state, **arguments)
                else:
                    result = {"error": f"Unknown tool: {function_name}"}
                
                # Add the tool result to the state
                state["messages"].append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": function_name,
                    "content": json.dumps(result)
                })
            
            # Continue the conversation with the LLM
            return {"next": "llm"}
        
        # Create the graph
        builder = StateGraph(AgentState)
        
        # Add nodes
        builder.add_node("llm", llm_node)
        builder.add_node("tool_executor", tool_executor)
        
        # Define the edges
        builder.add_edge(START, "llm")
        builder.add_conditional_edges(
            "llm",
            lambda state: state.get("next", "end"),
            {
                "tool_executor": "tool_executor",
                "end": END
            }
        )
        builder.add_conditional_edges(
            "tool_executor",
            lambda state: state.get("next", "end"),
            {
                "llm": "llm",
                "end": END
            }
        )
        
        # Compile the graph
        self.graph = builder.compile()
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the shopping assistant."""
        return """You are an AI shopping assistant that helps users find products they're looking for.
Your goal is to understand what the user wants and provide helpful recommendations.

Follow these guidelines:
1. Be conversational and friendly, but efficient and helpful.
2. Ask clarifying questions if the user's request is vague or missing important details.
3. When suggesting products, provide key information like price, features, and why it matches their needs.
4. If you can't find exactly what they're looking for, suggest alternatives.
5. Never make up products or details - only use information from the search results.
6. Use the search_products tool to find products based on user queries.
7. Use the get_product_details tool to get detailed information about a specific product.
8. Use the get_related_products tool to find similar products.

Remember to be helpful and provide value to the user's shopping experience."""
    
    def process_message(self, message: str, session_id: str) -> str:
        """
        Process a user message and generate a response.
        
        Args:
            message: User's message text
            session_id: Unique session identifier
            
        Returns:
            Assistant's response
        """
        # Initialize conversation if this is the first message
        if not hasattr(self, f"conversation_{session_id}"):
            # Create a new conversation state
            setattr(self, f"conversation_{session_id}", {
                "messages": [
                    {"role": "system", "content": self._create_system_prompt()},
                ],
                "session_id": session_id,
                "context": {"product_service": self.product_service}
            })
        
        # Get the conversation state
        conversation = getattr(self, f"conversation_{session_id}")
        
        # Add the user message
        conversation["messages"].append({"role": "user", "content": message})
        
        # Run the agent
        result = self.graph.invoke(conversation)
        
        # Update the conversation state
        setattr(self, f"conversation_{session_id}", result)
        
        # Find the last assistant message
        for msg in reversed(result["messages"]):
            if msg["role"] == "assistant":
                # Return just the content (not tool calls)
                return msg["content"] or "I'll help you find what you're looking for."
        
        # Fallback response if no assistant message found
        return "I'll help you find what you're looking for." 