from river.drift import ADWIN

drift_detector = ADWIN()


def detect_drift(probability):

    drift_detector.update(probability)

    return drift_detector.drift_detected
