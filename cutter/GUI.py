#!/usr/bin/python
'''
############################
#####
#####       cutter
#####      R. THOMAS
#####        2022
#####        Main
#####
##### Usage: photon [-h] [-t] file
#####---------------------------------------
#####
###########################
@License: GPL - see LICENCE.txt
'''
####Public General Libraries
import warnings
import os
from functools import partial
from astropy.io import fits
import numpy
from catscii import catscii

######Qt5
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import QGridLayout, QWidget, \
        QTabWidget, QTabWidget, QLineEdit, QInputDialog, \
        QHBoxLayout, QPushButton, QFileDialog,\
        QSplitter, QShortcut, QTableWidget,QAbstractItemView,\
        QTableWidgetItem, QLabel

###matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.colors as col
import matplotlib
import matplotlib.pyplot as plt
warnings.simplefilter(action='ignore', category=matplotlib.mplDeprecation)
warnings.simplefilter(action='ignore', category=UserWarning)

####some matplotlib fixed parameters
matplotlib.rcParams['savefig.dpi'] = 300
matplotlib.rcParams['savefig.directory'] = ''
matplotlib.rcParams['savefig.format'] = 'eps'

####local imports
from . import __info__


#####################FONT QT4, size and bold
myFont = QtGui.QFont()
myFont.setBold(True)
myFont.setPointSize(9)
#######################################################################################

