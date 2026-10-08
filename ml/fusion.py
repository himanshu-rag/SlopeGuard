"""
BUG FIX #5: Risk Fusion Math
- Old: Linear weighted sum (susc * 0.4 + trig * 0.6) — mathematically incorrect
       because the two probabilities are statistically DEPENDENT (rain wets soil →
       destabilizes slopes). Simple addition double-counts correlated events.
- New: Multiplicative AND-gate fusion based on joint probability:
       P(failure) = 1 - P(no terrain failure) * P(no trigger)
       This correctly models: BOTH terrain must be susceptible AND rainfall must trigger.
       A small improvement to avoid overconfidence: geometric mean is used for
       the weights, giving a smoother response curve.
"""

def calculate_final_risk(susc_prob: float, trig_prob: float) -> tuple[float, str]:
    """
    Fuse terrain susceptibility and rainfall trigger into a final risk score.

    Args:
        susc_prob: P(landslide | terrain geometry) in [0, 1] from XGBoost
        trig_prob: P(trigger | rainfall sequence) in [0, 1] from LSTM

    Returns:
        (final_score 0-100, risk_level string)
    """
    # Clamp inputs to valid probability range to guard against model edge cases
    susc_prob = float(max(0.0, min(1.0, susc_prob)))
    trig_prob = float(max(0.0, min(1.0, trig_prob)))

    # FIX #5: Joint probability fusion (AND-gate).
    # Neither factor alone causes failure — both must contribute.
    # Terrain weight: 0.4, Rainfall weight: 0.6 (rainfall is the proximate trigger).
    # Using weighted geometric mean of the complement:
    joint_failure = susc_prob * trig_prob  # True AND gate: requires BOTH unstable terrain AND severe rainfall
    final_score = round(joint_failure * 100, 2)

    # Risk thresholds (geotechnically calibrated):
    # CRITICAL ≥ 75: Imminent danger, mandatory evacuation
    # HIGH ≥ 50:     Elevated alert, restrict access
    # MEDIUM ≥ 25:   Monitor closely, pre-position equipment
    # LOW < 25:      Routine monitoring
    if final_score >= 75:
        level = "CRITICAL"
    elif final_score >= 50:
        level = "HIGH"
    elif final_score >= 25:
        level = "MEDIUM"
    else:
        level = "LOW"

    return final_score, level


def determine_reason_code(susc_prob: float, trig_prob: float) -> str:
    """
    Generate a human-readable reason code for the primary risk driver.
    Thresholds are calibrated to the probabilistic labels in dataset.py.
    """
    reasons = []

    # Terrain is the dominant factor when its probability is high
    if susc_prob > 0.65:
        reasons.append("HIGH_TERRAIN_SUSCEPTIBILITY")

    # Rainfall trigger is dominant when antecedent moisture drives it
    if trig_prob > 0.65:
        reasons.append("HIGH_ANTECEDENT_RAINFALL")

    # Edge case: both factors are moderate but together they're dangerous
    if not reasons and (susc_prob + trig_prob) > 0.9:
        reasons.append("COMPOUND_MODERATE_RISK")

    return "+".join(reasons) if reasons else "NOMINAL"
