import pytest
from fastapi.testclient import TestClient
from main import app
from fastapi import status
from router.auth import decode_token_to_get_user
from database import SessionLocal
from models import Transactions

client = TestClient(app)

def override_user():
    return{
        "id": 1,
        "username": "testuser"
    }

app.dependency_overrides[decode_token_to_get_user] = override_user


def test_create_transaction():
    db = SessionLocal()
    db.query(Transactions).filter(Transactions.id == 999).delete()
    db.commit()

    request_data = {
        "id": 999,
        "title": "Eggs+Chicken+Rice",
        "amount": 1000,
        "type": "expense",
        "category": "Grocery",
        "date": "2026-09-17T09:39:32.480000"
    }

    response = client.post("/transactions", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED


def test_get_all_transactions():
    response = client.get("/transactions")
    assert response.status_code == status.HTTP_200_OK

def test_transaction_by_id():
    response = client.get("/transactions/999")
    assert response.status_code == status.HTTP_200_OK


def test_update_transaction():
    request_data = {
            "title": "Eggs+Chicken+Rice+Vegetables",
            "amount": 1230,
        }
    
    response = client.put("/transactions/999", json=request_data)
    assert response.status_code == status.HTTP_200_OK

def test_delete_transaction():
    response = client.delete("/transactions/999")
    assert response.status_code == status.HTTP_200_OK
        