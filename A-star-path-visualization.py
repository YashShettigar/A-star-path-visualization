import pygame
import math
from queue import PriorityQueue

WIDTH = 800
WINDOW = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Algo")

colors = {
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "WHITE": (255, 255, 255),
    "YELLOW": (255, 255, 0),
    "BLACK": (0, 0, 0),
    "PURPLE": (128, 0, 128),
    "ORANGE": (255, 165, 0),
    "GREY": (128, 128, 128),
    "TURQUOISE": (64, 224, 208)
}

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row*width
        self.y = col*width
        self.color = colors.get("WHITE")
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    # state of the node that's being visted
    def get_pos(self):
        return self.row, self.col
    
    def is_closed(self):
        return self.color == colors.get("RED")        # node is visited

    def is_open(self):
        return self.color == colors.get("GREEN")      # node is in open set

    def is_barrier(self):
        return self.color == colors.get("BLACK")        # checck if a block is barrier

    def is_start(self):
        return self.color == colors.get("ORANGE")       # checks if the node is the starting of a path

    def is_end(self):
        return self.color == colors.get("TURQUOISE")       # node is the last of the path

    def reset(self):
        self.color = colors.get("WHITE")



    # actions on a node that's being visited
    def make_start(self):
        self.color = colors.get("ORANGE")

    def make_closed(self):
        self.color = colors.get("RED")
    
    def make_open(self):
        self.color = colors.get("GREEN")

    def make_barrier(self):
        self.color = colors.get("BLACK")

    def make_end(self):
        self.color = colors.get("TURQUOISE")

    def make_path(self):
        self.color = colors.get("PURPLE")

    def draw(self, WINDOW):
        pygame.draw.rect(WINDOW, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []

        # checks the constraints with window size so as to not crash the program while addition of new rows or new cols
        if self.row < self.total_rows-1 and not grid[self.row+1][self.col].is_barrier():    # checks DOWN
            self.neighbors.append(grid[self.row+1][self.col])
        if self.row > 0 and not grid[self.row-1][self.col].is_barrier():    # checks UP
            self.neighbors.append(grid[self.row-1][self.col])   
        if self.col > 0 and not grid[self.row][self.col-1].is_barrier():    # checks LEFT
            self.neighbors.append(grid[self.row][self.col-1])
        if self.col < self.total_rows-1 and not grid[self.row][self.col+1].is_barrier():    # checks RIGHT
            self.neighbors.append(grid[self.row][self.col+1])

    def __lt__(self, other):
        return False

# reconstruction of the path from within the queue
def reconstruct_path(origin_node, cur, draw):
    while cur in origin_node:
        cur = origin_node[cur]
        cur.make_path()
        draw()


#  The actual A* Algorithm
def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))

    origin_node = {}

    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0

    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = H(start.get_pos(), end.get_pos())

    open_set_hash = { start }

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        cur = open_set.get()[2]     # get the node of the lowest value f-score
        open_set_hash.remove(cur)   # pop out of the stack

        # Path found!
        if cur == end:
            reconstruct_path(origin_node, end, draw)
            start.make_start()  # to prevent overriding color of the start node
            end.make_end()      # to prevent overriding color of the end node
            return True

        for neighbor in cur.neighbors:
            tmp_g_score = g_score[cur]+1

            if tmp_g_score < g_score[neighbor]:       # if neighbor has a better path
                origin_node[neighbor] = cur
                g_score[neighbor] = tmp_g_score
                f_score[neighbor] = tmp_g_score + H(neighbor.get_pos(), end.get_pos())

                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)

                    neighbor.make_open()

        draw()

        if cur != start:
            cur.make_closed()
    
    return False

# Heuristic function
def H(p1, p2):
    # Manhattan distance
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1-x2)+abs(y1-y2)


# helper function
def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)

    return grid

def draw_grid(WINDOW, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(WINDOW, colors.get("GREY"), (0, i*gap), (width, i*gap))        # horizontal lines
        for j in range(rows):
            pygame.draw.line(WINDOW, colors.get("GREY"), (j*gap, 0), (j*gap, width))    # vertical lines


def draw(WINDOW, grid, rows, width):
    WINDOW.fill(colors.get("WHITE"))

    for row in grid:
        for node in row:
            node.draw(WINDOW)

    draw_grid(WINDOW, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col

def main(WINDOW, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    started = False

    while run:
        draw(WINDOW, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:   # LMB
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                if not start and node != end:
                    start = node
                    start.make_start()
                elif not end and node != start:
                    end = node
                    end.make_end()
                elif node != start and node != end:
                    node.make_barrier()
                    
                
            elif pygame.mouse.get_pressed()[2]:     #RMB
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]

                node.reset()

                if node == start:
                    start = None
                elif node ==  end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    
                    algorithm(lambda: draw(WINDOW, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()

main(WINDOW, WIDTH)