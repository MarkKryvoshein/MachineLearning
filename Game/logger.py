import numpy as np
import csv
import os

class LoggerRL:
    def __init__(self, q_dir="models/q_tables", log_file="logs/training.csv"):
        self.q_dir = q_dir
        self.log_file = log_file

        os.makedirs("logs", exist_ok=True)
        os.makedirs(q_dir, exist_ok=True)

        if not os.path.exists(log_file):
            with open(log_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["episode", "reward", "steps", "success"])

    def log_episode(self, episode, reward, steps, success):
        with open(self.log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([episode, reward, steps, success])

    def save_q_table(self, q_table):
        q_dict = dict(q_table)
        np.savez_compressed(f"{self.q_dir}/q_table.npz", q_table=q_dict)
