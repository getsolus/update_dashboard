# Module for retrieving package monitoring data

import subprocess
import pathlib
import yaml
from mistletoe import Document
from mistletoe.ast_renderer import AstRenderer
import json


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


def resolve_package_dir(package_name: str) -> pathlib.Path:
    if package_name.startswith('py'):
        output = pathlib.Path(f'packages/{package_name[0]}{package_name[1]}/{package_name}')
    else:
        output = pathlib.Path(f'packages/{package_name[0]}/{package_name}')
    return output


def get_metadata(workdir: pathlib.Path, package_name: str) -> dict:
    pkg_dir = workdir / resolve_package_dir(package_name)
    if not pkg_dir.exists():
        raise RuntimeError(f"Package {package_name}'s directory does not exist in the specified working directory.")
    package_file = workdir / pkg_dir / "package.yml"
    maintainers_file = workdir / pkg_dir / "MAINTAINERS.md"
    monitoring_file = workdir / pkg_dir / "monitoring.yaml"
    with open(package_file) as package_file:
        package = yaml.safe_load(package_file)
        homepage = package["homepage"]
    if maintainers_file.exists():
        with(open(maintainers_file, "r")) as maintainers_file:
            maintainers_ast = json.loads(AstRenderer().render(Document(maintainers_file)))
            maintainers = []
            for child in maintainers_ast['children']:
                if child['type'] == 'List':
                    for maintainer in child['children']:
                        maintainers.append(
                            {
                                'name': maintainer['children'][0]['children'][0]['content'],
                                'contact_methods': [
                                    contact_method['children'][0]['children'][0]['content']
                                    for contact_method
                                    in maintainer['children'][1]['children']
                                ]
                            }
                        )
    with(open(monitoring_file, "r")) as monitoring_file:
        monitoring = yaml.safe_load(monitoring_file)
        release_id = monitoring["releases"]["id"]
        monitoring_url = f"https://release-monitoring.org/api/v2/versions/?project_id={release_id}"
    return {
        "package_name": package_name,
        "homepage": homepage,
        "maintainers": maintainers,
        "monitoring_url": monitoring_url
    }
