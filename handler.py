# Creado por Cesar Rivas 30/01/2025

import json
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Orders')

sqs_client = boto3.client('sqs')

# ====== CREATE/UPDATE ORDER (API Gateway) ======
def create_update_order(event, context):
    """
    Esta función se invoca al hacer:
      - POST /orders
      - PUT /orders/{orderId}

    Se encarga de:
      1) Validar los datos de la orden
      2) Guardar/actualizar la orden en DynamoDB
      3) Enviar un mensaje a la cola SQS correspondiente según el estado
    """
    try:
        body = json.loads(event['body'])
    except (TypeError, json.JSONDecodeError):
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON in request body."})
        }

    # Validar campos requeridos
    required_fields = ["orderId", "status", "description"]
    for field in required_fields:
        if field not in body:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Missing required field: {field}"})
            }

    order_id = body["orderId"]
    status = body["status"]
    description = body["description"]
    register_date = body.get("registerDate", str(datetime.utcnow()))
    delivery_date = body.get("deliveryDate", "")
    reason_for_cancellation = body.get("reasonForCancellation", "")

    # Guardar en DynamoDB
    table.put_item(
        Item={
            'orderId': order_id,
            'status': status,
            'description': description,
            'registerDate': register_date,
            'deliveryDate': delivery_date,
            'reasonForCancellation': reason_for_cancellation
        }
    )

    # Enviar a la cola que corresponda
    queue_url = get_queue_url_by_status(status)
    if not queue_url:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Unknown status '{status}'"})
        }

    message_body = {
        "orderId": order_id,
        "status": status
    }

    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message_body)
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Order processed successfully"})
    }


def get_queue_url_by_status(status):
    """
    Devuelve la URL de la cola SQS según el estado de la orden.
    Ajusta estas URLs tras desplegar o usa variables de entorno si lo prefieres.
    """
    # NOTA: Al hacer `serverless deploy`, en la consola aparecerán
    # Se uso hardcode para simplificar el ejemplo de esta prueba técnica
    urls = {
        "received":    "https://sqs.us-east-1.amazonaws.com/123456789012/received-queue",
        "inprocess":   "https://sqs.us-east-1.amazonaws.com/123456789012/inprocess-queue",
        "completed":   "https://sqs.us-east-1.amazonaws.com/123456789012/completed-queue",
        "canceled":    "https://sqs.us-east-1.amazonaws.com/123456789012/canceled-queue"
    }
    return urls.get(status.lower(), None)


# ====== PROCESAR ÓRDENES DE CADA ESTADO ======

def process_order_received(event, context):
    """
    Función Lambda que se dispara cuando llega un mensaje a 'received-queue'.
    """
    for record in event["Records"]:
        body = json.loads(record["body"])
        order_id = body.get("orderId")
        status = body.get("status")
        print(f"Processing 'received' order: {order_id} - {status}")
    return


def process_order_in_process(event, context):
    """
    Función Lambda que se dispara cuando llega un mensaje a 'inprocess-queue'.
    """
    for record in event["Records"]:
        body = json.loads(record["body"])
        order_id = body.get("orderId")
        status = body.get("status")
        print(f"Processing 'in process' order: {order_id} - {status}")
    return


def process_order_completed(event, context):
    """
    Función Lambda que se dispara cuando llega un mensaje a 'completed-queue'.
    """
    for record in event["Records"]:
        body = json.loads(record["body"])
        order_id = body.get("orderId")
        status = body.get("status")
        print(f"Processing 'completed' order: {order_id} - {status}")
    return


def process_order_canceled(event, context):
    """
    Función Lambda que se dispara cuando llega un mensaje a 'canceled-queue'.
    """
    for record in event["Records"]:
        body = json.loads(record["body"])
        order_id = body.get("orderId")
        status = body.get("status")
        print(f"Processing 'canceled' order: {order_id} - {status}")
    return


# Nota 1: Para pruebas más completas, podriamos usar 
# librerías como moto para mockear AWS DynamoDB, SQS, etc., y así no depender de la nube al correr tests locales.

# Nota 2: También se podrian añadir pruebas de integración que verifiquen que efectivamente 
# se insertan los datos en la tabla y se envían mensajes a SQS (en un ambiente de test real).

# Nota 3: Se podrian añadir pruebas de rendimiento para verificar que el sistema escale correctamente.

