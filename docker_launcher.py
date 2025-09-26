import os, sys, platform, shutil, subprocess, time, webbrowser

ROOT = os.path.dirname(__file__)
CANDIDATES = [
    os.path.join(ROOT, "Docker_Files", "docker-compose.yml"),
    os.path.join(ROOT, "docker-compose.yml"),
]
COMPOSE_FILE = next((p for p in CANDIDATES if os.path.exists(p)), None)

if not COMPOSE_FILE:
    sys.exit("❌ docker-compose.yml not found (looked in Docker_Files/ and repo root).")

def have(cmd):
    return shutil.which(cmd) is not None

def run(cmd, check=True):
    return subprocess.run(cmd, check=check)

def linux_try_install():
    # Only attempt auto-install on Debian/Ubuntu-like systems with apt.
    if not have("apt"):
        return False

    print("🔧 Docker not found. Attempting Ubuntu/Debian install via apt (sudo required)…")
    try:
        run(["sudo", "apt", "update"])
        # docker engine + compose plugin (v2)
        run(["sudo", "apt", "install", "-y", "docker.io", "docker-compose-plugin"])
        run(["sudo", "systemctl", "enable", "--now", "docker"])
    except subprocess.CalledProcessError:
        print("❌ Failed to install Docker automatically with apt.")
        return False

    # Add current user to docker group (so no sudo needed)
    try:
        run(["sudo", "usermod", "-aG", "docker", os.getlogin()])
        print("ℹ️  Added you to the 'docker' group. You must log out/in (or reboot) for this to take effect.")
    except Exception:
        print("⚠️ Could not add user to 'docker' group automatically. You can run:")
        print(f"    sudo usermod -aG docker {os.getlogin()}")

    # Basic sanity check
    time.sleep(1)
    return have("docker")

def ensure_docker():
    sysname = platform.system().lower()
    if have("docker"):
        return True

    if "linux" in sysname:
        if linux_try_install():
            return True
        print("\n👉 Manual install (Ubuntu):")
        print("   sudo apt update && sudo apt install -y docker.io docker-compose-plugin")
        print("   sudo systemctl enable --now docker")
        print(f"   sudo usermod -aG docker {os.getlogin()}   # then log out/in")
        return False

    if "windows" in sysname:
        print("\n👉 Docker Desktop is required on Windows (admin & WSL2):")
        print("   winget install -e --id Docker.DockerDesktop")
        print("   (Ensure WSL2 is enabled; you may need a reboot.)")
        return False

    if "darwin" in sysname:
        print("\n👉 macOS:")
        print("   brew install --cask docker")
        print("   # Then start Docker.app once to finish setup")
        return False

    print("❌ Unsupported OS for auto-install. Please install Docker manually.")
    return False

def ensure_compose_plugin():
    # Compose v2 lives under `docker compose`
    try:
        out = subprocess.check_output(["docker", "compose", "version"], text=True)
        return "Docker Compose version" in out or "v2" in out.lower()
    except Exception:
        return False

PROJECT = "sep"  # match your manual command

def run_compose(args, use_sudo=False, **popen_kwargs):
    env = os.environ.copy()
    env["DOCKER_BUILDKIT"] = "0"  # match the working manual run
    base = (["sudo"] if use_sudo else []) + ["docker", "compose", "-f", COMPOSE_FILE, "-p", PROJECT]
    return subprocess.run(base + args, check=True, env=env, **popen_kwargs)

def start():
    if not ensure_docker():
        sys.exit("\n❌ Docker is not installed/ready...")

    if not ensure_compose_plugin():
        sys.exit("❌ Compose v2 plugin missing. On Ubuntu: sudo apt install -y docker-compose-plugin")

    # up --build (detached)
    try:
        run_compose(["up", "-d", "--build"])
    except subprocess.CalledProcessError:
        print("⚠️ docker compose up failed. Trying with sudo…")
        run_compose(["up", "-d", "--build"], use_sudo=True)

    url = "http://127.0.0.1:8000"

    # Wait up to 120s, not 30
    import urllib.request, time
    deadline = time.time() + 120
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2):
                break
        except Exception:
            time.sleep(1)

    # Optional: if not up yet, show quick diagnostics
    try:
        run_compose(["ps"])
    except Exception:
        pass

    print(f"✅ App is starting… {url}")
    print(f"ℹ️ To stop: python docker_shut_down.py   (or)   docker compose -f {COMPOSE_FILE} -p {PROJECT} down")

    try:
        webbrowser.open(url)
    except Exception:
        pass
    
def stop():
    try:
        run_compose(["down", "--remove-orphans"])
    except subprocess.CalledProcessError:
        print("⚠️ Trying with sudo…")
        run_compose(["down", "--remove-orphans"], use_sudo=True)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stop":
        stop()
    else:
        start()