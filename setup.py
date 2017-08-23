"""Install setup."""
import setuptools

setuptools.setup(
    name="veoibd_synapse",
    version="0.0.4",
    url="git@github.com:ScottSnapperLab/veoibd-synapse-data-manager.git",

    author="Gus Dunn",
    author_email="w.gus.dunn@gmail.com",

    description="Admin related logistics regarding uploading and annotating data to Synapse for members of the VEOIBD consortium.",
    # long_description=open('README.rst').read(),

    packages=setuptools.find_packages('src'),
    package_dir={"": "src"},


    install_requires=[],

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
