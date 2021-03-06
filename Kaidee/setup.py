from setuptools import setup, find_packages

setup(
    name='KaideeV',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'flask_login',
        'flask_cors',
        'MySQL',
        'wand',
        'pytest',
        'Flask-Session'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
