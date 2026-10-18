from setuptools import setup, find_packages

setup(
    name="ghostos-ai",
    version="1.0.0",
    author="KIB.best",
    author_email="GhostOS@kib.best",
    url="https://github.com/GhostOS-ai/GhostOS",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "ghost.ui": ["assets/*"],
    },
    install_requires=[
        "rich>=13.0.0",
        "pywebview>=5.0.0",
        "psutil>=5.9.0",
        "pypdf>=4.0.0",
        "python-docx>=1.0.0",
        "Pillow>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ghost=ghost.cli.main:main",
        ],
    },
)
