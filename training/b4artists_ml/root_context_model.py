"""Motion-relative plus explicit gravity-direction kernel candidate.

This is a research-only model family. It is deliberately separate from the
frozen V3/V4 modules so their source hashes and receipts remain immutable.
"""

import numpy as np

from kernel_motion import kernel, kernel_trials, training_targets
from motion_coverage import evaluate_predictions, fit_feature_normalization, observed_features
from sequence_data import semantic_output
from sequence_kinematics import forward
from sequence_model import statistics


SCHEMA = "motion_relative_gravity_v1"
BASE_FEATURE_DIMENSIONS = 427


def features(windows):
    rows = []
    for window in windows:
        environment = np.asarray(window.get("environment"), dtype=float)
        if environment.shape != (11,) or not np.isfinite(environment).all():
            raise ValueError("Known environmental context is required")
        if environment[4] != 1 or not np.isclose(np.linalg.norm(environment[:3]), 1.0, atol=1e-7):
            raise ValueError("This candidate requires a known gravity direction")
        rows.append(np.r_[observed_features(window), environment[:3], environment[4]])
    result = np.stack(rows)
    if result.shape[1] != BASE_FEATURE_DIMENSIONS + 4:
        raise ValueError("Unexpected root-context feature dimension")
    return result


def prepare(windows, importance):
    if not np.isfinite(importance) or importance <= 0:
        raise ValueError("Positive gravity feature importance required")
    x = features(windows)
    _, weights, _, _ = statistics(windows)
    mean, std = fit_feature_normalization(x, weights)
    std[-4:] /= importance
    return (x - mean) / std, weights, mean, std, training_targets(windows)


def fit(windows, importance, base_width, regularization):
    z, weights, mean, std, target = prepare(windows, importance)
    width = base_width * np.sqrt(BASE_FEATURE_DIMENSIONS / z.shape[1])
    _, alpha = next(kernel_trials(z, weights, target, width, [regularization]))
    return dict(
        kind="kernel",
        variant="motion_relative_gravity",
        feature_schema=SCHEMA,
        gravity_importance=float(importance),
        mean=mean,
        std=std,
        centers=z,
        width=width,
        alpha=alpha,
    )


def infer_coefficients(model, windows):
    if str(model.get("feature_schema", "")) != SCHEMA:
        raise ValueError("Unsupported root-context model schema")
    z = (features(windows) - model["mean"]) / model["std"]
    if not np.isfinite(z).all():
        raise ValueError("Nonfinite root-context model observations")
    result = np.empty((len(z), 564))
    for start in range(0, len(z), 64):
        result[start:start + 64] = kernel(z[start:start + 64], model["centers"], model["width"]) @ model["alpha"]
    if not np.isfinite(result).all():
        raise ValueError("Nonfinite root-context learned coefficients")
    return result.reshape(len(z), 4, 141)


def evaluate_model(model, windows, skeleton):
    coefficients = infer_coefficients(model, windows)
    predictions = []
    maximum_edge_error = 0.0
    for window, coefficient in zip(windows, coefficients, strict=True):
        local = window["baseline"] + window["basis_functions"] @ coefficient
        positions, _, _ = forward(local, window["offsets"], skeleton[1])
        parents = np.asarray(skeleton[1][1:])
        lengths = np.linalg.norm(positions[:, 1:] - positions[:, parents], axis=-1)
        maximum_edge_error = max(
            maximum_edge_error,
            float(abs(lengths - np.linalg.norm(window["offsets"][1:], axis=-1)).max()),
        )
        predictions.append(semantic_output(local, window["offsets"], skeleton))
    report = evaluate_predictions(windows, predictions)
    report["aggregate"]["true_edge_length_max"] = maximum_edge_error
    return report
