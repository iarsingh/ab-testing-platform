from fastapi import FastAPI, HTTPException
from abtest.abtest import InputError, analyze

app = FastAPI()


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/analyze")
def post_analyze(body: dict):
    try:
        return analyze(body.get("control_success"), body.get("control_n"), body.get("treatment_success"), body.get("treatment_n"))
    except InputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
