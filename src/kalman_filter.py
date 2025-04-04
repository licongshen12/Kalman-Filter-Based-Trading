# src/kalman_filter.py

import numpy as np

# === Standard Kalman Filter ===
class KalmanFilter:
    def __init__(self, delta=1e-2, R=0.001):
        self.delta = delta  # Process noise scaling factor
        self.R = R          # Observation noise
        self.reset()

    def reset(self):
        self.beta = np.zeros(2)  # [intercept, hedge ratio]
        self.P = np.eye(2)       # Covariance matrix
        self.Vw = self.delta / (1 - self.delta) * np.eye(2)  # Process noise covariance
        self.Ve = self.R                                     # Measurement noise

    def update(self, y, x):
        x_vec = np.array([1.0, x])  # [intercept, x_t]

        # prediction
        y_hat = np.dot(self.beta, x_vec)
        e = y - y_hat  # error

        # Kalman gain
        P_x = np.dot(self.P, x_vec)
        K = P_x / (np.dot(x_vec, P_x) + self.Ve)

        # update beta
        self.beta += K * e

        # update covariance
        self.P = self.P - np.outer(K, np.dot(x_vec, self.P)) + self.R

        return y_hat, e


# === Rolling Kalman Filter ===
class RollingKalmanFilter:
    def __init__(self, window=500, delta=1e-5, R=0.001):
        self.window = window  # Number of steps before resetting
        self.delta = delta
        self.R = R
        self.reset()

    def reset(self):
        self.beta = np.zeros(2)
        self.P = np.eye(2)
        self.Vw = self.delta / (1 - self.delta) * np.eye(2)
        self.Ve = self.R
        self.spread_history = []  # To track spread size over time

    def update(self, y, x):
        x_vec = np.asarray([1.0, x])

        # Predict
        self.P = self.P + self.Vw
        yhat = np.dot(self.beta, x_vec)
        e = y - yhat

        # Update
        S = np.dot(np.dot(x_vec, self.P), x_vec.T) + self.Ve
        K = np.dot(self.P, x_vec.T) / S
        self.beta = self.beta + K * e
        self.P = self.P - np.outer(K, np.dot(x_vec, self.P))

        # Manage window
        self.spread_history.append(e)
        if len(self.spread_history) > self.window:
            self.reset()

        return yhat, e
