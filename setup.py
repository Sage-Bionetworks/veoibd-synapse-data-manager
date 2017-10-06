"""Install setup."""
import setuptools

from pathlib import Path


def filter_req_paths(paths, func):
    """Return list of filtered libs."""
    if not isinstance(paths, list):
        raise ValueError("Paths must be a list of paths.")

    libs = set()
    junk = set(['\n'])
    for p in paths:
        with Path(p).open(mode='r') as reqs:
            lines = set([line for line in reqs if func(line)])
            libs.update(lines)

    return list(libs - junk)


def is_pipable(s):
    """Filter for pipable reqs."""
    if "# not_pipable" in s:
        return False
    elif s.startswith('#'):
        return False
    else:
        return True


req_paths = ["requirements.pip.txt",
             "requirements.txt"]


setuptools.setup(
    name="veoibd_synapse",
    version="version='0.1.0'",
    url="git@github.com:ScottSnapperLab/veoibd-synapse-data-manager.git",

    author="Gus Dunn",
    author_email="w.gus.dunn@gmail.com",

    description="Admin related logistics regarding uploading and annotating data to Synapse for members of the VEOIBD consortium.",
    # long_description=open('README.rst').read(),

    packages=setuptools.find_packages('src'),
    package_dir={"": "src"},


    install_requires=filter_req_paths(paths=req_paths,
                                      func=is_pipable),

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    entry_points={
        "console_scripts": [
            "veoibd_synapse = veoibd_synapse.cli.main:run",

        ]
    },
)
