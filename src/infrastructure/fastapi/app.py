from fastapi import FastAPI


def create_app() -> FastAPI:
    return FastAPI(title="Xubio-like API", version="0.1.0")


# Keep a singleton app for runtime, but allow tests to create isolated apps.
app = create_app()
