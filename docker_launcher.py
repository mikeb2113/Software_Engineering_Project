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

def start():
    if not ensure_docker():
        sys.exit("\n❌ Docker is not installed/ready. See instructions above, then re-run this launcher.")

    if not ensure_compose_plugin():
        sys.exit("❌ Compose v2 plugin missing. On Ubuntu: sudo apt install -y docker-compose-plugin")

    # If user just got added to docker group, they might still need sudo in this session.
    # Try without sudo first; if it fails with permission, hint them.
    try:
        run(["docker", "compose", "-f", COMPOSE_FILE, "up", "-d", "--build"])
    except subprocess.CalledProcessError as e:
        print("⚠️ docker compose up failed. Trying with sudo…")
        try:
            run(["sudo", "docker", "compose", "-f", COMPOSE_FILE, "up", "-d", "--build"])
        except subprocess.CalledProcessError:
            sys.exit("❌ Could not start containers. If this is Ubuntu, log out/in after group change, then retry.")

    # Retrieve mapped host port for container port 8000
    try:
        port_cmd = ["docker", "compose", "-f", COMPOSE_FILE, "port", "app", "8000"]
        result = subprocess.run(port_cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        # Try sudo fallback
        result = subprocess.run(["sudo"] + port_cmd, capture_output=True, text=True, check=True)

    addr = result.stdout.strip() or "127.0.0.1:8000"
    host, port = addr.replace("0.0.0.0", "127.0.0.1").split(":")
    url = f"http://{host}:{port}"
    print(f"✅ App is starting… {url}")
    print("ℹ️ To stop: python docker_shutdown.py   (or)   docker compose -f Docker_Files/docker-compose.yml down")
    try:
        webbrowser.open(url)
    except Exception:
        pass

def stop():
    try:
        run(["docker", "compose", "-f", COMPOSE_FILE, "down"])
    except subprocess.CalledProcessError:
        try:
            run(["sudo", "docker", "compose", "-f", COMPOSE_FILE, "down"])
        except subprocess.CalledProcessError:
            sys.exit("❌ Failed to stop containers. You may need to ensure Docker is running.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stop":
        stop()
    else:
        start()