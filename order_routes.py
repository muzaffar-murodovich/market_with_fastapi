from fastapi_jwt_auth import AuthJWT
from models import User, Product, Order
from schemas import OrderModel
from database import session, engine
from fastapi import APIRouter, Depends, status
from fastapi import HTTPException

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
        custom_data = [
            {
                "id": user.id,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
                "quantity": order.quantity,
                "order_statuses": order.order_statuses.value,
            }
            for order in orders
        ]
        return custom_data
    else:
        raise HTTPException(status_code=403, detail="You are not authorized to view this page")

@order_router.get('/{id}', status_code=status.HTTP_200_OK)
async def get_order_by_id(id: int, Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=401, detail="No valid access token provided")
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user).first()

    if current_user.is_staff:
        order = session.query(Order).filter(Order.id == id).first()
        if order:
            custom_order = {
                "id": order.id,
                "user": {
                    "id": order.user.id,
                    "username": order.user.username,
                    "email": order.user.email
                },
                    "product": {
                    "id": order.product.id,
                    "name": order.product.name,
                    "price": order.product.price
                },
                "quantity": order.quantity,
                "order_statuses": order.order_statuses.value,
                "total_price": order.quantity * order.product.price

            }
            return custom_order
        else:
            raise HTTPException(status_code=404,
                                detail=f"Order with {id} ID not found")
    else:
        raise HTTPException(status_code=403,
                            detail="Only superadmin is allowed to this request")