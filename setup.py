import pathlib
from distutils.core import setup

from therminbot import __version__ as version


here = pathlib.Path(__file__).parent.resolve()

with open("requirements.txt", "r") as file:
    install_requires = [x.strip() for x in file.readlines()]

setup(
    name="therminbot",
    packages=["therminbot"],
    version=version,
    license="MIT",
    description="Multifunctional human-friendly 20% sarcastic bot.",
    author = "Alexander Ryzhov",
    author_email = "thed4rkof@gmail.com",
    url = "https://github.com/ryzhovalex/therminbot",
    download_url = "",
    keywords = ["telegram-bot", "service-bot", "multi-bot"],
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
    ],
)