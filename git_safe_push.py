#!/usr/bin/env python3
import argparse
import datetime as dt
import getpass
import os
import subprocess
import sys

PROTECTED = {"main", "master", "develop"}  # protected branches

def run(cmd, check=True, quiet=False):
    stdout = subprocess.DEVNULL if quiet else None
    stderr = subprocess.DEVNULL if quiet else None
    return subprocess.run(cmd, check=check, stdout=stdout, stderr=stderr)

def ensure_repo():
    try:
        run(["git", "rev-parse", "--is-inside-work-tree"])
    except subprocess.CalledProcessError:
        sys.exit("❌ Not inside a git repository.")

def branch_exists_local(name):
    try:
        run(["git", "show-ref", "--verify", f"refs/heads/{name}"])
        return True
    except subprocess.CalledProcessError:
        return False

def checkout_or_create(branch):
    if branch_exists_local(branch):
        run(["git", "checkout", branch])
    else:
        run(["git", "checkout", "-b", branch])

def upstream_is_set():
    try:
        run(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    parser = argparse.ArgumentParser(description="Safe push to personal branches.")
    parser.add_argument("message", nargs="*", help="Commit message (optional).")
    parser.add_argument("--pull", action="store_true",
                        help="Fetch & rebase onto origin/<branch> before pushing.")
    args = parser.parse_args()

    ensure_repo()

    # Prompt for user name
    username = input("Enter your name: ").strip().lower()
    if not username:
        sys.exit("❌ Name cannot be empty.")
    target = username

    # Block protected names just in case
    if target in PROTECTED:
        sys.exit(f"⛔ '{target}' is a protected branch name. Please choose another.")

    # Switch to/create the branch
    checkout_or_create(target)

    # Stage & commit
    try:
        run(["git", "add", "-A"])
        msg = " ".join(args.message) if args.message else f"Auto-commit {dt.datetime.now().isoformat(timespec='seconds')}"
        subprocess.run(["git", "commit", "-m", msg], check=True)
        print(f"✅ Commit created: {msg}")
    except subprocess.CalledProcessError:
        print("ℹ️ Nothing to commit (working tree clean).")

    # Optional rebase
    if args.pull:
        run(["git", "fetch", "origin"])
        try:
            run(["git", "rebase", f"origin/{target}"])
            print(f"✅ Rebased onto origin/{target}")
        except subprocess.CalledProcessError:
            print("⚠️ Rebase had conflicts or failed. Resolve and retry.")
            sys.exit(1)

    # Push
    try:
        if upstream_is_set():
            run(["git", "push", "origin", target])
        else:
            run(["git", "push", "-u", "origin", target])
        print(f"🚀 Pushed branch '{target}' to origin.")
    except subprocess.CalledProcessError:
        sys.exit("❌ Push failed. Check remote permissions/connection.")

if __name__ == "__main__":
    main()