#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
'''
############################
#####
#####       cutter
#####      R. THOMAS
#####        2022
#####
###########################
@License: GPL - see LICENCE.txt
'''

###import libraries
import sys
import os
from subprocess import call
import socket


##third parties
from PyQt5.QtWidgets import QApplication

###Local modules
from . import cli
from . import GUI
from . import __info__ as info

def main():
    '''
    This is the main function of the code.
    if loads the command line interface and depending
    on the options specified by the user, start the 
    main window.
    '''
    ###load the command line interface
    args = cli.CLI().arguments

    if args.version == True:
        print('version %s'%info.__version__)
        sys.exit()

    ###terminal message
    print('\n\t\t\tcutter V%s'%info.__version__)
    print('\t\t        R. Thomas -2022-')

    if args.file == None:
        print('\n\t No file configuration given...exiting cutter...\n\
               Try cutter --help to look at the options\n')
    #    sys.exit()

    if args.file != None:
        print('\n\t Load file: %s\n'%args.file)

    ###Construct a QAppp
    app = QApplication(sys.argv)

    if args.width != None:
        win = GUI.Main_window(args)    
        win.resize(args.width, 1030)

    if args.width == None:
        args.width = 780
        win = GUI.Main_window(args)    
        win.resize(args.width, 1030)

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
