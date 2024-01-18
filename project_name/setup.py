from setuptools import find_packages, setup

setup(
    name="project_name",
    packages=find_packages(exclude=["project_name_tests"]),
    install_requires=["dagster", "dagster-cloud"],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
