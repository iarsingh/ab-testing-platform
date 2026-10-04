import math


class InputError(ValueError):
    pass


def rate(success, n):
    return success / n if n else 0


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
