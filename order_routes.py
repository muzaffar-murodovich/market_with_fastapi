from itertools import product

from fastapi_jwt_auth import AuthJWT
from models import User, Product, Order
from schemas import OrderModel, OrderStatusModel
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

@order_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderModel, Authorize: AuthJWT=Depends()):

    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=401, detail="No valid access token provided")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

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
            "product": {
                            "id": product.id,
                            "name": product.name,
                            "price": product.price,
                        },
            "quantity": new_order.quantity,
            "order_status": new_order.order_status,
            "total_price": new_order.quantity * new_order.product.price,
        }
    }

    response = data
    return response

@order_router.get("/list", status_code=status.HTTP_200_OK)
async def get_all_orders(Authorize: AuthJWT = Depends()):
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
                "product": {
                    "id": order.product.id,
                    "name": order.product.name,
                    "price": order.product.price,
                },
                "quantity": order.quantity,
                "order_status": order.order_status.value,
                "total_price": order.quantity * order.product.price,
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
                "order_status": order.order_status.value,
                "total_price": order.quantity * order.product.price
            }
            return custom_order
        else:
            raise HTTPException(status_code=404,
                                detail=f"Order with {id} ID not found")
    else:
        raise HTTPException(status_code=403,
                            detail="Only superadmin is allowed to this request")

@order_router.get('/user/orders', status_code=status.HTTP_200_OK)
async def get_user_orders(Authorize: AuthJWT=Depends()):

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No valid access token provided")

    username = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == username).first()

    custom_data = [
        {
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
            "order_status": order.order_status.value,
            "total_price": order.quantity * order.product.price
        }
        for order in user.orders
    ]
    return custom_data

@order_router.get('/user/order/{id}', status_code=status.HTTP_200_OK)
async def get_user_order_by_id(id: int, Authorize: AuthJWT=Depends()):

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No valid access token provided")

    username = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == username).first()
    order = session.query(Order).filter(Order.id == id, Order.user == current_user).first()

    if order:
        order_data = {
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
            "order_status": order.order_status.value,
            "total_price": order.quantity * order.product.price
        }
        return order_data
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Order {id} not found")


@order_router.put('/{id}/update', status_code=status.HTTP_200_OK)
async def update_order(id: int, order: OrderModel, Authorize: AuthJWT=Depends()):

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="No valid access token provided")
    username = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == username).first()

    order_to_update = session.query(Order).filter(Order.id == id).first()
    if order_to_update.user != user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You cannot update this order")

    order_to_update.quantity = order.quantity
    order_to_update.product_id = order.product_id
    session.commit()

    custom_response = {
        "success": True,
        "code": 200,
        "message": "Your order has been updated!",
        "data": {
            "id": order.id,
            "quantity": order.quantity,
            "product": order.product_id,
            "order_status": order.order_status
        }
    }
    return custom_response


@order_router.patch('/{id}/update-status', status_code=status.HTTP_200_OK)
async def update_order_status(id: int, order: OrderStatusModel, Authorize: AuthJWT=Depends()):

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="No valid access token provided")
    username = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == username).first()
    if user.is_staff:
        order_to_update = session.query(Order).filter(Order.id == id).first()
        order_to_update.order_status = order.order_status
        session.commit()

        custom_response = {
            "success": True,
            "code": 200,
            "message": "User order updated successfully",
            "data": {
                "id": order_to_update.id,
                "order_status": order_to_update.order_status
            }
        }
        return custom_response

@order_router.delete('/{id}/delete', status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(id: int, Authorize: AuthJWT=Depends()):

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="No valid access token provided")
    username = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == username).first()

    order = session.query(Order).filter(Order.id == id).first()
    if order.user != user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You cannot delete this order!")

    # if order.order_status != "PENDING":
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail="You cannot delete pending orders!")

    session.delete(order)
    session.commit()
    custom_response = {
        "success": True,
        "code": 200,
        "message": "User order deleted successfully",
        "data": None
    }
    return custom_response