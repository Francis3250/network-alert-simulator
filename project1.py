from pathlib import Path
import  heapq
import itertools
import sys


def _read_input_file_path() -> Path:
    """Reads the input file path from the standard input"""
    return Path(input())

class Simulation:
    def __init__(self):
        self.len=0
        self.devi=set()
        self.propagations={}
        self.alerts=[]
        self.cancel=[]

    def load(self,p:Path):

        with p.open() as file:
            for line in file:
                line=line.strip()
                if not line or line.startswith('#'):
                    continue

                parts=line.split()
                cmd=parts[0].upper()

                if cmd=='LENGTH':
                    self.len=int(parts[1])
                elif cmd=='DEVICE':
                    self.devi.add(int(parts[1]))
                elif cmd=='PROPAGATE':
                    w,h,y=map(int,parts[1:])
                    self.propagations[(w,h)]=y
                elif cmd=="ALERT":
                    dev,msg,time=int(parts[1]),parts[2],int(parts[3])
                    self.alerts.append((dev,msg,time))
                elif cmd=='CANCEL':
                    dev,msg,time=int(parts[1]),parts[2],int(parts[3])
                    self.cancel.append((dev,msg,time))
                else:
                    raise ValueError(f"Unknown command: {cmd}")

        print(f"Simulation length: {self.len}")
        print(f"Devices: {self.devi}")
        print(f"Propagations: {self.propagations}")
        print(f"Alerts: {self.alerts}")
        print(f"Cancellations: {self.cancel}")





def main() -> None:
    """Runs the simulation program in its entirety"""
    input_file_path = _read_input_file_path()
    sim=Simulation()
    sim.load(input_file_path)


if __name__ == '__main__':
    main()
