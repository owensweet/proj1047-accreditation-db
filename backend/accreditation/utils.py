import csv
import io

def get_cell(rows, row_number, col_letter):
    """
    Extracts the value from a specific cell in pre-parsed CSV data.

    :param rows: List of rows from CSV.
    :param row_number: Row number of the cell (0-indexed).
    :param col_letter: Column letter of the cell (e.g., 'A', 'B', etc.).
    :return: The value of the specified cell as a string.
    """
    col_number = ord(col_letter.upper()) - ord('A')
    try:
        return rows[row_number][col_number]
    except IndexError:
        raise ValueError("Specified row or column is out of range.")