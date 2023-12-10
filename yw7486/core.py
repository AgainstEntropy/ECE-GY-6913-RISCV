from copy import deepcopy
from pathlib import Path

from constants import (FS_STATE_RESULT_FILE, INSTR_TYPES, PERFORMANCE_FILE,
                       RF_FILE, SS_STATE_RESULT_FILE, STAGES, WORD_LEN)
from instruction import Instruction
from mem import DataMem, InsMem
from misc import signed_int_to_binary_str
from monitors import Monitor
from state import StageManager, State


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
        op.extend([f"{signed_int_to_binary_str(val)}\n" for val in self.Registers])
        if cycle == 0:
            perm = "w"
        else:
            perm = "a"
        with open(self.outputFile, perm) as file:
            file.writelines(op)


class Core(object):
    def __init__(self, core_type: str, outDir: Path, imem: InsMem, dmem: DataMem):
        match core_type:
            case "Single Stage":
                outPath = outDir / f"SS_{RF_FILE}"
                self.opFilePath = outDir / SS_STATE_RESULT_FILE
            case "Five Stage":
                outPath = outDir / f"FS_{RF_FILE}"
                self.opFilePath = outDir / FS_STATE_RESULT_FILE

        self.myRF = RegisterFile(outPath)
        self.monitor = Monitor(core_type, outputFile=outDir / PERFORMANCE_FILE)
        
        self.cycle: int = 0
        self.halted: bool = False
        
        self.state = State()
        self.nextState = State()
        self.ext_imem: InsMem = imem
        self.ext_dmem: DataMem = dmem

    @staticmethod
    def parse_instruction(instruction: str):
        parsed_instruction = Instruction(instruction)
        return parsed_instruction


