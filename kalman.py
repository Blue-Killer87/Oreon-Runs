import numpy as np

class KalmanFilter:
    def __init__(self, initial_state_mean, initial_state_covariance, transition_matrix, observation_matrix, observation_covariance, process_covariance):
        self.state_mean = initial_state_mean
        self.state_covariance = initial_state_covariance
        self.transition_matrix = transition_matrix
        self.observation_matrix = observation_matrix
        self.observation_covariance = observation_covariance
        self.process_covariance = process_covariance

    def predict(self):
        # Předpověd dalšího stavu
        self.state_mean = np.dot(self.transition_matrix, self.state_mean)
        self.state_covariance = np.dot(self.transition_matrix, np.dot(self.state_covariance, self.transition_matrix.T)) + self.process_covariance

    def update(self, observation):
        # Updatuj na základě pozorování
        innovation = observation - np.dot(self.observation_matrix, self.state_mean)
        innovation_covariance = np.dot(self.observation_matrix, np.dot(self.state_covariance, self.observation_matrix.T)) + self.observation_covariance
        kalman_gain = np.dot(self.state_covariance, np.dot(self.observation_matrix.T, np.linalg.inv(innovation_covariance)))
        self.state_mean = self.state_mean + np.dot(kalman_gain, innovation)
        self.state_covariance = self.state_covariance - np.dot(kalman_gain, np.dot(self.observation_matrix, self.state_covariance))

class KalmanSmoother:
    def __init__(self, initial_state_mean, initial_state_covariance, transition_matrix, observation_matrix, observation_covariance, process_covariance):
        self.filter = KalmanFilter(initial_state_mean, initial_state_covariance, transition_matrix, observation_matrix, observation_covariance, process_covariance)

    def smooth(self, observations):
        smoothed_states = []

        for observation in observations:
            self.filter.predict()
            self.filter.update(observation)

        for observation in reversed(observations):
            smoothed_states.append(self.filter.state_mean)
            kalman_gain = np.dot(self.filter.state_covariance, np.dot(self.filter.transition_matrix.T, np.linalg.inv(self.filter.state_covariance)))
            self.filter.state_mean = self.filter.state_mean + np.dot(kalman_gain, smoothed_states[-1] - np.dot(self.filter.transition_matrix, self.filter.state_mean))

        return list(reversed(smoothed_states))
