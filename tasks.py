#!/usr/bin env python
"""Project automation code using Invoke.py as replacement for `make`."""

import os
import sys
import datetime as dt
import webbrowser
from urllib.request import pathname2url
from pathlib import Path

from invoke import task

PROJECT_ROOT = str(Path(__file__).parent)

MY_CONDA_ROOT = os.environ["MY_CONDA_ROOT"]
PACKAGE_NAME = "veoibd_synapse"
CONDA_ENV_NAME = "veoibd_synapse"
SRC_DIR = "src"
SOURCE_CONDA = f"source {MY_CONDA_ROOT}/etc/profile.d/conda.sh"
ACTIVATE = f"{SOURCE_CONDA} && conda activate {CONDA_ENV_NAME}"


def browser(path):
    webbrowser.open("file://" + pathname2url(os.path.abspath(path)))


@task
def clean_build(ctx):
    """Remove build artifacts."""
    with ctx.prefix(ACTIVATE):
        ctx.run("rm -fr build/")
        ctx.run("rm -fr dist/")
        ctx.run("rm -fr .eggs/")
        ctx.run("find . -name '*.egg-info' -exec rm -fr {} +")
        ctx.run("find . -name '*.egg' -exec rm -f {} +")


@task
def clean_pyc(ctx):
    """Remove Python file artifacts."""
    with ctx.prefix(ACTIVATE):
        ctx.run("find . -name '*.pyc' -exec rm -f {} +")
        ctx.run("find . -name '*.pyo' -exec rm -f {} +")
        ctx.run("find . -name '*~' -exec rm -f {} +")
        ctx.run("find . -name '__pycache__' -exec rm -fr {} +")


@task
def clean_test(ctx):
    """Remove test and coverage artifacts."""
    with ctx.prefix(ACTIVATE):
        ctx.run("rm -fr .tox/")
        ctx.run("rm -f .coverage")
        ctx.run("rm -fr htmlcov/")


@task
def clean_docs(ctx):
    """Remove docs artifacts."""
    with ctx.prefix(ACTIVATE):
        ctx.run("make -C docs clean")


@task
def mypy(ctx):
    """Check typing with mypy."""
    with ctx.prefix(ACTIVATE):
        ctx.run(f"mypy --ignore-missing-imports {PACKAGE_NAME}")


@task(clean_build, clean_pyc, clean_test)
def clean(ctx):
    """Remove all build, test, coverage and Python artifacts."""
    with ctx.prefix(ACTIVATE):
        ctx.run("echo clean")


@task
def lint(ctx):
    """Check style with flake8."""
    with ctx.prefix(ACTIVATE):
        ctx.run(f"flake8 {SRC_DIR}")


@task
def test(ctx):
    """Run tests quickly with the default Python."""
    with ctx.prefix(ACTIVATE):
        ctx.run(f"pytest")


@task
def test_all(ctx):
    """Run tests on every Python version with tox."""
    with ctx.prefix(ACTIVATE):
        ctx.run(f"tox")


@task
def coverage(ctx):
    """Check code coverage quickly with the default Python."""
    with ctx.prefix(ACTIVATE):
        ctx.run(f"coverage run --source {SRC_DIR} -m pytest")
        ctx.run(f"coverage report -m")
        ctx.run(f"coverage html")
        browser(path="htmlcov/index.html")


@task
def docs(ctx):
    """Generate Sphinx HTML documentation, including API docs."""
    with ctx.prefix(ACTIVATE):
        ctx.run(f"rm -f docs/{PACKAGE_NAME}.rst")
        ctx.run(f"rm -f docs/{PACKAGE_NAME}.*.rst")
        # ctx.run(f"rm -f docs/modules.rst")
        ctx.run(f"make -C docs clean")
        ctx.run(f"make -C docs html")
        # browser(path="docs/_build/html/index.html")


@task(docs)
def servedocs(ctx):
    """Compile the docs watching for changes."""
    with ctx.prefix(ACTIVATE):
        ctx.run(f"watchmedo shell-command -p '*.rst' -c 'make -C docs html' -R -D .")


@task(clean)
def release(ctx):
    """Package and upload a release."""
    with ctx.prefix(ACTIVATE):
        ctx.run(f"python setup.py sdist upload")
        ctx.run(f"python setup.py bdist_wheel upload")


@task(clean)
def dist(ctx):
    """Builds source and wheel package."""
    with ctx.prefix(ACTIVATE):
        ctx.run(f"python setup.py sdist")
        ctx.run(f"python setup.py bdist_wheel")
        ctx.run(f"ls -l dist")


@task
def jupyter_notebook(ctx):
    """Serve the jupyter notebook."""
    with ctx.prefix(ACTIVATE):
        ctx.run(f"jupyter notebook --notebook-dir notebooks")


@task
def jupyter_lab(ctx):
    """Serve the jupyter lab."""
    with ctx.prefix(ACTIVATE):
        ctx.run(f"jupyter lab --notebook-dir notebooks")


@task
def install(ctx):
    """Installs virtual environments and requirements."""
    with ctx.prefix(SOURCE_CONDA):
        ctx.run(f"conda create -n {CONDA_ENV_NAME} 'python >=3.6' --file requirements.txt --yes")
    with ctx.prefix(ACTIVATE):
        ctx.run("pip install -r requirements.pip.txt")
        ctx.run("pip install -e .")
        ctx.run(
            f"""python -m ipykernel install --sys-prefix --name {CONDA_ENV_NAME} --display-name "{CONDA_ENV_NAME}" """
        )
        ctx.run("jupyter labextension install jupyterlab-toc")


@task
def uninstall(ctx):
    """Uninstalls virtual environments and requirements."""
    with ctx.prefix(SOURCE_CONDA):
        ctx.run(f"conda remove -n {CONDA_ENV_NAME} --all -y")


@task
def nb_to_html(ctx, nbfile):
    """Convert nbfile to an HTML file with imgs embedded."""
    with ctx.prefix(ACTIVATE):
        ctx.run(f"""jupyter nbconvert --to html_toc --ExtractOutputPreprocessor.enabled=False {nbfile}""")

