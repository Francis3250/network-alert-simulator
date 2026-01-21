from pathlib import Path
import heapq
import itertools


def _read_input_file_path() -> Path:
    """Reads the input file path from the standard input"""
    return Path(input())


class Simulation:
    def __init__(self):
        self.len = 0
        self.devi = set()
        self.propagations = {}
        self.alerts = []
        self.cancel = []
        self._event_queue = []
        self.counter = itertools.count()
        self.received_alerts = set()
        self.received_cancels = set()

    def load(self, p: Path):

        with p.open() as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                parts = line.split()
                cmd = parts[0].upper()

                if cmd == 'LENGTH':
                    self.len = int(parts[1])
                elif cmd == 'DEVICE':
                    self.devi.add(int(parts[1]))
                elif cmd == 'PROPAGATE':
                    w, h, y = map(int, parts[1:])
                    self.propagations.setdefault(w, []).append((h, y))
                elif cmd == "ALERT":
                    dev, msg, time = int(parts[1]), parts[2], int(parts[3])
                    self.alerts.append((dev, msg, time))
                elif cmd == 'CANCEL':
                    dev, msg, time = int(parts[1]), parts[2], int(parts[3])
                    self.cancel.append((dev, msg, time))

    def sched_event(self, time: int, event_type: str, data):
        if time > self.len:
            return
        count = next(self.counter)
        heapq.heappush(self._event_queue, (time, count, event_type, data))

    def run(self):
        for dev, msg, t in self.alerts:
            self.sched_event(t, 'ALERT_SEND', (dev, msg))
        for dev, msg, t in self.cancel:
            self.sched_event(t, 'CANCEL_SEND', (dev, msg))

        while self._event_queue:
            time, _, event_type, data = heapq.heappop(self._event_queue)
            if event_type == 'ALERT_SEND':
                dev, msg = data
                if (dev,msg) in self.received_cancels:
                    continue
                for dest, delay in self.propagations.get(dev, []):
                    print(f"@{time}: #{dev} SENT ALERT TO #{dest}: {msg}")
                    recv_time = time + delay
                    self.sched_event(recv_time, "ALERT_RECV", (dest, dev, msg))

            elif event_type == 'ALERT_RECV':
                dest,src,msg = data
                self.received_alerts.add((dest, msg))
                print(f"@{time}: #{dest} RECEIVED ALERT FROM #{src}: {msg}")
                for next_dest, delay in self.propagations.get(dest, []):
                    if (dest, msg) in self.received_cancels:
                        continue
                    recv_time = time+delay
                    self.sched_event(recv_time,"ALERT_RECV",(next_dest,dest,msg))
                    print(f"@{time}: #{dest} SENT ALERT TO #{next_dest}: {msg}")

            elif event_type=='CANCEL_SEND':
                src,msg=data
                self.received_cancels.add((src, msg))
                for dest,delay in self.propagations.get(src,[]):
                    print(f"@{time}: #{src} SENT CANCELLATION TO #{dest}: {msg}")
                    recv_time=time+delay
                    self.sched_event(recv_time,"CANCEL_RECV",(dest,src,msg))

            elif event_type == "CANCEL_RECV":
                dest, src, msg = data
                print(f"@{time}: #{dest} RECEIVED CANCELLATION FROM #{src}: {msg}")
                if (dest, msg) in self.received_cancels:
                    continue
                self.received_cancels.add((dest, msg))
                for next_dest, delay in self.propagations.get(dest, []):
                    recv_time = time + delay
                    self.sched_event(recv_time, "CANCEL_RECV", (next_dest,dest, msg))
                    print(f"@{time}: #{dest} SENT CANCELLATION TO #{next_dest}: {msg}")

        print(f"@{self.len}: END")


def main() -> None:
    """Runs the simulation program in its entirety"""
    input_file_path = _read_input_file_path()
    sim = Simulation()
    sim.load(input_file_path)
    sim.run()


if __name__ == '__main__':
    main()
