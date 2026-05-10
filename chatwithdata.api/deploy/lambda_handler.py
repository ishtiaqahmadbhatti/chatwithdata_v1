"""
AWS Lambda Handler for SmartConverter API
Uses Mangum to adapt FastAPI/ASGI app to Lambda events
"""
from mangum import Mangum
from app.main import app

# Mangum wraps FastAPI to handle AWS Lambda + API Gateway events
handler = Mangum(app, lifespan="off")
