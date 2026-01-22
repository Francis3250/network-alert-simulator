"""
Unit tests for ICS 33 Project 1: Calling All Stations
Tests the simulation, event queue, and input parsing functionality.
"""

import io
import sys
import tempfile
from pathlib import Path
import unittest

from project1 import _read_input_file_path, main
from simulation import Simulation
from event import EventQueue
from input_parser import parse_input_file, SimulationConfig


class TestEventQueue(unittest.TestCase):
    """Tests for the EventQueue class."""

    def setUp(self):
        self.queue = EventQueue()

    def test_schedule_and_pop_single_event(self):
        self.queue.schedule(100, "TEST_EVENT", {"data": "test"}, 1000)
        time, event_type, data = self.queue.pop()
        self.assertEqual(time, 100)
        self.assertEqual(event_type, "TEST_EVENT")
        self.assertEqual(data, {"data": "test"})

    def test_schedule_multiple_events_chronological_order(self):
        self.queue.schedule(300, "EVENT3", None, 1000)
        self.queue.schedule(100, "EVENT1", None, 1000)
        self.queue.schedule(200, "EVENT2", None, 1000)

        time1, event_type1, _ = self.queue.pop()
        self.assertEqual(time1, 100)
        self.assertEqual(event_type1, "EVENT1")

        time2, event_type2, _ = self.queue.pop()
        self.assertEqual(time2, 200)
        self.assertEqual(event_type2, "EVENT2")

        time3, event_type3, _ = self.queue.pop()
        self.assertEqual(time3, 300)
        self.assertEqual(event_type3, "EVENT3")

    def test_schedule_beyond_max_time_ignored(self):
        self.queue.schedule(1500, "LATE_EVENT", None, 1000)
        self.assertTrue(self.queue.is_empty())

    def test_is_empty(self):
        self.assertTrue(self.queue.is_empty())
        self.queue.schedule(100, "EVENT", None, 1000)
        self.assertFalse(self.queue.is_empty())
        self.queue.pop()
        self.assertTrue(self.queue.is_empty())


class TestInputParser(unittest.TestCase):
    """Tests for the input parsing functionality."""

    def test_parse_basic_input_file(self):
        content = """# comment line
        LENGTH 100
        DEVICE 1
        DEVICE 2
        PROPAGATE 1 2 50
        ALERT 1 TestAlert 10
        CANCEL 2 TestCancel 80
        """
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt") as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        config = parse_input_file(path)

        self.assertEqual(config.simulation_length, 100)
        self.assertIn(1, config.devices)
        self.assertIn(2, config.devices)
        self.assertIn(1, config.propagation_rules)
        self.assertEqual(config.propagation_rules[1], [(2, 50)])
        self.assertEqual(config.alerts, [(1, "TestAlert", 10)])
        self.assertEqual(config.cancellations, [(2, "TestCancel", 80)])

        path.unlink()

    def test_parse_empty_lines_and_comments(self):
        content = """
        # This is a comment
        LENGTH 50

        DEVICE 1
        # Another comment

        DEVICE 2
        """
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt") as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        config = parse_input_file(path)

        self.assertEqual(config.simulation_length, 50)
        self.assertEqual(len(config.devices), 2)

        path.unlink()


