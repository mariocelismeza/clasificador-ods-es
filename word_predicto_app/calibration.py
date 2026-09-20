"""Calibración multiclase del pipeline final, sin usar el test para ajustar."""

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.special import softmax
from sklearn.base import clone
from sklearn.metrics import log_loss
from sklearn.model_selection import StratifiedGroupKFold, cross_val_predict


class TemperatureCalibratedPipeline:
    """Pipeline final más una temperatura escalar aprendida fuera de fold."""

    def __init__(self, pipeline, inverse_temperature):
        self.pipeline = pipeline
        self.inverse_temperature = float(inverse_temperature)
        self.classes_ = np.asarray(pipeline.classes_)

    def predict(self, X):
        return self.pipeline.predict(X)

    def predict_proba(self, X):
        margins = np.asarray(self.pipeline.decision_function(X))
        return softmax(self.inverse_temperature * margins, axis=1)


def top_label_ece(y_true, probabilities, classes, n_bins=10):
    """Error de calibración esperado de la clase con mayor probabilidad."""
    confidence = probabilities.max(axis=1)
    prediction = classes[probabilities.argmax(axis=1)]
    correct = prediction == np.asarray(y_true)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    rows = []
    error = 0.0
    for index, (lower, upper) in enumerate(zip(edges[:-1], edges[1:])):
        mask = (confidence >= lower) & (confidence <= upper if index == n_bins - 1 else confidence < upper)
        count = int(mask.sum())
        if not count:
            continue
        mean_confidence = float(confidence[mask].mean())
        accuracy = float(correct[mask].mean())
        error += count / len(confidence) * abs(accuracy - mean_confidence)
        rows.append({
            "intervalo": f"[{lower:.1f}, {upper:.1f}{']' if index == n_bins - 1 else ')'}",
            "n_textos": count,
            "probabilidad_media": mean_confidence,
            "acierto_observado": accuracy,
        })
    return float(error), rows


def fit_and_evaluate_calibration(model, X_train, y_train, groups_train, X_test, y_test, random_state=42):
    """Ajusta temperatura con folds agrupados; evalúa una vez en el test aislado."""
    X_train = np.asarray(X_train)
    y_train = np.asarray(y_train)
    groups_train = np.asarray(groups_train)
    X_test = np.asarray(X_test)
    y_test = np.asarray(y_test)
    classes = np.asarray(model.classes_)

    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=random_state)
    splits = list(cv.split(X_train, y_train, groups=groups_train))
    for train_indices, calibration_indices in splits:
        assert set(groups_train[train_indices]).isdisjoint(groups_train[calibration_indices])
        assert set(classes) == set(y_train[train_indices]) == set(y_train[calibration_indices])

    out_of_fold_margins = cross_val_predict(
        clone(model), X_train, y_train, cv=splits,
        method="decision_function", n_jobs=2,
    )
    assert out_of_fold_margins.shape == (len(X_train), len(classes))

    def out_of_fold_log_loss(log_inverse_temperature):
        beta = np.exp(log_inverse_temperature)
        return log_loss(y_train, softmax(beta * out_of_fold_margins, axis=1), labels=classes)

    optimum = minimize_scalar(out_of_fold_log_loss, bounds=(-5.0, 5.0), method="bounded")
    assert optimum.success
    beta = float(np.exp(optimum.x))
    calibrated = TemperatureCalibratedPipeline(model, beta)
    assert np.array_equal(calibrated.classes_, classes)

    probabilities = calibrated.predict_proba(X_test)
    assert probabilities.shape == (len(X_test), len(classes))
    assert np.all(np.isfinite(probabilities))
    assert np.all((probabilities >= 0) & (probabilities <= 1))
    assert np.allclose(probabilities.sum(axis=1), 1.0)

    original_predictions = model.predict(X_test)
    calibrated_predictions = calibrated.predict(X_test)
    assert np.array_equal(original_predictions, calibrated_predictions), "La calibración alteró alguna clase predicha."

    uncalibrated_softmax = softmax(model.decision_function(X_test), axis=1)
    ece, table = top_label_ece(y_test, probabilities, classes)
    baseline_ece, _ = top_label_ece(y_test, uncalibrated_softmax, classes)
    one_hot = (y_test[:, None] == classes[None, :]).astype(float)
    summary = {
        "metodo": "temperature",
        "temperatura": 1.0 / beta,
        "temperatura_inversa": beta,
        "log_loss_fuera_de_fold_entrenamiento": float(optimum.fun),
        "cv_folds": len(splits),
        "n_test": len(X_test),
        "ods_modelados": [int(value) for value in classes],
        "predicciones_preservadas": bool(np.array_equal(original_predictions, calibrated_predictions)),
        "log_loss_test": float(log_loss(y_test, probabilities, labels=classes)),
        "log_loss_softmax_sin_calibrar_test": float(log_loss(y_test, uncalibrated_softmax, labels=classes)),
        "brier_multiclase_test": float(np.mean(np.sum((probabilities - one_hot) ** 2, axis=1))),
        "ece_top_label_test": ece,
        "ece_top_label_softmax_sin_calibrar_test": baseline_ece,
    }
    return calibrated, summary, table
