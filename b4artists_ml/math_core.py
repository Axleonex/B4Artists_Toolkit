"""Small local deterministic baseline. No learned weights or network calls."""
import math


def finite_vector(values, size):
    if not isinstance(values, (list, tuple)) or len(values) != size:
        raise ValueError(f"Expected {size} numeric components")
    if any(isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(v) for v in values):
        raise ValueError("Components must be finite numbers")
    return tuple(float(v) for v in values)


def unit_quaternion(values):
    q = finite_vector(values, 4)
    scale=max(abs(v) for v in q)
    if scale < 1e-10:
        raise ValueError("Zero-length quaternion")
    scaled=tuple(v/scale for v in q)
    norm=math.hypot(*scaled)
    return tuple(v/norm for v in scaled)


def slerp(start, end, t):
    if not math.isfinite(t) or not 0 <= t <= 1:
        raise ValueError("Blend factor must be between zero and one")
    a, b = unit_quaternion(start), unit_quaternion(end)
    dot = sum(x*y for x, y in zip(a, b))
    if dot < 0:
        b, dot = tuple(-v for v in b), -dot
    dot = min(1.0, max(-1.0, dot))
    if dot > 0.9995:
        return unit_quaternion(tuple(x + t*(y-x) for x, y in zip(a, b)))
    theta = math.acos(dot)
    denom = math.sin(theta)
    return tuple((math.sin((1-t)*theta)*x + math.sin(t*theta)*y)/denom for x, y in zip(a, b))


def timing_weight(t, easing="SMOOTH", bias=0.0):
    """Return a monotonic endpoint-preserving timing weight.

    ``bias`` moves the visual breakdown without moving either authored pose.
    Positive values arrive earlier; negative values arrive later.  The bounded
    rational remap keeps every input in [0, 1] and maps an unbiased midpoint to
    0.1..0.9 across the exposed -1..1 control range.
    """
    if (isinstance(t, bool) or not isinstance(t, (int, float)) or
            not math.isfinite(t) or not 0 <= t <= 1):
        raise ValueError("Blend factor must be between zero and one")
    if (isinstance(bias, bool) or not isinstance(bias, (int, float)) or
            not math.isfinite(bias) or not -1 <= bias <= 1):
        raise ValueError("Timing bias must be between minus one and one")
    if easing not in {"LINEAR", "SMOOTH", "EASE_IN", "EASE_OUT"}:
        raise ValueError("Unknown interpolation")
    if t in {0, 1}:
        shifted = float(t)
    else:
        midpoint = 0.5 + 0.4 * float(bias)
        shifted = t / (((1.0 / midpoint - 2.0) * (1.0 - t)) + 1.0)
    if easing == "SMOOTH":
        return shifted * shifted * (3.0 - 2.0 * shifted)
    if easing == "EASE_IN":
        return shifted * shifted
    if easing == "EASE_OUT":
        return 1.0 - (1.0 - shifted) * (1.0 - shifted)
    return shifted


def timing_window(t, departure_hold=0.0, arrival_hold=0.0):
    """Map an interval into its active transition window, preserving endpoints."""
    if (isinstance(t, bool) or not isinstance(t, (int, float)) or
            not math.isfinite(t) or not 0 <= t <= 1):
        raise ValueError("Blend factor must be between zero and one")
    values = (departure_hold, arrival_hold)
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) or
           not math.isfinite(value) or not 0 <= value <= .9 for value in values):
        raise ValueError("Transition holds must be between zero and 0.9")
    departure_hold, arrival_hold = map(float, values)
    if departure_hold + arrival_hold > .900001:
        raise ValueError("Transition holds must leave at least ten percent for motion")
    if t <= departure_hold:
        return 0.0
    if t >= 1.0 - arrival_hold:
        return 1.0
    return (float(t) - departure_hold) / (1.0 - departure_hold - arrival_hold)


def blend_pose(a, b, t, easing="SMOOTH", bias=0.0,
               departure_hold=0.0, arrival_hold=0.0):
    if not math.isfinite(t) or not 0 <= t <= 1:
        raise ValueError("Blend factor must be between zero and one")
    weight = timing_weight(timing_window(t, departure_hold, arrival_hold), easing, bias)
    result = {}
    if a.keys() != b.keys():
        raise ValueError("Pose anchors contain different control sets; recapture both")
    for name in a:
        x, y = a[name], b[name]
        if x["mode"] != y["mode"] or x["channels"] != y["channels"]:
            raise ValueError(f"Control rotation mode or locks changed: {name}")
        result[name] = {"mode": x["mode"], "channels": x["channels"],
                        "rotation": slerp(x["rotation"], y["rotation"], weight)}
        for key in ("location", "scale"):
            first, second = finite_vector(x[key], 3), finite_vector(y[key], 3)
            if weight == 0.0:
                result[name][key] = first
            elif weight == 1.0:
                result[name][key] = second
            else:
                result[name][key] = tuple((1.0-weight)*v + weight*w
                                          for v, w in zip(first, second))
    return result


def two_bone_positions(root, target, pole, upper_length, lower_length, max_bend=180.):
    """Analytic non-stretch reach, with maximum flexion in degrees (zero is straight)."""
    root, target, pole = (finite_vector(v, 3) for v in (root, target, pole))
    if not all(math.isfinite(v) and v > 0 for v in (upper_length, lower_length)):
        raise ValueError("Bone lengths must be positive and finite")
    if not math.isfinite(max_bend) or not 0 < max_bend <= 180:
        raise ValueError("Maximum bend must be in (0, 180] degrees")
    epsilon = min(upper_length, lower_length) * 1e-7
    sub = lambda a, b: tuple(x-y for x, y in zip(a, b))
    dot = lambda a, b: sum(x*y for x, y in zip(a, b))
    delta = sub(target, root)
    raw_distance = math.sqrt(dot(delta, delta))
    axis = tuple(v/raw_distance for v in delta) if raw_distance > epsilon else (0., 1., 0.)
    minimum = math.sqrt(max(0., upper_length**2 + lower_length**2 +
                             2*upper_length*lower_length*math.cos(math.radians(max_bend))))
    distance = max(minimum, abs(upper_length-lower_length) + epsilon,
                   min(raw_distance, upper_length+lower_length-epsilon))
    plane = sub(pole, root)
    projection = dot(plane, axis)
    plane = tuple(v-projection*n for v, n in zip(plane, axis))
    norm = math.sqrt(dot(plane, plane))
    if norm < epsilon:
        fallback = min(((1.,0.,0.), (0.,1.,0.), (0.,0.,1.)), key=lambda v: abs(dot(v, axis)))
        projection = dot(fallback, axis)
        plane = tuple(v-projection*n for v, n in zip(fallback, axis))
        norm = math.sqrt(dot(plane, plane))
    plane = tuple(v/norm for v in plane)
    along = (upper_length**2 - lower_length**2 + distance**2)/(2*distance)
    height = math.sqrt(max(0., upper_length**2 - along**2))
    joint = tuple(r + along*n + height*p for r, n, p in zip(root, axis, plane))
    end = tuple(r + distance*n for r, n in zip(root, axis))
    return joint, end
