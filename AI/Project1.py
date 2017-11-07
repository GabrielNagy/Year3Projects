#!/usr/bin/env python
import heapq
import logging
import sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


class Cell(object):
    def __init__(self, x, y, reachable):
        # Cell constructor
        self.reachable = reachable  # is cell reachable
        self.x = x  # x coordinate
        self.y = y  # y coordinate
        self.parent = None
        self.g = 0  # cost to move from starting cell to given cell
        self.h = 0  # cost to move from given cell to ending cell
        self.f = 0  # sum of costs


class IDAStar(object):
    def __init__(self):
        self.opened = []
        heapq.heapify(self.opened)  # open list
        self.closed = set()  # visited cells list
        self.cells = []  # grid cells
        self.grid_height = None
        self.grid_width = None

    def initialize_grid(self, width, height, walls, start, end):
        self.grid_height = height
        self.grid_width = width
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if (x, y) in walls:
                    reachable = False
                else:
                    reachable = True
                self.cells.append(Cell(x, y, reachable))
        self.start = self.get_cell(*start)
        self.end = self.get_cell(*end)

    def get_distance(self, cell):
        # computes distance between this cell and ending cell and multiplies by 10
        return (abs(cell.x - self.end.x) + abs(cell.y - self.end.y)) * 10

    def get_cell(self, x, y):
        # returns cell from the list
        return self.cells[x * self.grid_height + y]

    def get_adjacent_cells(self, cell):
        # returns adjacent cells of a cell, clockwise starting from the right
        cells = []
        if cell.x < self.grid_width - 1:
            cells.append(self.get_cell(cell.x + 1, cell.y))
        if cell.y > 0:
            cells.append(self.get_cell(cell.x, cell.y - 1))
        if cell.x > 0:
            cells.append(self.get_cell(cell.x - 1, cell.y))
        if cell.y < self.grid_height - 1:
            cells.append(self.get_cell(cell.x, cell.y + 1))
        return cells

    def display_path(self):
        # print found path from ending cell to starting cell
        cell = self.end
        path = [(cell.x, cell.y)]
        while cell.parent is not self.start:
            cell = cell.parent
            path.append((cell.x, cell.y))
            # logging.debug('path: cell: %d, %d' % (cell.x, cell.y))

        path.append((self.start.x, self.start.y))
        path.reverse()
        return path

    def update_cell(self, adjacent, cell):
        # updates adjacent cell to current cell
        adjacent.g = cell.g + 10
        adjacent.h = self.get_distance(adjacent)
        adjacent.parent = cell
        adjacent.f = adjacent.h + adjacent.g

    def process(self):
        limit = self.get_distance(self.start)
        INFINITY = float("inf")
        # logging.debug("Starting limit: %d" % limit)
        while limit < INFINITY:
            self.opened = []
            self.closed = set()
            heapq.heapify(self.opened)  # open list
            heapq.heappush(self.opened, (self.start.f, self.start))
            while len(self.opened):  # while we have elements in the open list
                # logging.debug("Current open list: ")
                # logging.debug(self.opened)
                # logging.debug("Current closed list: ")
                # logging.debug(self.closed)
                # pop cell from heap queue
                f, cell = heapq.heappop(self.opened)
                # logging.debug("Current cell: (%d, %d), f value: %d" % (cell.x, cell.y, f))
                if f > limit:
                    heapq.heappop(self.opened)
                # add cell to closed list
                self.closed.add(cell)
                # if cell is ending cell, display path
                if cell is self.end:
                    print("FOUND PATH!")
                    return self.display_path()
                # get adjacent cells
                adjacent_cells = self.get_adjacent_cells(cell)
                for adjacent_cell in adjacent_cells:
                    if adjacent_cell.reachable and adjacent_cell not in self.closed:
                        if (adjacent_cell.f, adjacent_cell) in self.opened:
                            # logging.debug("CHECK IF PATH IS BETTER FOR EXISTING CELL - Current cell: (%d, %d), f value: %d" % (adjacent_cell.x, adjacent_cell.y, adjacent_cell.f))
                            # if adjacent cell is in open list
                            # check if current path is better than the previous one for this adjacent cell
                            if adjacent_cell.g > cell.g + 10:
                                self.update_cell(adjacent_cell, cell)
                        else:
                            self.update_cell(adjacent_cell, cell)
                            # add adjacent cell to open list
                            if adjacent_cell.f <= limit:
                                heapq.heappush(self.opened, (adjacent_cell.f, adjacent_cell))
            limit += 10
            print("Did not find solution. Raising f limit to: %d" % limit)
            # logging.debug("Current limit: %d" % (limit))


if __name__ == "__main__":
    #         ., ., ., ., ., #
    #         #, #, ., ., ., #
    #         ., ., ., #, ., .    - table a
    #         ., #, #, ., ., #
    #         ., #, ., ., #, .
    #         S, #, ., ., ., F

    #          10 ., ., ., ., ., #, #, #, ., ., ., F
    #          9  ., ., ., ., ., #, #, #, ., ., ., #
    #          8  ., ., ., ., ., #, #, #, ., ., ., #
    #          7  ., ., #, #, #, #, ., ., ., ., ., #
    #          6  ., ., ., ., ., #, ., ., ., ., ., #
    #          5  ., #, ., ., ., #, ., ., ., ., ., #    - table b
    #          4  ., #, ., ., ., #, ., ., ., ., ., #
    #          3  ., #, ., ., ., ., ., ., ., ., ., #
    #          2  ., #, ., ., ., #, ., ., ., ., ., #
    #          1  ., #, ., ., ., #, #, #, ., ., ., #
    #          0  S, #, ., ., ., #, #, #, ., ., ., #
    #             0  1  2  3  4  5  6  7  8  9  10 11
    #
    #

    a = IDAStar()
    a.initialize_grid(6, 6, ((0, 5), (1, 0), (1, 1), (1, 5), (2, 3), (3, 1), (3, 2), (3, 5), (4, 1), (4, 4), (5, 1)), (0, 0), (5, 5))
    print(a.process())

    b = IDAStar()
    b.initialize_grid(12, 11, ((1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (2, 7), (3, 7), (4, 7), (5, 0), (5, 1), (5, 2), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9), (5, 10), (6, 0), (6, 1), (6, 8), (6, 9), (6, 10), (7, 0), (7, 1), (7, 8), (7, 10), (7, 9), (11, 0), (11, 1), (11, 2), (11, 3), (11, 4), (11, 5), (11, 6), (11, 7), (11, 8), (11, 9)), (0, 0), (11, 10))
    print(b.process())
