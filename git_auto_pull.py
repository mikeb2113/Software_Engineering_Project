#!/usr/bin/env python3
import subprocess
import sys

# Map numbers to branch names
BRANCHES = {
    "1": "main",
    "2": "michael",
    "3": "marvin",
    "4": "saksham",
}

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

def main():
    print("Select a branch to pull from:")
    for num, name in BRANCHES.items():
        print(f" {num}. {name}")

    choice = input("Enter number (1-4): ").strip()
    if choice not in BRANCHES:
        sys.exit("❌ Invalid choice.")

    branch = BRANCHES[choice]

    try:
        # Always fetch latest info from remote
        run(["git", "fetch", "origin"])

        if branch_exists(branch):
            # Branch already exists locally → just switch
            run(["git", "checkout", branch])
        else:
            # Branch missing locally → create it tracking remote
            run(["git", "checkout", "-b", branch, f"origin/{branch}"])

        # Pull latest updates into the branch
        run(["git", "pull", "origin", branch])
        print(f"✅ Branch '{branch}' is now up to date with origin/{branch}.")
    except subprocess.CalledProcessError:
        sys.exit("❌ Failed to pull branch.")

if __name__ == "__main__":
    main()