from pathlib import Path

from constants import FS_STATE_RESULT_FILE, RF_FILE, SS_STATE_RESULT_FILE, STAGES
from mem import DataMem, InsMem
from state import StageManager, State
from instruction import Instruction
from monitors import Monitor


class RegisterFile(object):
    def __init__(self, outPath: Path):
        self.outputFile = outPath
        self.Registers = [0x0 for _ in range(32)]

    def readRF(self, Reg_addr: int):
        return self.Registers[Reg_addr]

    def writeRF(self, Reg_addr: int, Wrt_reg_data: int):
        self.Registers[Reg_addr] = Wrt_reg_data

    def outputRF(self, cycle: int):
        op = ["-" * 70 + "\n", f"State of RF after executing cycle: {cycle}\n"]
        op.extend([f"{val}\n" for val in self.Registers])
        if cycle == 0:
            perm = "w"
        else:
            perm = "a"
        with open(self.outputFile, perm) as file:
            file.writelines(op)


class Core(object):
    def __init__(self, outPath: Path, imem: InsMem, dmem: DataMem):
        self.myRF = RegisterFile(outPath)
        self.cycle: int = 0
        self.halted: bool = False
        # self.ioDir: Path = ioDir
        self.state = State()
        self.nextState = State()
        self.ext_imem: InsMem = imem
        self.ext_dmem: DataMem = dmem

        self.monitor = Monitor()

    @staticmethod
    def parse_instruction(instruction: str):
        parsed_instruction = Instruction(instruction)
        return parsed_instruction


class SingleStageCore(Core):
    def __init__(self, ioDir: Path, imem: InsMem, dmem: DataMem):
        super(SingleStageCore, self).__init__(ioDir / f"SS_{RF_FILE}", imem, dmem)
        self.opFilePath = ioDir / SS_STATE_RESULT_FILE

        self.stage_manager = StageManager()

    def step(self):
        if self.state.IF["nop"]:
            self.halted = True
        else:
            self.IF_forward()

            self.ID_forward()

        self.myRF.outputRF(self.cycle)  # dump RF
        self.printState(
            self.nextState, self.cycle
        )  # print states after executing cycle 0, cycle 1, cycle 2 ...

        self.state = (
            self.nextState
        )  # The end of the cycle and updates the current state with the values calculated in this cycle
        self.cycle += 1

    def IF_forward(self):
        self.state.ID["Instr"] = self.ext_imem.readInstr(self.state.IF["PC"])
        self.stage_manager.forward()

    def ID_forward(self):
        self.instruction = self.parse_instruction(self.state.ID["Instr"])
        if self.instruction.is_halt():
            self.state.IF['nop'] = 1
            self.stage_manager.reset()
            return
        
        if self.instruction.rs1 is not None:
            self.state.EX["Read_data1"] = self.myRF.readRF(self.instruction.rs1)
        
        if self.instruction.rs2 is not None:
            self.state.EX["Read_data2"] = self.myRF.readRF(self.instruction.rs2)

        if self.instruction.rd is not None:
            self.state.EX["Wrt_reg_addr"] = self.instruction.rd

        if self.instruction.imm is not None:
            self.state.EX["Imm"] = self.instruction.imm
        
        self.stage_manager.forward()
    
    def printState(self, state: State, cycle: int):
        printstate = [
            "-" * 70 + "\n",
            "State after executing cycle: " + str(cycle) + "\n",
        ]
        printstate.append("IF.PC: " + str(state.IF["PC"]) + "\n")
        printstate.append("IF.nop: " + str(state.IF["nop"]) + "\n")

        perm = "w" if cycle == 0 else "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)


class FiveStageCore(Core):
    def __init__(self, ioDir: Path, imem: InsMem, dmem: DataMem):
        super(FiveStageCore, self).__init__(ioDir / f"FS_{RF_FILE}", imem, dmem)
        self.opFilePath = ioDir / FS_STATE_RESULT_FILE

    def step(self):
        # Your implementation
        # --------------------- WB stage ---------------------

        # --------------------- MEM stage --------------------

        # --------------------- EX stage ---------------------

        # --------------------- ID stage ---------------------

        # --------------------- IF stage ---------------------

        self.halted = True
        if (
            self.state.IF["nop"]
            and self.state.ID["nop"]
            and self.state.EX["nop"]
            and self.state.MEM["nop"]
            and self.state.WB["nop"]
        ):
            self.halted = True

        self.myRF.outputRF(self.cycle)  # dump RF
        self.printState(
            self.nextState, self.cycle
        )  # print states after executing cycle 0, cycle 1, cycle 2 ...

        self.state = (
            self.nextState
        )  # The end of the cycle and updates the current state with the values calculated in this cycle
        self.cycle += 1

    def printState(self, state: State, cycle: int):
        printstate = [
            "-" * 70 + "\n",
            "State after executing cycle: " + str(cycle) + "\n",
        ]
        printstate.extend(
            ["IF." + key + ": " + str(val) + "\n" for key, val in state.IF.items()]
        )
        printstate.extend(
            ["ID." + key + ": " + str(val) + "\n" for key, val in state.ID.items()]
        )
        printstate.extend(
            ["EX." + key + ": " + str(val) + "\n" for key, val in state.EX.items()]
        )
        printstate.extend(
            ["MEM." + key + ": " + str(val) + "\n" for key, val in state.MEM.items()]
        )
        printstate.extend(
            ["WB." + key + ": " + str(val) + "\n" for key, val in state.WB.items()]
        )

        if cycle == 0:
            perm = "w"
        else:
            perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)