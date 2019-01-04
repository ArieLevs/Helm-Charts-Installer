import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="helm-charts",
    version="1.0.12",
    author="Arie Lev",
    author_email="levinsonarie@gmail.com",
    description="Helm Charts installer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ArieLevs/Helm-Charts-Installer",
    license='Apache License 2.0',
    include_package_data=True,
    packages=setuptools.find_packages(),
    install_requires=[
        'urwid',
      ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Unix",
        "Operating System :: MacOS",
    ),
    entry_points={
        'console_scripts': [
            'helm_charts = helm_charts.k8s_charts_installer:main'
        ],
    },
)
