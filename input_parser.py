"""
Input file parsing functionality for the simulation.
"""

from pathlib import Path


class SimulationConfig:
    """
    Stores the configuration data parsed from an input file.
    """

    def __init__(self):
        self.simulation_length = 0
        self.devices = set()
        self.propagation_rules = {}  # device_id -> [(target_id, delay), ...]
        self.alerts = []  # [(device_id, description, time), ...]
        self.cancellations = []  # [(device_id, description, time), ...]


def parse_input_file(file_path: Path) -> SimulationConfig:
    """
    Parse a simulation input file and return a configuration object.

    Args:
        file_path: Path to the input file

    Returns:
        A SimulationConfig object containing the parsed data
    """
    config = SimulationConfig()

    with file_path.open() as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split()
            command = parts[0].upper()

            if command == 'LENGTH':
                config.simulation_length = int(parts[1])
            elif command == 'DEVICE':
                config.devices.add(int(parts[1]))
            elif command == 'PROPAGATE':
                source_id, target_id, delay = map(int, parts[1:])
                config.propagation_rules.setdefault(source_id, []).append((target_id, delay))
            elif command == "ALERT":
                device_id, description, time = int(parts[1]), parts[2], int(parts[3])
                config.alerts.append((device_id, description, time))
            elif command == 'CANCEL':
                device_id, description, time = int(parts[1]), parts[2], int(parts[3])
                config.cancellations.append((device_id, description, time))

    return config
