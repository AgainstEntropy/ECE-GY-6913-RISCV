
from constants import INSTR_TYPES, ENDIAN_TYPES
from misc import sign_ext, signed_binary_str_to_int
from alu import ALU_OPs

OPCODE_TO_INSTR_TYPE = {
    "0110011": INSTR_TYPES.R,
    "0010011": INSTR_TYPES.I,
    "1101111": INSTR_TYPES.J,
    "1100011": INSTR_TYPES.B,
    "0000011": INSTR_TYPES.LOAD_I,
    "0100011": INSTR_TYPES.S,
    "1111111": INSTR_TYPES.HALT
}

class Instruction:

    def reset(self):
        self.opcode = None
        self.type = None
        self.funct3 = None
        self.funct7 = None
        self.rs1 = None
        self.rs2 = None
        self.rd = None
        self.imm = None
        self.alu_op = None

        # self.control = None
        # self.alu_control = None

    def __init__(self, instruction: str, endian: str = ENDIAN_TYPES.BIG):
        self.raw_instr = instruction
        self.endian = endian
        self.reset()

        self.parse_type()
        self.parse_func()
        self.parse_registers()
        self.parse_imm()
        self.parse_alu()

        if self.type == INSTR_TYPES.HALT:
            return

    def parse_type(self):
        self.opcode = self.slice(0, 6)
        self.type = OPCODE_TO_INSTR_TYPE[self.opcode]

    def parse_func(self):
        if self.type != INSTR_TYPES.J:
            self.funct3 = self.slice(12, 14)

        if self.type == INSTR_TYPES.R:
            self.funct7 = self.slice(25, 31)

    def parse_registers(self):
        if self.type != INSTR_TYPES.J:
            self.rs1 = signed_binary_str_to_int(self.slice(15, 19))

        if self.type in [INSTR_TYPES.R, INSTR_TYPES.S, INSTR_TYPES.B]:
            self.rs2 = signed_binary_str_to_int(self.slice(20, 24))

        if self.type not in [INSTR_TYPES.S, INSTR_TYPES.B]:
            self.rd = signed_binary_str_to_int(self.slice(7, 11))

    def parse_imm(self):
        imm = None
        if self.type in [INSTR_TYPES.I, INSTR_TYPES.LOAD_I]:
            imm = self.slice(20, 31)
        elif self.type == INSTR_TYPES.J:
            imm = self.slice(31) + self.slice(12, 19) + \
                self.slice(20) + self.slice(21, 30) + '0'
        elif self.type == INSTR_TYPES.B:
            imm = self.slice(31) + self.slice(7) + \
                self.slice(25, 30) + self.slice(8, 11) + '0'
        elif self.type == INSTR_TYPES.S:
            imm = self.slice(25, 31) + self.slice(7, 11)

        self.imm = signed_binary_str_to_int(sign_ext(imm)) if imm else None

    def parse_alu(self):
        try:
            self.alu_op = ALU_OPs[(self.funct7, self.funct3)]
        except KeyError:
            self.alu_op = None

    def is_halt(self):
        return self.type == INSTR_TYPES.HALT
    
    def is_branch(self):
        return self.type == INSTR_TYPES.B
    
    def is_jump(self):
        return self.type == INSTR_TYPES.J
    
    def is_beq(self):
        return self.funct3 == '000'
    
    def is_bne(self):
        return self.funct3 == '001'

    def slice(self, start: int, end: int = None):
        """Slice the instruction according to the start and end.
           Slicing manner depends on the endian type. 
        """
        end = end or start
        assert start >= 0 and end <= 31, "Invalid start or end index"

        if self.endian == ENDIAN_TYPES.BIG:
            return self.raw_instr[::-1][start: end+1][::-1]
        elif self.endian == ENDIAN_TYPES.SMALL:
            return self.raw_instr[start: end+1]
        else:
            raise NotImplementedError
