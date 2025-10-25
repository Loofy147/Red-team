from setuptools import setup, find_packages

setup(
    name="red_team",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'red_team=red_team.final_main_execution:main',
        ],
    },
)
