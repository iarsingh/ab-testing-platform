# ab-testing-platform — interview questions and answers

[README](README.md) · [Project architecture](PROJECT_ARCHITECTURE.md)

Answers below use this repository’s files and implementation. They distinguish existing behavior from suggested extensions; source links let you verify each walkthrough.

## 1. What problem does ab-testing-platform address, and what can you demonstrate?

Compare control and treatment success counts. A |z| above 1.96 names a winner; otherwise none.

I would demonstrate the linked implementation or examples and distinguish that evidence from any planned production features. Start with [`README.md`](README.md).

## 2. How is this repository organized?

- [`src/abtest/main.py`](src/abtest/main.py): Implementation or supporting configuration.
- [`src/abtest/ops.py`](src/abtest/ops.py): Implementation or supporting configuration.
- [`src/abtest/abtest.py`](src/abtest/abtest.py): Implementation or supporting configuration.
- [`requirements.txt`](requirements.txt): Implementation or supporting configuration.
- [`src/abtest/__init__.py`](src/abtest/__init__.py): Implementation or supporting configuration.
- [`Dockerfile`](Dockerfile): Container build/service configuration.
- [`Makefile`](Makefile): Implementation or supporting configuration.
- [`docker-compose.yml`](docker-compose.yml): Container build/service configuration.

[PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) contains the component diagram and the implementation walkthrough.

## 3. Can you walk through `analyze` and explain the decision it makes?

