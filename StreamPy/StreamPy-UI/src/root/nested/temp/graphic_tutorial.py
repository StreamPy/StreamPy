# Import for drawing
from Tkinter import *

# Set up for drawing

# Create a canvas to draw on
#aCanvas = Canvas(aTk, width=400, height=400)
#aCanvas.pack()

# Draw several shapes in different colours

def make_oval(aCanvas):
    aCanvas.create_oval(50, 100, 360, 390, fill="blue")
    aCanvas.create_polygon(10, 100, 60, 0, 110, 100, fill="yellow", outline="blue")
    
    
def make_rect(aCanvas, w, h, x, y):
    aCanvas.create_rectangle(h, w, x, y, fill="orange")
    

def finish(aCanvas):
    mainloop()

# Issue: want this to only fire once


def rep():
    for i in range(5):
        aCanvas = Canvas(Tk(), width=400, height=400)
        aCanvas.pack()
        make_oval(aCanvas)
        make_rect(aCanvas, 100, 10, i * 50, i * 30)
        print i
        mainloop()
# Issue: want this to only fire once

#rep()
###################################
import matplotlib.pyplot as plt

def consecutive_ints(curr_num):
    return curr_num + 1

def show(curr_num, stop_num):
    
    if curr_num == stop_num:
        print str(curr_num) + ' is' + str(stop_num)
        plt.show()
    
def make_shapes(curr_num):
    j = curr_num * 0.01
    plt.xticks(())
    plt.yticks(())
    
    circle = plt.Circle((j, j), radius=0.2, fc='y')
    plt.gca().add_patch(circle)
    
    rectangle = plt.Rectangle((j, j), 1, .1, fc='r')
    plt.gca().add_patch(rectangle)
    #points = [[2, 1], [8, 1], [8, 4]]
    points = [[1 * j, 1 * j], [3 * j, 1 * j], [2 * j, 4 * j]]
    polygon = plt.Polygon(points, fill='r')
    plt.gca().add_patch(polygon)


def make_rec():
    fig = plt.figure()
    ax = fig.add_subplot(111)
    rect = ax.patch  # a Rectangle instance
    rect.set_facecolor('green')

    fig.canvas.draw()

def make_rec2():
    figure, ax = plt.subplots()
    figure.canvas.draw()
    figure.canvas.flush_events()

def run():
    curr_num = 0
    for i in range(5):
        #curr_num = consecutive_ints(curr_num)
        #make_shapes(curr_num)
        make_rec2()
        #show(i, 5)

#run()

def animation():
    """
    Pyplot animation example.
    
    The method shown here is only for very simple, low-performance
    use.  For more demanding applications, look at the animation
    module and the examples that use it.
    """
    
    import matplotlib.pyplot as plt
    import numpy as np
    

    for i in xrange(5):
        plt.xticks(())
        plt.yticks(())
        x = np.zeros((6,), dtype=np.int)
        y = np.zeros((5,), dtype=np.int)
        z = x * y[:,np.newaxis]
        print z
        if i==0:
            #p = plt.imshow(z)
            p = plt.imshow(z)
            fig = plt.gcf()
            plt.clim()   # clamp the color limits
            plt.title("Boring slide show")
        else:
            j = i * 0.5
            rectangle = plt.Rectangle((j, j), 1, .1, fc='r')
            plt.gca().add_patch(rectangle)
            #z = z + 2
            #p.set_data(z)
    
        print("step", i)
        plt.pause(0.5)
#animation()

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, Polygon
import numpy as np

def make_canvas():
    plt.xticks(())
    plt.yticks(())
    x = np.ones((6,), dtype=np.int)
    y = np.ones((5,), dtype=np.int)
    z = x * y[:,np.newaxis]
    p = plt.imshow(z)
    #fig = plt.gcf()
    plt.title("Fun with shapes!")
    return plt


def make_rectangle(plt):
    j = i * 0.5
    rectangle = plt.Rectangle((j, j), 1, .1, fc='r')
    plt.gca().add_patch(rectangle)
    plt.pause(0.5)

def make_triangle(plt):
    j = i * 0.5
    points = [[1 * j, 1 * j], [3 * j, 1 * j], [2 * j, 4 * j]]
    polygon = plt.Polygon(points, fill='r')
    plt.gca().add_patch(polygon)
    plt.pause(0.5)

def make_circle(x, y, radius):
    circle = plt.Circle((x, y), radius=radius, fc='pink', linewidth=0)
    return circle

def show_shape(shape):
    plt.gca().add_patch(shape)
    plt.pause(0.5)

def make_donut(plt):
    j = i * 0.5
    donut = Wedge((j,j), .2, 0, 360, width=0.05, fc='pink', alpha = 0.5)
    plt.gca().add_patch(donut)
    
def make_polygon(plt):
    polygon = Polygon(np.random.rand(3,2), True)
    plt.gca().add_patch(polygon)
    
for i in range(5):
    #make_rectangle(make_canvas())
    make_canvas()
    show_shape(make_circle(i, i * 2, i))
    #make_triangle(make_canvas())
    #make_donut(make_canvas())
    #make_polygon(make_canvas())
    
'''
import numpy as np
import pylab as pl
n = 1024
X = np.random.normal(0, 1, n)
Y = np.random.normal(0, 1, n)
T = np.arctan2(Y, X)

pl.axes([0.025, 0.025, 0.95, 0.95])
pl.scatter(X, Y, s=100, c=T, alpha=.5)

pl.xlim(-1.5, 1.5)
pl.xticks(())
pl.ylim(-1.5, 1.5)
pl.yticks(())

pl.show()
'''

'''
from pylab import *
import time
    
ion()

tstart = time.time()               # for profiling
x = arange(0,2*pi,0.01)            # x-array
line, = plot(x,sin(x))
for i in arange(1,200):
    line.set_ydata(sin(x+i/10.0))  # update the data
    draw()                         # redraw the canvas
   
print 'FPS:' , 200/(time.time()-tstart)
'''