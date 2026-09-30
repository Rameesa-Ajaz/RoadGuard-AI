"""
Traffic flow prediction using LSTM.
"""
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from pathlib import Path
import joblib
from loguru import logger
from config.settings import MODEL_DIR


class TrafficLSTM(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=2, output_size=1, dropout=0.2):
        super(TrafficLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                           batch_first=True, dropout=dropout)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        # x shape: (batch, seq_len, input_size)
        out, _ = self.lstm(x)
        # Use last time step
        out = self.fc(out[:, -1, :])
        return out


class TrafficFlowPredictor:
    def __init__(self, sequence_length=24, model_path=None):
        self.sequence_length = sequence_length
        self.scaler = MinMaxScaler()
        self.model_path = model_path or MODEL_DIR / "traffic_lstm.pt"
        self.model = TrafficLSTM()
        self._trained = False

    def predict_future(self, data, steps=12):
        """Predict future traffic flow. Returns array of predictions."""
        if not self._trained:
            logger.warning("Model not trained. Returning naive forecast.")
            return np.array([data[-1] + np.random.normal(0, 10) for _ in range(steps)])

        # Scale input
        data_scaled = self.scaler.transform(np.array(data).reshape(-1, 1))

        predictions = []
        current_seq = data_scaled[-self.sequence_length:].copy()

        self.model.eval()
        with torch.no_grad():
            for _ in range(steps):
                x = torch.FloatTensor(current_seq).unsqueeze(0)  # (1, seq_len, 1)
                pred = self.model(x).item()
                predictions.append(pred)
                # Slide window
                current_seq = np.roll(current_seq, -1)
                current_seq[-1] = pred

        # Inverse transform
        predictions = self.scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
        return predictions.flatten()

    def train(self, series, epochs=50, lr=0.001):
        """Train the LSTM on a time series."""
        # Scale
        series = np.array(series).reshape(-1, 1)
        series_scaled = self.scaler.fit_transform(series)

        # Create sequences
        X, y = [], []
        for i in range(len(series_scaled) - self.sequence_length):
            X.append(series_scaled[i:i + self.sequence_length])
            y.append(series_scaled[i + self.sequence_length])

        X = torch.FloatTensor(np.array(X))
        y = torch.FloatTensor(np.array(y))

        # Train
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)

        self.model.train()
        for epoch in range(epochs):
            optimizer.zero_grad()
            outputs = self.model(X)
            loss = criterion(outputs, y)
            loss.backward()
            optimizer.step()
            if (epoch + 1) % 10 == 0:
                logger.info(f"LSTM Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}")

        self._trained = True
        self.save()

    def save(self):
        """Save model and scaler."""
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        torch.save(self.model.state_dict(), self.model_path)
        joblib.dump(self.scaler, self.model_path.with_suffix('.scaler.pkl'))
        logger.info(f"Model saved to {self.model_path}")

    def load(self):
        """Load model and scaler."""
        if not Path(self.model_path).exists():
            raise FileNotFoundError(f"Model not found at {self.model_path}. Train first.")
        self.model.load_state_dict(torch.load(self.model_path))
        self.scaler = joblib.load(self.model_path.with_suffix('.scaler.pkl'))
        self._trained = True
        logger.info(f"Model loaded from {self.model_path}")
