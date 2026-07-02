from fastapi import FastAPI

app = FastAPI(title="NeuroVest", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "phase": "phase_1_skeleton",
        "live_trading": "locked",
        "broker_orders": "locked",
    }
