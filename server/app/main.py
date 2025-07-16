from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse
# from fastapi.staticfiles import StaticFiles
import os
from app.api.v1 import auth, campaigns, subscriptions, gmail_oauth, google_auth
from app.routes import auth as auth_routes, senders, templates, files, stats, folders, contacts

app = FastAPI()

# Remove all static/HTML serving
# @app.get("/", include_in_schema=False)
# def read_root():
#     return FileResponse(os.path.join("app", "static", "index.html"))
# app.mount("/static", StaticFiles(directory="app/static"), name="static")
# app.mount("/app", StaticFiles(directory="../../client/build", html=True), name="react-app")

# CORS setup (if needed for React dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(auth_routes.router, prefix="/api/auth", tags=["auth"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(senders.router, prefix="/api/senders", tags=["senders"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(folders.router, prefix="/api/folders", tags=["folders"])
app.include_router(contacts.router, prefix="/api/contacts", tags=["contacts"])
app.include_router(subscriptions.router, prefix="/api/v1/subscriptions", tags=["subscriptions"])

@app.on_event("startup")
async def startup_event():
    from app.db.mongodb import MongoDB
    await MongoDB.connect_to_mongo()
    print("✅ MongoDB connected successfully")

@app.on_event("shutdown")
async def shutdown_event():
    from app.db.mongodb import MongoDB
    await MongoDB.close_mongo_connection()
    print("✅ MongoDB connection closed")

@app.get("/health")
async def health_check():
    return {"status": "ok"} 