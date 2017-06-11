import collections
import operator

assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'
isDiagnol=1


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Find all instances of naked twins -- boxes with len =2
    p = peers()
    potential_twins_boxes = [box for box in values.keys() if len(values[box]) == 2]

    # Build a subdict of potential twins
    potential_twins_boxes_dict = {k: values[k] for k in potential_twins_boxes}

    # For a box in potential twins, find another box in peer of box1 which has same value as box1 --> naked twin
    naked_twins = [[box1, box2] for box1 in potential_twins_boxes for box2 in p[box1] if values[box1] == values[box2]]

    for i in range(len(naked_twins)):

        box1 = naked_twins[i][0]
        box2 = naked_twins[i][1]

        peers_box1 = set(p[box1])
        peers_box2 = set(p[box2])

        digits = values[box1]  # the value we are planning to replace -- the twin prime value
        all_peers = peers_box1.intersection(peers_box2)
        for peer in all_peers:
            val_in_peer = values[peer]  ### value the peer holds currently
            val_to_replace = ''.join([c for c in val_in_peer if c not in digits])
            # print("Replacing value {}  in box {} with {} -- twin value {}".format(val_in_peer,peer,val_to_replace,digits))
            assign_value(values, peer, val_to_replace)
            #    display(values)
    return values
    # Eliminate the naked twins as possibilities for their peers


def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s + t for s in A for t in B]
    pass


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes(), chars))


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1 + max(len(values[s]) for s in boxes())
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


def reduce_puzzle(values):
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # eliminate extraneous values
        values = eliminate(values)
        # use only choice to fill up
        values = only_choice(values)

        # naked twins
        values = naked_twins(values)

        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after

        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False

    return values


def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False;  ## failed earlier
    if all(len(values[s]) == 1 for s in boxes()):
        return values  ##solved
    # display(values)
    # print("**************************************************************************************************")
    len_dict = {key: len(value) for key, value in values.items()}
    # Choose one of the unfilled squares with the fewest possibilities
    # filter solved ones
    unsolved_dict = {key: value for key, value in len_dict.items() if value > 1}
    box_to_solve = min(unsolved_dict, key=unsolved_dict.get)
    poss_val = values[box_to_solve]
    # print("solving for box {} for value {}".format(box_to_solve, poss_val))
    for digit in poss_val:
        val_copy = values.copy()
        val_copy[box_to_solve] = digit
        attempt = search(val_copy)
        if attempt:
            return attempt


def boxes():
    return cross(rows, cols)


def rowUnits():
    return [cross(r, cols) for r in rows]


def colUnits():
    return [cross(rows, c) for c in cols]


def squareUnits():
    return [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]


def units():
    if isDiagnol == 0:
        unitlist = rowUnits() + colUnits() + squareUnits()
    elif isDiagnol == 1:
        unitlist = rowUnits() + colUnits() + squareUnits() + diagnol_boxes()
    return dict((s, [u for u in unitlist if s in u]) for s in boxes())


def peers():
    peers = dict((s, set(sum(units()[s], [])) - set([s])) for s in boxes())
    return peers


def diagnol_boxes():
    d1 = [[rows[i] + cols[i] for i in range(len(rows))]]
    cols_reversed = cols[::-1]
    d2 = [[rows[i] + cols_reversed[i] for i in range(len(rows))]]
    return d1 + d2


def eliminate(values):
    p = peers()
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    # keys = values.keys()
    # solved_boxes = []
    # for key in keys:
    #     soln = values[key]
    #     if(len(soln)==1):
    #         solved_boxes.append(soln)
    for box in solved_values:
        digit = values[box]
        for peer in p[box]:
            assign_value(values, peer, values[peer].replace(digit, ''))
            # values[peer] = values[peer].replace(digit, '')
    return values


def only_choice(values):
    """Finalize all values that are the only choice for a unit.

       Go through all the units, and whenever there is a unit with a value
       that only fits in one box, assign the value to this box.

       Input: Sudoku in dictionary form.
       Output: Resulting Sudoku in dictionary form after filling in only choices.
       """
    # unitlist = self.rowUnits() + self.colUnits() + self.squareUnits()

    fillUpUnits(rowUnits(), values)
    fillUpUnits(colUnits(), values)
    fillUpUnits(squareUnits(), values)
    return values


def fillUpUnits(unitlist, values):
    for unit in unitlist:
        # print('unit =' + ''.join(unit))
        for digit in '123456789':
            ##Find all places where there is a box with a single digit.
            # print("searching for digit : " + digit)
            splaces = []
            for box in unit:
                # print('box = ' + box + " values in box " + values[box])
                if (digit in values[box]):
                    # print('adding box to splace ' + box)
                    splaces.append(box)

            if (len(splaces) == 1):
                # print("Setting the value at " + splaces[0] + " to " + digit)
                # values[splaces[0]] = digit
                assign_value(values, splaces[0], digit)
                # splaces = [box for box in unit if digit in values[box]]
                # print("Boxes with only " + digit + " in them " + ','.join(splaces))
                # if (len(splaces) == 1):
                #     print("Setting the value at " + splaces[0] + " to " + digit)
                #     values[splaces[0]] = digit


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    values = search(values)
    return values


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    # display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments

        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
