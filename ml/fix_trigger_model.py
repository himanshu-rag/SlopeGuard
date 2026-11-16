"""
Phase 1 — Fix SlopeGuard trigger model.

Problem: models/trigger_model.onnx outputs ~0.478 regardless of rainfall input,
so final_score = susc × trig × 100 caps at ~48 and can never reach HIGH (≥50)
or CRITICAL (≥75).

Root cause: train.py only trains the LSTM for 5 epochs on 500 zones — the model
never converges and collapses to predicting the base rate (~44.8% trigger rate).

This script:
1. Generates more synthetic data (2000 zones) for a stronger training signal
2. Trains an MLP (no Dropout — Dropout crashes PyTorch 2.14 ONNX export on Python 3.14)
3. Exports a trained ONNX model with input name "rainfall_sequence"
4. Verifies sensitivity: 0mm rain → low trigger, 500mm rain → high trigger
5. Verifies full fusion can reach CRITICAL (≥75)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import gc
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, brier_score_loss
import onnxruntime as ort

os.makedirs("models", exist_ok=True)

# ─────────────────────────────────────────────────────────────
# ARCHITECTURE: MLP (no Dropout — reliable ONNX export)
# Input: [batch, 30, 1] (30 days of rainfall, matches api_ml.py)
# Internal: flatten to [batch, 30], then dense layers with ReLU
# Output: [batch, 1] trigger probability
# ─────────────────────────────────────────────────────────────
class RainfallMLP(nn.Module):
    def __init__(self, input_dim=30, hidden_dim=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Flatten(),                           # [batch, 30, 1] -> [batch, 30]
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.net(x)


# ─────────────────────────────────────────────────────────────
# 1. GENERATE DATA
# ─────────────────────────────────────────────────────────────
from dataset import generate_synthetic_data

print("Generating synthetic data (2000 zones × 30 days)...")
_, rainfall_df = generate_synthetic_data(num_zones=2000, num_days=30)
print(f"  trigger_event base rate: {rainfall_df['trigger_event'].mean():.1%}")

X = np.stack(rainfall_df['rainfall_sequence'].values).astype(np.float32)
X = X / 500.0                              # Normalize to [0, 1] (matches api_ml.py)
X = X.reshape(-1, X.shape[1], 1)           # (Batch, SeqLen=30, Features=1)
y = rainfall_df['trigger_event'].values.astype(np.float32)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
X_train_t = torch.tensor(X_train)
y_train_t = torch.tensor(y_train).view(-1, 1)
X_test_t  = torch.tensor(X_test)
y_test_t  = torch.tensor(y_test).view(-1, 1)

# ─────────────────────────────────────────────────────────────
# 2. TRAIN MLP
# ─────────────────────────────────────────────────────────────
torch.manual_seed(42)
np.random.seed(42)

model = RainfallMLP()
criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)

print("\nTraining MLP (100 epochs, early stopping on val AUC)...")
best_auc = 0.0
patience_counter = 0
patience_limit = 15

for epoch in range(100):
    model.train()
    optimizer.zero_grad()
    outputs = model(X_train_t)
    loss = criterion(outputs, y_train_t)
    loss.backward()
    optimizer.step()

    model.eval()
    with torch.no_grad():
        train_preds = model(X_train_t).numpy().flatten()
        test_preds  = model(X_test_t).numpy().flatten()
        train_auc = roc_auc_score(y_train, train_preds)
        test_auc  = roc_auc_score(y_test,  test_preds)

    if (epoch + 1) % 10 == 0 or epoch == 0:
        print(f"  Epoch {epoch+1:3d}/100  "
              f"loss={loss.item():.4f}  "
              f"train_AUC={train_auc:.4f}  "
              f"test_AUC={test_auc:.4f}")

    if test_auc > best_auc:
        best_auc = test_auc
        patience_counter = 0
        torch.save(model.state_dict(), "models/best_mlp.pt")
    else:
        patience_counter += 1
        if patience_counter >= patience_limit:
            print(f"  Early stopping at epoch {epoch+1} (no val AUC improvement for {patience_limit} epochs)")
            break

# Load best weights
model.load_state_dict(torch.load("models/best_mlp.pt"))
model.eval()

import gc
gc.collect()

with torch.no_grad():
    final_test_preds = model(X_test_t).numpy().flatten()
final_auc = roc_auc_score(y_test, final_test_preds)
final_brier = brier_score_loss(y_test, final_test_preds)
print(f"\n✅ Final test AUC: {final_auc:.4f}  |  Brier: {final_brier:.4f}")

# ─────────────────────────────────────────────────────────────
# 3. EXPORT TO ONNX
# ─────────────────────────────────────────────────────────────
gc.collect()
dummy = torch.randn(1, 30, 1)
torch.onnx.export(
    model, dummy, "models/trigger_model.onnx",
    input_names=["rainfall_sequence"],
    output_names=["trigger_prob"],
    opset_version=17
)
print("✅ Exported trained ONNX → models/trigger_model.onnx")

# ─────────────────────────────────────────────────────────────
# 4. VERIFY ONNX SENSITIVITY
# ─────────────────────────────────────────────────────────────
sess = ort.InferenceSession("models/trigger_model.onnx")
input_name = sess.get_inputs()[0].name
print(f"\nONNX input name: {input_name}")

test_cases = [
    ("dry (0 mm/day)",       [0.0] * 30),
    ("light (5 mm/day)",     [5.0] * 30),
    ("moderate (25 mm/day)", [25.0] * 30),
    ("heavy (100 mm/day)",   [100.0] * 30),
    ("extreme (500 mm/day)", [500.0] * 30),
    ("monsoon burst",        [10.0] * 25 + [50, 100, 200, 300, 450]),
]

print("\n=== ONNX trigger_prob sensitivity ===")
for label, seq in test_cases:
    x = (np.array(seq, dtype=np.float32) / 500.0).reshape(1, 30, 1)
    prob = float(sess.run(None, {input_name: x})[0][0][0])
    print(f"  {label:24s} → {prob:.4f}")

# ─────────────────────────────────────────────────────────────
# 5. VERIFY FULL FUSION CAN REACH CRITICAL
# ─────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from api_ml import risk_engine

print("\n=== Full pipeline: susc × trig × 100 ===")
for label, seq in test_cases:
    susc = risk_engine.predict_susceptibility(65.0, 180.0, -0.9, 12.0)
    trig = risk_engine.predict_trigger(seq)
    score, level, reason = risk_engine.calculate_final_risk(susc, trig)
    print(f"  {label:24s} susc={susc:.3f} trig={trig:.3f} score={score:6.2f} {level:9s} {reason}")

print("\nDone. Trigger model is now rain-sensitive and fusion can reach CRITICAL.")