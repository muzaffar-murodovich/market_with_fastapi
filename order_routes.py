from fastapi_jwt_auth import AuthJWT
from models import User, Product, Order
from schemas import OrderModel
from database import session, engine
from fastapi import APIRouter, Depends, status
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

order_router = APIRouter(
    prefix="/order",
)

session = session(bind=engine)

@order_router.get("/")
async def welcome_page(Authorize: AuthJWT = Depends()):

    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=401, detail="No valid access token provided")

    return {
        "message": "Welcome to the Order Page",
        }

@order_router.post("/make", status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderModel, Authorize: AuthJWT=Depends()):

    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=401, detail="No valid access token provided")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    # Check if product exists
    product = session.query(Product).filter(Product.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")


    new_order = Order(
        quantity=order.quantity,
        product_id = order.product_id
    )
    new_order.user = user
    session.add(new_order)
    session.commit()
    data = {
        "success": True,
        "code": 201,
        "message": "Order Created",
        "data": {
            "id": new_order.id,
            "quantity": new_order.quantity,
            "order_statuses": new_order.order_statuses,

        }
    }

    response = data
    return response

@order_router.get("/list")
async def get_orders(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=401, detail="No valid access token provided")
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if user.is_staff:
        orders = session.query(Order).all()
        return orders
    else:
        raise HTTPException(status_code=403, detail="You are not authorized to view this page")

