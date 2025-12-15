from monitoring import get_outdated, get_metadata
import pathlib
from rich.progress import track
import typer
from rich import print
from jinja2 import Environment, PackageLoader
from jinja2_lucide import LucideExtension

app = typer.Typer()

env = Environment(
    loader=PackageLoader('main', 'templates'),
    autoescape=True,
    extensions=[LucideExtension],
)

@app.command()
def render_outdated(packages_dir: pathlib.Path, output_filename: pathlib.Path = pathlib.Path('./deploy/outdated.html')):
    print("Finding outdated packages using ent...")
    ent_packages = get_outdated(packages_dir)
    print("Done!")
    outdated_packages = [
        dict(**get_metadata(packages_dir, package['name']), current_version=package.get('current_version'), new_version=package.get('new_version'))
        for package in track(ent_packages, description='Getting metadata for all outdated packages...')
    ]
    template = env.get_template('outdated_packages.html')
    with output_filename.open('w') as output_file:
        output_file.write(template.render(outdated_packages=outdated_packages, page_title='Outdated packages', num_outdated=len(outdated_packages)))
    # print(template.render(outdated_packages=outdated_packages))

if __name__ == '__main__':
    app()
