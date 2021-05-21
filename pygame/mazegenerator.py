import random

class MazeGenerator:

    """ mazegenerator by "exciteabletom"; edited into a class by me:

        https://github.com/exciteabletom/mazegenerator """

    def __init__(self, size):
        self.generate(size[0], size[1], "path")
        self.changeSymbols()

    def getConclusionLine(self, line, symbol):
        x = line.index(symbol)
        c = []
        for i in range(len(line)):
            if i in (x - 1, x, x + 1):
                c.append("1")
            else:
                c.append("0")
        return c

    def changeSymbols(self):
        temp = []
        l = self.getConclusionLine(self.maze[0], "s")
        temp.append(l)
        for i in self.maze:
            t = []
            for u in i:
                if u == "#":
                    t.append("1")
                elif u == ".":
                    t.append("0")
                else:
                    t.append(u)
            temp.append(t)
        l = self.getConclusionLine(self.maze[-1], "e")
        temp.append(l)
        self.maze = temp

    def change_string_length(self, string, length):
        """
        Append spaces to a string until it reaches 'length'
        """
        diff = length - len(string)
        return string + (" " * diff)
    
    def print_maze(self):
        """
        Prints out the maze matrix in a human readable format, useful for debugging.
        """
        for i in self.maze:
            print(i)
        print("\n")
    
    def get_cell_value(self, coords):
        """
        Gets the value of the cell at the specified coordinates
    
        :param coords: tuple containing x and y values
        :return: value of the cell at the specifed coordinates
        """
        try:
            return self.maze[coords[0]][coords[1]]
        # Sometimes we get an IndexError if the maze doesn't have borders
        # This solution is not perfect, so it is still best practice to use borders
        except IndexError:
            return False
    
    def get_cells_by_value(self, value):
        """
        Get cell coordinates based on the value of the cell.
    
        :param value: The value to search cells for
        :return: list of all coordinates that contain the specified value
        """
        all_matching_cells = []  # the list containing all the coordinates of cells
        for row_index, row in enumerate(self.maze):
            for column_index, cell in enumerate(row):
                if cell == value:
                    all_matching_cells.append((row_index, column_index))
    
        return all_matching_cells
    
    def is_edge(self, coords):
        """
        Check if a piece is an edge or not.
    
        :param coords: A tuple (x,y)
        :return: True if piece is an edge piece False otherwise
        """
        if coords[0] == 0 or coords[0] == len(self.maze) - 1 \
              or coords[1] == 0 or coords[1] == len(self.maze[0]) - 1:  # if edge piece
            return True
    
        return False
    
    def get_cell_by_value(self, value):
        """
        The same as get_cells_by_value, except raises a ValueError if there is more than one cell with that value
    
        :param value: The value to search cells for
        :raises ValueError: If more then one of the value is found in the maze.
        :return: the cell coordinate that contains the value
        """
        values = self.get_cells_by_value(value)
        if len(values) > 1:
            raise ValueError("Expected only one cell to have value '{value}'. {len(values)} cells contained the value.")
    
        return values[0]
    
    def set_cell_value(self, coords, value):
        """
        Sets the value of a cell at the specified coordinates.
    
        :param coords: The coordinates of the cell to be changed
        :param value: The value we want the cell to be set to
        """
        self.maze[coords[0]][coords[1]] = value
    
    def check_cell_exists(self, coords):
        """
        Checks if a cell exists within the maze.
    
        :param coords: A tuple (x,y), representing a cell
        :return bool: True if cell exists, False otherwise
        """
        try:
            _ = self.maze[coords[0]][coords[1]]  # Will throw IndexError if the cell is out of the maze area
            return True  # Cell exists
        except IndexError:
            return False  # Cell doesn't exist
    
    def get_cell_neighbours(self, coords, empty_cell = None, directions = None):
        """
        Gets the values of all cells that neighbour the cell at the specified coordinates
    
        :param coords: Tuple containing the x and y values of the cell to check the neighbours of
        :param empty_cell: specifies an empty cell as a string
        :param directions: String containing directions to be checked for.
        :return: coordinates of all neighbours that have not been visited in
                    a list of tuples. Example: [(x,y), (x,y), (x,y)]
        """
        # different tuples that contain the coords of all positions
        # relative to our input tuple
        up = (coords[0] - 1, coords[1])
        down = (coords[0] + 1, coords[1])
        left = (coords[0], coords[1] - 1)
        right = (coords[0], coords[1] + 1)
    
        # list containing all directional tuples
        all_dirs = [up, down, right, left]
        if directions:
            all_dirs = []
            if "up" in directions:
                all_dirs.append(up)
            if "down" in directions:
                all_dirs.append(down)
            if "right" in directions:
                all_dirs.append(right)
            if "left" in directions:
                all_dirs.append(left)
    
            if not all_dirs:
                raise ValueError("Directions {directions} not recognised.")
    
        visitable_coordinates = []
    
        if type(empty_cell) == str:
            for dir in all_dirs:
                cell_value = self.get_cell_value(dir)
    
                if cell_value == empty_cell:
                    if self.is_edge(dir):
                        continue
    
                    if dir[0] < 0 or dir[1] < 0:  # If negative number
                        continue
    
                    visitable_coordinates.append(dir)  # Don't remove
    
        return visitable_coordinates
    
    def get_cell_neighbour_direction_names(self, coords, direction="all", empty_cell="."):
        """
        Checks which directions can be moved to.
    
        :param coords: A tuple (x,y).
        :param direction: String containing a directions to check. If left out will check every directions.
        :param empty_cell: What value is considered empty
        :return: A list containing directions that can be moved to. E.g. ["right", "up", "left"].
        """
    
        # different tuples that contain the coords of all positions
        # relative to our input tuple
        up = (coords[0] - 1, coords[1])
        down = (coords[0] + 1, coords[1])
        left = (coords[0], coords[1] - 1)
        right = (coords[0], coords[1] + 1)
    
        all_dirs = [(up, "up"), (down, "down"), (right, "right"), (left, "left")]
        good_dirs = []
    
        if direction == "all":
            for cell_data in all_dirs:
                if self.is_edge(cell_data[0]) or self.get_cell_value(cell_data[0]) != empty_cell:
                    continue
                good_dirs.append(cell_data[1])
    
        else:
            if direction == "up":
                index = 0
            elif direction == "down":
                index = 1
            elif direction == "right":
                index = 2
            elif direction == "left":
                index = 3
            else:
                raise ValueError("Direction {direction}, not recognised.")
    
            if get_cell_value(all_dirs[index]) == empty_cell and not is_edge(all_dirs[index]):
                good_dirs.append(direction)
    
        return good_dirs
    
    def next_to_edge(self, coords):
        """
        Function for checking if a cell is next to the edge of the maze.
    
        :param coords: Tuple (x, y)
        :rtype: bool
        :return: True if next to edge, false otherwise
        """
        next_to_wall = False
    
        if coords[0] == 1 or coords[0] == len(self.maze) - 2:
            next_to_wall = True
    
        elif coords[1] == 1 or coords[1] == len(self.maze[-1]) - 2:
            next_to_wall = True
    
        return next_to_wall
    
    def check_seed(self):
        """
        Creates a random seed if one is not defined already
        """
        seed = ""
        if not seed:  # If no user-defined seed
            # Create random seed
            random_chars = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s",
                                "t", "u", "v", "w" "x", "y", "z", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
            for _ in range(15):
                rand_bool = random.random() < 0.5
                rand_char = random_chars[random.randint(0, len(random_chars) - 1)]
    
                if rand_bool:
                    rand_char = rand_char.upper()
    
                seed = seed + rand_char
    
        random.seed(seed)
    
    def init_maze(self, width, height):
        """
        Initialises a maze with only walls
        :param width: The width of the maze
        :param height: The height of the maze
        """
        self.maze = []
    
        for _ in range(height):
            self.maze.append([])
            for _ in range(width):
                self.maze[-1].append("#")
    
    def branch(self, coords, direction, no_exit = False, noise_offset = 0.0):
        """
        Branches out to the side of a target cell, either left, right or down, used to add tree like structure
    
        :param coords: (x,y) indicating a cell position
        :param direction: 'left', 'right' or 'down'
        :param no_exit: Bool indicating whether to not stop randomly
        :param noise_offset: float that affects some of the random chances
        :return: The cell that was last visited
        :rtype: tuple
        """
    
        while True:
            rand_float = random.random() + noise_offset
            if rand_float < 0.05 and not no_exit:
                return coords
    
            neighbour_directions = self.get_cell_neighbour_direction_names(coords, empty_cell="#")
    
            if direction in neighbour_directions:
                final_direction = direction
                if 0.05 < rand_float < 0.45 + noise_offset:
                    final_direction = "down"
    
                try:
                    next_coords = self.get_cell_neighbours(coords, "#", final_direction)[0]
                except IndexError:
                    return coords
    
                if not self.is_edge(next_coords):
                    if next_coords[0] == len(self.maze) - 1:
                        breakpoint()
                    self.set_cell_value(next_coords, ".")
                    coords = next_coords
                else:
                    return coords
            else:
                return coords
    
    def init_solution_path(self):
        """
        Creates a randomized solution path through the maze.
        """
    
        # Find the beginning of the maze
        start_pos = random.randint(1, len(self.maze[0]) - 2)
        self.maze[0][start_pos] = "s"
        start = self.get_cell_by_value("s")
    
        # Set the current cell to be the cell under start
        current_cell = (start[0] + 1, start[1])
        self.set_cell_value(current_cell, ".")
    
        no_up = True
    
        if random.random() < 0.5:
            h_prefer = "right"
            not_h_prefer = "left"
        else:
            h_prefer = "left"
            not_h_prefer = "right"
    
        rows = len(self.maze) - 2
        last_row = 0
    
        # Path from start
        while True:
            if current_cell[0] != last_row:
                last_row = current_cell[0]
    
            if current_cell[0] == len(self.maze) - 2:  # If on second last row of maze
                self.set_cell_value((len(self.maze) - 1, current_cell[1]), "e")
                break
    
            # Possible directions we could travel to
            directions = self.get_cell_neighbour_direction_names(current_cell, empty_cell="#")
    
            if no_up and "up" in directions:  # Currently will always be triggered
                directions.remove("up")
    
            # A random direction
            rand_direction = directions[random.randint(0, len(directions) - 1)]
    
            if h_prefer in directions and random.random() < 0.6:
                rand_direction = h_prefer
    
            elif random.random() < 0.01:
                current_cell = self.branch(current_cell, h_prefer)
                last_row = current_cell[0]
                if random.random() < 0.5:
                    h_prefer, not_h_prefer = (not_h_prefer, h_prefer)
                continue
    
            next_cell = self.get_cell_neighbours(current_cell, "#", rand_direction)[0]
            self.set_cell_value(next_cell, ".")
    
            if self.next_to_edge(current_cell):
                if random.random() < 0.60:
                    h_prefer, not_h_prefer = (not_h_prefer, h_prefer)
    
            current_cell = next_cell
    
    def expand_rows(self, noise_offset):
        """
        'expands' rows by adding random paths on, above, and below the rows
        :param noise_offset: An offset applied to some of the random float values generated
                                A negative offset reduces noise, a positive one increases noise
        """
        for row_index, row in enumerate(self.maze):
            if row_index % 3 == 0:
                continue
    
            if row_index == len(self.maze) - 1:
                continue
    
            for cell_index, cell in enumerate(row):
                if cell_index in (0, len(self.maze[0]) - 1):
                    continue
    
                cell_coords = (row_index, cell_index)
                rand = random.randint(0, 13)
    
                if cell == "#":  # If cell is wall
                    cell_neighbours = self.get_cell_neighbours(cell_coords, empty_cell=".")
    
                    if cell_neighbours and rand < 1:
                        self.set_cell_value(cell_coords, ".")
                    elif rand in (2, 3):
                        rand_direction = ""
    
                        if random.random() < 0.005:
                            rand_direction = "down"
                        elif rand == 2:
                            rand_direction = "left"
                        elif rand == 3:
                            rand_direction = "right"
                        else:
                            raise ValueError("DEVERROR: Random integer out of range")
    
                        self.branch(cell_coords, rand_direction, random.random() < 0.001, noise_offset)
    
    def generate(self, width, height, noise_bias):
        """
        Main function that creates the maze.
        :param width: Width of the matrix
        :param height: Height of the matrix
        :param noise_bias: Either "wall", "less", "none", or and empty string indicating no bias
        """
        self.check_seed()
        self.init_maze(width, height)
        self.init_solution_path()
    
        if noise_bias != "none":  # If we should generate noise
            noise_offset = 0
    
            if noise_bias == "walls":  # Draw less paths
                print("Creating more walls")
                noise_offset = -0.09
    
            elif noise_bias == "paths":  # Draw more paths
                # print("Creating more paths")
                noise_offset = 0.25
    
            self.expand_rows(noise_offset)
        else:
            print("Only rendering solution path")
    
