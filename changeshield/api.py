from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from changeshield.analysis import analyze
from changeshield.models import ChangeRequest
from changeshield.security import Role, require_role
from changeshield.store import Store


def create_app(database_path="data/changeshield.sqlite3"):
    app = FastAPI(title="ChangeShield", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )
    store = Store(database_path)
    app.state.store = store

    @app.get("/health")
    def health():
        return {"status": "ok", "mode": "read-only"}

    @app.post("/api/v1/analyses", status_code=201)
    def create(request: ChangeRequest, _=Depends(require_role(Role.analyst))):
        return store.save({"name": request.name, **analyze(request)})

    @app.get("/api/v1/analyses")
    def list_analyses(_=Depends(require_role(Role.viewer))):
        return store.list()

    @app.get("/api/v1/analyses/{identifier}")
    def get_analysis(identifier: str, _=Depends(require_role(Role.viewer))):
        result = store.get(identifier)
        if not result:
            raise HTTPException(404, "Analysis not found")
        return result

    return app


app = create_app()
