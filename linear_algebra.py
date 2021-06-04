class Matrix():
    def __init__(self, matrix: list = None, rows: int = None, cols: int = None):
        if matrix:
            assert not rows and not cols
            self.matrix = matrix
        elif rows and cols:
            assert not matrix
            assert rows > 0 and cols > 0
            self.matrix = []
            for i in range(rows):
                temp = []
                for j in range(cols):
                    temp.append(0)
                self.matrix.append(temp)
        else:
            raise

    def swap_rows(self, row_a: int, row_b: int):
        self.matrix[row_a], self.matrix[row_b] = self.matrix[row_b], self.matrix[row_a]

    def __str__(self):
        new_str = ''
        for row in self.matrix:
            new_str += f'{row}\n'
        return new_str

    __repr__ = __str__

    def multiply_row_by_nonzero_number(self, row: int, multiple: float):
        assert multiple != 0
        self.matrix[row] = [multiple * value for value in self.matrix[row]]

    def add_multiple_of_one_row_to_another_row(self, multiplied_row: int, multiple: float, destination_row: int):
        self.matrix[destination_row] = [sum(col) for col in zip(self.matrix[destination_row],
                                                                [multiple * value for value in
                                                                 self.matrix[multiplied_row]])]


class GaussianEliminationMatrix(Matrix):
    def __init__(self, matrix: list = None, rows: int = None, cols: int = None):
        super().__init__(matrix, rows, cols)
        if rows and cols:
            assert rows >= 1 and cols >= 2
        elif matrix:
            assert len(matrix) >= 1 and len(matrix[0]) >= 2

    def __str__(self):
        new_str = ''
        SEPARATION_LENGTH = 3
        for row in self.matrix:
            row_str = '['
            row.insert(-1, '|')
            for item in row:
                row_str += f'{item:>{SEPARATION_LENGTH}}'
            row_str += ']\n'
            new_str += row_str
        return new_str


mat = GaussianEliminationMatrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
mat.add_multiple_of_one_row_to_another_row(0, -3, 1)
print(mat)
