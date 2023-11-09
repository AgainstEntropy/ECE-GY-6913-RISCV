class Monitor:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.num_instr = 0
        self.num_cycles = 0
    
    def update(self, num_instr: int, num_cycles: int) -> None:
        self.num_instr += num_instr
        self.num_cycles += num_cycles
    
    def cpi(self) -> float:
        return self.num_cycles / self.num_instr
