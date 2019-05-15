# Interactive plotting program to display voltammograms produced by cyclic voltammetry
# using the KStat potentiostat and Hg-film electrodes
# 2019, Nico Fröhberg
# nfroeh@hawaii.edu

# files can be 'raw' from the KStat or filtered using KStat_noiseFilter.py
# place this script in folder with output csv files and run

# original skeleton of this script retrieved from https://matplotlib.org/gallery/user_interfaces/embedding_in_tk_sgskip.html

import matplotlib
matplotlib.use("TkAgg")
import tkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from pandas import Series, read_csv
from glob import glob
from peakutils import baseline
from scipy import signal
from os import remove

    
root = tkinter.Tk()
root.wm_title("KStat Voltammogram Analysis")

def iir_noise_filter(name, df, current_col):

    #extracting sampling rate from parameter file
    parafile = name + '-parameters.txt'
    try:
        params = read_csv(parafile, delim_whitespace=True, engine='python', names=['0','1','2','3'], index_col=0)
    except:
        print('Cannot find parameter file')
    samplerate = params['2']['Samplerate']
    Samplingrates = {"2.5Hz":2.5, "5Hz":5.0, "10Hz":10.0, "15Hz":15.0,
                         "25Hz":25.0, "30Hz":30.0, "50Hz":50.0, "60Hz":60.0,
                         "100Hz":100.0, "500Hz":500.0, "1KHz":1000.0, "2KHz":2000.0,
                         "3.75KHz":3750.0, "7.5KHz":7500.0, "15KHz":1500.0, "30KHz":30000.0}
    samplerate = Samplingrates[samplerate]

    #constructing IIR notch filters
    fs = samplerate   # Sample frequency (Hz)
    f0 = 60.0  # Frequency to be removed from signal (Hz)
    Q = 2.0  # Quality factor
    # Design notch filter
    b, a = signal.iirnotch(f0, Q, fs)
    c, d = signal.iirnotch(f0*2, Q, fs)
    e, f = signal.iirnotch(f0*4, Q, fs)
    g, h = signal.iirnotch(f0*5, Q, fs)
    i, j = signal.iirnotch(f0*6, Q, fs)
    
    #apply filters
    yf1 = signal.filtfilt(b,a,df[current_col]) #60Hz filter
    yf2 = signal.filtfilt(c,d,yf1) #120Hz filter
    yf3 = signal.filtfilt(e,f,yf2) #240Hz filter
    yf4 = signal.filtfilt(g,h,yf3) #300Hz filter
    yf5 = signal.filtfilt(i,j,yf4) #360Hz filter

    return yf5