class SingleStageCore(Core):
    def __init__(self, ioDir: Path, imem: InsMem, dmem: DataMem):
        super(SingleStageCore, self).__init__("Single Stage", ioDir, imem, dmem)
        
        self.stage_manager = StageManager()

    def IF_forward(self):
        self.nextState.ID["Instr"] = self.ext_imem.readInstr(self.nextState.IF["PC"])
        self.monitor.update_instr()
        self.stage_manager.forward()

    def ID_forward(self):
        current_instr = self.parse_instruction(self.nextState.ID["Instr"])
        self.nextState.EX["is_I_type"] = (current_instr.type == INSTR_TYPES.I)
        
        if current_instr.type == INSTR_TYPES.HALT:
            self.nextState.IF["nop"] = True
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

        if current_instr.type == INSTR_TYPES.J:
            self.myRF.writeRF(self.nextState.EX["Wrt_reg_addr"], self.nextState.IF["PC"] + WORD_LEN)
            self.nextState.IF["PC"] += self.nextState.EX["Imm"]
            self.stage_manager.reset()
            return
        
        if current_instr.type == INSTR_TYPES.B:
            rs_equal = (self.nextState.EX["Read_data1"] == self.nextState.EX["Read_data2"])
            if (current_instr.is_beq() and rs_equal) or (current_instr.is_bne() and not rs_equal):
                self.nextState.IF["PC"] += self.nextState.EX["Imm"]
            else:
                self.nextState.IF["PC"] += WORD_LEN
            self.stage_manager.reset()
            return
        
        self.instr_type = current_instr.type
        
        self.stage_manager.forward()

    def EX_forward(self):
        operand_1 = self.nextState.EX["Read_data1"]
        if self.instr_type in [INSTR_TYPES.R, INSTR_TYPES.B]:
            operand_2 = self.nextState.EX["Read_data2"]
        else:
            operand_2 = self.nextState.EX["Imm"]

        self.nextState.MEM["ALUresult"] = self.nextState.EX["alu_op"](operand_1, operand_2)

        self.nextState.MEM["Wrt_reg_addr"] = self.nextState.EX["Wrt_reg_addr"]
        
        self.nextState.MEM["Store_data"] = self.nextState.EX["Read_data2"]

        self.stage_manager.forward()
    
    def MEM_forward(self):
        if self.instr_type == INSTR_TYPES.S:
            self.ext_dmem.writeDataMem(self.nextState.MEM["ALUresult"], self.nextState.MEM["Store_data"])
        
        if self.instr_type == INSTR_TYPES.LOAD_I:
            read_addr = self.nextState.MEM["ALUresult"]
            read_val = self.ext_dmem.readDataMem(read_addr)
            self.nextState.WB["Wrt_data"] = read_val
        else:
            self.nextState.WB["Wrt_data"] = self.nextState.MEM["ALUresult"]
        
        self.nextState.WB["Wrt_reg_addr"] = self.nextState.MEM["Wrt_reg_addr"]

        self.stage_manager.forward()
    
    def WB_forward(self):
        if self.instr_type in [INSTR_TYPES.R, INSTR_TYPES.I, INSTR_TYPES.LOAD_I]:
            self.myRF.writeRF(self.nextState.WB["Wrt_reg_addr"], self.nextState.WB["Wrt_data"])

        self.nextState.IF["PC"] += WORD_LEN
        self.stage_manager.reset()

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

        # The end of the cycle and updates the current state with the values calculated in this cycle
        self.state = deepcopy(self.nextState)  
        self.cycle += 1
        self.monitor.update_cycle()
    
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
        super(FiveStageCore, self).__init__("Five Stage", ioDir, imem, dmem)
        
        self.buffer = State()

    def IF_forward(self):
        if self.nextState.ID["halted"]:
            return

        self.buffer.ID["Instr"] = self.ext_imem.readInstr(self.nextState.IF["PC"])
        self.nextState.IF["PC"] += 4

        self.monitor.update_instr()

    def ID_forward(self):
        if self.nextState.ID["halted"]:
            self.nextState.EX["halted"] = True
            self.nextState.ID["nop"] = True
            return

        self.nextState.ID["Instr"] = self.buffer.ID["Instr"]
        
        if not self.nextState.ID["Instr"]:
            return

        current_instr = Instruction(self.buffer.ID["Instr"])

        if current_instr.type == INSTR_TYPES.HALT:
            self.nextState.ID["halted"] = True
            self.nextState.EX["halted"] = True
            self.nextState.ID["nop"] = True
            self.nextState.IF["nop"] = True
            return

        if self.check_load_use_data(current_instr):
            return

        # pass the instruction itself to the buffer along with state relevant data
        self.buffer.EX["parsed_instr"] = current_instr
        if not current_instr.rs1 is None:
            self.buffer.EX["Read_data1"] = self.myRF.readRF(current_instr.rs1)
        
        if not current_instr.rs2 is None:
            self.buffer.EX["Read_data2"] = self.myRF.readRF(current_instr.rs2)
        
        if current_instr.control.Branch == 1 and self.check_branching(current_instr):
            self.nextState.EX["nop"] = True
            self.nextState.IF["PC"] = self.nextState.IF["PC"] - 4 + current_instr.imm
            return

        if not current_instr.imm is None:
            self.buffer.EX["Imm"] = current_instr.imm
        
        if not current_instr.alu_op is None:
            self.buffer.EX["alu_op"] = current_instr.alu_op
        
        if not current_instr.rd is None:
            self.buffer.EX["Wrt_reg_addr"] = current_instr.rd

        if current_instr.control.Jump == 1:
            self.myRF.writeRF(current_instr.rd,self.nextState.IF["PC"])
            self.nextState.IF["PC"] = self.nextState.IF["PC"] - 4 + current_instr.imm
            self.nextState.EX["nop"] = True
            return
        
    def EX_forward(self):
        if self.nextState.EX["halted"]:
            self.nextState.MEM["halted"] = True
            self.nextState.EX["nop"] = True
            return

        if self.nextState.EX["nop"]:
            self.buffer.reset_EX()
            self.nextState.MEM["nop"] = True
            self.nextState.EX["nop"] = False
            return


        forwardA, forwardB = self.check_forwarding()

        self.nextState.EX["parsed_instr"]: Instruction = self.buffer.EX["parsed_instr"]

        self.nextState.EX["Read_data1"] = self.buffer.EX["Read_data1"]

        self.nextState.EX["Read_data2"] = self.buffer.EX["Read_data2"]
        

        self.nextState.EX["Imm"] = self.buffer.EX["Imm"]
        self.nextState.EX["alu_op"] = self.buffer.EX["alu_op"]
        self.nextState.EX["Wrt_reg_addr"] = self.buffer.EX["Wrt_reg_addr"]

        if forwardA == 0b01:
            self.nextState.EX["Read_data1"] = self.buffer.WB["Wrt_data"]
        elif forwardA == 0b10:
            self.nextState.EX["Read_data1"] = self.buffer.MEM["ALUresult"]
            
        if forwardB == 0b01:
            self.nextState.EX["Read_data2"] = self.buffer.WB["Wrt_data"]
        elif forwardB == 0b10:
            self.nextState.EX["Read_data2"] = self.buffer.MEM["ALUresult"]

        if self.nextState.EX["parsed_instr"]:
            self.buffer.MEM["parsed_instr"] = self.nextState.EX["parsed_instr"]

            operand_1 = self.nextState.EX["Read_data1"]
            if self.nextState.EX["parsed_instr"].control.AluSrc == 0:
                operand_2 = self.nextState.EX["Read_data2"]
            else:
                operand_2 = self.nextState.EX["Imm"]

            self.buffer.MEM["ALUresult"] = self.nextState.EX["alu_op"](operand_1, operand_2)

            self.buffer.MEM["Wrt_reg_addr"] = self.nextState.EX["Wrt_reg_addr"]
            
            self.buffer.MEM["Store_data"] = self.nextState.EX["Read_data2"]

    
    def MEM_forward(self):
        if self.nextState.MEM["halted"]:
            self.nextState.WB["halted"] = True
            self.nextState.MEM["nop"] = True
            return

        if self.nextState.MEM["nop"]:
            self.buffer.reset_MEM()
            self.nextState.WB["nop"] = True
            self.nextState.MEM["nop"] = False
            return

        self.nextState.MEM["parsed_instr"]: Instruction = self.buffer.MEM["parsed_instr"]
        self.nextState.MEM["ALUresult"] = self.buffer.MEM["ALUresult"]
        self.nextState.MEM["Store_data"] = self.buffer.MEM["Store_data"]
        self.nextState.MEM["Wrt_reg_addr"] = self.buffer.MEM["Wrt_reg_addr"]


        if self.nextState.MEM["parsed_instr"]:

            self.buffer.WB["parsed_instr"]: Instruction = self.nextState.MEM["parsed_instr"]

            if self.nextState.MEM["parsed_instr"].control.MemWrite == 1:
                self.ext_dmem.writeDataMem(self.nextState.MEM["ALUresult"],self.nextState.MEM["Store_data"])
            
            if self.nextState.MEM["parsed_instr"].control.MemtoReg == 1:
                if self.nextState.MEM["parsed_instr"].control.MemRead == 1:
                    read_addr = self.nextState.MEM["ALUresult"]
                    read_val = self.ext_dmem.readDataMem(read_addr)
                    self.buffer.WB["Wrt_data"] = read_val

            elif self.nextState.MEM["parsed_instr"].control.MemtoReg == 0:
                self.buffer.WB["Wrt_data"] = self.nextState.MEM["ALUresult"]
            
            self.buffer.WB["Wrt_reg_addr"] = self.nextState.MEM["Wrt_reg_addr"]
    
    def WB_forward(self):
        if self.nextState.WB["halted"]:
            self.nextState.WB["nop"] = True
            return

        if self.nextState.WB["nop"]:
            self.buffer.reset_WB()
            self.nextState.WB["nop"] = False
            return

        self.nextState.WB["parsed_instr"]: Instruction = self.buffer.WB["parsed_instr"]
        self.nextState.WB["Wrt_reg_addr"] = self.buffer.WB["Wrt_reg_addr"]
        self.nextState.WB["Wrt_data"] = self.buffer.WB["Wrt_data"]
        
        if self.nextState.WB["parsed_instr"] and self.nextState.WB["parsed_instr"].control.RegWrite:
                self.myRF.writeRF(self.nextState.WB["Wrt_reg_addr"],self.nextState.WB["Wrt_data"])    

    def check_branching(self, instr: Instruction) -> bool:
        val1, val2 = self.buffer.EX["Read_data1"],self.buffer.EX["Read_data2"]

        if self.buffer.WB["parsed_instr"] and self.buffer.WB["parsed_instr"].control.RegWrite:
            if instr.rs1 and instr.rs1 == self.buffer.WB["Wrt_reg_addr"]:
                val1 = self.buffer.WB["Wrt_data"]
            elif instr.rs2 and instr.rs2 == self.buffer.WB["Wrt_reg_addr"]:
                val2 = self.buffer.WB["Wrt_data"]

        if instr.rs1 and instr.rs1 == self.buffer.MEM["Wrt_reg_addr"]:
            val1 = self.buffer.MEM["ALUresult"]
        elif instr.rs2 and instr.rs2 == self.buffer.MEM["Wrt_reg_addr"]:
            val2 = self.buffer.MEM["ALUresult"]
        
        rs_equal = (val1 == val2)

        return (instr.is_beq() and rs_equal) or (instr.is_bne() and not rs_equal)
    
    def check_load_use_data(self, instr: Instruction) -> bool:
        if self.buffer.EX["parsed_instr"] and self.buffer.EX["parsed_instr"].control.MemRead:
            if (self.buffer.EX["parsed_instr"].rd == instr.rs1) or (self.buffer.EX["parsed_instr"].rd == instr.rs2):
                self.nextState.IF["PC"] -= 4
                self.nextState.EX["nop"] = True
                return True
        return False
    
    def check_forwarding(self) -> tuple[int, int]:
        forwardA, forwardB = 0b00,0b00

        if self.buffer.WB["parsed_instr"] and self.buffer.EX["parsed_instr"] and self.buffer.EX["parsed_instr"].control.RegWrite:
            if self.buffer.MEM["parsed_instr"] and self.buffer.MEM["parsed_instr"].rd and self.buffer.MEM["parsed_instr"].rd == self.buffer.EX["parsed_instr"].rs1:
                forwardA = 0b10
            elif self.buffer.WB["parsed_instr"].rd and self.buffer.WB["parsed_instr"].rd == self.buffer.EX["parsed_instr"].rs1:
                forwardA = 0b01
        
            if self.buffer.MEM["parsed_instr"] and self.buffer.MEM["parsed_instr"].rd and self.buffer.MEM["parsed_instr"].rd == self.buffer.EX["parsed_instr"].rs2:
                forwardB = 0b10
            elif self.buffer.WB["parsed_instr"].rd and self.buffer.WB["parsed_instr"].rd == self.buffer.EX["parsed_instr"].rs2:
                forwardB = 0b01
        
        return forwardA, forwardB

    def step(self):
        # Your implementation
        # --------------------- WB stage ---------------------
        self.WB_forward()
        
        # --------------------- MEM stage --------------------
        self.MEM_forward()
        
        # --------------------- EX stage ---------------------
        self.EX_forward()
        
        # --------------------- ID stage ---------------------
        self.ID_forward()
        
        # --------------------- IF stage ---------------------
        self.IF_forward()

        if (
            self.nextState.IF["nop"]
            and self.nextState.ID["nop"]
            and self.nextState.EX["nop"]
            and self.nextState.MEM["nop"]
            and self.nextState.WB["nop"]
        ):
            self.halted = True

        self.myRF.outputRF(self.cycle)  # dump RF
        self.printState(
            self.nextState, self.cycle
        )  # print states after executing cycle 0, cycle 1, cycle 2 ...

        self.state = deepcopy(self.nextState)  # The end of the cycle and updates the current state with the values calculated in this cycle
        self.cycle += 1
        self.monitor.update_cycle()

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