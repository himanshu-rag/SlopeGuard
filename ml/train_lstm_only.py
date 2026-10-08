"""
Fast LSTM-only trainer — runs in ~20 seconds on CPU.
XGBoost is already trained and saved. This only retrains the LSTM trigger model.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from dataset import generate_synthetic_data

os.makedirs("models", exist_ok=True)

class RainfallLSTM(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return self.sigmoid(out)

print("Generating data...")
_, rainfall_df = generate_synthetic_data(num_zones=500, num_days=30)

X = np.stack(rainfall_df['rainfall_sequence'].values).astype(np.float32)
X = X / 500.0  # Normalize to a global 500mm absolute maximum
X = X.reshape(-1, 30, 1)
y = rainfall_df['trigger_event'].values.astype(np.float32)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
X_train_t = torch.tensor(X_train)
y_train_t = torch.tensor(y_train).view(-1, 1)
X_test_t  = torch.tensor(X_test)

model     = RainfallLSTM()
criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.002)

print("Training LSTM (5 epochs)...")
for epoch in range(5):
    model.train()
    optimizer.zero_grad()
    loss = criterion(model(X_train_t), y_train_t)
    loss.backward()
    optimizer.step()
    print(f"  Epoch {epoch+1}/5  Loss: {loss.item():.4f}")

model.eval()
with torch.no_grad():
    preds = model(X_test_t).numpy().flatten()
auc = roc_auc_score(y_test, preds)
print(f"LSTM AUC: {auc:.4f}")

# Export trained model
dummy = torch.randn(1, 30, 1)
torch.onnx.export(
    model, dummy, "models/trigger_model.onnx",
    input_names=["rainfall_sequence"], output_names=["trigger_prob"],
    dynamic_axes={"rainfall_sequence": {0: "batch_size"}, "trigger_prob": {0: "batch_size"}},
    opset_version=17
)
print("✅ Saved trained ONNX → models/trigger_model.onnx")
