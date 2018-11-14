import tkinter.ttk
from tkinter import *
from functools import partial
import matplotlib.pyplot as plot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

seqText = 'Enter a sequence (Ex: AABCC)'
matchText = 'Enter match (Int ≥ 0)'
mismatchText = 'Enter mismatch (Int ≤ 0)'
gapText = 'Enter gap (Int ≤ 0)'
allowedStrings = [seqText, matchText, mismatchText, gapText]
errorLbl = None

def main():
    window = Tk()
    window.geometry("520x320")
    window.title("Global Sequence Alignment")
    window.grid_rowconfigure(0, weight=1)

    ##  Create frames
    frameLeft = Frame(window)
    frameLeft.grid(row=0, column=0, sticky=NS)
    frameMid = Frame(window)
    frameMid.grid(row=0, column=1, sticky=NS)
    frameMid.rowconfigure(0, weight=1)
    frameRight = Frame(window)
    frameRight.grid(row=0, column=2, sticky=NS)

    ##  Entry for the first sequence
    seqEntry1 = Entry(frameLeft, fg='light grey', relief=FLAT, width=26)
    seqEntry1.insert(0, seqText)
    seqEntry1.grid(row=1, column=0, pady=(60,0), padx=(10,10))
    seqEntry1.bind('<FocusIn>', partial(onFocusIn, seqEntry1))
    seqEntry1.bind('<FocusOut>', partial(onFocusOut, seqEntry1, 'S'))

    ##  Entry for the second sequence
    seqEntry2 = Entry(frameLeft, fg='light grey', relief=FLAT, width=26)
    seqEntry2.insert(0, seqText)
    seqEntry2.grid(row=2, column=0, pady=(5,0), padx=(10,10))
    seqEntry2.bind('<FocusIn>', partial(onFocusIn, seqEntry2))
    seqEntry2.bind('<FocusOut>', partial(onFocusOut, seqEntry2, 'S'))

    ##  Match entry
    match = Entry(frameLeft, fg='light grey', relief=FLAT, width=26)
    match.insert(0, matchText)
    match.grid(row=3, column=0, pady=(5,0), padx=(10,10))
    match.bind('<FocusIn>', partial(onFocusIn, match))
    match.bind('<FocusOut>', partial(onFocusOut, match, 'M'))

    ##  Mismatch entry
    mismatch = Entry(frameLeft, fg='light grey', relief=FLAT, width=26)
    mismatch.insert(0, mismatchText)
    mismatch.grid(row=4, column=0, pady=(5,0), padx=(10,10))
    mismatch.bind('<FocusIn>', partial(onFocusIn, mismatch))
    mismatch.bind('<FocusOut>', partial(onFocusOut, mismatch, 'I'))

    ##  Gap entry
    gap = Entry(frameLeft, fg='light grey', relief=FLAT, width=26)
    gap.insert(0, gapText)
    gap.grid(row=5, column=0, pady=(5,0), padx=(10,10))
    gap.bind('<FocusIn>', partial(onFocusIn, gap))
    gap.bind('<FocusOut>', partial(onFocusOut, gap, 'G'))

    ##  Submit button
    submitBtn = Button(frameLeft, text='Submit', cursor='hand2')
    submitBtn.config(command=partial(submit, frameLeft, frameRight, seqEntry1, seqEntry2, match, mismatch, gap))
    submitBtn.grid(row=6, column=0, pady=(5,0), padx=(10,10))

    ##  Separator
    sep = ttk.Separator(frameMid, orient=VERTICAL)
    sep.grid(row=0, column=1, pady=(20,20), padx=(10,10), sticky=NS)

    window.mainloop()

##  Remove placeholder text when the user focuses in
def onFocusIn(entry, e):
    if entry.get() in allowedStrings:
        entry.delete(0, END)
    entry.config(fg='black')

##  Replace placeholder text if the user focuses out and no input was given
def onFocusOut(entry, entryType, e):
    if entry.get() == '':
        if entryType == 'S':
            entry.insert(0, seqText)
        elif entryType == 'M':
            entry.insert(0, matchText)
        elif entryType == 'I':
            entry.insert(0, mismatchText)
        elif entryType == 'G':
            entry.insert(0, gapText)
            
        entry.config(fg='light grey')

##  Check that user entries are valid
def checkEntries(seqEntry1, seqEntry2, match, mismatch, gap):
    valid = True
    err = ''

    ##  Check that sequences are alphanumeric
    if not (seqEntry1.get().isalnum() and seqEntry2.get().isalnum()):
        valid = False
        err = 'ERROR: Sequences must be alphanumeric.'
    try:
        ##  Match must be an integer >= 0
        if int(match.get()) < 0:
            valid = False
            err = 'ERROR: Match must be an integer ≥ 0.'
        ##  Mismatch must be an integer <= 0
        elif int(mismatch.get()) > 0:
            valid = False
            err = 'ERROR: Mismatch must be an integer ≤ 0.'
        ##  Gap must be an integer <= 0
        elif int(gap.get()) > 0:
            valid = False
            err = 'ERROR: Gap must be an integer ≤ 0.'
    except:
        valid = False
        err = 'ERROR: Match, mismatch, and gap must be integers.'

    return valid, err

