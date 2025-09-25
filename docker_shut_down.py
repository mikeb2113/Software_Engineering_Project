import os, subprocess, sys

ROOT = os.path.dirname(__file__)
COMPOSE_FILE = os.path.join(ROOT, "Docker_Files", "docker-compose.yml")
if not os.path.exists(COMPOSE_FILE):
    COMPOSE_FILE = os.path.join(ROOT, "docker-compose.yml")

if not os.path.exists(COMPOSE_FILE):
    sys.exit("❌ docker-compose.yml not found.")

try:
    subprocess.run(["docker", "compose", "-f", COMPOSE_FILE, "down"], check=True)
except subprocess.CalledProcessError:
    subprocess.run(["sudo", "docker", "compose", "-f", COMPOSE_FILE, "down"], check=True)
print("✅ Docker environment stopped.")