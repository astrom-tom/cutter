'''
cutter
------
File: cli.py

This file configures the Command line interface

@author: R. THOMAS
@year: 2022
@place:  ESO
@License: GPL v3.0 - see LICENCE.txt
'''

#### Python Libraries
import argparse

class CLI:
    """
    This Class defines the arguments to be calle to use SPARTAN
    For the help, you can use 'SPARTAN -h' or 'SPARTAN --help'
    """
    def __init__(self,):
        """
        Class constructor, defines the attributes of the class
        and run the argument section
        """
        self.args()

    def args(self,):
        """
        This function creates defines the 7 main arguments of SPARTAN using the argparse module
        """
        parser = argparse.ArgumentParser(description="cutter, R. Thomas, 2022, \
                This program comes with ABSOLUTELY NO WARRANTY; and is distributed under \
                the GPLv3.0 Licence terms.See the version of this Licence distributed along \
                this code for details.\n website: https://github.com/astrom-tom/Photon")

        parser.add_argument("-f", '--file', help="Your catalog of data to visualize, \
                this is mandatory, this is mandatory if you do not use -p option")
        parser.add_argument("-d", "--dire", type = str,
                            help="Directory where the original spectra are located")
        parser.add_argument("-w", "--width", type = int, help="Width of the GUI, default = 780")
        parser.add_argument("--version", action = "store_true", help="display version of photon")

        ##### GET the Arguments for SPARTAN startup
        self.arguments = parser.parse_args()
