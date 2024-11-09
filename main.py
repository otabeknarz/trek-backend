# import os
# import sys
#
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trek.database import engine, Base
from fastapi import FastAPI
from users.urls import router as users_router
from core.urls import router as core_router
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Allow all origins (use caution in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify allowed domains
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.include_router(users_router)
app.include_router(core_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
