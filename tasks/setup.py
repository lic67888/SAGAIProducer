# %%
import re
from pathlib import Path
from subprocess import run

import requests
from invoke.context import Context
from invoke.tasks import task


root_dir: Path = Path(__file__).parent.parent


class PackageDetails:
    """Get package details from the user."""

    def __init__(self) -> None:
        self._package_name = self.get_git_remote_package_name()
        self.description = ""
        self.version = "0.1.0"
        self.author = "Vince Faller"
        self.get_inputs()

    def __repr__(self) -> str:
        return f"PackageDetails(package_name={self.package_name}, description={self.description}, version={self.version}, author={self.author})"

    @property
    def package_name(self) -> str:
        """Get the package name."""
        return self._package_name

    @property
    def package_name_under(self) -> str:
        """Get the package name with dashes replaced with underscores."""
        return self._package_name.replace("-", "_")

    @package_name.setter
    def package_name(self, package_name: str) -> None:
        """Set the package name."""
        if self.check_package_name_on_pypi(package_name):
            msg = f"Package name '{package_name}' already exists on PyPI"
            raise ValueError(msg)
        self._package_name = package_name

    def get_git_remote_package_name(self) -> str:
        """Get the package name from the git remote."""
        r = run(["git", "config", "--local", "remote.origin.url"], check=True, capture_output=True)  # noqa: S603, S607
        remote_url = r.stdout.decode()
        package_name = remote_url.split("/")[-1].split(".")[0]
        return package_name

    def get_inputs(self) -> None:
        """Get the user inputs."""
        package_name = input(f"Package name [{self.package_name}]: ") or self.package_name
        self.package_name = package_name.strip()
        description = input("Description ['']: ") or ""
        self.description = description.strip()
        version = input("Version [0.1.0]: ") or "0.1.0"
        self.version = version.strip()
        author = input("Author [Vince Faller]: ") or "Vince Faller"
        self.author = author.strip()

    def check_package_name_on_pypi(self, package_name: str) -> bool:
        """Check if the package name exists on PyPI."""
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=5)
        return response.status_code == 200  # noqa: PLR2004


def rename_pyproject_toml(package_details: PackageDetails) -> str:
    """Asks the user for package details and overwrites the pyproject.toml file."""
    with (root_dir / "pyproject.toml").open("r") as f:
        txt = f.read()
    version = package_details.version
    description = package_details.description
    author = package_details.author
    package_name = package_details.package_name
    pattern = r'\[tool\.poetry\]\nname = "[^"]+"\nversion = "[^"]+"\ndescription = "[^"]*"\nauthors = \["[^"]+"\]\n'
    replace_str = re.search(pattern, txt).group(0)
    replace_with = f'[tool.poetry]\nname = "{package_name}"\nversion = "{version}"\ndescription = "{description}"\nauthors = ["{author}"]\n'
    print(f"Replacing\n{replace_str}\nwith\n{replace_with}")
    txt = txt.replace(replace_str, replace_with)
    with (root_dir / "pyproject.toml").open("w") as f:
        f.write(txt)
    return package_name


def edit_readme(package_details: PackageDetails) -> None:
    """Edit the README file."""
    readme_path = root_dir / "README.md"
    readme_path.unlink()
    downstream_readme_path = root_dir / "README_downstream.md"
    downstream_readme_path.rename(readme_path)
    with readme_path.open("r") as f:
        txt = f.read()
    txt = txt.replace("python-template", package_details.package_name, 1)
    txt = txt.replace("REPLACE_ME_DESCRIPTION", package_details.description)
    with readme_path.open("w") as f:
        f.write(txt)


@task
def rename(ctx: Context) -> None:
    """Rename the package in all the spots."""
    with (root_dir / "pyproject.toml").open("r") as f:
        tomltxt = f.read()

    if "python-template" not in tomltxt:
        print("Package name already set in pyproject.toml")
        return
    package_details = PackageDetails()
    package_name = rename_pyproject_toml(package_details=package_details)
    edit_readme(package_details=package_details)

    # rename the package in the __init__.py file
    with root_dir / "tests/main_test.py" as f:
        txt = f.read_text()
    txt = txt.replace("python_template", package_details.package_name_under)
    with root_dir / "tests/main_test.py" as f:
        f.write_text(txt)

    # rename python_template to the new package name
    cmd = f"git mv -f python_template {package_name}"
    ctx.run(cmd)


@task
def precommit(ctx: Context) -> None:
    """Install pre-commit hooks."""
    ctx.run("poetry run pre-commit install")


@task
def update_from_template(ctx: Context) -> None:
    """Update the project from the template."""
    # check if remote is already added
    try:
        ctx.run("git remote get-url template", hide=True)
    except Exception:
        print("Adding remote template")
        ctx.run("git remote add template https://github.com/lite-dsa/python-template.git")

    ctx.run("git fetch template", hide=True)
    ctx.run("git merge template/main --allow-unrelated-histories")


@task
def first_time_setup(ctx: Context) -> None:
    """Run all setup tasks."""
    rename(ctx)
    precommit(ctx)


@task(
    pre=[
        precommit,
    ],
    default=True,
)
def all_tasks(_: Context) -> None:
    """Run all setup tasks."""
