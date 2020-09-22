from setuptools import setup

url = ""
version = "0.1.0"
readme = open('README.md').read()

setup(
    name="ml5_test",
    packages=["ml5_test"],
    version=version,
    description="test version of ml5_ipynb",
    long_description=readme,
    include_package_data=True,
    author="Lingrui Luo",
    author_email="ll3356@columbia.edu",
    url=url,
    install_requires=[
        "jp_proxy_widget", 
        "jp_doodle",
        "numpy", 
        "pandas",
        "pillow", 
        "imageio",
        "jupyter-ui-poll",
        ],
    license="MIT"
)