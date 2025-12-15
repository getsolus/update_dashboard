from monitoring import get_outdated, get_metadata
import pathlib
from rich.progress import track
import typer
from rich import print

app = typer.Typer()


@app.command()
def render_outdated(packages_dir: pathlib.Path):
    print("Finding outdated packages using ent...")
    ent_packages = get_outdated(packages_dir)
    print("Done!")
    outdated_packages = [
        dict(**get_metadata(packages_dir, package['name']), current_version=package.get('current_version'), new_version=package.get('new_version'))
        for package in track(ent_packages, description='Getting metadata for all outdated packages...')
    ]
    print(outdated_packages)


if __name__ == '__main__':
    app()