##  Remove any existing errors and display the new error (if there is one)
def displayError(frameLeft, valid, err):
    global errorLbl
    
    if errorLbl is not None:
        errorLbl.destroy()

    if valid == False:
        errVar = StringVar()
        errVar.set(err)

        errorLbl = Label(frameLeft, textvariable=errVar, fg='red', wraplength=160)
        errorLbl.grid(row=7, column=0, pady=(10,0))

##  Each element in the matrix is a Cell object
##  Value is the integer value of the cell
##  PointsTo is a list of Cells that the cell's value came from (the "arrows")
class Cell:
    def __init__(self, value, pointsTo):
        self.value = value
        self.pointsTo = pointsTo

    def __repr__(self):
        return str(self.value)

##  Initialize the first row and column of the matrix
def initializeMatrix(seq1, seq2, gap):
    ##  Create a blank matrix; Add one extra space to the length of the sequences
    matrix = [0] * (len(seq1) + 1)
    for i in range (0, len(matrix)):
        matrix[i] = [0] * (len(seq2) + 1)

    ##  Set top-left cell's value to 0
    matrix[0][0] = Cell(0, [])

    ##  Fill first column and row
    for i in range(1, len(matrix)):
        matrix[i][0] = Cell(matrix[i-1][0].value + gap, matrix[i-1][0])
    for j in range(1, len(matrix[0])):
        matrix[0][j] = Cell(matrix[0][j-1].value + gap, matrix[0][j-1])

    return matrix

##  Determine if two sequence characters match
def same(i, j, seq1, seq2):
    if seq1[i-1] == seq2[j-1]:
        return True
    return False

##  Fill the matrix
def fillMatrix(matrix, match, mismatch, gap, seq1, seq2):
    for i in range(1, len(matrix)):
        for j in range(1, len(matrix[0])):
            ##  Calculate values from all 3 neighbors
            s = same(i, j, seq1, seq2)
            if s == True:
                s = match
            else:
                s = mismatch
            diagonal = matrix[i-1][j-1].value + s
            above = matrix[i][j-1].value + gap
            beside = matrix[i-1][j].value + gap

            ##  Store values in array and calculate the max
            array = [diagonal, above, beside]
            value = max(array)

            ##  Determine which neighbors produced the max values; Add to pointsTo
            pointsTo = []
            if array[0] == value:
                pointsTo.append(matrix[i-1][j-1])
            if array[1] == value:
                pointsTo.append(matrix[i][j-1])
            if array[2] == value:
                pointsTo.append(matrix[i-1][j])

            matrix[i][j] = Cell(value, pointsTo)

    return matrix

##  Create image of matrix and display it in the UI
def createPlot(frameRight, matrix, seq1, seq2):
    ##  Add extra space to sequences
    seq1 = '-' + seq1
    seq2 = '-' + seq2

    figure = plot.figure()
    chart = figure.add_subplot(111)

    ##  Create and format ticks
    xlim = len(seq1)
    ylim = len(seq2)

    chart.set_xlim(left=0, right=xlim)
    chart.set_ylim(bottom=ylim, top=0)
    chart.xaxis.tick_top()
    chart.set_xticks(range(0, xlim, 1))
    chart.set_yticks(range(0, ylim, 1))
    chart.set_xticks([i+0.5 for i in range(0, xlim)], minor=True)
    chart.set_yticks([i+0.5 for i in range(0, ylim)], minor=True)
    chart.xaxis.set_major_formatter(plot.NullFormatter())
    chart.yaxis.set_major_formatter(plot.NullFormatter())
    chart.set_xticklabels(list(seq1), minor=True)
    chart.set_yticklabels(list(seq2), minor=True)
    chart.tick_params(axis='both', which='minor', length=0, width=0)
    chart.grid(True)

    ##  Add values of matrix in plot
    for i in range(0, len(matrix)):
        for j in range(0, len(matrix[0])):
            x = i + 0.5
            y = j + 0.5
            chart.text(x, y, matrix[i][j].value, ha='center', va='center', color='blue')

    ##  Display the plot in the UI
    canvas = FigureCanvasTkAgg(figure, master=frameRight)
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=2, padx=(10,10), pady=(10,0))
    canvas.get_tk_widget().config(width=300, height=300)

##  Submit input and run the algorithm
def submit(frameLeft, frameRight, seqEntry1, seqEntry2, match, mismatch, gap):
    ##  Check user input
    valid, err = checkEntries(seqEntry1, seqEntry2, match, mismatch, gap)
    displayError(frameLeft, valid, err)

    if valid == True:
        ##  Initialize and fill the matrix
        matrix = initializeMatrix(seqEntry1.get(), seqEntry2.get(), int(gap.get()))
        matrix = fillMatrix(matrix, int(match.get()), int(mismatch.get()),
                            int(gap.get()), seqEntry1.get(), seqEntry2.get())
        createPlot(frameRight, matrix, seqEntry1.get(), seqEntry2.get())

if __name__ == '__main__':
    main()
