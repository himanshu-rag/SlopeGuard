import torch
import torch.nn as nn
import os

class RainfallLSTM(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=2):
        super(RainfallLSTM, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return self.sigmoid(out)

model = RainfallLSTM()
model.eval()

# Export to ONNX
os.makedirs("models", exist_ok=True)
dummy_input = torch.randn(1, 30, 1)
torch.onnx.export(model, dummy_input, "models/trigger_model.onnx",
                  input_names=["input"], output_names=["output"],
                  dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}})
print("Exported untrained ONNX model successfully.")