def change_vgram():
    global peak_current, noise_filter, name, files, file_index, canvas, ax
    global vgramfwd, vgrambslrm, vgrambwd, vgrambsl, bsl_poly_box, first
    global dyn, x_pts, y_pts, fwdbwd_i, bsl_i, bsl_poly, rescale
    files = glob('*.csv')
    file = files[file_index]
    
    name = file[0:-4]
    df = read_csv(file)

    peak_current = 0
    # check if data are filtered or not (column names change after filtering from the original KStat output
    if 'Potential' in df.columns:
        df.CurrentFiltered = df.CurrentFiltered * -1
        potential_col = 'Potential'
    else:
        potential_col = 'potential'
    if 'CurrentFiltered' in df.columns:
        current_col = 'CurrentFiltered'
    else:
        current_col = 'current'
        df.current = df.current *-1

    if noise_filter:
        df['CurrentIIR'] = iir_noise_filter(name, df, current_col)
        current_col = 'CurrentIIR'

    #split scan into forward and backward scans   
    fwd = df[1:df[potential_col].idxmin()+1]
    bwd = df[df[potential_col].idxmin():]

    # remove previous current & baseline plots if existing and clear points, lines etc created by user
    # not executed in first iteration
    if not first:
        try:
            vgramfwd.remove()
        except:
            pass
        try:
            vgrambwd.remove()
        except:
            pass
        try:
            vgrambsl.remove()
        except:
            pass
        try:
            vgrambslrm.remove()
        except:
            pass
        for element in dyn:
            element.remove()
        dyn = []
        x_pts = []
        y_pts = []

    # set plot parameters    
    else:
        ax.invert_xaxis()
        plt.xlabel('Potential [mV]')
        plt.ylabel('Current [nA]')

    # update plot title to current name
    plt.title(name)

    # Plot current according to forward/backward mode if not in baseline subtraction mode
    if (fwdbwd_i == 0 or fwdbwd_i == 1) and bsl_i != 2:
        vgramfwd, = ax.plot(fwd[potential_col], fwd[current_col]*1000000000, color= '#0039ca')
    if (fwdbwd_i == 0 or fwdbwd_i == 2) and bsl_i != 2:
        vgrambwd, = ax.plot(bwd[potential_col], bwd[current_col]*1000000000, color = '#6487e1')

    # baseline plotting: 
    if bsl_i != 0:
        # get polynomial degree from text box
        try:
            bsl_poly = int(bsl_poly_box.get())
        except:
            pass

        #compute baseline
        bsl_df = Series(baseline(fwd[current_col], deg=bsl_poly, max_it=100, tol=.0000001))

        # plot baseline with current or subtract it from current depending on baseline mode
        if bsl_i == 1:
            vgrambsl, = ax.plot(fwd[potential_col], bsl_df*1000000000, color= '#be6b12')
        if bsl_i == 2:
            bslrmvd = (fwd[current_col] - bsl_df).drop(0)
            vgrambslrm, = ax.plot(fwd[potential_col], bslrmvd*1000000000, color= '#0039ca')
    if rescale:      
        # rescale the axes to fit the data (normally automatic but does not work fully in all instances)
        ax.relim()
        ax.autoscale()
        rescale = False
    first = False
    canvas.draw()

#################################################################################
# declare global variables

file_index = 0
first = True
x_pts = []
y_pts = []
dyn = []
fwdbwd_i = 0
bsl_i = 0
bsl_poly = 8
noise_filter = False
peak_current = 0
rescale = False

fig = plt.figure()
ax = fig.add_subplot(111)

#################################################################################
# set up canvas and toolbar

# The program is set up in a grid of 5 columns & 4 rows
# The plot takes up the middle 3 columns of the first row and adapts to window size
canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.draw()
canvas.get_tk_widget().grid(row =1, column = 2, columnspan=3, sticky = 'nsew')

tkinter.Grid.columnconfigure(root, 2, weight=1)
tkinter.Grid.columnconfigure(root, 3, weight=1)
tkinter.Grid.columnconfigure(root, 4, weight=1)
tkinter.Grid.rowconfigure(root, 1, weight=1)

# Matplotlib toolbar (zoom, pan etc)
toolbar_frame = tkinter.Frame(root)
toolbar_frame.grid(row=2, column = 2, columnspan=3, sticky = 'W')
toolbar = NavigationToolbar2Tk( canvas, toolbar_frame )
toolbar.update()

# initialize plot
change_vgram()

#################################################################################
# Button to end program:

def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate


quit_button = tkinter.Button(master=root, text="Quit\nProgram", command=_quit,
                             background = '#d33f3f', width = 6)
quit_button.grid(row=4, column=5, sticky='SE')

#################################################################################
# Button to delete current file:

def delete(event = ''):
    global name
    remove(name+'.csv')
    remove(name+'.png')
    remove(name+'-parameters.txt')
    change_vgram()

quit_button = tkinter.Button(master=root, text='Delete\nFile', command=delete,
                             background = '#d33f3f', width = 6)
quit_button.grid(row=4, column=1, sticky='W')

#################################################################################
# Button to activate 60Hz filter:

def iir_filter():
    global filter_button, noise_filter
    if not noise_filter:
        filter_button.config(background = '#00790c')
        noise_filter = True
    else:
        filter_button.config(background = '#66cc70')
        noise_filter = False
    change_vgram()

