import os, subprocess, sys

ROOT = os.path.dirname(__file__)
CANDIDATES = [
    os.path.join(ROOT, "Docker_Files", "docker-compose.yml"),
    os.path.join(ROOT, "docker-compose.yml"),
]
COMPOSE_FILE = next((p for p in CANDIDATES if os.path.exists(p)), None)

if not COMPOSE_FILE:
    sys.exit("❌ docker-compose.yml not found (looked in Docker_Files/ and repo root).")

PROJECT = "sep"  # must match the project name you used in `up`

def run_compose(args, use_sudo=False):
    base = (["sudo"] if use_sudo else []) + [
        "docker", "compose", "-f", COMPOSE_FILE, "-p", PROJECT
    ]
    return subprocess.run(base + args, check=True)

try:
    run_compose(["down", "--remove-orphans"])
except subprocess.CalledProcessError:
    print("⚠️  Trying with sudo…")
    run_compose(["down", "--remove-orphans"], use_sudo=True)

print("✅ Docker environment stopped.")