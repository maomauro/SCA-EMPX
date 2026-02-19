"""
Punto de entrada del proyecto SCA-EMPX. Arranca la API backend.
"""
import uvicorn


def main():
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["backend", "frontend"],
        reload_excludes=["*.pyc", "__pycache__", "*.db"],
    )


if __name__ == "__main__":
    main()
