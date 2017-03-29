import os.path, codecs, re

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = codecs.open(os.path.join(here, 'README.md'), encoding='utf8').read()
CHANGES = codecs.open(os.path.join(here, 'CHANGES'), encoding='utf8').read()

with codecs.open(os.path.join(os.path.dirname(__file__), 'needles', '__init__.py'),
                 encoding='utf8') as version_file:
    metadata = dict(re.findall(r"""__([a-z]+)__ = "([^"]+)""", version_file.read()))

setup(name='needles',
      version=metadata['version'],
      description='Conversion between binary buffers and LSTM input sequences.',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        ],
      author='Yijun Yu',
      author_email='y.yu@open.ac.uk',
      url='https://github.com/yijunyu/needles/',
      keywords=['needles', 'packaging'],
      license='GPL',
      packages=[
          'needles',
          ],
      extras_require={
          ':python_version=="2.6"': ['argparse'],
          'signatures': ['keyring', 'keyrings.alt'],
          'signatures:sys_platform!="win32"': ['pyxdg'],
          'signatures:python_version=="2.6"': ['importlib'],
          'needleser-signatures': ['ed25519ll'],
          'tool': []
          },
      tests_require=['jsonschema', 'pytest', 'coverage', 'pytest-cov'],
      include_package_data=True,
      zip_safe=False,
      entry_points = """\
[console_scripts]
needles = needles.needles:main

[distutils.commands]
bdist_needles = needles.bdist_needles:bdist_needles"""
      )

