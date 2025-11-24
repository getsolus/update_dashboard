# Module for retrieving package monitoring data

import subprocess
import pathlib


def get_outdated(workdir: pathlib.Path):
    try:
        outdated_text = subprocess.check_output(
            [
                "ent",
                "check",
                "updates",
            ],
            cwd=workdir,
        )
    except subprocess.CalledProcessError:
        raise RuntimeError("Failed to run ent. Is it installed?")

    outdated_lines = outdated_text.splitlines()
    outdated = [
        {
            "name": line.split()[0],
            "current_version": line.split()[1],
            "new_version": line.split()[2],
        }
        for line in outdated_lines
        if len(line.split()) == 3
        and not line.startswith(b"---")
        and not line.startswith(b"Checking ")
        and not line.startswith(b"Package  ")
    ]
    return outdated
