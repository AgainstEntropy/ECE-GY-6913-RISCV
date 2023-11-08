class State(object):
    def __init__(self):
        self.IF = {"nop": False, "PC": 0}
        self.ID = {"nop": False, "Instr": 0}
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
        }
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
        }
        self.WB = {
            "nop": False,
            "Wrt_data": 0,
            "Rs": 0,
            "Rt": 0,
            "Wrt_reg_addr": 0,
            "wrt_enable": 0,
        }