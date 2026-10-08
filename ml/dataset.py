import pandas as pd
import numpy as np

def generate_synthetic_data(num_zones=500, num_days=30):
    """
    BUG FIX #4 & #6:
    - Old: Label was a perfect boolean oracle (slope > 30 AND twi > 6).
           XGBoost just memorized the rule, not learned real patterns.
    - New: Labels derived from a probabilistic logistic model, injecting
           realistic noise that mirrors real-world uncertainty.
    - Old: LSTM trigger was a hard threshold (last 3 days > 40mm).
    - New: Uses antecedent moisture + peak intensity to mirror the
           real physics of debris-flow initiation.
    """
    print(f"Generating realistic synthetic data for {num_zones} zones over {num_days} days...")

    rng = np.random.default_rng(42)  # Reproducible seed

    # --- TERRAIN DATA ---
    slope = rng.uniform(5, 65, num_zones)
    aspect = rng.uniform(0, 360, num_zones)
    curvature = rng.normal(0, 0.8, num_zones)
    twi = rng.uniform(2, 12, num_zones)

    terrain = pd.DataFrame({
        'zone_id': range(1, num_zones + 1),
        'slope_deg': slope,
        'aspect_deg': aspect,
        'curvature': curvature,
        'twi': twi,
    })

    # FIX #4: Probabilistic label via logistic function — not a hard boolean.
    # Geotechnical basis: slope angle and wetness are the two dominant factors.
    # South-facing slopes (aspect ~180°) are drier → lower risk.
    south_facing_penalty = np.cos(np.radians(aspect - 180)) * 0.3

    log_odds = (
        -7.0                          # Baseline (most terrain is stable)
        + 0.12 * slope                # Steeper = more risk
        + 0.35 * twi                  # Higher wetness index = more risk
        - 0.5 * curvature             # Convex slopes shed water (negative curvature = concave = collects water)
        + south_facing_penalty        # South-facing slopes less risky in Indian context
    )
    landslide_prob = 1.0 / (1.0 + np.exp(-log_odds))
    terrain['historical_landslide'] = rng.binomial(1, landslide_prob)

    print(f"  Terrain label balance: {terrain['historical_landslide'].mean():.1%} positive (landslide) zones")

    # --- RAINFALL / TRIGGER DATA ---
    rainfall_data = []
    for zone in range(1, num_zones + 1):
        # Realistic rainfall: exponential distribution with occasional extreme events
        base_rain = rng.exponential(scale=4.5, size=num_days)
        # Occasionally inject a heavy-rainfall event (monsoon burst)
        if rng.random() < 0.3:
            burst_day = rng.integers(num_days - 5, num_days)
            base_rain[burst_day:burst_day + 3] += rng.uniform(20, 60, min(3, num_days - burst_day))

        rain_seq = np.clip(base_rain, 0, None)

        # FIX #6: Trigger uses antecedent moisture + peak intensity.
        # Physics basis: saturated soil + intense event = debris flow.
        antecedent_7day = rain_seq[-7:].sum()   # Last 7 days (not including today)
        peak_intensity = rain_seq[-3:].max()       # Max daily rain in last 3 days

        # Probabilistic trigger — not a hard threshold
        trig_log_odds = -4.5 + 0.06 * antecedent_7day + 0.10 * peak_intensity
        trig_prob = 1.0 / (1.0 + np.exp(-trig_log_odds))
        trigger = int(rng.random() < trig_prob)

        rainfall_data.append({
            'zone_id': zone,
            'rainfall_sequence': rain_seq,
            'trigger_event': trigger
        })

    rainfall_df = pd.DataFrame(rainfall_data)
    print(f"  Rainfall label balance: {rainfall_df['trigger_event'].mean():.1%} trigger events")

    return terrain, rainfall_df
