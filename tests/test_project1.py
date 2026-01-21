import io
import sys
import tempfile
from pathlib import Path
import unittest

from project1 import Simulation, _read_input_file_path, main


class TestSimulation(unittest.TestCase):
    def setUp(self):
        self.sim = Simulation()

    def test_load_and_basic_attributes(self):
        content = """# comment line
        LENGTH 10
        DEVICE 1
        DEVICE 2
        PROPAGATE 1 2 1
        ALERT 1 msgA 1
        CANCEL 2 msgB 3
        """
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        self.sim.load(path)
        self.assertEqual(self.sim.len, 10)
        self.assertIn(1, self.sim.devi)
        self.assertIn(2, self.sim.devi)
        self.assertIn(1, self.sim.propagations)
        self.assertEqual(self.sim.alerts, [(1, "msgA", 1)])
        self.assertEqual(self.sim.cancel, [(2, "msgB", 3)])

    def test_sched_event_and_run_alert_cancel_flow(self):
        content = """LENGTH 5
                DEVICE 1
                DEVICE 2
                PROPAGATE 1 2 1
                PROPAGATE 2 1 1
                ALERT 1 hello 1
                CANCEL 2 hello 2
                """
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        self.sim.load(path)

        old_stdout=sys.stdout
        sys.stdout=io.StringIO()
        self.sim.run()
        output=sys.stdout.getvalue()
        sys.stdout=old_stdout

        self.assertIn("SENT ALERT", output)
        self.assertIn("RECEIVED ALERT", output)
        self.assertIn("SENT CANCELLATION", output)
        self.assertIn("RECEIVED CANCELLATION", output)
        self.assertIn("@5: END", output)

        prev_len = len(self.sim._event_queue)
        self.sim.sched_event(100, "ALERT_SEND", (1, "x"))
        self.assertEqual(len(self.sim._event_queue), prev_len)

    def test_no_propagations_and_multiple_events(self):
        content = """LENGTH 3
                DEVICE 1
                ALERT 1 msg 1
                CANCEL 1 msg 2
                """
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        self.sim.load(path)
        old_stdout=sys.stdout
        sys.stdout=io.StringIO()
        self.sim.run()
        output=sys.stdout.getvalue()
        sys.stdout=old_stdout

        self.assertIn("END", output)
        self.assertIn("@3: END", output)
        self.assertIn((1, "msg"), self.sim.received_cancels)

    def test_read_input_file_path_and_main(self):
        content = """LENGTH 2
                DEVICE 1
                ALERT 1 hi 1
                """
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        old_stdin=sys.stdin
        sys.stdin=io.StringIO(str(path) + "\n")
        old_stdout=sys.stdout
        sys.stdout=io.StringIO()
        try:
            main()
            main_output=sys.stdout.getvalue()
        finally:
            sys.stdin=old_stdin
            sys.stdout=old_stdout

        self.assertIn("END", main_output)

    def test_sched_event_ordering_and_counter(self):
        self.sim.len=5
        self.sim.sched_event(1, "E1", "a")
        self.sim.sched_event(1, "E2", "b")
        self.sim.sched_event(2, "E3", "c")
        prev_queue = list(self.sim._event_queue)
        self.assertEqual(len(prev_queue), 3)
        times=[t for t, *_ in prev_queue]
        self.assertTrue(all(t <= 5 for t in times))

    def test_event_exceeds_length_breaks_run_loop(self):
        self.sim.len = 2
        self.sim.sched_event(5, "ALERT_SEND", (1, "late_event"))
        old_stdout=sys.stdout
        sys.stdout=io.StringIO()
        try:
            self.sim.run()
            output=sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        self.assertIn("@2: END",output)
        self.assertNotIn("SENT ALERT",output)

    def test_sample_input_scenario(self):
        content="""# sample_input.txt


#
# ICS 33 Fall 2025
# Project 1: Calling All Stations
#
# This is a sample input file that matches the example scenario described
# in the section of the project write-up titled "The simulation model".


# The simulation's length is high enough that every event occurring in the
# example will occur before the simulation ends.
LENGTH 9999


# These are the four devices from that example
DEVICE 1
DEVICE 2
DEVICE 3
DEVICE 4


# These are the propagation rules described in that example
PROPAGATE 1 2 750
PROPAGATE 2 3 1250
PROPAGATE 3 4 500
PROPAGATE 4 1 1000


# Here, we have the one scheduled alert and its subsequent cancellation
# described in that example
ALERT 1 Trouble 0
CANCEL 1 Trouble 2200
"""
        with tempfile.NamedTemporaryFile(mode="w+",delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        sim =Simulation()
        sim.load(path)
        old_stdout=sys.stdout
        sys.stdout=io.StringIO()
        try:
            sim.run()
            output = sys.stdout.getvalue()
        finally:
            sys.stdout=old_stdout

        self.assertIn("SENT ALERT", output)
        self.assertIn("RECEIVED ALERT", output)
        self.assertIn("SENT CANCELLATION", output)
        self.assertIn("RECEIVED CANCELLATION", output)
        self.assertIn("@9999: END", output)


if __name__ == "__main__":
    unittest.main()



