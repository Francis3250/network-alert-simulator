"""
ICS 33 Project 1: Calling All Stations
Main entry point for the distributed system alert propagation simulation.
"""

from pathlib import Path
from simulation import Simulation


def _read_input_file_path() -> Path:
    """
    Reads the input file path from the standard input.

    Returns:
        Path object representing the input file location
    """
    return Path(input())


# This function lacks full test coverage because testing file existence
# in an automated way would require filesystem mocking, which is beyond
# the scope of techniques taught so far in this course.
def main() -> None:
    """
    Runs the simulation program in its entirety.
    Reads input file path, loads configuration, and runs the simulation.
    """
    input_file_path = _read_input_file_path()

    # Check if the file exists
    if not input_file_path.exists():
        print("FILE NOT FOUND")
        return

    # Load and run the simulation
    simulation = Simulation()
    simulation.load_from_file(input_file_path)
    simulation.run()


# This block is not covered by unit tests because it only executes
# when the module is run directly, not when imported for testing.
if __name__ == '__main__':  # pragma: no cover
    main()
