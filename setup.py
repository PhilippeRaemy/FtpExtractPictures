from setuptools import setup

setup(
    name="ftp_extract_pictures",
    version="1.0",
    py_modules=["ftp_extract_pictures"],
    include_package_data=True,
    install_requires=["click"],
    entry_points="""
        [console_scripts]
        ftp_extract_pictures=ftp_extract_pictures:cli
    """,
)
