#!/usr/bin/env python3
import os, subprocess, sys

BRANCHES = {"1":"main","2":"michael","3":"marvin","4":"saksham"}
REPO_URL = "https://github.com/mikeb2113/Software_Engineering_Project.git"

def run(cmd, check=True, quiet=False):
    stdout = subprocess.DEVNULL if quiet else None
    stderr = subprocess.DEVNULL if quiet else None
    return subprocess.run(cmd, check=check, stdout=stdout, stderr=stderr)

def ensure_repo():
    """Ensure we're inside a usable git clone; clone or wire up remote if needed."""
    if not os.path.exists(".git"):
        print("ℹ️  No .git found. Initializing by cloning…")
        if os.listdir("."):
            print("⚠️ Folder not empty. Cloning into 'repo_clone/' and switching there.")
            clone_path = os.path.join(os.getcwd(), "repo_clone")
            run(["git", "clone", REPO_URL, clone_path])
            os.chdir(clone_path)
        else:
            run(["git", "clone", REPO_URL, "."])
        print("✅ Repository initialized.")
    else:
        # If .git exists (e.g., from a prior `git init`), ensure we have an origin.
        has_origin = run(["git", "remote", "get-url", "origin"], check=False, quiet=True).returncode == 0
        if not has_origin:
            print("ℹ️  No 'origin' remote. Wiring it up…")
            run(["git", "remote", "add", "origin", REPO_URL])
    # Always make sure we have the latest references
    run(["git", "fetch", "origin"])

def main():
    ensure_repo()

    print("Select a branch to pull from:")
    for n, b in BRANCHES.items():
        print(f" {n}. {b}")
    choice = input("Enter number (1–4): ").strip()
    branch = BRANCHES.get(choice)
    if not branch:
        sys.exit("❌ Invalid choice.")

    try:
        # Force local branch to point at the exact remote tip (creates it if missing)
        # and set upstream in one shot.
        run(["git", "checkout", "-B", branch, f"origin/{branch}"])
        # Pull in case there are new commits since fetch (fast and idempotent)
        run(["git", "pull", "--ff-only", "origin", branch])
        print(f"✅ '{branch}' now matches origin/{branch}.")
    except subprocess.CalledProcessError:
        sys.exit("❌ Failed to sync branch. Check network/permissions.")

if __name__ == "__main__":
    main()