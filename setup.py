from setuptools import setup, find_packages

setup(
    name="mtl",
    version="0.1.0",
    description="A command line tool for payroll management",
    author="Tinashe Kucherera",
    author_email="tkucherera86@gmail.com",
    find_packages=find_packages(),
    entry_points={
        "console_scripts": [
            "mtl=mtl_cli.mtl:main"
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.10.7",
    install_requires=[
        "argparse-manpage==4.6",
        "cachetools==5.5.0",
        "certifi==2024.8.30",
        "charset-normalizer==3.4.0",
        "google-api-core==2.23.0",
        "google-api-python-client==2.154.0",
        "google-auth==2.36.0",
        "google-auth-httplib2==0.2.0",
        "google-auth-oauthlib==1.2.1",
        "googleapis-common-protos==1.66.0",
        "httplib2==0.22.0",
        "idna==3.10",
        "oauthlib==3.2.2",
        "proto-plus==1.25.0",
        "protobuf==5.29.1",
        "pyasn1==0.6.1",
        "pyasn1_modules==0.4.1",
        "pyparsing==3.2.0",
        "python-dotenv==1.0.1",
        "requests==2.32.3",
        "requests-oauthlib==2.0.0",
        "rsa==4.9",
        "setuptools==75.6.0",
        "uritemplate==4.1.1",
        "urllib3==2.2.3",
    ],
)
