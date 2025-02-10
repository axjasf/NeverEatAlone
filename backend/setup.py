from setuptools import setup, find_packages

setup(
    name="nevereatalone",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "sqlalchemy",
        "pydantic",
        "alembic",
        "pytest",
        "python-multipart",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
    ],
)
