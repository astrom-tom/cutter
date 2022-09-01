from setuptools import setup  # Always prefer setuptools over distutils

__author__ = "Romain Thomas"
__credits__ = "Romain Thomas"
__license__ = "GNU GPL v3"
__version__ = "22.8.1"
__maintainer__ = "Romain Thomas"
__email__ = "the.spartan.proj@gmail.com"
__status__ = "Development"

setup(
   name = 'cutter',
   version = __version__,
   author = __author__,
   author_email = __email__,
   packages = ['cutter'],
   entry_points = {'gui_scripts': ['cutter = cutter.__main__:main',],},
   license = __license__,
   description = 'Python tool for easy spectrum cutting',
   python_requires = '>=3.6',
   install_requires = [
      "PyQt5 >= v5.10.1",
      "scipy >= 1.0.1",
      "numpy >=1.14.2",
      "matplotlib >= 2.2.2",
      "astropy >= 3.0.2",
      "Pillow >=5.1.0",
   ],
   include_package_data=True,
)