filter_button = tkinter.Button(master=root, text="60 Hz  IIR filter",
                               command=iir_filter, background = '#66cc70')
filter_button.grid(row=4, column=3, sticky='N')

#################################################################################
# Button to autoscale axes:

def rescale_bt():
    global rescale
    rescale = True
    change_vgram()

rescale_button = tkinter.Button(master=root, text="Rescale\nAxes",
                               command=rescale_bt)
rescale_button.grid(row=1, column=1, sticky='SE')

#################################################################################
# Button to change to next file:

def next_file(event=''):
    global file_index, files
    file_index = file_index + 1
    if file_index >= len(files):
        file_index = 0
    change_vgram()
    
next_button = tkinter.Button(master=root, text="►", command=next_file,
                             height = 1, width = 2)
next_button.config(font=('helvetica', 25))
next_button.grid(row=1, column=5, sticky='E')

#################################################################################
# Button to change to previous file:

def previous_file(event=''):
    global file_index, files
    file_index = file_index - 1
    if file_index < 0:
        file_index = len(files)-1
    change_vgram()
    
previous_button = tkinter.Button(master=root, text="◄", command=previous_file,
                                 height = 1, width = 2)
previous_button.config(font=('helvetica', 25))
previous_button.grid(row=1, column=1, sticky='W')

#################################################################################
# Button to change forward/backward current view

def fwdbwd():
    global fwdbwd_i, fwdbwd_button, bsl_i, bsl_button

    # Setting mode: 0 = forward & backward current, 1 = only forward, 2 = only backward
    fwdbwd_i = fwdbwd_i +1
    if fwdbwd_i > 2:
        fwdbwd_i = 0

    # changing baseline mode to be compatible with forward/backward mode
    if bsl_i == 2:
        bsl_i = 1
        bsl_button.config(text="Baseline")
    if fwdbwd_i ==2 and bsl_i == 1:
        bsl_i = 0
        bsl_button.config(text="No Baseline")

    # updating button label
    if fwdbwd_i == 0:
        fwdbwd_button.config(text="Forward & Backward\nCurrent")
    elif fwdbwd_i == 1:
        fwdbwd_button.config(text="Forward\nCurrent")
    else:
        fwdbwd_button.config(text="Backward\nCurrent")
    change_vgram()
    
fwdbwd_button = tkinter.Button(master=root, text="Forward & Backward\nCurrent",
                               command=fwdbwd, height = 2, width = 17)
fwdbwd_button.config(font=('helvetica', 14))
fwdbwd_button.grid(row=3, column=2, sticky='W')

#################################################################################
# Button to change whether or not to display or subtract a polynomially fitted baseline

def bsl():
    global bsl_i, bsl_button, fwdbwd_i, fwdbwd_button
    
    # Setting Mode: 0 = no baseline, 1 = baseline displayed with current, 2 = baseline subtracted from current
    bsl_i = bsl_i +1
    if bsl_i > 2:
        bsl_i = 0
        
    # Changing forward/backward current view to be compatible with showing baseline (baseline is only computed for froward current)
    if fwdbwd_i == 2 and bsl_i == 1:
        bsl_i = 2
        fwdbwd_i = 1
        fwdbwd_button.config(text="Forward\nCurrent")

    # Updating Button label
    if bsl_i == 0:
        bsl_button.config(text="No Baseline")
    elif bsl_i == 1:
        bsl_button.config(text="Baseline")
    else:
        bsl_button.config(text="Baseline subtracted")
        fwdbwd_i = 1
        fwdbwd_button.config(text="Forward\nCurrent")
    change_vgram()

bsl_button = tkinter.Button(master=root, text="No Baseline", command=bsl, height = 2, width = 17)
bsl_button.config(font=('helvetica', 14))
bsl_button.grid(row=3, column=4, sticky='E')

#################################################################################
# Text box to enter polynomial degree for baseline fitting:

