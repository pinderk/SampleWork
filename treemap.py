# CS 121: Drawing TreeMaps
#
# Code for constructing a treemap.
#
# YOUR NAME: Kyle Pinder

import sys
import csv
import json

from drawing import ChiCanvas, ColorKey


MIN_RECT_SIDE_FOR_TEXT = 0.03
X_SCALE_FACTOR = 12
Y_SCALE_FACTOR = 10


def compute_internal_counts(t):
    '''
    Assign a count to the interior nodes.  The count of the leaves
    should already be set.  The count of an internal node is the sum
    of the counts of its children.

    Inputs:
        t: a tree

    Returns:
        The count at that node. This is count for leaf nodes, and the sum of
            the counts of the children of internal nodes. The input tree t
            should be modified so that every internal node's count is set
            to be the sum of the counts of its children.
    '''

    if t.num_children() == 0:
        return t.count

    total_val = 0
    for st in t.children:
        total_val += compute_internal_counts(st)
        t.count = total_val
    return total_val


def compute_verbose_labels(t, prefix=None):
    '''
    Assign a verbose label to non-root nodes. Verbose labels contain the
    full path to that node through the tree. For example, following the
    path "Google" --> "female" --> "white" should create the verbose label
    "Google: female: white"

    Inputs:
        t: a tree

    Outputs:
        No explicit output. The input tree t should be modified to contain
            verbose labels for all non-root nodes
    '''

    if t.num_children() == 0:
        t.verbose_label = prefix + ": " + t.label
        return 

    for st in t.children:
        if (prefix is None) or (prefix == ""):
            pl = t.label
        else:
            pl = prefix + ": " + t.label
        t.verbose_label = pl
        compute_verbose_labels(st, pl)


def draw_treemap(t,
                 bounding_rec_height=1.0,
                 bounding_rec_width=1.0,
                 output_filename=None):

    '''
    Draw a treemap and the associated color key

    Inputs:
        t: a tree
        bounding_rec_height: the height of the bounding rectangle.
        bounding_rec_width: the width of the bounding rectangle.
        output_filename: (string or None) the name of a file for
        storing the image or None, if the image should be shown.
    '''

    canvas = ChiCanvas(X_SCALE_FACTOR, Y_SCALE_FACTOR)
    ckset = get_color_key_set(t)
    ck = ColorKey(ckset)

    compute_partitions(t, canvas, ck, bounding_rec_height, \
    bounding_rec_width, x0=0, y0=0, w=bounding_rec_width, \
    h=bounding_rec_height, orientation=0)

    if output_filename == None:
        canvas.show()
    else:
        canvas.savefig(output_filename)
  

def get_color_key_set(t, ckset=set([])):
    '''
    Creates a set of colors to implement into the canvas.

    Inputs:
        t: A tree
        ckset: An empty set to be filled with a set of colors.

    Returns: The color key set.
    '''

    if t.num_children() == 0:
        if t.label not in ckset:
            ckset.add(t.label)
        return ckset
    
    for st in t.children:
        get_color_key_set(st)
    return ckset


def compute_partitions(t, canvas, ck, brh, brw, x0, y0, w, h, orientation):
    '''
    Creates the partitions necessary to make the canvas that shows the
    distribution of diversity.

    Inputs:
        t: A tree
        canvas: An empty canvas
        ck: A color key
        brh: The bounding rectangle height
        brw: The bounding rectangle width
        x0: The starting point on the x-axis of the rectangle being drawn.
        y0: The starting point on the y-axis of the rectangle being drawn.
        w: The width of the rectangle being drawn.
        h: The height of the rectangle being drawn.
        orientation: The orientation of rectangles in the canvas (either
                     horizontal or vertical).

    Returns: No explicit output.  Creates the desired canvas.
    '''

    orientation = orientation % 2

    if t.num_children() == 0:
        leaf_color = ck.get_color(t.label) 
        canvas.draw_rectangle(x0, y0, x0 + w, y0 + h, fill = leaf_color)    
        if w > MIN_RECT_SIDE_FOR_TEXT and h > MIN_RECT_SIDE_FOR_TEXT:            
            if w >= h:
                canvas.draw_text(x0 + w / 2, y0 + h / 2, w, t.verbose_label, \
                fg="black")
            else: 
                canvas.draw_text_vertical(x0 + w / 2, y0 + h / 2, h, \
                t.verbose_label, fg="black")
        return

    else:
        for st in t.children:
            weight = st.count / t.count
            if orientation == 0:
                w = brw * weight
            else:
                h = brh * weight

            compute_partitions(st, canvas, ck, h, w, x0, y0, w, h, \
            orientation + 1)

            if orientation == 0:
                x0 += w
            else:
                y0 += h 
        
