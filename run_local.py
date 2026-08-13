import os
import sys
import time
import subprocess

# Set environment variables for local non-Docker routing
os.environ["USER_SERVICE_URL"] = "http://localhost:8001"
os.environ["TRIP_SERVICE_URL"] = "http://localhost:8002"
os.environ["RECOMMENDATION_SERVICE_URL"] = "http://localhost:8003"
os.environ["AI_SERVICE_URL"] = "http://localhost:8004"
os.environ["PREDICTION_SERVICE_URL"] = "http://localhost:8005"
os.environ["NOTIFICATION_SERVICE_URL"] = "http://localhost:8006"
os.environ["DATABASE_URL"] = "sqlite:///./travelmind.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["DEMO_MODE"] = "false"

root_dir = os.path.abspath(os.path.dirname(__file__))

services = [
    ("User Service", [sys.executable, "services/user-service/app/main.py"]),
    ("Trip Service", [sys.executable, "services/trip-service/app/main.py"]),
    ("Recommendation Service", [sys.executable, "services/recommendation-service/app/main.py"]),
    ("AI Service", [sys.executable, "services/ai-service/app/main.py"]),
    ("Prediction Service", [sys.executable, "services/prediction-service/app/main.py"]),
    ("Notification Service", [sys.executable, "services/notification-service/app/main.py"]),
    ("API Gateway", [sys.executable, "gateway/app/main.py"]),
]

processes = []

print("Starting TravelMind AI Local Microservices...")

for name, cmd in services:
    print(f"Starting {name}...")
    p = subprocess.Popen(cmd, cwd=root_dir, env=os.environ.copy())
    processes.append((name, p))
    time.sleep(1)

print("\nAll microservices and API Gateway are running!")
print("API Gateway Health Check: http://localhost:8000/health")

try:
    for name, p in processes:
        p.wait()
except KeyboardInterrupt:
    print("\nStopping all microservices...")
    for name, p in processes:
        p.terminate()
