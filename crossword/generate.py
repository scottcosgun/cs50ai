from collections import deque
from contextlib import nullcontext
import sys
import random

from crossword_ import Crossword, Variable


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains.keys():
            for word in self.domains[var].copy():
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        overlap = self.crossword.overlaps[x,y]
        # If there is an overlap
        if overlap:
            i, j = overlap
            # Iterate through X's domain
            for xval in self.domains[x].copy():
                check = False
                # Iterate through Y's domain
                for yval in self.domains[y]:
                    # If X[i] == Y[j], we've found a match. Don't need to keep going through y's
                    try:
                        if xval[i] == yval[j] and xval != yval:
                            check = True
                            break
                    except IndexError:
                        continue
                if not check:
                    self.domains[x].remove(xval)
                    revised = True

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        q = []
        # If arcs is not None, add all arcs to queue
        if arcs:
            for arc in arcs:
                q.append(arc)
        else:
            for var1 in self.domains:
                for var2 in self.crossword.neighbors(var1):
                    if var1 != var2:
                        q.append((var1, var2))
        while q:
            (x, y) = q.pop()
            # If we remove non arc-consistent values from x
            if self.revise(x,y):
                # If nothing left in X's domain, return False. No solution possible
                if len(self.domains[x]) == 0:
                    return False
                # Ensure arc consistency with values in changed domain
                for z in self.crossword.neighbors(x):
                    if z != y:
                        q.append((z,x))
        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.domains:
            if var not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # All values must be distinct
        words = list(assignment.values())
        if len(words) != len(set(words)):
            return False
        # Every value is correct length
        for var in assignment:
            if var.length != len(assignment[var]):
                return False
        # No conflicts with between neighboring values
        for var in assignment:
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    x, y = self.crossword.overlaps[var, neighbor]
                    if assignment[var][x] != assignment[neighbor][y]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Iterate through the variable's domain of values
        dictionary = {}
        for value in self.domains[var]:
            eliminated = 0
            # Iterate through neighbors of var
            for neighbor in self.crossword.neighbors(var):
                # Any variable present in assignment should not be counted
                if neighbor not in assignment and neighbor != var:
                    x,y = self.crossword.overlaps[var, neighbor]
                    for word in self.domains[neighbor]:
                        if value[x] != word[y]:
                            eliminated += 1
            # Add eliminated words to dict
            dictionary[value] = eliminated

        return sorted(dictionary, key=lambda key: dictionary[key])
        
    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Add all unassigned variables to a dict along with # values in domain
        numvals = {var: len(self.domains[var]) for var in self.domains if var not in assignment}
        # Sort dictionary by # values
        sorted_numvals = dict(sorted(numvals.items(), key=lambda item: item[1]))
        # Determine if multiple variables have the same min # values in domain
        minval = min(sorted_numvals.values())
        minimum = [k for k, v in sorted_numvals.items() if v == minval]
        # If a tie:
        if len(minimum) > 1:
            # Find var with the most neighbors
            degree = {var: len(self.crossword.neighbors(var)) for var in minimum}
            maxval = max(degree.values())
            maximum = [k for k, v in degree.items() if v == maxval]
            # If a tie, return any var
            if len(maximum) > 1:
                return maximum[random.randrange(len(maximum))]
            return maximum[0]
        return minimum[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # If assignment is complete, return it
        if self.assignment_complete(assignment):
            return assignment
        # Select an unassigned variable from the assignment
        var = self.select_unassigned_variable(assignment)
        # Iterate over values in domain
        for value in self.order_domain_values(var, assignment):
            # Add to assignment
            assignment[var] = value
            # If consistent, backtrack
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                # Return result if there is one
                if result:
                    return result
            # If not consistent, delete from assignment
            del assignment[var]
        # If no solution, return None
        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
