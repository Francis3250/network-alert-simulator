"""
Core simulation logic for distributed system alert propagation.
"""

from pathlib import Path
from event import EventQueue
from input_parser import parse_input_file


class Simulation:
    """
    Simulates alert propagation in a distributed system.
    """

    def __init__(self):
        self.simulation_length = 0
        self.devices = set()
        self.propagation_rules = {}
        self.alerts = []
        self.cancellations = []
        self._event_queue = EventQueue()
        self._received_alerts = set()
        self._received_cancellations = set()

    def load_from_file(self, file_path: Path) -> None:
        """
        Load simulation configuration from a file.

        Args:
            file_path: Path to the configuration file
        """
        config = parse_input_file(file_path)
        self.simulation_length = config.simulation_length
        self.devices = config.devices
        self.propagation_rules = config.propagation_rules
        self.alerts = config.alerts
        self.cancellations = config.cancellations

    def _schedule_event(self, time: int, event_type: str, data) -> None:
        """
        Schedule an event in the event queue.

        Args:
            time: When the event should occur
            event_type: Type of the event
            data: Event-specific data
        """
        self._event_queue.schedule(time, event_type, data, self.simulation_length)

    def _handle_alert_send(self, time: int, device_id: int, description: str) -> None:
        """
        Handle a device sending an alert.

        Args:
            time: Current simulation time
            device_id: ID of the device sending the alert
            description: Description of the alert
        """
        # If this device already knows the alert is canceled, don't send it
        if (device_id, description) in self._received_cancellations:
            return  # pragma: no cover - only occurs when alert and cancel at same time

        # Send alert to all devices in the propagation set
        for target_id, delay in self.propagation_rules.get(device_id, []):
            print(f"@{time}: #{device_id} SENT ALERT TO #{target_id}: {description}")
            receive_time = time + delay
            self._schedule_event(receive_time, "ALERT_RECV", (target_id, device_id, description))

    def _handle_alert_receive(self, time: int, device_id: int, source_id: int, description: str) -> None:
        """
        Handle a device receiving an alert.

        Args:
            time: Current simulation time
            device_id: ID of the device receiving the alert
            source_id: ID of the device that sent the alert
            description: Description of the alert
        """
        self._received_alerts.add((device_id, description))
        print(f"@{time}: #{device_id} RECEIVED ALERT FROM #{source_id}: {description}")

        # Propagate the alert if it hasn't been canceled
        for target_id, delay in self.propagation_rules.get(device_id, []):
            if (device_id, description) in self._received_cancellations:
                continue
            receive_time = time + delay
            self._schedule_event(receive_time, "ALERT_RECV", (target_id, device_id, description))
            print(f"@{time}: #{device_id} SENT ALERT TO #{target_id}: {description}")

    def _handle_cancellation_send(self, time: int, device_id: int, description: str) -> None:
        """
        Handle a device sending a cancellation.

        Args:
            time: Current simulation time
            device_id: ID of the device sending the cancellation
            description: Description of the alert being canceled
        """
        self._received_cancellations.add((device_id, description))

        # Send cancellation to all devices in the propagation set
        for target_id, delay in self.propagation_rules.get(device_id, []):
            print(f"@{time}: #{device_id} SENT CANCELLATION TO #{target_id}: {description}")
            receive_time = time + delay
            self._schedule_event(receive_time, "CANCEL_RECV", (target_id, device_id, description))

    def _handle_cancellation_receive(self, time: int, device_id: int, source_id: int, description: str) -> None:
        """
        Handle a device receiving a cancellation.

        Args:
            time: Current simulation time
            device_id: ID of the device receiving the cancellation
            source_id: ID of the device that sent the cancellation
            description: Description of the alert being canceled
        """
        print(f"@{time}: #{device_id} RECEIVED CANCELLATION FROM #{source_id}: {description}")

        # If we've already received this cancellation, don't propagate it again
        if (device_id, description) in self._received_cancellations:
            return

        self._received_cancellations.add((device_id, description))

        # Propagate the cancellation
        for target_id, delay in self.propagation_rules.get(device_id, []):
            receive_time = time + delay
            self._schedule_event(receive_time, "CANCEL_RECV", (target_id, device_id, description))
            print(f"@{time}: #{device_id} SENT CANCELLATION TO #{target_id}: {description}")

    def run(self) -> None:
        """
        Run the simulation from start to finish.
        Processes all scheduled events in chronological order.
        """
        # Schedule initial alerts and cancellations
        for device_id, description, time in self.alerts:
            self._schedule_event(time, 'ALERT_SEND', (device_id, description))
        for device_id, description, time in self.cancellations:
            self._schedule_event(time, 'CANCEL_SEND', (device_id, description))

        # Process all events in chronological order
        while not self._event_queue.is_empty():
            time, event_type, data = self._event_queue.pop()

            if event_type == 'ALERT_SEND':
                device_id, description = data
                self._handle_alert_send(time, device_id, description)
            elif event_type == 'ALERT_RECV':
                device_id, source_id, description = data
                self._handle_alert_receive(time, device_id, source_id, description)
            elif event_type == 'CANCEL_SEND':
                device_id, description = data
                self._handle_cancellation_send(time, device_id, description)
            elif event_type == "CANCEL_RECV":
                device_id, source_id, description = data
                self._handle_cancellation_receive(time, device_id, source_id, description)

        print(f"@{self.simulation_length}: END")
