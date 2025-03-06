from fastapi import APIRouter
from backend.agent.shopping_agent import ShoppingAgent
from backend.models.action_models import ActionConfirmRequest, ActionResult

router = APIRouter()

@router.post("/confirm")
async def confirm_action(request: ActionConfirmRequest) -> ActionResult:
    agent = ShoppingAgent()
    
    if request.action_type == "checkout":
        result = agent.process_checkout(request.session_id)
        
        # Check if there was an error
        if result["status"] == "error":
            return ActionResult(
                status="error",
                message=result["message"],
                data=result.get("data")
            )
        
        # Success case
        return ActionResult(
            status="success",
            message="Checkout initiated successfully. Redirecting to payment page...",
            data=result["data"]
        )
    
    # ... existing code ... 