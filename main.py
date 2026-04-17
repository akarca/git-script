import argparse
import os
import shlex
import subprocess
import sys
import warnings

from fabric import Connection

warnings.simplefilter("ignore")

HOOK_FILENAME = "create-post-update-hook.sh"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def scp_upload(ssh_host_alias: str, local_path: str, remote_path: str) -> None:
    """Upload a file using scp -O (for servers without SFTP support)."""
    cmd = ["scp", "-O", local_path, f"{ssh_host_alias}:{remote_path}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"scp failed: {result.stderr.strip()}")


def run_remote_setup(ssh_host_alias: str, remote_path: str) -> None:
    local_hook = os.path.join(SCRIPT_DIR, HOOK_FILENAME)
    if not os.path.exists(local_hook):
        raise FileNotFoundError(f"Hook file not found: {local_hook}")

    quoted_path = shlex.quote(remote_path)
    quoted_hook = shlex.quote(HOOK_FILENAME)

    print(f"--- Connecting to {ssh_host_alias}... ---")
    c = Connection(ssh_host_alias)

    print(f"[*] Creating directory: {remote_path}")
    c.run(f"mkdir -p {quoted_path}")

    print("[*] Initializing git repo...")
    with c.cd(remote_path):
        c.run("git init .")

    print(f"[*] Uploading {HOOK_FILENAME}...")
    scp_upload(ssh_host_alias, local_hook, f"{remote_path}/{HOOK_FILENAME}")

    print("[*] Running hook script...")
    with c.cd(remote_path):
        c.run(f"chmod +x {quoted_hook}")
        c.run(f"./{quoted_hook}")
        c.run(f"rm -f {quoted_hook}")

    print("\n--- Done! ---")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Set up a remote directory as a git push target with auto-deploy.",
    )
    parser.add_argument("host", help="SSH config host alias (e.g. myserver)")
    parser.add_argument("repo_path", help="Absolute path on the remote server (e.g. /var/www/myapp)")
    args = parser.parse_args()

    try:
        run_remote_setup(args.host, args.repo_path)
    except Exception as e:
        print(f"\n[!] Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
