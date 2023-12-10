from pathlib import Path


class Monitor:
    def __init__(self, core_type: str, outputFile: Path) -> None:
        self.outputFile = outputFile
        self.core_type = core_type
        self.reset()

    def reset(self) -> None:
        self.total_instr = 0
        self.total_cycles = 0
    
    def update_cycle(self, num_cycles: int = 1) -> None:
        self.total_cycles += num_cycles

    def update_instr(self, num_instr: int = 1) -> None:
        self.total_instr += num_instr
    
    def ipc(self) -> float:
        return self.total_instr / self.total_cycles
    
    def cpi(self) -> float:
        return self.total_cycles / self.total_instr
    
    def writePerformance(self, mode: str = 'w') -> None:
        with self.outputFile.open(mode) as f:
            if mode == 'a': f.write("\n")
            f.write(f"Performance of {self.core_type}:\n")
            f.write(f"#Cycles -> {self.total_cycles}\n")
            f.write(f"#Instructions -> {self.total_instr}\n")
            f.write(f"CPI -> {self.cpi()}\n")
            f.write(f"IPC -> {self.ipc()}\n")
