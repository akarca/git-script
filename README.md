# git-script

Turns an empty directory on a remote server into a `git push` deploy target. Once set up, running `git push myserver main` from your local machine automatically pulls the code into the server directory and updates the working tree.

## What it does

On the given SSH host:

1. Creates the target directory (`mkdir -p`).
2. Runs `git init` inside it.
3. Uploads `create-post-update-hook.sh`, executes it, and cleans up. The hook:
   - Writes `.git/hooks/post-update`, which updates the working tree via `git reset --hard HEAD` after each push and auto-stashes any dirty changes.
   - Sets `git config receive.denyCurrentBranch ignore` so pushes to a non-bare repo are accepted.

Result: the remote directory behaves like a deploy-on-push git remote.

## Requirements

```bash
pip install fabric
```

`scp` must also be available on your PATH (standard on macOS/Linux).

The target host must be defined in your SSH config (`~/.ssh/config`):

```
Host myserver
    HostName example.com
    User deploy
    IdentityFile ~/.ssh/id_ed25519
```

## Usage

```bash
python main.py <host> <repo_path>
```

Examples:

```bash
python main.py myserver /var/www/myapp
python main.py staging /home/deploy/api
```

Each command:
- connects to the given host over SSH,
- creates the directory and initializes it as a git repo,
- installs the post-update hook.

## Adding the remote locally

After the script runs, inside the project you want to deploy:

```bash
git remote add myserver ssh://deploy@example.com/var/www/myapp
git push myserver main
```

After the push, the code running in `/var/www/myapp` on the server is updated automatically.
