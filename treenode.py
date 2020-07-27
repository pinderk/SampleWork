#!/usr/bin/python
# -*- coding: utf-8 -*-
# CS121: Treemap assignment
#
# Class for representing tree nodes
#
#####################################
# DO NOT MODIFY THE CODE IN THIS FILE
#####################################

import textwrap


class TreeNode(object):

    def __init__(self, label, count=None, children=None):
        '''
        construct a Tree node

        Inputs:
            label: (string) a label that identifies the node
            count: (float) an application specific weight
            children: (list of TreeNodes) child nodes, or None if no children
        '''
        self._label = label
        self._count = count
        self._children = children
        self._verbose_label = None

    @property
    def label(self):
        return self._label

    @property
    def count(self):
        return self._count

    @property
    def children(self):
        return self._children

    @property
    def verbose_label(self):
        return self._verbose_label

    @label.setter
    def label(self, label):
        self._label = label

    @count.setter
    def count(self, count):
        self._count = count

    @children.setter
    def children(self, children):
        self._children = children

    @verbose_label.setter
    def verbose_label(self, verbose_label):
        self._verbose_label = verbose_label

    def num_children(self):
        if self._children is None:
            return 0
        else:
            return len(self._children)

    def tree_print_r(self, prefix, last, kformat, vformat, maxdepth):
        if maxdepth is not None:
            if maxdepth == 0:
                return
            else:
                maxdepth -= 1

        if len(prefix) > 0:
            if last:
                lprefix1 = prefix[:-3] + u"  └──"
            else:
                lprefix1 = prefix[:-3] + u"  ├──"
        else:
            lprefix1 = u""

        if len(prefix) > 0:
            lprefix2 = prefix[:-3] + u"  │"
        else:
            lprefix2 = u""

        if last:
            lprefix3 = lprefix2[:-1] + "   "
        else:
            lprefix3 = lprefix2 + "  "

        if self.count is None:
            ltext = (kformat).format(self.label)
        else:
            ltext = (kformat + ": " + vformat).format(self.label, self.count)

        ltextlines = textwrap.wrap(ltext, 80, initial_indent=lprefix1,
                                   subsequent_indent=lprefix3)

        print(lprefix2)
        print(u"\n".join(ltextlines))

        if self.children is None:
            return
        else:
            for i, st in enumerate(self.children):
                if i == len(self.children) - 1:
                    newprefix = prefix + u"   "
                    newlast = True
                else:
                    newprefix = prefix + u"  │"
                    newlast = False

                st.tree_print_r(newprefix, newlast, kformat, vformat, maxdepth)

    def tree_print(self, kformat="{}", vformat="{}", maxdepth=None):
        '''
        Inputs: self: (the tree object)
                kformat: (format string) specifying format for label
                vformat: (format string) specifying format for label and count
                maxdepth: (integer) indicating number of levels to print.
                          None sets no limit

        Returns:  no return value, but a tree is printed to screen
        '''
        self.tree_print_r(u"", False, kformat, vformat, maxdepth)
