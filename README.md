# Network Alert Simulator

A **discrete-event simulator** of alert and cancellation messages spreading through a network of devices.

> Course project — ICS 33 (Intermediate Programming), UC Irvine, Winter 2026 ("Calling All Stations"). Built on course-provided starter scaffolding; the simulation itself is my implementation.

## How it works

Devices forward alerts to their neighbors with a fixed propagation delay. A cancellation chases the alert through the network and stops devices from passing it on. The simulator processes everything as timed events:

- **`event.py`**: a priority **event queue built on `heapq`**. A monotonically increasing counter breaks ties, so events scheduled for the same time always run in the same order and the output is deterministic.
- **`input_parser.py`**: reads the scenario file (simulation length, devices, propagation delays, scheduled alerts and cancellations).
- **`simulation.py`**: tracks each device's state (alerts received, cancellations received) and schedules the follow-up send/receive events.
- **`tests/`**: 14 unit tests covering event ordering, propagation, and cancellation timing.

## Running

```bash
python project1.py
# then enter the path to a scenario file, e.g. samples/sample_input.txt
python -m unittest discover tests   # all tests passing
```

`samples/` holds an example scenario and its expected output.
