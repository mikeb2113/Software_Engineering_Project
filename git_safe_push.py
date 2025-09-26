#!/usr/bin/env python3
import argparse
import datetime as dt
import getpass
import os
import subprocess
import sys

PROTECTED = {"main", "master", "develop"}  # add more if you’d like

def run(cmd, check=True, capture=False):
    if capture:
        return subprocess.check_output(cmd, text=True).strip()
    return subprocess.run(cmd, check=check)

def ensure_repo():
    try:
        run(["git", "rev-parse", "--is-inside-work-tree"])
    except subprocess.CalledProcessError:
        sys.exit("❌ Not inside a git repository.")

def current_branch():
    return run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture=True)

def have_remote(remote="origin"):
    try:
        run(["git", "remote", "get-url", remote])
        return True
    except subprocess.CalledProcessError:
        return False

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
    parser.add_argument("--branch", "-b", help="Branch name to use (create if needed).")
    parser.add_argument("--allow-protected", action="store_true",
                        help="Allow pushing to protected branches (not recommended).")
    parser.add_argument("--pull", action="store_true",
                        help="Fetch & rebase onto origin/<branch> before pushing.")
    args = parser.parse_args()

    ensure_repo()

    if not have_remote("origin"):
        sys.exit("❌ No 'origin' remote found. Set it with:\n   git remote add origin <URL>")

    # Determine target branch
    if args.branch:
        target = args.branch
        checkout_or_create(target)
    else:
        curr = current_branch()
        if curr in ("HEAD", ""):
            # Detached HEAD: make a new branch
            uname = getpass.getuser() or "user"
            stamp = dt.datetime.now().strftime("%Y-%m-%d-%H%M")
            target = f"{uname}/{stamp}"
            checkout_or_create(target)
            print(f"ℹ️  Detached HEAD: created and switched to '{target}'.")
        else:
            target = curr

    # Block protected branches unless explicitly allowed
    if (target in PROTECTED) and not args.allow_protected:
        sys.exit(
            f"⛔ Branch '{target}' is protected. "
            f"Use --branch <name> (e.g., '{getpass.getuser()}/feature-x') or pass --allow-protected if you really mean it."
        )

    # Stage & commit
    try:
        run(["git", "add", "-A"])
        msg = " ".join(args.message) if args.message else f"Auto-commit {dt.datetime.now().isoformat(timespec='seconds')}"
        # `git commit` exits non-zero if there's nothing to commit
        subprocess.run(["git", "commit", "-m", msg], check=True)
        print(f"✅ Commit created: {msg}")
    except subprocess.CalledProcessError:
        print("ℹ️ Nothing to commit (working tree clean).")

    # Optional fetch/rebase for a cleaner history
    if args.pull:
        run(["git", "fetch", "origin"])
        try:
            run(["git", "rebase", f"origin/{target}"])
            print(f"✅ Rebased onto origin/{target}")
        except subprocess.CalledProcessError:
            print("⚠️ Rebase had conflicts or failed. Resolve and run the script again, or push without --pull.")
            sys.exit(1)

    # Push (set upstream if first time)
    try:
        if upstream_is_set():
            run(["git", "push", "origin", target])
        else:
            run(["git", "push", "-u", "origin", target])
        print(f"🚀 Pushed '{target}' to origin.")
    except subprocess.CalledProcessError:
        sys.exit("❌ Push failed. Check remote permissions/connection.")

if __name__ == "__main__":
    main()