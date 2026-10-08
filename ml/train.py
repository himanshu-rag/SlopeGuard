"""
BUG FIX #1, #2:
- Old: Model was exported UNTRAINED (random weights → random predictions).
- Old: Input name was "input" in exporter, "rainfall_sequence" in train.py → mismatch.
- New: Trains the LSTM properly on synthetic data, then exports the trained model.
- New: Standardized input name is "rainfall_sequence" everywhere.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import pandas as pd
import xgboost as xgb
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import roc_auc_score, brier_score_loss
from sklearn.calibration import CalibratedClassifierCV
import joblib
from dataset import generate_synthetic_data

os.makedirs("models", exist_ok=True)

# ─────────────────────────────────────────────────────────────
# ARCHITECTURE (must match api_ml.py and export exactly)
# ─────────────────────────────────────────────────────────────
class RainfallLSTM(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size, hidden_size, num_layers,
            batch_first=True, dropout=0.2
        )
        self.fc = nn.Linear(hidden_size, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])   # Take last time-step hidden state
        return self.sigmoid(out)


# ─────────────────────────────────────────────────────────────
# 1. SUSCEPTIBILITY MODEL (XGBoost + Platt Scaling)
# ─────────────────────────────────────────────────────────────
def train_susceptibility_model(terrain_df):
    print("\n── Training XGBoost Susceptibility Model ──")
    features = ['slope_deg', 'aspect_deg', 'curvature', 'twi']
    X = terrain_df[features].values
    y = terrain_df['historical_landslide'].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    base_clf = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective='binary:logistic',
        eval_metric='auc',
        random_state=42,
    )

    # Platt scaling calibration over 5-fold CV
    clf = CalibratedClassifierCV(base_clf, method='sigmoid', cv=5)
    clf.fit(X_train, y_train)

    preds = clf.predict_proba(X_test)[:, 1]
    auc   = roc_auc_score(y_test, preds)
    brier = brier_score_loss(y_test, preds)
    print(f"  AUC: {auc:.4f}  |  Brier Score: {brier:.4f}")

    joblib.dump(clf, 'models/susceptibility_model.pkl')
    print("  Saved → models/susceptibility_model.pkl")
    return clf


# ─────────────────────────────────────────────────────────────
# 2. TRIGGER MODEL (PyTorch LSTM → ONNX)
# ─────────────────────────────────────────────────────────────
def train_trigger_model(rainfall_df):
    print("\n── Training PyTorch LSTM Trigger Model ──")

    X = np.stack(rainfall_df['rainfall_sequence'].values).astype(np.float32)
    # Normalize by max observed rainfall to keep values in [0, 1]
    X = X / 500.0  # Normalize by global max 500mm to match api_ml.py
    X = X.reshape(-1, X.shape[1], 1)   # (Batch, SeqLen=30, Features=1)
    y = rainfall_df['trigger_event'].values.astype(np.float32)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    X_train_t = torch.tensor(X_train)
    y_train_t = torch.tensor(y_train).view(-1, 1)
    X_test_t  = torch.tensor(X_test)

    model     = RainfallLSTM()
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)

    print("  Training for 5 epochs (CPU-optimized)...")
    for epoch in range(5):
        model.train()
        optimizer.zero_grad()
        outputs = model(X_train_t)
        loss    = criterion(outputs, y_train_t)
        loss.backward()
        optimizer.step()
        scheduler.step()
        if (epoch + 1) % 1 == 0:
            print(f"    Epoch {epoch+1}/30  Loss: {loss.item():.4f}")

    model.eval()
    with torch.no_grad():
        test_preds = model(X_test_t).numpy().flatten()

    auc = roc_auc_score(y_test, test_preds)
    print(f"  AUC: {auc:.4f}")

    # FIX #1 + #2: Export TRAINED model, standardized input name = "rainfall_sequence"
    dummy = torch.randn(1, 30, 1)
    torch.onnx.export(
        model, dummy, "models/trigger_model.onnx",
        input_names=["rainfall_sequence"],    # FIX #2: Matches api_ml.py exactly
        output_names=["trigger_prob"],
        dynamic_axes={
            "rainfall_sequence": {0: "batch_size"},
            "trigger_prob":      {0: "batch_size"}
        },
        opset_version=17
    )
    print("  Saved TRAINED ONNX → models/trigger_model.onnx")
    return model


if __name__ == "__main__":
    terrain_df, rainfall_df = generate_synthetic_data(num_zones=500, num_days=30)
    train_susceptibility_model(terrain_df)
    train_trigger_model(rainfall_df)
    print("\n✅ All models trained and exported successfully.")
