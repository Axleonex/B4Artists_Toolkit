"""draw_to_keys_math.py — the geometry behind Draw to Keys (design §8 decision 15), with no bpy.

Strokes are lists of 3D points (any 3-sequence). The longest stroke is the path; every other stroke is a
timing dash. Each dash that comes within ``tolerance × path length`` of the path marks one crossing: the
path point of closest approach, reported with its arclength fraction ``t`` in [0, 1]. Crossings sorted
along the path become keys at start, start + step, start + 2·step, ...
"""

from __future__ import annotations

from typing import Optional, Sequence

Point = tuple[float, float, float]


def _sub(a, b) -> Point:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _add(a, b) -> Point:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _scale(a, s: float) -> Point:
    return (a[0] * s, a[1] * s, a[2] * s)


def _dot(a, b) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _length(a) -> float:
    return _dot(a, a) ** 0.5


def polyline_length(points: Sequence[Sequence[float]]) -> float:
    return sum(_length(_sub(points[i + 1], points[i])) for i in range(len(points) - 1))


def longest_stroke(strokes: Sequence[Sequence[Sequence[float]]]) -> int:
    """Index of the longest stroke (by polyline length), or -1 for none. Ties keep the first."""
    best, best_len = -1, -1.0
    for index, stroke in enumerate(strokes):
        length = polyline_length(stroke)
        if length > best_len:
            best, best_len = index, length
    return best


def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def closest_points_between_segments(p1, q1, p2, q2) -> tuple[float, float, float]:
    """(s, t, distance): parameters on segment p1-q1 and p2-q2 of their closest points (Ericson, RTCD 5.1.9)."""
    d1, d2, r = _sub(q1, p1), _sub(q2, p2), _sub(p1, p2)
    a, e, f = _dot(d1, d1), _dot(d2, d2), _dot(d2, r)
    eps = 1e-12
    if a <= eps and e <= eps:
        return 0.0, 0.0, _length(r)
    if a <= eps:
        s, t = 0.0, _clamp01(f / e)
    else:
        c = _dot(d1, r)
        if e <= eps:
            t, s = 0.0, _clamp01(-c / a)
        else:
            b = _dot(d1, d2)
            denom = a * e - b * b
            s = _clamp01((b * f - c * e) / denom) if denom > eps else 0.0
            t = (b * s + f) / e
            if t < 0.0:
                t, s = 0.0, _clamp01(-c / a)
            elif t > 1.0:
                t, s = 1.0, _clamp01((b - c) / a)
    c1 = _add(p1, _scale(d1, s))
    c2 = _add(p2, _scale(d2, t))
    return s, t, _length(_sub(c1, c2))


def dash_crossing(path: Sequence[Sequence[float]], dash: Sequence[Sequence[float]],
                  max_distance: float) -> Optional[tuple[float, Point]]:
    """(arclength along the path, path point) where ``dash`` first comes within ``max_distance`` of the path,
    walking the dash from its first point (a dash that wiggles across twice counts once), or None."""
    cumulative = [0.0]
    for i in range(len(path) - 1):
        cumulative.append(cumulative[-1] + _length(_sub(path[i + 1], path[i])))
    for j in range(len(dash) - 1):
        # Within one dash segment the first crossing is the one the dash reaches first (smallest position
        # along the dash), not the closest one: a single stroke across both legs of a U meets the near leg first.
        best = None
        for i in range(len(path) - 1):
            s, t, distance = closest_points_between_segments(path[i], path[i + 1], dash[j], dash[j + 1])
            if distance <= max_distance and (best is None or (t, distance) < best[0]):
                best = ((t, distance), i, s)
        if best is not None:
            _order, i, s = best
            point = _add(path[i], _scale(_sub(path[i + 1], path[i]), s))
            return cumulative[i] + s * (cumulative[i + 1] - cumulative[i]), point
    return None


def crossings(path: Sequence[Sequence[float]], dashes: Sequence[Sequence[Sequence[float]]],
              tolerance: float) -> list[tuple[float, Point]]:
    """(t in [0, 1], path point) for every dash that crosses the path, sorted along the path.
    A dash counts when its closest approach is within ``tolerance × path length``."""
    length = polyline_length(path)
    if length <= 0.0 or len(path) < 2:
        return []
    found = []
    for dash in dashes:
        if len(dash) < 2:
            continue
        hit = dash_crossing(path, dash, tolerance * length)
        if hit is not None:
            found.append((hit[0] / length, hit[1]))
    return sorted(found, key=lambda item: item[0])


def frames_from_crossings(count: int, start: float, step: float) -> list[float]:
    """Key frames for ``count`` crossings: start, start + step, ..."""
    return [start + i * step for i in range(count)]
