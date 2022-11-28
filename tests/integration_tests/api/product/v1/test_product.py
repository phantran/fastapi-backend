import pytest

from app.product.schemas.product import ProductCreateRequestSchema
from app.product.services.product import ProductService
from app.user.services import UserService


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "product, role, expected",
    [
        (
            {"product_name": "pepsi", "amount_available": 5, "cost": 5},
            None,
            {"status_code": 404, "message": "user not found"},
        ),
        (
            {"product_name": "pepsi", "amount_available": 5, "cost": 5},
            "buyer",
            {
                "status_code": 400,
                "message": "As a buyer, you cannot change this product",
            },
        ),
        (
            {"product_name": "pepsi", "amount_available": 5, "cost": 2},
            "seller",
            {"status_code": 422, "message": None},
        ),
        (
            {"product_name": "pepsi", "amount_available": -1, "cost": 5},
            "seller",
            {"status_code": 422, "message": None},
        ),
        (
            {"product_name": "pepsi", "amount_available": 5, "cost": 5},
            "seller",
            {"status_code": 200, "message": "Product created successfully"},
        ),
    ],
)
async def test_create_product(client, test_db, product, role, expected):
    if role:
        await client.post(
            "/api/v1/user",
            json={
                "username": "mvpmatch",
                "password1": "abcde",
                "password2": "abcde",
                "role": role,
            },
        )

    response = await client.post("/api/v1/product/create", json=product)
    assert response.status_code == expected["status_code"]
    assert response.json().get("message") == expected["message"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload, product, role, deposit, expected",
    [
        (
            {"amount": 1, "product_id": 1},
            None,
            None,
            0,
            {"status_code": 404, "message": "user not found"},
        ),
        (
            {"amount": 1, "product_id": 1},
            None,
            "buyer",
            0,
            {"status_code": 404, "message": "product not found"},
        ),
        (
            {"amount": 1, "product_id": 1},
            {"product_name": "pepsi", "amount_available": 5, "cost": 5, "seller_id": 1},
            "seller",
            0,
            {"status_code": 400, "message": "only buyers can buy products"},
        ),
        (
            {"amount": 1, "product_id": 1},
            {"product_name": "pepsi", "amount_available": 5, "cost": 5, "seller_id": 1},
            "buyer",
            0,
            {"status_code": 400, "message": "In sufficient balance to buy product"},
        ),
        (
            {"amount": 1, "product_id": 1},
            {"product_name": "pepsi", "amount_available": 5, "cost": 5, "seller_id": 1},
            "buyer",
            100,
            {
                "status_code": 200,
                "total_spent": 5,
                "product_name": "pepsi",
                "product_id": 1,
                "change": [50, 20, 20, 5],
            },
        ),
        (
            {"amount": 2, "product_id": 1},
            {"product_name": "pepsi", "amount_available": 5, "cost": 5, "seller_id": 1},
            "buyer",
            100,
            {
                "status_code": 200,
                "total_spent": 10,
                "product_name": "pepsi",
                "product_id": 1,
                "change": [50, 20, 20],
            },
        ),
        (
            {"amount": 1, "product_id": 1},
            {"product_name": "pepsi", "amount_available": 0, "cost": 5, "seller_id": 1},
            "buyer",
            100,
            {"status_code": 200, "detail": "Product pepsi is out of stock"},
        ),
    ],
)
async def test_buy_product(client, test_db, payload, product, role, deposit, expected):
    if role:
        await client.post(
            "/api/v1/user",
            json={
                "username": "buyer",
                "password1": "abcde",
                "password2": "abcde",
                "role": role,
                "deposit": deposit,
            },
        )
    if product:
        await UserService().create_user(
            **{
                "username": "seller",
                "password1": "abcde",
                "password2": "abcde",
                "role": "seller",
                "deposit": 0,
            }
        )
        await ProductService().create_product(
            user_id=2, payload=ProductCreateRequestSchema(**product)
        )

    response = await client.post("/api/v1/buy", json=payload)
    assert response.status_code == expected["status_code"]
    assert response.json().get("message") == expected.get("message")
    assert response.json().get("detail") == expected.get("detail")
    assert response.json().get("total_spent") == expected.get("total_spent")
    assert response.json().get("product_name") == expected.get("product_name")
    assert response.json().get("product_id") == expected.get("product_id")
    assert response.json().get("change") == expected.get("change")
