#   Kyle Pinder
#
#   CS121: Schelling Model of Housing Segregation
#
#   Program for simulating of a variant of Schelling's model of
#   housing segregation.  This program takes four parameters:
#
#    filename -- name of a file containing a sample city grid
#
#    R - The radius of the neighborhood: home at Location (k, l) is in
#        the neighborhood of the home at Location (i, j)
#        if i-R <= k <= i+R and j-R <= l <= j+R
#
#    threshold - minimum acceptable threshold for ratio of the number
#                of similar neighbors to the number of occupied homes
#                in a neighborhood.
#
#    max_steps - the maximum number of passes to make over the city
#                during a simulation.
#
#  Sample use: 
#  python3 schelling.py --grid_file=tests/a17-sample-grid.txt --r=1 --threshold=0.44 --max_steps=2
#

import os
import sys
import utility
import click
import copy

def compute_similarity_score(grid, R, location):
    ''' 
    Compute the similarity score for the homeowner at the specified
    location using a neighborhood of radius R.

    Inputs: 
        grid (list of lists of strings): the grid
        R (int): radius for the neighborhood
        location (pair of ints): a grid location
      
    Returns: float
    '''

    assert utility.is_grid(grid), ("The grid argument has the wrong type.  "
                                   "It should be a list of lists of strings "
                                   "with the same number of rows and columns")

    assert unoccupied_home(grid, location), \
        ("The location does not contain an occupied home.") 

    (row, column) = location
    row_list = list(range(row - R, row + (R + 1)))
    column_list = list(range(column - R, column + (R + 1)))
    rl_length = len(row_list)
    cl_length = len(column_list)
    S = 0
    H = 0

    if R == 0:
        return 1.0
    
    if R > 0:
        for r in row_list:
            if row_list[0] < 0:
                del row_list[0]
            if row_list[-1] > len(grid) - 1:
                del row_list[-1]
        for c in column_list:
            if column_list[0] < 0:
                del column_list[0]
            if column_list[-1] > len(grid) - 1:
                del column_list[-1]

    for x in row_list:
        for y in column_list:
            if grid[x][y] == "B" or "R":
                H += 1
            if grid[x][y] == "O":
                H -= 1

            if grid[row][column] == grid[x][y]:
                S += 1
  
    similarity_score = S/H

    return similarity_score


def unoccupied_home(grid, location):
    '''
    Compute whether or not the specified location is unoccupied.

    Inputs:
        grid: (list of list of strings)
        location: (pair of ints) a grid location

    Returns: boolean
    '''
    
    (row, column) = location

    if grid[row][column] == "O":
        return False
    if grid[row][column] == "B" or grid[row][column] == "R":
        return True


def swap_location(grid, occupied_location, unoccupied_location):
    '''
    Swaps the labels of two locations in the grid.

    Inputs:
        grid: (list of list of strings)
        occupied_location: (pair of ints) an occupied grid location
        unoccupied_location: (pair of ints) an unoccupied grid location

    Returns: Updated grid with swapped locations.
    '''
    grid_2 = []
    for r in list(range(len(grid))):
        grid_2.append(grid[r])
    (row1, column1) = occupied_location
    (row2, column2) = unoccupied_location
    
    grid_2[row2][column2] = grid_2[row1][column1]
    grid_2[row1][column1] = "O"

    return grid_2

def make_unoccupied_list(grid):
    '''
    Creates a list of the unoccupied locations in a grid.

    Inputs:
        grid: (list of list of strings)

    Returns: list
    '''

    grid_range = list(range(0, len(grid)))
    unoccupied_list = []

    for row in grid_range:
        for column in grid_range:
            if grid[row][column] == "O":
                unoccupied_list.append((row, column))

    return unoccupied_list


def relocate(grid, R, threshold):
    '''
    Relocates all individuals to the best possible location.
    
    Inputs: 
        grid: (list of list of strings)
        R: (int) the radius of the neighborhood
        threshold: (float) the specified minimum satisfaction 

    Returns: An updated grid with all the relocations.
    '''

    grid_range = list(range(len(grid)))
    num_relocations = 0

    for row in grid_range:
        for column in grid_range:
            if grid[row][column] == "B" or grid[row][column] == "R":
                similarity_score = compute_similarity_score \
                (grid, R, (row, column))
                if similarity_score < threshold:
                    ul_satisfaction = []
                    unoccupied_list = make_unoccupied_list(grid)
                    ul_range = list(range(0, len(unoccupied_list)))
                    for r in ul_range:
                        grid = swap_location(grid, (row, column), \
                        unoccupied_list[r])
                        ul_satisfaction.append \
                        (compute_similarity_score(grid, R, \
                        (unoccupied_list[r])))
                        grid = swap_location(grid, unoccupied_list[r], \
                        (row, column))                  
                    for z in ul_range:
                        if ul_satisfaction[z] < threshold:
                            ul_satisfaction[z] = 2 
                    for z in ul_range:
                        if ul_satisfaction[z] > min(ul_satisfaction):
                            ul_satisfaction[z] = 2
                    good_satisfaction = len([1 for z in \
                    ul_satisfaction if z < 1.1])
                    if good_satisfaction > 1:
                        num_relocations += 1 - good_satisfaction

                    for z in ul_range:
                        if ul_satisfaction[z] < 1.1:
                            grid = swap_location(grid, (row, column), \
                                unoccupied_list[z]) 
                            num_relocations += 1             
                            unoccupied_list.append((row, column)) 
                            del unoccupied_list[z]
                            continue  

    return grid, num_relocations


def do_simulation(grid, R, threshold, max_steps):
    '''
    Do a full simulation.

    Inputs:
        grid: (list of lists of strings) the grid
        R: (int) radius for the neighborhood
        threshold: (float) satisfaction threshold
        max_steps: (int) maximum number of steps to do

    Returns:
        (int) The number of relocations completed.
    '''
    assert utility.is_grid(grid), ("The grid argument has the wrong type.  "
                                   "It should be a list of lists of strings "
                                   "with the same number of rows and columns")
    step_count = 0
    num_relocations = 0
    if max_steps == 0:
        return num_relocations
    grid_list = [copy.deepcopy(grid)]
    
    while True:
        (new_grid, num_new_relocations) = relocate \
        (copy.deepcopy(grid_list[0]), R, threshold)
        (grid, n) = relocate(grid, R, threshold)
        grid_list.append(new_grid)
        step_count += 1
        num_relocations += num_new_relocations
        if step_count == max_steps:
            return num_relocations
        mismatch = utility.find_mismatch(grid_list[0], grid_list[1])
        if mismatch == None:
            return num_relocations
        del grid_list[0]
        if step_count < max_steps:
            continue

@click.command(name="schelling")
@click.option('--grid_file', type=click.Path(exists=True))
@click.option('--r', type=int, default=1, help="neighborhood radius")
@click.option('--threshold', type=float, default=0.44,
                                         help="satisfaction threshold")
@click.option('--max_steps', type=int, default=1)
def go(grid_file, r, threshold, max_steps):
    '''
    Put it all together: do the simulation and process the results.
    '''

    if grid_file is None:
        print("No parameters specified: just loading the code.")
        return

    grid = utility.read_grid(grid_file)

    if len(grid) < 20:
        print("Initial state of city:")
        for row in grid:
            print(row)
        print()

    num_relocations = do_simulation(grid, r, threshold, max_steps)
    print("Number of relocations done: " + str(num_relocations))

    if len(grid) < 20:
        print()
        print("Final state of the city:")
        for row in grid:
            print(row)

if __name__ == "__main__":
    go()