class Main_window(QWidget):

    def __init__(self, cli_args):
        '''
        Class constructor
        '''
        super().__init__()
        self.args = cli_args
        self.displayed = []
        self.crosshair_lines = []
        self.cut_spectrum_plots = []
        self.spectrum_path = ''
        self.counter_table = 0
        self.previousSearch = None
        self.initUI()
        self.setWindowTitle('cutter V%s' %(__info__.__version__))
        self.spec_counter = 0

    def initUI(self):
        '''
        This method creates the main window
        '''

        ### 1 we create the grid
        hbox = QHBoxLayout(self)

        split = QSplitter(QtCore.Qt.Vertical)

        grid = QGridLayout()
        grid_p = QWidget()
        grid_p.setLayout(grid)
            
        hbox.addWidget(split)
        self.setLayout(hbox)

        ###shortcuts
        SC_next_spec = QShortcut(QtGui.QKeySequence("n"), self)
        SC_next_spec.activated.connect(self.next_spec)

        SC_prev_spec = QShortcut(QtGui.QKeySequence("p"), self)
        SC_prev_spec.activated.connect(self.prev_spec)

        save_plot_cut = QShortcut(QtGui.QKeySequence("s"), self)
        save_plot_cut.activated.connect(self.save_spec)

        ### a- space for plot
        self.tab = QTabWidget()
        self.figure = Figure()
        self.figure.subplots_adjust(hspace=0, right=0.95, top=0.94, left=0.15)
        self.win = FigureCanvas(self.figure)
        self.win.mpl_connect('motion_notify_event', self.crosshair)
        self.win.mpl_connect('button_press_event', self.get_limits)
        self.toolbar = NavigationToolbar(self.win, self.win)
        grid.addWidget(self.win, 0, 0, 1, 4)
        grid.addWidget(self.toolbar, 1, 0, 1, 4) 
        self.plot = self.figure.add_subplot(111)
        self.plot.set_ylabel(r'Flux density erg/s/cm$^2$/$\mathrm{\AA}$')
        self.plot.set_xlabel(r'Wavelength [$\mathrm{\AA}$]')
        self.plot.minorticks_on()

        ##buttons
        prev_spec = QPushButton('Prev spec')
        grid.addWidget(prev_spec, 2, 0, 1, 1)
        next_spec = QPushButton('next spec')
        grid.addWidget(next_spec, 2, 1, 1, 1)
        save_spec = QPushButton('save spec')
        grid.addWidget(save_spec, 2, 2, 1, 2)

        origin =  QPushButton('Original Spectral folder')
        grid.addWidget(origin, 3, 0, 1, 1)
        self.orig_folder = QLineEdit()
        self.orig_folder.setFixedWidth(320)
        grid.addWidget(self.orig_folder, 3, 1, 1, 1)

 
        destination = QPushButton('Destination folder')
        grid.addWidget(destination, 4, 0, 1, 1)
        self.dest_folder = QLineEdit()
        self.dest_folder.setFixedWidth(320)
        grid.addWidget(self.dest_folder, 4, 1, 1, 1)
        ##temp
        self.dest_folder.setText('/home/romain/GITHUB/cutter/cutter/test/cut_test')
        self.saved_directory = '/home/romain/GITHUB/cutter/cutter/test/cut_test'
        

        ##search
        search_label = QLabel('Search table:')
        grid.addWidget(search_label, 3, 2, 1, 1)
        self.search_str = QLineEdit()
        grid.addWidget(self.search_str, 3, 3, 1, 1)


        check_cut = QPushButton('Check')
        grid.addWidget(check_cut, 4, 2, 1, 1)
 
        ##limits for cutting
        x1 = QLabel('X low:')
        grid.addWidget(x1, 5, 0, 1, 1)
        self.x1 = QLabel('----')
        grid.addWidget(self.x1, 5, 1, 1, 1)

        x2 = QLabel('X high:')
        grid.addWidget(x2, 5, 2, 1, 1)
        self.x2 = QLabel('----')
        grid.addWidget(self.x2, 5, 3, 1, 1)


        ####we create a horizontal split and add it the to global
        ####box
        panels = QHBoxLayout()
        panels_cont = QWidget()
        panels_cont.setLayout(panels)

        ###Spectrum table area
        ### a - we create the grid in a scroll area
        ##add table
        self.properties = QGridLayout()
        self.table = QTableWidget()
        self.table.setRowCount(100)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Spectrum', 'Noise Spectrum', 'redshift', 'Already Cut'])
        self.table.resizeColumnsToContents()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.properties.addWidget(self.table, 0, 0, 3, 3)
        self.table.doubleClicked.connect(self.onDoubleClick)
    
        ###put everything in the split
        split.addWidget(grid_p)
        split.addWidget(self.table)
        split.setSizes([600,400])

        ##adjust figure
        self.figure.tight_layout()
        self.win.draw()

        ##set up the interface with the given configuration
        if self.args.dire:
            self.orig_folder.setText(self.args.dire)
            self.original_folder = self.args.dire
        else:
            self.original_folder = os.path.dirname(os.path.realpath(__file__))
            self.orig_folder.setText(self.original_folder)
        self.table_setup()
        self.table.selectRow(self.counter_table)
        self.onDoubleClick()

        ###button cnnection
        destination.clicked.connect(partial(self.dialog_folder, 'destination'))
        origin.clicked.connect(partial(self.dialog_folder, 'origin'))
        check_cut.clicked.connect(self.check_cut)
        prev_spec.clicked.connect(self.prev_spec)
        next_spec.clicked.connect(self.next_spec)
        save_spec.clicked.connect(self.save_spec)
        self.search_str.returnPressed.connect(self.search)

        #logo
        dir_path = os.path.dirname(os.path.realpath(__file__))
        logo = os.path.join(dir_path, 'logo.png')
        self.setWindowIcon(QtGui.QIcon(logo))

        ###check spectrs
        self.check_cut()

        ###display the window on screen
        self.show()

    def prev_spec(self):
        '''
        Go to prev spec
        '''
        if self.counter_table == 0:
            self.counter_table = self.length_table-1
        else:
            self.counter_table -= 1
 
        self.table.selectRow(self.counter_table)
        self.onDoubleClick()

    def next_spec(self):
        '''
        Go to next spec
        '''
        if self.counter_table == self.length_table-1:
            self.counter_table = 0
        else:
            self.counter_table += 1

        self.table.selectRow(self.counter_table)
        self.onDoubleClick()

    def save_spec(self):
        '''
        Save the cut spectrum along the normal spectrum
        '''
        if hasattr(self, 'wave'):
            spec_name, extension = os.path.splitext(self.spectrum_path)
            spec_name = spec_name.split('/')[-1]
            ascii_spec = os.path.join(self.saved_directory, spec_name+'.ascii')
            cut_spec = os.path.join(self.saved_directory, spec_name+'_cut.ascii')
            numpy.savetxt(cut_spec, numpy.array([self.cutx, self.cuty, self.cuty_noise]).T)

    def dialog_folder(self, type_folder):
        '''
        This set up the destination folder where the cut spectra
        will be stored
        '''
        directory = QFileDialog.getExistingDirectory(self, 'Choose destination directory')
        if type_folder == 'destination':
            self.saved_directory = directory
            self.dest_folder.setText(directory)

        if type_folder == 'origin':
            self.orig_folder.setText(directory)
            self.original_folder = directory

    def search(self):
        '''
        This methods set up the search algorithm
        '''
        ###get the text from the search box
        get_text = self.search_str.text() 
        ###find ALL the item containing the search string
        items = self.table.findItems(get_text, QtCore.Qt.MatchContains)

        if items:
            #Check if the current search is the same as the previous
            if self.previousSearch == self.search_str.text():
                #If so, go to the next item in list (increment searchInd)
                self.searchInd += 1
                #If at end of list,, reset searchInd
                if self.searchInd >= len(items):
                    self.searchInd = 0
            else:
                #If the search isn't the same, update searchInd to start with first item
                self.searchInd = 0
            #Go to the current searchInd index of the items, and highlight the row
            self.table.selectRow(items[self.searchInd].row()) 
            #Update the previous search text
            self.previousSearch = self.search_str.text()
            ##display it
            self.onDoubleClick()



    def check_cut(self):
        '''
        This method check, for each line on the table
        if a cut spectra was found
        '''

        ##loop through the table
        for i in range(self.table.rowCount()):
            spec = self.table.item(i, 0).text()
            spec_name, extension = os.path.splitext(spec)

            ##name of the cut spec name
            cut_name = os.path.join(self.saved_directory, spec_name + '_cut.ascii')

            ##check if that file exist
            if os.path.isfile(cut_name):
                self.table.setItem(i, 3, QTableWidgetItem('Yes'))
                self.table.item(i,3).setBackground(QtGui.QColor(0,255,0))
            else:
                self.table.setItem(i, 3, QTableWidgetItem('No'))
                self.table.item(i,3).setBackground(QtGui.QColor(255,0,0))

    def table_setup(self):
        '''
        This method fill the table based on the
        file fiven in arguments 
        '''

        ##check if the file exist
        if os.path.isfile(self.args.file):

            ###load catalog
            cat = catscii.load_cat(self.args.file, False)
            spec = cat.get_column('Col1')
            noise = cat.get_column('Col2')
            redshift = cat.get_column('Col3')
            self.length_table = len(spec)

            ##set up row number
            self.table.setRowCount(self.length_table)

            ##fill it with data
            for i,spectrum in enumerate(spec):
                self.table.setItem(i, 0, QTableWidgetItem(spectrum))
                self.table.setItem(i, 1, QTableWidgetItem(noise[i]))
                self.table.setItem(i, 2, QTableWidgetItem(redshift[i]))

            ###adjust column width
            self.table.resizeColumnsToContents()

    def crosshair(self, event):
        '''
        draw the cross hair of in the plot and update the coordinates
        '''
        if event.xdata is not None and event.ydata is not None:
            ###we remove the lines first
            if len(self.crosshair_lines) > 0:
                for i in self.crosshair_lines:
                    i.remove()
                self.crosshair_lines = []

            ##get the position of the line
            ix, iy = float(event.xdata), float(event.ydata)

            ##draw the crosshair
            line_x = self.plot.axhline(iy, lw=0.5, color='blue', ls='--')
            line_y = self.plot.axvline(ix, lw=0.5, color='blue', ls='--')
            self.crosshair_lines.append(line_x)
            self.crosshair_lines.append(line_y)

            ##and redraw
            self.win.draw()
            self.win.flush_events()

    def get_limits(self, event):
        '''
        SAve the x coordinates in case the mouse button is clicked
        in case two clicks are down, cut the spectrum and display it
        '''
        if event.xdata is not None and event.ydata is not None:

            if self.x1.text() == '----':
                self.x1.setText(str(event.xdata))
                self.x1.setStyleSheet("color: red")
            elif self.x2.text() == '----':
                self.x2.setText(str(event.xdata))
                self.x2.setStyleSheet("color: red")
                ###if we set the second limit then we can plot the
                ###to-be-saved spectum
                self.cut_spectrum(self.spectrum_path)
            else:
                self.x1.setText('----')
                self.x1.setStyleSheet("color: black")
                self.x2.setText('----')
                self.x2.setStyleSheet("color: black")
                ##remove cut spectrum
                for i in self.cut_spectrum_plots:
                    i.remove()
                self.cut_spectrum_plots = []
                self.win.draw()

    def onDoubleClick(self):
        '''
        On double click on the table, the
        corresponding spectrum is displayed
        '''
        ##save selected row
        self.counter_table = self.table.currentRow()

        ###get spectrum from table
        spectrum = self.table.item(self.table.currentRow(), 0).text()
        noise_spectrum = self.table.item(self.table.currentRow(), 1).text()

        ##add path
        self.spectrum_path = os.path.join(self.original_folder, spectrum)
        self.noise_spectrum_path = os.path.join(self.original_folder, noise_spectrum)

        ##open it and display it
        if os.path.isfile(self.spectrum_path):
            self.open_spec_and_display(self.spectrum_path, self.noise_spectrum_path)
 

        ##check if a cut spectrum is there, if yes display it
        spec_name, extension = os.path.splitext(spectrum)
        cut_name = os.path.join(self.saved_directory, spec_name + '_cut.ascii')
        if os.path.isfile(cut_name):
            cut_spec = catscii.load_cat(cut_name, False)
            self.cutx = cut_spec.get_column('Col1', float)
            self.cuty = cut_spec.get_column('Col2', float)
            self.cuty_noise = cut_spec.get_column('Col3', float)
            cut = self.plot.plot(self.cutx, self.cuty, color='r', lw='0.7')
            self.win.draw()
            self.cut_spectrum_plots.append(cut[0])
            self.x1.setText(str(min(self.cutx)))
            self.x2.setText(str(max(self.cutx)))
            self.x1.setStyleSheet("color: red")
            self.x2.setStyleSheet("color: red")
 
        #recheck table to update the cut column   
        self.check_cut()

    def cut_spectrum(self, spectrum):
        '''
        cut the loaded spectrum to the limits self.x1, self.x2
        '''
        ##remove plot
        for i in self.cut_spectrum_plots:
            i.remove()
        self.cut_spectrum_plots = []
        self.win.draw()

        ###cut the spectrum
        if spectrum:
            self.cutx = []
            self.cuty = []
            self.cuty_noise = []
            for i in range(len(self.wave)):
                if float(self.x1.text())<self.wave[i]<float(self.x2.text()):
                    self.cutx.append(self.wave[i])
                    self.cuty.append(self.flux[i])
                    self.cuty_noise.append(self.noise[i])

            cut = self.plot.plot(self.cutx, self.cuty, color='r', lw='0.7')
            self.win.draw()
            self.cut_spectrum_plots.append(cut[0])
            


    def open_spec_and_display(self, path_to_spec, path_to_spec_noise):
        '''
        Open the spectrum and display it
        '''
        ##remove cut spectrum
        for i in self.cut_spectrum_plots:
            i.remove()
        self.cut_spectrum_plots = []

        ##reinitialize limits
        self.x1.setText('----')
        self.x2.setText('----')
        self.x1.setStyleSheet("color: black")
        self.x2.setStyleSheet("color: black")

        spec = fits.open(path_to_spec)
        spec_noise = fits.open(path_to_spec_noise)

        ##wavelength grid
        header = spec[0].header
        N = int(header['NAXIS1'])
        l0 = float(header['CRVAL1'])
        dl = float(header['CDELT1'])
        self.wave = numpy.linspace(l0, l0+N*dl, num=N)

        ##flux 
        self.flux = spec[0].data
        self.noise = spec_noise[0].data
        if isinstance(self.noise[0], numpy.ndarray):
            self.noise = self.noise[0]

        ##delete all previously displayed data
        for i in self.displayed:
            i.remove()
        self.displayed = []
        self.win.draw()

        ##plot
        plot = self.plot.plot(self.wave, self.flux, lw=1, color='0.8')
        self.plot.set_xlim(min(self.wave)-50, max(self.wave+50))
        self.plot.set_ylim(min(self.flux), max(self.flux))
        hor_line = self.plot.axhline(0, ls='--', color='k', lw=0.5)
        self.plot.title.set_text(path_to_spec.split('/')[-1])
        
        ###save it 
        self.displayed.append(plot[0])
        self.displayed.append(hor_line)

        self.figure.tight_layout()
        self.win.draw()
        
        
