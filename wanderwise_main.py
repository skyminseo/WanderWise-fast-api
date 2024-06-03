from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from prediction import router as prediction_router

app = FastAPI()

# Middleware to handle CORS
# Example

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["https://example.com"],  # Only allow a specific origin
#     allow_credentials=True,  # Allow cookies and credentials
#     allow_methods=["GET", "POST"],  # Only allow specific methods
#     allow_headers=["Authorization", "Content-Type"],  # Only allow specific headers
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prediction_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
