import sys
import warnings

from psyk.interpreter.interpreter import interpret_intermediate
from psyk.project import psyk_to_intermediate

warnings.filterwarnings('ignore')


def main():
    if len(sys.argv) != 2:
        raise ValueError('Missing file name')

    (_, file_name) = sys.argv

    if not file_name.endswith('.psyk'):
        raise ValueError('File must be a .psyk file')

    with open(file_name, 'r') as file:
        file_contents = file.read()

    intermediate = psyk_to_intermediate(file_contents)
    interpret_intermediate(intermediate)


if __name__ == '__main__':
    main()
