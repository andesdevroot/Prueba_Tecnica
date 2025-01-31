# Creado por César Rivas 31/01/2025

import json
import pytest
from handler import create_update_order

def test_create_update_order_ok():
    event = {
        "body": json.dumps({
            "orderId": "test123",
            "status": "received",
            "description": "Test order"
        })
    }
   
    response = create_update_order(event, {})
    assert response["statusCode"] == 200

def test_create_update_order_missing_field():
    event = {
        "body": json.dumps({
            "status": "received",
            "description": "Missing orderId!"
        })
    }
    response = create_update_order(event, {})
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert "Missing required field: orderId" in body["error"]

