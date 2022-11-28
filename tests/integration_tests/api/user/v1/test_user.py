import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, role, expected",
    [
        (
            5,
            None,
            {"status_code": 404, "message": "user not found"},
        ),
        (
            5,
            "seller",
            {"status_code": 400, "message": "only buyers can change deposit"},
        ),
        (
            1,
            "buyer",
            {"status_code": 422, "message": None},
        ),
        (
            5,
            "buyer",
            {"status_code": 200, "message": "successful", "balance": 5, "added": 5},
        ),
    ],
)
async def test_deposit_once(client, test_db, value, role, expected):
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

    response = await client.post("/api/v1/deposit", json={"value": value})
    assert response.status_code == expected["status_code"]
    assert response.json().get("message") == expected["message"]
    assert response.json().get("balance") == expected.get("balance")
    assert response.json().get("added") == expected.get("added")


async def test_deposit_multiple_times(client, test_db):
    await client.post(
        "/api/v1/user",
        json={
            "username": "mvpmatch",
            "password1": "abcde",
            "password2": "abcde",
            "role": "buyer",
        },
    )

    response = await client.post("/api/v1/deposit", json={"value": 5})
    assert response.status_code == 200
    assert response.json() == {"message": "successful", "balance": 5, "added": 5}

    await client.post(
        "/api/v1/user",
        json={
            "username": "mvpmatch",
            "password1": "abcde",
            "password2": "abcde",
            "role": "buyer",
        },
    )

    response = await client.post("/api/v1/deposit", json={"value": 50})
    assert response.status_code == 200
    assert response.json() == {"message": "successful", "balance": 55, "added": 50}
