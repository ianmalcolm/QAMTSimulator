import numpy as np

from matplotlib import pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches


# borrowed from https://medium.com/@thepyprogrammer/2d-image-convolution-with-numpy-with-a-handmade-sliding-window-view-946c4acb98b4
def convolve(image, kernel, op=None, agg=None):
    """ 2d image convolution with customised operator and aggregation
        In tradition convolution, it is element wise multiplication plus
        summation. But you can use np.logcial_xor for op, and
        lambda x: np.all(x, axis=(2,3)) for agg.
    """
    
    # We start off by defining some constants, which are required for this code
    kernelH, kernelW = kernel.shape
    imageH, imageW = image.shape
    h, w = imageH + 1 - kernelH, imageW + 1 - kernelW
    
    # filter1 creates an index system that calculates the sum of the x and y indices at each point
    # Shape of filter1 is h x kernelW
    filter1 = np.arange(kernelW) + np.arange(h)[:, np.newaxis]
    
    # intermediate is the stepped data, which has the shape h x kernelW x imageH
    intermediate = image[filter1]
    
    # transpose the inner dimensions of the intermediate so as to enact another filter
    # shape is now h x imageH x kernelW
    intermediate = np.transpose(intermediate, (0, 2, 1))
    
    # filter2 similarly creates an index system
    # Shape of filter2 is w * kernelH
    filter2 = np.arange(kernelH) + np.arange(w)[:, np.newaxis]
    
    # Apply filter2 on the inner data piecewise, resultant shape is h x w x kernelW x kernelH
    intermediate = intermediate[:, filter2]
    
    # transpose inwards again to get a resultant shape of h x w x kernelH x kernelW
    intermediate = np.transpose(intermediate, (0, 1, 3, 2))
    
    # piecewise multiplication with kernel
    product = op(intermediate, kernel) if op else intermediate * kernel
    
    # find the sum of each piecewise product, shape is now h x w
    convolved = agg(product) if agg else product.sum(axis = (2,3))
    
    return convolved


def plotTime(inst, labels=None, ax=None):
    """ Given an instruction, plot time v.s. resource utilisation
    """
    
    if ax is None:
        fig, ax = plt.subplots()

    t_start = inst.time_start
    t_end   = inst.time_end
    t_program = inst.time_program
    t_sample = inst.time_sample
    t = t_start + 0
    
    labels = labels or [t.name for t in inst.getTasks()]
    allocs = inst.getAllocs()
    total = allocs[0].size
    usage = sum(a.sum() for a in allocs) / total
    per_usage = [a.sum() / total for a in allocs]
    cdf_usage = [0] + [sum(per_usage[:i]) for i in range(1, len(per_usage)+1)]
    
    if t_program > 0:
        rect = mpatches.Rectangle((t, 0), t_program, usage, facecolor='gray', edgecolor='k')
        ax.add_patch(rect)
        t += t_program
        
    if t_sample > 0:
        for n, u_start, u in zip(labels, cdf_usage[:-1], per_usage):
            rect = mpatches.Rectangle((t, u_start), t_sample, u, fill=False)
            ax.add_patch(rect)
            rx, ry = rect.get_xy()
            cx = rx + rect.get_width()/2.0
            cy = ry + rect.get_height()/2.0
            ax.annotate(n, (cx, cy), ha='center', va='center')

    ax.set_xlim([min(p.get_x() for p in ax.patches), max(p.get_x()+p.get_width() for p in ax.patches)])
    ax.set_ylim([0, 1])

    return ax


def findCorners(alloc):
    """ Given a bitmap of allocation, find out all corners, in the form of
        type, row id, col id. The definition of the type of corners are

        c1q1: convex corner in quadrant 1
        c1q2: convex corner in quadrant 2
        c1q3: convex corner in quadrant 3
        c1q4: convex corner in quadrant 4
        c3qb1 concave corner in quadrant 1, complementary of c1q1
        c3qb2 concave corner in quadrant 2, complementary of c1q2
        c3qb3 concave corner in quadrant 3, complementary of c1q3
        c3qb4 concave corner in quadrant 4, complementary of c1q4
        
    """
    
    alloc_pad = np.pad(alloc, 1)

    corner_filters = [
        (['c1q1',  ]       ,  np.asarray([[0,1],[0,0]])),
        (['c1q2',  ]       ,  np.asarray([[1,0],[0,0]])),
        (['c1q3',  ]       ,  np.asarray([[0,0],[1,0]])),
        (['c1q4',  ]       ,  np.asarray([[0,0],[0,1]])),
        (['c1q1', 'c1q3', ],  np.asarray([[0,1],[1,0]])),
        (['c1q2', 'c1q4', ],  np.asarray([[1,0],[0,1]])),
        (['c3qb1', ]       ,  np.asarray([[1,0],[1,1]])),
        (['c3qb2', ]       ,  np.asarray([[0,1],[1,1]])),
        (['c3qb3', ]       ,  np.asarray([[1,1],[0,1]])),
        (['c3qb4', ]       ,  np.asarray([[1,1],[1,0]])),
    ]

    corners = []
    for names, filt in corner_filters:
        img = convolve(alloc_pad, 
                       filt, 
                       op=np.logical_xor, 
                       agg=lambda x: np.all(~x, axis=(2,3)))
        img = img.astype(int)
        for x, y in zip(*np.where(img==1)):
            for name in names:
                corners.append((name, x, y))

    return corners


def oppDir(d):
    """ Given n (north) return s, given e (east), return w.
    """
    assert d in ['n', 'w', 'e', 's'], f'Direction {d} not in news'
    if d == 'n':
        return 's'
    elif d == 's':
        return 'n'
    elif d == 'e':
        return 'w'
    else:
        return 'e'


