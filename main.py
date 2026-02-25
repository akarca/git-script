import sys

from fabric import task

if not sys.warnoptions:
    import warnings

    warnings.simplefilter("ignore")


def my_wrapper_function():
    hosts = [sys.argv[1]]

    def work(c):
        repo_path = sys.argv[2]
        c.run("mkdir -p %s" % repo_path)
        c.put("create-post-update-hook.sh", remote=repo_path)
        c.run("chmod +x %s/create-post-update-hook.sh" % repo_path)
        with c.cd(repo_path):
            c.run("git init .")
            c.run("./create-post-update-hook.sh")

    wrapped_task = task(hosts=hosts)(work)

    return wrapped_task()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: main.py <host> <repo_path>")
        sys.exit(1)

    my_wrapper_function()
