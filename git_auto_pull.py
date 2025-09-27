#!/usr/bin/env python3
import os
import subprocess
import sys

# Map numbers to branch names
BRANCHES = {
    "1": "main",
    "2": "michael",
    "3": "marvin",
    "4": "saksham",
}

# Your GitHub repo URL
REPO_URL = "https://github.com/mikeb2113/Software_Engineering_Project.git"

def run(cmd, check=True):
    return subprocess.run(cmd, check=check)

def branch_exists(branch):
    """Check if a branch exists locally"""
    result = subprocess.run(
        ["git", "show-ref", "--verify", f"refs/heads/{branch}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0

def ensure_repo():
    """Ensure we are inside a git repo, or clone if not"""
    if not os.path.exists(".git"):
        print("ℹ️  No .git directory found. Initializing repository...")
        # Remove ZIP-style contents to avoid conflicts
        if os.listdir("."):
            print("⚠️ Current folder is not empty. Cloning repo into 'repo_clone' instead.")
            clone_path = os.path.join(os.getcwd(), "repo_clone")
            run(["git", "clone", REPO_URL, clone_path])
            os.chdir(clone_path)
        else:
            run(["git", "clone", REPO_URL, "."])
        print("✅ Repository initialized and connected to remote.")

def main():
    ensure_repo()

    print("Select a branch to pull from:")
    for num, name in BRANCHES.items():
        print(f" {num}. {name}")

    choice = input("Enter number (1-4): ").strip()
    if choice not in BRANCHES:
        sys.exit("❌ Invalid choice.")

    branch = BRANCHES[choice]

    try:
        # Always fetch latest info
        run(["git", "fetch", "origin"])

        if branch_exists(branch):
            run(["git", "checkout", branch])
        else:
            run(["git", "checkout", "-b", branch, f"origin/{branch}"])

        run(["git", "pull", "origin", branch])
        print(f"✅ Branch '{branch}' is now up to date with origin/{branch}.")
    except subprocess.CalledProcessError:
        sys.exit("❌ Failed to pull branch.")

if __name__ == "__main__":
    main()