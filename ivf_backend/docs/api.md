# IVF Chatbot API Documentation

## Base URL
http://localhost:8000


Or your deployed backend URL in production.

## Authentication
Currently, the API uses session-based authentication. All endpoints require a valid `session_id`.

## Endpoints

### Health Check

#### GET /health
Check API health and status.

**Response:**
```json
{
  "status": "ok",
  "faiss_vectors": 1500,
  "version": "3.0",
  "features": [
    "basic_ivf_qa",
    "feedback_system", 
    "enhanced_safety",
    "conversation_memory",
    "document_processing"
  ]
}