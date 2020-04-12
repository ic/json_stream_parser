import sys
from setuptools import setup

if sys.version_info[:2] < (3, 5):
    raise SystemExit('require Python3.5+')

setup(
    name='json_stream_parser',
    url='https://github.com/account-login/json_stream_parser',
    author='account-login',
    author_email='',
    version='0.2dev',
    py_modules=['json_stream_parser'],
    entry_points='''
        [console_scripts]
        json_stream_parser=json_stream_parser:main
    ''',
    license='MIT',
    description='parsing a stream of json objects without loading the whole stream into memory',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        'Operating System :: OS Independent',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='json stream parser lazy',
)
