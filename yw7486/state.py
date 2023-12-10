from constants import STAGES


class State(object):
    def __init__(self):
        self.reset_IF()
        self.reset_ID()
        self.reset_EX()
        self.reset_MEM()
        self.reset_WB()

    def reset_IF(self):
        self.IF = {"nop": False, "PC": 0, "halted":False}

    def reset_ID(self):
        self.ID = {"nop": False, "Instr": None, "halted":False}

    def reset_EX(self):
        self.EX = {
            "nop": False,
            "Read_data1": 0,
            "Read_data2": 0,
            "Imm": 0,
            "Rs": 0,
            "Rt": 0,
            "Wrt_reg_addr": 0,
            "is_I_type": False,
            "rd_mem": 0,
            "wrt_mem": 0,
            "alu_op": 0,
            "wrt_enable": 0,
            "parsed_instr":None,
            "halted":False
        }

    def reset_MEM(self):
        self.MEM = {
            "nop": False,
            "ALUresult": 0,
            "Store_data": 0,
            "Rs": 0,
            "Rt": 0,
            "Wrt_reg_addr": 0,
            "rd_mem": 0,
            "wrt_mem": 0,
            "wrt_enable": 0,
            "parsed_instr":None,
            "halted":False
        }

    def reset_WB(self):
        self.WB = {
            "nop": False,
            "Wrt_data": 0,
            "Rs": 0,
            "Rt": 0,
            "Wrt_reg_addr": 0,
            "wrt_enable": 0,
            "parsed_instr":None,
            "halted":False
        }


class StageManager:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.current_stage: STAGES = STAGES.IF
    
    def set_stage(self, stage: int = None) -> None:
        if stage is not None:
            self.current_stage = stage
        
    def forward(self) -> None:
        self.current_stage = STAGES(self.current_stage.value + 1)

    def is_stage(self, stage: int) -> bool:
        return self.current_stage == stage