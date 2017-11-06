#!/usr/bin/env python
import heapq


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


class AStar(object):
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
            print('path: cell: %d, %d' % (cell.x, cell.y))

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
        heapq.heappush(self.opened, (self.start.f, self.start))
        while len(self.opened):
            # pop cell from heap queue
            f, cell = heapq.heappop(self.opened)
            # add cell to closed list
            self.closed.add(cell)
            # if cell is ending cell, display path
            if cell is self.end:
                return self.display_path()
            # get adjacent cells
            adjacent_cells = self.get_adjacent_cells(cell)
            for adjacent_cell in adjacent_cells:
                if adjacent_cell.reachable and adjacent_cell not in self.closed:
                    if (adjacent_cell.f, adjacent_cell) in self.opened:
                        # if adjacent cell is in open list
                        # check if current path is better than the previous one for this adjacent celll
                        if adjacent_cell.g > cell.g + 10:
                            self.update_cell(adjacent_cell, cell)
                    else:
                        self.update_cell(adjacent_cell, cell)
                        # add adjacent cell to open list
                        heapq.heappush(self.opened, (adjacent_cell.f, adjacent_cell))

if __name__ == "__main__":
    a = AStar()
    a.initialize_grid(6, 6, ((0, 5), (1, 0), (1, 1), (1, 5), (2, 3), (3, 1), (3, 2), (3, 5), (4, 1), (4, 4), (5, 1)), (0, 0), (5, 5))
    print(a.process())
