"""A module for saving map layouts and determining shortest paths."""

import config
import utils
import math
import cv2
import pickle
from os.path import join, isfile


class QuadTree:
    """Represents some possible player positions in a map layout."""

    TOLERANCE = config.move_tolerance / 2

    class Node:
        """Represents a vertex on a quadtree."""

        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.up_left = None
            self.up_right = None
            self.down_left = None
            self.down_right = None

        def children(self):
            """
            Returns an array of this Node's children if they exist.
            :return:    This Node's children.
            """

            result = []
            if self.up_left:
                result.append(self.up_left)
            if self.up_right:
                result.append(self.up_right)
            if self.down_left:
                result.append(self.down_left)
            if self.down_right:
                result.append(self.down_right)
            return result

        def __str__(self):
            """
            Returns a string representation of this Node as a coordinate point.
            :return:    A string of the form '(x, y)'.
            """

            return str(tuple(self))

        def __iter__(self):
            """
            Support converting a Node into a tuple.
            :return:    This Node's x and y positions.
            """

            yield self.x
            yield self.y

    def __init__(self):
        self.root = None
        self.num_points = 0

    def add(self, x, y):
        """
        Adds a Node to the quadtree at position (X, Y) if it does not already exist.
        :param x:   The x-position of the new point.
        :param y:   The y-position of the new point.
        :return:    None
        """

        def add_helper(point):
            if not point:
                return QuadTree.Node(x, y)
            if y >= point.y and x < point.x:
                point.up_left = add_helper(point.up_left)
            elif y >= point.y and x >= point.x:
                point.up_right = add_helper(point.up_right)
            elif y < point.y and x < point.x:
                point.down_left = add_helper(point.down_left)
            else:
                point.down_right = add_helper(point.down_right)
            return point

        def no_collision(point):
            return utils.distance(tuple(point), (x, y)) >= QuadTree.TOLERANCE

        checks = map(no_collision, self.search(x - QuadTree.TOLERANCE,
                                               x + QuadTree.TOLERANCE,
                                               y - QuadTree.TOLERANCE,
                                               y + QuadTree.TOLERANCE))

        if all(checks):
            self.root = add_helper(self.root)
            self.num_points += 1

    def search(self, x_min, x_max, y_min, y_max):
        """
        Returns a list of all Nodes bounded horizontally by X_MIN and X_MAX, and bounded
        vertically by Y_MIN and Y_MAX.
        :param x_min:   The left boundary of the range.
        :param x_max:   The right boundary of the range.
        :param y_min:   The bottom boundary of the range.
        :param y_max:   The top boundary of the range.
        :return:        A list of all Nodes in the range.
        """

        nodes = []

        def search_helper(point):
            if point:
                if x_min <= point.x <= x_max and y_min <= point.y <= y_max:
                    nodes.append(point)
                if x_min < point.x:
                    if y_min < point.y:
                        search_helper(point.down_left)
                    if y_max >= point.y:
                        search_helper(point.up_left)
                if x_max >= point.x:
                    if y_min < point.y:
                        search_helper(point.down_right)
                    if y_max >= point.y:
                        search_helper(point.up_right)

        search_helper(self.root)
        return nodes

    # def get_nearest(self, x, y):      TODO: improve or delete this, very inefficient.
    #     """
    #     Returns the nearest Node to the given position (X, Y).
    #     :param x:   The given x position.
    #     :param y:   The given y position.
    #     :return:    The Node closest in distance to (X, Y).
    #     """
    #
    #     def nearest_helper(point, best_point):
    #         if not point:
    #             return best_point
    #         if utils.distance(tuple(point), (x, y)) < utils.distance(tuple(best_point), (x, y)):
    #             best_point = point
    #
    #         # Determine the 'good quadrants' of the current node
    #         children = set()
    #         if y >= point.y:
    #             children.update([point.up_left, point.up_right])
    #         else:
    #             children.update([point.down_left, point.down_right])
    #         if x >= point.x:
    #             children.update([point.up_right, point.down_right])
    #         else:
    #             children.update([point.up_left, point.down_left])
    #
    #         # Search the 'good quadrants' for potentially even better nodes
    #         for child in children:
    #             best_point = nearest_helper(child, best_point)
    #         return best_point
    #
    #     return nearest_helper(self.root, self.root)

    def draw(self, image):
        """
        Draws the points in this QuadTree onto IMAGE using in-order traversal.
        :param image:   The image to draw on.
        :return:        None
        """

        height, width, _ = image.shape

        def draw_helper(point):
            if point:
                draw_helper(point.up_left)
                draw_helper(point.down_left)

                center = (int(round(point.x * width)), int(round(point.y * height)))
                cv2.circle(image, center, 2, (0, 165, 255) , -1)

                draw_helper(point.up_right)
                draw_helper(point.down_right)

        draw_helper(self.root)


class Layout:
    """An class representing an in-game map layout as a graph."""

    layouts_dir = './layouts'

    def __init__(self, name):
        self.name = name
        self.quadtree = QuadTree()

    @staticmethod
    def load(name):
        """
        Loads the Layout object with FILE_NAME. Creates and returns a new Layout if the
        specified Layout does not exist.
        :param name:    The name of the Layout to load.
        :return:        A Layout object.
        """

        target = join(Layout.layouts_dir, name)
        if isfile(target):
            return pickle.load(target)
        else:
            new_layout = Layout(name)
            new_layout.save()
            return new_layout

    def save(self):
        """
        Pickles this Layout instance to a file that is named after the routine in which
        this Layout was generated.
        :return:    None
        """

        with open(join(Layout.layouts_dir, self.name), 'w') as file:
            pickle.dump(self, file)







import numpy as np
import time
from random import random


q = QuadTree()
q.add(0.5, 0.5)
q.add(0.3, 0.4)
q.add(0.2, 0.3)
q.add(0.5, 0.6)
q.add(0.1, 0.1)
q.add(0.9, 0.9)

for node in q.search(0.3, 0.6, 0.3, 0.6):
    print(node)


start = time.time()
blank = np.zeros([512, 512, 3], dtype=np.uint8)
blank.fill(255)

longest_time = 0.0
times = []

for _ in range(500000):
    # q.add(random(), int(random() * 10) / 10)
    start = time.time()
    q.add(random(), random())
    elapsed = time.time() - start
    times.append(elapsed)
    longest_time = max(elapsed, longest_time)
    # q.draw(blank)
    # cv2.imshow('test', blank)
    # if cv2.waitKey(1) & 0xFF == 27:     # 27 is ASCII for the Esc key
    #     break

q.draw(blank)

print(longest_time)
print(sum(times) / len(times))


cv2.imshow('test', blank)
cv2.waitKey(0)

