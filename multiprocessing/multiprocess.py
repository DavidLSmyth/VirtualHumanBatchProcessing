import subprocess


def run_multiprocessed(subprocess_args):

    for arg in subprocess_args:
        print("running subprocess", arg)
        subprocess.Popen(arg)