class TestSimulation(unittest.TestCase):
    """Tests for the Simulation class."""

    def setUp(self):
        self.sim = Simulation()

    def test_load_from_file_basic(self):
        content = """LENGTH 100
        DEVICE 1
        DEVICE 2
        PROPAGATE 1 2 10
        ALERT 1 msg1 5
        CANCEL 1 msg1 50
        """
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt") as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        self.sim.load_from_file(path)

        self.assertEqual(self.sim.simulation_length, 100)
        self.assertIn(1, self.sim.devices)
        self.assertIn(2, self.sim.devices)
        self.assertEqual(self.sim.propagation_rules[1], [(2, 10)])
        self.assertEqual(self.sim.alerts, [(1, "msg1", 5)])
        self.assertEqual(self.sim.cancellations, [(1, "msg1", 50)])

        path.unlink()

    def test_run_simple_alert_propagation(self):
        content = """LENGTH 200
        DEVICE 1
        DEVICE 2
        PROPAGATE 1 2 50
        ALERT 1 TestMsg 10
        """
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt") as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        self.sim.load_from_file(path)

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        self.sim.run()
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        self.assertIn("@10: #1 SENT ALERT TO #2: TestMsg", output)
        self.assertIn("@60: #2 RECEIVED ALERT FROM #1: TestMsg", output)
        self.assertIn("@200: END", output)

        path.unlink()

    def test_run_alert_and_cancellation(self):
        content = """LENGTH 500
        DEVICE 1
        DEVICE 2
        PROPAGATE 1 2 100
        PROPAGATE 2 1 100
        ALERT 1 Alert1 50
        CANCEL 2 Alert1 200
        """
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt") as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        self.sim.load_from_file(path)

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        self.sim.run()
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        self.assertIn("SENT ALERT", output)
        self.assertIn("RECEIVED ALERT", output)
        self.assertIn("SENT CANCELLATION", output)
        self.assertIn("RECEIVED CANCELLATION", output)
        self.assertIn("@500: END", output)

        path.unlink()

    def test_device_with_no_propagation_rules(self):
        content = """LENGTH 100
        DEVICE 1
        ALERT 1 Lonely 50
        """
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt") as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        self.sim.load_from_file(path)

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        self.sim.run()
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        # Device 1 has no propagation rules, so no alerts are sent
        self.assertNotIn("SENT ALERT", output)
        self.assertIn("@100: END", output)

        path.unlink()

    def test_sample_input_scenario(self):
        """Test the exact sample scenario from the project description."""
        content = """# Sample input
        LENGTH 9999
        DEVICE 1
        DEVICE 2
        DEVICE 3
        DEVICE 4
        PROPAGATE 1 2 750
        PROPAGATE 2 3 1250
        PROPAGATE 3 4 500
        PROPAGATE 4 1 1000
        ALERT 1 Trouble 0
        CANCEL 1 Trouble 2200
        """
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt") as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        sim = Simulation()
        sim.load_from_file(path)

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        sim.run()
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        # Verify key events occur
        self.assertIn("@0: #1 SENT ALERT TO #2: Trouble", output)
        self.assertIn("@750: #2 RECEIVED ALERT FROM #1: Trouble", output)
        self.assertIn("@2200: #1 SENT CANCELLATION TO #2: Trouble", output)
        self.assertIn("@9999: END", output)

        path.unlink()


class TestMain(unittest.TestCase):
    """Tests for the main function and program entry point."""

    def test_read_input_file_path(self):
        old_stdin = sys.stdin
        sys.stdin = io.StringIO("/path/to/file.txt\n")
        try:
            path = _read_input_file_path()
            self.assertEqual(str(path), "/path/to/file.txt")
        finally:
            sys.stdin = old_stdin

    def test_main_with_valid_file(self):
        content = """LENGTH 100
        DEVICE 1
        ALERT 1 Test 50
        """
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt") as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        old_stdin = sys.stdin
        old_stdout = sys.stdout
        sys.stdin = io.StringIO(str(path) + "\n")
        sys.stdout = io.StringIO()
        try:
            main()
            output = sys.stdout.getvalue()
        finally:
            sys.stdin = old_stdin
            sys.stdout = old_stdout

        self.assertIn("@100: END", output)

        path.unlink()

    def test_main_with_nonexistent_file(self):
        nonexistent_path = "/tmp/nonexistent_file_12345.txt"

        old_stdin = sys.stdin
        old_stdout = sys.stdout
        sys.stdin = io.StringIO(nonexistent_path + "\n")
        sys.stdout = io.StringIO()
        try:
            main()
            output = sys.stdout.getvalue()
        finally:
            sys.stdin = old_stdin
            sys.stdout = old_stdout

        self.assertEqual(output.strip(), "FILE NOT FOUND")


# This line is not covered because it only executes when this test
# module is run directly, which is not how the test framework runs it.
if __name__ == "__main__":  # pragma: no cover
    unittest.main()
