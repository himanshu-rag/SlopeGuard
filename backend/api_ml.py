import joblib
import numpy as np
import onnxruntime as ort
import os
import sys

# Ensure ml/ module is importable for fusion logic
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ml'))
from fusion import calculate_final_risk, determine_reason_code

SUSC_MODEL_PATH = os.path.join(os.path.dirname(__file__), '../ml/models/susceptibility_model.pkl')
TRIG_MODEL_PATH = os.path.join(os.path.dirname(__file__), '../ml/models/trigger_model.onnx')


class RiskEngine:
    def __init__(self):
        self.susc_model   = None
        self.trig_session = None
        self._load_models()

    def _load_models(self):
        if os.path.exists(SUSC_MODEL_PATH):
            self.susc_model = joblib.load(SUSC_MODEL_PATH)
            print(f"[RiskEngine] Loaded XGBoost from {SUSC_MODEL_PATH}")
        else:
            print(f"[RiskEngine] WARNING: XGBoost model not found at {SUSC_MODEL_PATH}. Using fallback.")

        if os.path.exists(TRIG_MODEL_PATH):
            self.trig_session = ort.InferenceSession(TRIG_MODEL_PATH)
            # FIX #2: Use the actual input name from the ONNX graph instead of hardcoding
            self._onnx_input_name = self.trig_session.get_inputs()[0].name
            print(f"[RiskEngine] Loaded ONNX LSTM. Input name: '{self._onnx_input_name}'")
        else:
            print(f"[RiskEngine] WARNING: ONNX model not found at {TRIG_MODEL_PATH}. Using fallback.")

    def predict_susceptibility(self, slope_deg: float, aspect_deg: float, curvature: float, twi: float) -> float:
        """
        Returns P(landslide | terrain) in [0, 1].
        Falls back to physics-based heuristic if model is not loaded.
        """
        if self.susc_model:
            import pandas as pd
            df = pd.DataFrame([[slope_deg, aspect_deg, curvature, twi]],
                              columns=['slope_deg', 'aspect_deg', 'curvature', 'twi'])
            return float(self.susc_model.predict_proba(df)[0][1])

        # Fallback: geotechnical heuristic (angle-of-repose based)
        slope_factor = max(0.0, (slope_deg - 15.0) / 50.0)  # Normalised: 15° = stable, 65° = certain failure
        twi_factor   = max(0.0, (twi - 3.0) / 9.0)
        return float(min(1.0, 0.5 * slope_factor + 0.5 * twi_factor))

    def predict_trigger(self, rainfall_seq: list) -> float:
        """
        Returns P(trigger | rainfall) in [0, 1].
        BUG FIX #3: Pads sequences shorter than 30 days instead of crashing.
        Falls back to antecedent rainfall heuristic if ONNX model not loaded.
        """
        # FIX #3: Handle sequences shorter than 30 days — pad with zeros on the left
        seq = list(rainfall_seq)
        if len(seq) < 30:
            seq = [0.0] * (30 - len(seq)) + seq
        seq = seq[-30:]  # Always use exactly the last 30 days

        if self.trig_session:
            # Normalize (max observed in the sequence)
            arr   = np.array(seq, dtype=np.float32)
            arr   = arr / 500.0  # Must match global 500mm norm from training
            x     = arr.reshape(1, 30, 1)
            outs  = self.trig_session.run(None, {self._onnx_input_name: x})
            return float(outs[0][0][0])

        # Fallback: antecedent rainfall heuristic
        arr           = np.array(seq)
        antecedent_7d = arr[-7:].sum()  # Last 7 days including today
        peak_3d       = arr[-3:].max()
        log_odds      = -4.5 + 0.06 * antecedent_7d + 0.10 * peak_3d
        return float(1.0 / (1.0 + np.exp(-log_odds)))

    def calculate_final_risk(self, susc_prob: float, trig_prob: float):
        """
        Delegates to the centralized fusion module (fusion.py).
        FIX #5: Now uses multiplicative AND-gate fusion from fusion.py.
        """
        final_score, risk_level = calculate_final_risk(susc_prob, trig_prob)
        reason_code = determine_reason_code(susc_prob, trig_prob)
        return final_score, risk_level, reason_code


risk_engine = RiskEngine()
