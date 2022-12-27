from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nonebot-plugin-backup",
    version="1.0.4",
    author="Yueli",
    author_email="yuelioi1210@gmail.com",
    description="A plugin based on NoneBot2 to backup files in qq group.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Yuelioi/nonebot-plugin-backup",
    project_urls={
        "Bug Tracker": "https://github.com/Yuelioi/nonebot-plugin-backup/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    packages=["nonebot_plugin_backup"],
    python_requires=">=3.7",
    install_requires=[
        "nonebot2 >= 2.0.0b2",
        "nonebot-adapter-onebot >= 2.0.0b1",
        "requests >= 1.0.0"
    ],
)