The main walkthrough here is `analyze(control_success, control_n, treatment_success, treatment_n)` in [`src/abtest/abtest.py`](src/abtest/abtest.py#L12).

```python
def analyze(control_success, control_n, treatment_success, treatment_n):
    nums = (control_success, control_n, treatment_success, treatment_n)
    if any(not isinstance(v, int) or isinstance(v, bool) or v < 0 for v in nums):
        raise InputError("counts must be non-negative integers")
    if control_n < 1 or treatment_n < 1:
        raise InputError("each arm needs at least one observation")
    if control_success > control_n or treatment_success > treatment_n:
        raise InputError("successes cannot exceed observations")
    p1, p2 = rate(control_success, control_n), rate(treatment_success, treatment_n)
    lift = p2 - p1
    pooled = rate(control_success + treatment_success, control_n + treatment_n)
    se = math.sqrt(pooled * (1 - pooled) * (1 / control_n + 1 / treatment_n)) if 0 < pooled < 1 else 0
    z = lift / se if se else 0
    return {
        "control": round(p1, 4),
        "treatment": round(p2, 4),
        "lift": round(lift, 4),
        "z": round(z, 4),
        "winner": "treatment" if z > 1.96 else "control" if z < -1.96 else "none",
    }
```

The implementation calls `InputError`, `any`, `isinstance`, `math.sqrt`, `rate`, `round`. In an interview, trace those calls in execution order using a fixture input.

## 4. What responsibility does `rate` have?

`rate(success, n)` is defined in [`src/abtest/abtest.py`](src/abtest/abtest.py#L8).

Its return expressions include:

- `success / n if n else 0`

## 5. What input validation and failure behavior are implemented?

Explicit failure paths include:

- `InputError('counts must be non-negative integers')` in [`src/abtest/abtest.py`](src/abtest/abtest.py#L15).
- `InputError('each arm needs at least one observation')` in [`src/abtest/abtest.py`](src/abtest/abtest.py#L17).
- `InputError('successes cannot exceed observations')` in [`src/abtest/abtest.py`](src/abtest/abtest.py#L19).
- `HTTPException(status_code=422, detail=str(exc))` in [`src/abtest/main.py`](src/abtest/main.py#L19).
- `HTTPException(status_code=404, detail='workspace not found')` in [`src/abtest/ops.py`](src/abtest/ops.py#L77).
- `HTTPException(status_code=404, detail='job not found')` in [`src/abtest/ops.py`](src/abtest/ops.py#L100).
- `HTTPException(status_code=404, detail='job not found')` in [`src/abtest/ops.py`](src/abtest/ops.py#L109).

I would test both the condition that reaches each exception and the caller that translates it. An explicit raise does not mean every malformed input or dependency failure is handled.

## 6. Which test would you use to demonstrate correctness?

[`tests/test_ab.py`](tests/test_ab.py#L7) contains `test_clear_lift_picks_treatment`:

```python
def test_clear_lift_picks_treatment():
    payload = client.post("/analyze", json={
        "control_success": 10, "control_n": 200,
        "treatment_success": 80, "treatment_n": 200,
    }).json()
    assert payload["winner"] == "treatment"
    assert payload["lift"] > 0
```

This is a concrete regression example from the repository. Its assertions establish that case; they do not establish behavior for every input or under production load.

## 7. What HTTP interface does the code expose?

- `GET /healthz` → `healthz` in [`src/abtest/main.py`](src/abtest/main.py#L10).
- `POST /analyze` → `post_analyze` in [`src/abtest/main.py`](src/abtest/main.py#L15).
- `GET /readyz` → `readyz` in [`src/abtest/ops.py`](src/abtest/ops.py#L74).
- `POST /workspaces` → `create_workspace` in [`src/abtest/ops.py`](src/abtest/ops.py#L80).
- `GET /workspaces` → `list_workspaces` in [`src/abtest/ops.py`](src/abtest/ops.py#L98).
- `POST /workspaces/{workspace_id}/jobs` → `create_job` in [`src/abtest/ops.py`](src/abtest/ops.py#L106).
- `GET /jobs/{job_id}` → `get_job` in [`src/abtest/ops.py`](src/abtest/ops.py#L130).
- `POST /jobs/{job_id}/approve` → `approve_job` in [`src/abtest/ops.py`](src/abtest/ops.py#L140).

These are literal decorators. Application/router prefixes, authentication, and middleware must be checked in the corresponding setup code.

## 8. Where does state live, and what happens with multiple workers?

Module-level containers include `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS` in [`src/abtest/ops.py`](src/abtest/ops.py).

These containers belong to a Python process. Inspect which are constant fixtures and which are mutated. Mutable process state needs an explicit shared-storage or synchronization strategy before multiple workers can provide consistent behavior.

## 9. How would another engineer reproduce your walkthrough?

Start from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

These commands follow repository manifests; environment setup and command results still need to be checked on the target machine.

## 10. What does automation verify, and what does it not prove?

Inspect [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for triggers, permissions, and job commands. I would name the checks that those definitions run and show the latest run separately. A workflow definition alone does not establish a successful deployment, security review, or production SLO.

## 11. How would you present this project in a Forward Deployed Engineer interview?

Start with the user and operational problem described in [`README.md`](README.md). Explain one constraint that changes the implementation, show the linked code or example, and walk through a success case and a failure case. Agree on a measurable acceptance criterion before expanding the solution, and leave a handoff with data boundaries and rollback ownership. Any proposed production or business metric should be identified as a target until measured.

## 12. What is the input-to-output contract of `analyze`?

In [`src/abtest/abtest.py`](src/abtest/abtest.py#L12), `analyze(control_success, control_n, treatment_success, treatment_n)` receives the inputs. The function computes these intermediate values:

- `nums = (control_success, control_n, treatment_success, treatment_n)`
- `p1, p2 = (rate(control_success, control_n), rate(treatment_success, treatment_n))`
- `lift = p2 - p1`
- `pooled = rate(control_success + treatment_success, control_n + treatment_n)`
- `se = math.sqrt(pooled * (1 - pooled) * (1 / control_n + 1 / treatment_n)) if 0 < pooled < 1 else 0`
- `z = lift / se if se else 0`

Its result is defined by:

- `{'control': round(p1, 4), 'treatment': round(p2, 4), 'lift': round(lift, 4), 'z': round(z, 4), 'winner': 'treatment' if z > 1.96 else 'control' if z < -1.96 else 'none'}`

## 13. Which decision rules or boundary conditions should an interviewer challenge?

The implementation in [`src/abtest/abtest.py`](src/abtest/abtest.py#L12) branches on:

- `any((not isinstance(v, int) or isinstance(v, bool) or v < 0 for v in nums))`
- `control_n < 1 or treatment_n < 1`
- `control_success > control_n or treatment_success > treatment_n`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.

## 14. What does the operations plane add, and where is its limit?

[`src/abtest/ops.py`](src/abtest/ops.py) declares `GET /readyz`, `POST /workspaces`, `GET /workspaces`, `POST /workspaces/{workspace_id}/jobs`, `GET /jobs/{job_id}`, `POST /jobs/{job_id}/approve`, `GET /audit`, `GET /metrics`. Inspect the application’s `include_router` call for its URL prefix.

Its state containers are `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS`. The job-approval handler defines whether a target is accepted or refused; check that branch and the associated tests instead of treating a recorded job as a successful infrastructure apply.
