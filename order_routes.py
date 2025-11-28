from fastapi import APIRouter

order_router = APIRouter(
    prefix="/order",
)

@order_router.get("/")
async def order():
    return {
        "message": "Welcome to the Order Page",
        }