def bsl_entry(event):
    global bsl_poly, bsl_i, bsl_button
    try:
        bsl_poly = int(event.widget.get())
        if bsl_i == 0:
            bsl_i = 1
            bsl_button.config(text="Baseline")
        change_vgram()
        canvas.get_tk_widget().focus_force()
    except Exception as e:
        print(e)

labelDir=tkinter.Label(master = root, text='Baseline polynomial degree')
labelDir.grid(row=3, column=3, sticky='N')

bsl_poly_box = tkinter.Entry(master = root, justify = 'center', width=3)
bsl_poly_box.insert(10, str(bsl_poly))
bsl_poly_box.config(font=('helvetica', 14))
bsl_poly_box.bind('<Return>', bsl_entry)
bsl_poly_box.grid(row=3, column=3)

#################################################################################
# Button save current of selected peak to file:

def save_peak():
    global peak_current, name
    parafile = name + '-parameters.txt'
    try:
        params = read_csv(parafile, delim_whitespace=True, engine='python', names=['0','1','2','3'], index_col=0)
    except:
        print('Cannot find parameter file')
    slope = params['2']['slope']
    f = open('peaks.csv', 'a')
    f.write('\n{},{:.3f},{}'.format(name, peak_current, slope))
    f.flush()
    f.close()
    
peak_button = tkinter.Button(master=root, text="Save\nPeak", command=save_peak,
                             width = 6)
peak_button.grid(row=1, column=1, sticky='NE')

#################################################################################
# Adding points at leftclick location in plot, displaying vertical difference between two points
# Removing last point on right click

def onpick(event):
    global canvas, ax, x_pts, y_pts, dyn, toolbar, peak_current
    #checking that click was in plot area and no toolbar button (zoom etc) is activated
    if event.inaxes and toolbar.mode == '':
        m_button = event.button
        global x_pts
        global y_pts
        global dyn

        #right click removes last added point:
        if m_button == 3:
            if len(x_pts) == 1:
                for element in dyn:
                    element.remove()
                dyn=[]
            else:
                for element in dyn[-4:]:
                    element.remove()
                dyn = dyn[0:-4]
            x_pts = x_pts[0:-1]
            y_pts = y_pts[0:-1]
            
        # left click adds point   
        elif m_button == 1:
            
            #when there already are two points, remove them and start a new one
            if len(x_pts) >= 2:
                for element in dyn:
                    element.remove()
                dyn = []
                y_pts = []
                x_pts = []
                
            # get mouse coordinates and save in list
            m_x, m_y = event.x, event.y
            x, y = ax.transData.inverted().transform([m_x, m_y])
            x1, y1= ax.transAxes.inverted().transform([m_x, m_y])
            if y1 >= 0:
                x_pts.append(x)
                y_pts.append(y)
                
                # add horizontal line and point at mouse position
                dyn.append(ax.hlines(y_pts, -1850, -100))
                dyn.append(ax.scatter(x_pts, y_pts, c = 'black', s = 10))

                # when a second point is added, connect horizontal lines with vertical lines and display vertical distance
                if len(x_pts) >= 2:
                    dyn.append(ax.vlines(x = (x_pts[0]+x_pts[1])/2, ymin = y_pts[0], ymax = y_pts[1]))
                    props = dict(boxstyle='round', facecolor='grey', alpha=0.5)
                    peak_current = y_pts[1]-y_pts[0]
                    dyn.append(ax.text(0.05, 0.95, '{:.3f} nA'.format(peak_current),
                                        transform=ax.transAxes, fontsize=14,verticalalignment='top', bbox=props))
        canvas.draw()

canvas.mpl_connect('button_press_event', onpick)

#################################################################################
# Manage Keyboard inpput

def on_key_press(event):

    #Matplotlib Toolbar keybindings:
    key_press_handler(event, canvas, toolbar)


canvas.get_tk_widget().bind("<Left>", previous_file)
canvas.get_tk_widget().bind("<Right>", next_file)
canvas.get_tk_widget().bind("<Delete>", delete)
canvas.mpl_connect("key_press_event", on_key_press)

#################################################################################
        
tkinter.mainloop()
