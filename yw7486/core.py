from pathlib import Path

from constants import FS_STATE_RESULT_FILE, INSTR_TYPES, RF_FILE, SS_STATE_RESULT_FILE, STAGES, WORD_LEN
from mem import DataMem, InsMem
from state import StageManager, State
from instruction import Instruction
from misc import signed_binary_str_to_int
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
            if self.stage_manager.is_stage(STAGES.IF):
                self.IF_forward()

            if self.stage_manager.is_stage(STAGES.ID):
                self.ID_forward()

            if self.stage_manager.is_stage(STAGES.EX):
                self.EX_forward()

            if self.stage_manager.is_stage(STAGES.MEM):
                self.MEM_forward()

            if self.stage_manager.is_stage(STAGES.WB):
                self.WB_forward()

        self.myRF.outputRF(self.cycle)  # dump RF
        self.printState(
            self.nextState, self.cycle
        )  # print states after executing cycle 0, cycle 1, cycle 2 ...

        self.state = (
            self.nextState
        )  # The end of the cycle and updates the current state with the values calculated in this cycle
        self.cycle += 1

    def IF_forward(self):
        self.nextState.ID["Instr"] = self.ext_imem.readInstr(self.nextState.IF["PC"])
        self.stage_manager.forward()

    def ID_forward(self):
        current_instr = self.parse_instruction(self.nextState.ID["Instr"])
        self.nextState.EX["is_I_type"] = current_instr.is_i_type()
        
        if current_instr.is_halt():
            self.nextState.IF['nop'] = True
            self.stage_manager.reset()
            return

        if current_instr.rs1 is not None:
            self.nextState.EX["Read_data1"] = self.myRF.readRF(current_instr.rs1)
        
        if current_instr.rs2 is not None:
            self.nextState.EX["Read_data2"] = self.myRF.readRF(current_instr.rs2)

        if current_instr.rd is not None:
            self.nextState.EX["Wrt_reg_addr"] = current_instr.rd

        if current_instr.imm is not None:
            self.nextState.EX["Imm"] = current_instr.imm

        if current_instr.alu_op is not None:
            self.nextState.EX["alu_op"] = current_instr.alu_op

        if current_instr.is_jump():
            self.myRF.writeRF(self.nextState.EX["Wrt_reg_addr"], self.nextState.IF["PC"] + WORD_LEN)
            self.nextState.IF["PC"] += self.nextState.EX["Imm"]
            self.stage_manager.reset()
            return
        
        if current_instr.is_branch():
            rs_equal = (self.nextState.EX["Read_data1"] == self.nextState.EX["Read_data2"])
            if (current_instr.is_beq() and rs_equal) or (current_instr.is_bne() and not rs_equal):
                self.nextState.IF["PC"] += self.nextState.EX["Imm"]
            else:
                self.nextState.IF["PC"] += WORD_LEN
            self.stage_manager.reset()
            return
        
        self.instruction = current_instr
        
        self.stage_manager.forward()

    def EX_forward(self):
        operand_1 = self.nextState.EX["Read_data1"]
        if self.instruction.is_r_type() or self.instruction.is_branch():
            operand_2 = self.nextState.EX["Read_data2"]
        else:
            operand_2 = self.nextState.EX["Imm"]

        self.nextState.MEM["ALUresult"] = self.nextState.EX["alu_op"](operand_1, operand_2)

        self.nextState.MEM["Wrt_reg_addr"] = self.nextState.EX["Wrt_reg_addr"]
        
        self.nextState.MEM["Store_data"] = self.nextState.EX["Read_data2"]
    
    def MEM_forward(self):
        if self.instruction.is_save():
            self.ext_dmem.writeDataMem(self.state.MEM["ALUresult"], self.state.MEM["Store_data"])
        
        if self.instruction.is_loadi():
            read_addr = self.nextState.MEM["ALUresult"]
            read_val = signed_binary_str_to_int(self.ext_dmem.readDataMem(read_addr))
            self.nextState.WB["Wrt_data"] = read_val
        else:
            self.nextState.WB["Wrt_data"] = self.nextState.MEM["ALUresult"]
        
        self.nextState.WB["Wrt_reg_addr"] = self.nextState.MEM["Wrt_reg_addr"]

        self.stage_manager.forward()
    
    def WB_forward(self):
        if self.instruction.is_i_type() or self.instruction.is_r_type() or self.instruction.is_loadi():
            self.myRF.writeRF(self.state.WB["Wrt_reg_addr"], self.state.WB["Wrt_data"])

        self.state.IF["PC"] += WORD_LEN
        self.stage_manager.reset()
    
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