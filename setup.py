from setuptools import setup

setup(
    name='OnlineJudge',
    version='0.0.1',
    packages=['OJ', 'OJ.db', 'OJ.app', 'OJ.util', 'OJ.views', 'OJ.views.admin', 'OJ.models', 'OJ.middleware'],
    url='',
    license='',
    author='cslzc',
    author_email='',
    description='',
    install_requires=[
        'fastapi',
        'redis',
        'requests',
        'SQLAlchemy',
        'urllib3',
        'fastapi-pagination',
        'pycryptodome',
        'PyMySQL',
        'uvicorn',
        'python-multipart',
    ]
)
