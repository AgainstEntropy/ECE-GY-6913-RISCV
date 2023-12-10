from constants import INSTR_TYPES


class Control:
    def __init__(self, **kwargs):
        self.AluSrc   = kwargs.pop('AluSrc')
        self.MemtoReg = kwargs.pop('MemtoReg')
        self.RegWrite = kwargs.pop('RegWrite')
        self.MemRead  = kwargs.pop('MemRead')
        self.MemWrite = kwargs.pop('MemWrite')
        self.Branch   = kwargs.pop('Branch')
        self.AluOp1   = kwargs.pop('AluOp1')
        self.AluOp0   = kwargs.pop('AluOp0')
        self.Jump     = kwargs.pop('Jump')

INSTR_TYPE_TO_CONTROL = {
    INSTR_TYPES.R: Control(
        AluSrc   = 0,
        MemtoReg = 0,
        RegWrite = 1,
        MemRead  = 0,
        MemWrite = 0,
        Branch   = 0,
        AluOp1   = 1,
        AluOp0   = 0,
        Jump     = 0
    ),
    INSTR_TYPES.I: Control(
        AluSrc   = 1,
        MemtoReg = 0,
        RegWrite = 1,
        MemRead  = 0,
        MemWrite = 0,
        Branch   = 0,
        AluOp1   = 0,
        AluOp0   = 0,
        Jump     = 0
    ),
    INSTR_TYPES.LOAD_I: Control(
        AluSrc   = 1,
        MemtoReg = 1,
        RegWrite = 1,
        MemRead  = 1,
        MemWrite = 0,
        Branch   = 0,
        AluOp1   = 0,
        AluOp0   = 0,
        Jump     = 0
    ),
    INSTR_TYPES.S: Control(
        AluSrc   = 1,
        MemtoReg = 0,
        RegWrite = 0,
        MemRead  = 0,
        MemWrite = 1,
        Branch   = 0,
        AluOp1   = 0,
        AluOp0   = 0,
        Jump     = 0
    ),
    INSTR_TYPES.B: Control(
        AluSrc   = 0,
        MemtoReg = 0,
        RegWrite = 0,
        MemRead  = 0,
        MemWrite = 0,
        Branch   = 1,
        AluOp1   = 0,
        AluOp0   = 1,
        Jump     = 0
    ),
    INSTR_TYPES.J: Control(
        AluSrc   = 1,
        MemtoReg = 0,
        RegWrite = 0,
        MemRead  = 0,
        MemWrite = 0,
        Branch   = 0,
        AluOp1   = 0,
        AluOp0   = 0,
        Jump     = 1
    )
}