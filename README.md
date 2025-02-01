# Solución Completa - Prueba Técnica Serverless (AWS)

Este **README** contiene **toda** la información solicitada para la prueba técnica:  
- Descripción y objetivos del proyecto.  
- Diagrama de arquitectura.  
- Decisiones técnicas.  
- Guía paso a paso de despliegue y ejecución.  
- Uso de la API.  
- Pruebas (tests).  
- Código funcional (serverless.yml, handler.py y test_handler.py) integrado en el mismo documento.  
- Posibles mejoras y escalabilidad.

---

## Tabla de Contenidos

1. [1. Introducción y Objetivos](#1-introducción-y-objetivos)  
2. [2. Arquitectura General](#2-arquitectura-general)  
   - [2.1 Diagrama](#21-diagrama)  
3. [3. Decisiones Técnicas](#3-decisiones-técnicas)  
4. [4. Estructura de Archivos](#4-estructura-de-archivos)  
5. [5. Guía de Despliegue Completa](#5-guía-de-despliegue-completa)  
   - [5.1 Configurar Credenciales de AWS](#51-configurar-credenciales-de-aws)  
   - [5.2 Instalar Dependencias (Python)](#52-instalar-dependencias-python)  
   - [5.3 Desplegar con Serverless Framework](#53-desplegar-con-serverless-framework)  
   - [5.4 Actualizar las URLs de las Colas SQS](#54-actualizar-las-urls-de-las-colas-sqs)  
   - [5.5 (Opcional) Ejecución Local (Offline)](#55-opcional-ejecución-local-offline)  
6. [6. Uso de la API](#6-uso-de-la-api)  
   - [6.1 Crear una Orden (POST)](#61-crear-una-orden-post)  
   - [6.2 Actualizar una Orden (PUT)](#62-actualizar-una-orden-put)  
7. [7. Pruebas (Tests)](#7-pruebas-tests)  
8. [8. Escalabilidad y Mejoras Futuras](#8-escalabilidad-y-mejoras-futuras)  
9. [9. Código Funcional](#9-código-funcional)  
   - [9.1 serverless.yml](#91-serverlessyml)  
   - [9.2 handler.py](#92-handlerpy)  
   - [9.3 tests/test_handler.py](#93-teststest_handlerpy)  
10. [10. Creación de Repositorio en GitHub (Guía)](#10-creación-de-repositorio-en-github-guía)  
11. [11. Conclusiones](#11-conclusiones)


---

## 1. Introducción y Objetivos

Esta solución **serverless** se diseñó para una **prueba técnica** enfocada en procesar órdenes de un servicio técnico. El sistema debe:

1. **Recibir** órdenes vía API (métodos REST).  
2. **Almacenar** los datos en una base de datos NoSQL (DynamoDB).  
3. **Encolar** las órdenes en una cola de mensajes (SQS) según el estado (received, inprocess, completed, canceled).  
4. **Procesar** las órdenes asíncronamente a través de funciones Lambda especializadas.

El objetivo es demostrar un **flujo escalable** y **desacoplado** que aproveche los servicios administrados de **AWS**.

---

## 2. Arquitectura General

La arquitectura propuesta se basa en los siguientes componentes de AWS:

1. **Amazon API Gateway**: Expone la API REST (endpoints `/orders`, `/orders/{orderId}`).  
2. **AWS Lambda** (Función principal):  
   - Valida la orden.  
   - Guarda/actualiza en **DynamoDB**.  
   - Envía un mensaje a **SQS** según el estado de la orden.  
3. **Amazon DynamoDB**: Base de datos NoSQL para almacenar los datos de cada orden.  
4. **Amazon SQS**: Colas independientes para cada estado de la orden.  
5. **AWS Lambda** (Funciones de procesamiento): Al llegar un mensaje a cada cola, se activa automáticamente la Lambda correspondiente para ese estado.

### 3. Diagrama

```plaintext
┌───────────────┐
│ API Gateway   │  (Endpoints: POST /orders, PUT /orders/{orderId})
└──────┬────────┘
       ▼
  ┌───────────────────┐
  │ Lambda create/    │
  │ update (handler)  │
  └──────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ DynamoDB - Table    │
│ "Orders"            │
└──────┬──────────────┘
       ▼
┌───────────────────────┐
│ SQS (cola por estado) │
└──────┬────────────────┘
       ▼
┌───────────────────────┐
│ Lambdas procesadoras  │
│ (una por estado)      │
└───────────────────────┘
```
### 4. Decisiones Técnicas

1.- Python 3.9

Uso de boto3 para integrar con AWS.
Facilidad para escribir y testear funciones Lambda.

2.- Serverless Framework

Permite definir la infraestructura (API Gateway, DynamoDB, SQS, IAM, etc.) en un solo archivo (serverless.yml).
Simplifica el despliegue a AWS.

3.- DynamoDB

Base de datos NoSQL con escalado automático y modelo de pago por solicitud.
Tablas flexibles para almacenar la información de las órdenes.

4.-  SQS

Se crea una cola por estado para un manejo desacoplado y claro.
Cada Lambda procesadora maneja un estado diferente.

5.- Separación de Funciones

Una función Lambda para la parte de API (crear / actualizar órdenes).
Varias funciones Lambda para el consumo de las colas (cada estado se procesa por separado).

### 5. Estructura de Archivos

Carpeta raíz del proyecto:-

```plaintext
technical-test
├── serverless.yml       # Despliegue (API Gateway, DynamoDB, SQS, Lambdas)
├── handler.py           # Funciones Lambda (crear/actualizar y procesar)
├── requirements.txt     # Dependencias de Python (boto3, pytest, etc.)
├── README.md            # Este documento
└── tests
    └── test_handler.py  # Pruebas unitarias
```
### 6. Guía de Despliegue Completa

6.1 Configurar Credenciales de AWS

Para que Serverless cree recursos en tu cuenta AWS, configura tus credenciales. Ejemplos:

- Archivo ~/.aws/credentials:

```plaintext
[default]
aws_access_key_id = TU_AWS_ACCESS_KEY_ID
aws_secret_access_key = TU_AWS_SECRET_ACCESS_KEY
```
- Variables de entorno: AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY.
- Command line con Serverless:

```plaintext
serverless config credentials \
  --provider aws \
  --key TU_AWS_ACCESS_KEY_ID \
  --secret TU_AWS_SECRET_ACCESS_KEY
```
6.2 Instalar Dependencias (Python)

Desde la carpeta raíz del proyecto:
```plaintext
pip install -r requirements.txt
```
Asegúrate de tener Python 3.9 o compatible.

6.3 Desplegar con Serverless Framework

1.Verifica si Serverless está instalado:
```plaintext
serverless --version
```
2.Despliega la infraestructura y funciones:
```plaintext
serverless deploy
```
3.Al finalizar, tendremos:
- Tabla DynamoDB Orders.
- Colas SQS (received, inprocess, completed, canceled).
- Varias Lambda (crear/actualizar y procesadoras).
- Endpoints de API Gateway (POST /orders, PUT /orders/{orderId}).

6.4 Actualizar las URLs de las Colas SQS

Tras el despliegue, la consola de Serverless (o CloudFormation) mostrará las URLs reales de las colas. En handler.py, la función get_queue_url_by_status usa URLs de ejemplo. Reemplázalas por las de AWS del proyecto:
```plaintext
def get_queue_url_by_status(status):
    urls = {
        "received":  "https://sqs.us-east-1.amazonaws.com/123456789012/received-queue",
        "inprocess": "https://sqs.us-east-1.amazonaws.com/123456789012/inprocess-queue",
        "completed": "https://sqs.us-east-1.amazonaws.com/123456789012/completed-queue",
        "canceled":  "https://sqs.us-east-1.amazonaws.com/123456789012/canceled-queue"
    }
    return urls.get(status.lower())
```
5.5 (Opcional) Ejecución Local (Offline)

Puedes usar serverless-offline para probar la API localmente:
```plaintext
npm install --save-dev serverless-offline
```
Agrega en serverless.yml:
```plaintext
plugins:
  - serverless-offline
```
Y luego:
```plaintext
serverless offline
```
Tendrás la API en http://localhost:3000.

  Nota: Para simular DynamoDB y SQS localmente, se puede usar LocalStack o la librería moto

### 6. Uso de la API

Al finalizar el despliegue, Serverless mostrará la URL base de la API Gateway. Por ejemplo:
```plaintext
https://abcdefghij.execute-api.us-east-1.amazonaws.com/dev
```
6.1  Crear una Orden (POST)
- Endpoint: POST /orders
- Ejemplo:
```plaintext
curl -X POST \
  https://abcdefghij.execute-api.us-east-1.amazonaws.com/dev/orders \
  -H "Content-Type: application/json" \
  -d '{
        "orderId": "ORD-001",
        "status": "received",
        "description": "Mantenimiento básico",
        "registerDate": "2025-01-31T08:00:00Z"
      }'
```
Respuesta:
```plaintext
{
  "message": "Order processed successfully"
}
```
6.2 Actualizar una Orden (PUT)

- Endpoint: PUT /orders/{orderId}
- Ejemplo:
```plaintext
curl -X PUT \
  https://abcdefghij.execute-api.us-east-1.amazonaws.com/dev/orders/ORD-001 \
  -H "Content-Type: application/json" \
  -d '{
        "orderId": "ORD-001",
        "status": "canceled",
        "description": "Cliente se retracta",
        "reasonForCancellation": "Motivo X"
      }'
```
Respuesta:
```plaintext
{
  "message": "Order processed successfully"
}
```
### 7. Pruebas(Tests)

Las pruebas unitarias se encuentran en el directorio tests/. Para ejecutarlas:
```plaintext
pytest
```
Ejemplo en tests/test_handler.py:
```plaintext
import json
from handler import create_update_order

def test_create_order_ok():
    event = {
        "body": json.dumps({
            "orderId": "test123",
            "status": "received",
            "description": "Testing order creation"
        })
    }
    response = create_update_order(event, {})
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["message"] == "Order processed successfully"
```
### 8. Escalabilidad y Mejoras Futuras

1. Colas FIFO

   - Si se requiere garantizar el orden de llegada, conviene usar colas FIFO (.fifo).

2. AWS Step Functions
   - Para flujos más complejos y orquestación de múltiples pasos antes de completar/cancelar.
3. Dead Letter Queue (DLQ)
   - Colas de respaldo para manejar mensajes con errores tras varios reintentos.
4. Monitoreo y Alertas
   - Usar CloudWatch para logs/métricas y crear alarmas (ej. fallos en Lambda, cola atascada).
5. Notificaciones
   - Integrar con Amazon SNS o EventBridge para avisar a otros sistemas cuando cambien los estados.

### 9. Código Funcional
A continuación, se muestra todo el código principal del proyecto.
9.1 serverless.yml
```plaintext
service: technical-test-service
frameworkVersion: '3'

provider:
  name: aws
  runtime: python3.9
  region: us-east-1
  stage: dev
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - dynamodb:*
          Resource: "*"
        - Effect: Allow
          Action:
            - sqs:SendMessage
            - sqs:ReceiveMessage
            - sqs:DeleteMessage
            - sqs:GetQueueAttributes
          Resource: "*"

functions:
  createUpdateOrder:
    handler: handler.create_update_order
    events:
      - http:
          path: orders
          method: post
      - http:
          path: orders/{orderId}
          method: put

  processOrderReceived:
    handler: handler.process_order_received
    events:
      - sqs:
          arn:
            Fn::GetAtt: [ ReceivedQueue, Arn ]

  processOrderInProcess:
    handler: handler.process_order_in_process
    events:
      - sqs:
          arn:
            Fn::GetAtt: [ InProcessQueue, Arn ]

  processOrderCompleted:
    handler: handler.process_order_completed
    events:
      - sqs:
          arn:
            Fn::GetAtt: [ CompletedQueue, Arn ]

  processOrderCanceled:
    handler: handler.process_order_canceled
    events:
      - sqs:
          arn:
            Fn::GetAtt: [ CanceledQueue, Arn ]

resources:
  Resources:
    OrdersTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: Orders
        AttributeDefinitions:
          - AttributeName: orderId
            AttributeType: S
        KeySchema:
          - AttributeName: orderId
            KeyType: HASH
        BillingMode: PAY_PER_REQUEST

    ReceivedQueue:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: received-queue

    InProcessQueue:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: inprocess-queue

    CompletedQueue:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: completed-queue

    CanceledQueue:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: canceled-queue
```
9.2 handler.py
```plaintext
import json
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Orders')

sqs_client = boto3.client('sqs')

def create_update_order(event, context):
    """
    Lambda que maneja:
      - POST /orders
      - PUT /orders/{orderId}

    1) Valida datos de la orden.
    2) Guarda/actualiza en DynamoDB.
    3) Envía un mensaje a SQS según el estado.
    """
    try:
        body = json.loads(event.get('body', '{}'))
    except (TypeError, json.JSONDecodeError):
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON"})
        }

    required_fields = ["orderId", "status", "description"]
    for f in required_fields:
        if f not in body:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Missing required field: {f}"})
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
            "orderId": order_id,
            "status": status,
            "description": description,
            "registerDate": register_date,
            "deliveryDate": delivery_date,
            "reasonForCancellation": reason_for_cancellation
        }
    )

    # Enviar a la cola correspondiente
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
    Retorna la URL de la cola SQS para el estado dado.
    Debes actualizarlas con las URLs de tu despliegue.
    """
    urls = {
        "received":  "https://sqs.us-east-1.amazonaws.com/123456789012/received-queue",
        "inprocess": "https://sqs.us-east-1.amazonaws.com/123456789012/inprocess-queue",
        "completed": "https://sqs.us-east-1.amazonaws.com/123456789012/completed-queue",
        "canceled":  "https://sqs.us-east-1.amazonaws.com/123456789012/canceled-queue"
    }
    return urls.get(status.lower())

def process_order_received(event, context):
    for record in event["Records"]:
        body = json.loads(record["body"])
        order_id = body.get("orderId")
        print(f"Processing 'received' order: {order_id}")
        # Lógica adicional para órdenes en estado 'received'
    return

def process_order_in_process(event, context):
    for record in event["Records"]:
        body = json.loads(record["body"])
        order_id = body.get("orderId")
        print(f"Processing 'inprocess' order: {order_id}")
        # Lógica adicional para órdenes en estado 'inprocess'
    return

def process_order_completed(event, context):
    for record in event["Records"]:
        body = json.loads(record["body"])
        order_id = body.get("orderId")
        print(f"Processing 'completed' order: {order_id}")
        # Lógica adicional para órdenes en estado 'completed'
    return

def process_order_canceled(event, context):
    for record in event["Records"]:
        body = json.loads(record["body"])
        order_id = body.get("orderId")
        print(f"Processing 'canceled' order: {order_id}")
        # Lógica adicional para órdenes en estado 'canceled'
    return
```
9.3 tests/test_handler.py
```plaintext
import json
from handler import create_update_order

def test_create_order_ok():
    event = {
        "body": json.dumps({
            "orderId": "test123",
            "status": "received",
            "description": "Testing order creation"
        })
    }
    response = create_update_order(event, {})
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["message"] == "Order processed successfully"

def test_create_order_missing_field():
    event = {
        "body": json.dumps({
            "status": "received",
            "description": "But missing orderId!"
        })
    }
    response = create_update_order(event, {})
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert "Missing required field: orderId" in body["error"]
```






