def findNeighbourCorners(corner_a, corners):
    """ Given a corner in the form of (type, row_id, col_id), and a complete
        list of all corners, find its the two neighbour corners, which have
        direct connections with it. 
    """

    dir2cor = {
        ('n', 'l'): ['c1q2', 'c3qb1'],
        ('n', 'r'): ['c1q1', 'c3qb2'],
        ('s', 'l'): ['c1q3', 'c3qb4'],
        ('s', 'r'): ['c1q4', 'c3qb3'],
        ('e', 'u'): ['c1q1', 'c3qb4'], 
        ('e', 'd'): ['c1q4', 'c3qb1'], 
        ('w', 'u'): ['c1q2', 'c3qb3'], 
        ('w', 'd'): ['c1q3', 'c3qb2'], 
    }

    cor2dir = {
        'c1q1' : [('n', 'r'), ('e', 'u'),],
        'c1q2' : [('n', 'l'), ('w', 'u'),],
        'c1q3' : [('s', 'l'), ('w', 'd'),],
        'c1q4' : [('s', 'r'), ('e', 'd'),],
        'c3qb1': [('n', 'l'), ('e', 'd'),],
        'c3qb2': [('n', 'r'), ('w', 'd'),],
        'c3qb3': [('s', 'r'), ('w', 'u'),],
        'c3qb4': [('s', 'l'), ('e', 'u'),],
    }

    a_name, a_x, a_y = corner_a
    corner_bs = []
    for dir_news, dir_side in cor2dir[a_name]:
        if dir_news == 'n':
            cols = [(_n, _x, _y) for _n, _x, _y in corners if a_y == _y and a_x > _x]
            cols = sorted(cols, key=lambda x: abs(a_x - x[1]))
        elif dir_news == 's':
            cols = [(_n, _x, _y) for _n, _x, _y in corners if a_y == _y and a_x < _x]
            cols = sorted(cols, key=lambda x: abs(a_x - x[1]))
        elif dir_news == 'e':
            cols = [(_n, _x, _y) for _n, _x, _y in corners if a_x == _x and a_y < _y]
            cols = sorted(cols, key=lambda x: abs(a_y - x[2]))
        else:
            cols = [(_n, _x, _y) for _n, _x, _y in corners if a_x == _x and a_y > _y]
            cols = sorted(cols, key=lambda x: abs(a_y - x[2]))
        
        while cols:
            col_n, col_x, col_y = cols.pop(0)
            if col_n in dir2cor[oppDir(dir_news), dir_side]:
                corner_bs.append((col_n, col_x, col_y))
                break
        else:
            msg = f'({a_name}, {a_x}, {a_y}) cannot find neighbours in ({dir_news}, {dir_side})'
            raise RuntimeError(msg)
            
    return corner_bs


def findOutline(alloc):
    """ Given an allocation, find the outline (a list of corners). Each corner
        is in the form of (type, coordinate x, coordinate y), where the
        coordinate system is inverted in y axis, so that the origin is the top
        left corner.
    """
    corners = findCorners(alloc)
    corner_start = sorted(corners, key=lambda x: x[1]+x[2])[0]
    outline = [corner_start]
    while True:
        corner_bs = findNeighbourCorners(outline[-1], corners)
        if corner_bs[0] not in outline:
            outline.append(corner_bs[0])
        elif corner_bs[1] not in outline:
            outline.append(corner_bs[1])
        else:
            outline.append(outline[0])
            break
    outline = [(n, y, x) for n, x, y in outline]
    return outline


def findCenter(alloc):
    """ Given an allocation find the coordinate of the geometric center
    """
    xs, ys = np.where(alloc!=0)
    x_mean, y_mean = np.mean(xs) + 0.5, np.mean(ys) + 0.5
    return y_mean, x_mean


def shrink(corner, dist=0.1):
    """ move the corner inwards for dist distance
    """
    n, x, y = corner
    if n == 'c1q1':
        x += dist
        y -= dist
    elif n == 'c1q2':
        x -= dist
        y -= dist
    elif n == 'c1q3':
        x -= dist
        y += dist
    elif n == 'c1q4':
        x += dist
        y += dist
    elif n == 'c3qb1':
        x -= dist
        y += dist
    elif n == 'c3qb2':
        x += dist
        y += dist
    elif n == 'c3qb3':
        x += dist
        y -= dist
    else: # n == 'c3qb4':
        x -= dist
        y -= dist
    return n, x, y


def plotAlloc(alloc, label=None, dist=0.1, ax=None):
    """ Given an allocation, plot its polygon
    """

    outline = findOutline(alloc)
    outline = [shrink(o, dist) for o in outline]
    names, xs, ys = zip(*outline)
    if ax is None:
        fig, ax = plt.subplots()
        H, W = alloc.shape
        ax.set_xlim([0, W])
        ax.set_ylim([0, H])
        ax.invert_yaxis()
        ax.set_aspect('equal')
        ax.xaxis.set_major_locator(mtick.MaxNLocator(integer=True))
        ax.yaxis.set_major_locator(mtick.MaxNLocator(integer=True))
        ax.xaxis.tick_top()
    ax.fill(xs, ys, facecolor='lightgray', edgecolor='k')
    
    if label:
        ax.annotate(label, xy=findCenter(alloc), ha='center', va='center')

    return ax

    
def createAllocPlot(alloc):
    fig, ax = plt.subplots()
    H, W = alloc.shape
    ax.set_xlim([0, W])
    ax.set_ylim([0, H])
    ax.invert_yaxis()
    ax.set_aspect('equal')
    ax.xaxis.set_major_locator(mtick.MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(mtick.MaxNLocator(integer=True))
    ax.xaxis.tick_top()

    return fig, ax
