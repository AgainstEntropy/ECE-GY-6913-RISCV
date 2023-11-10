from easydict import EasyDict

ALU_OPs = EasyDict(
    ADD = lambda a, b: a + b,
    SUB = lambda a, b: a - b,
    XOR = lambda a, b: a ^ b,
    OR  = lambda a, b: a | b,
    AND = lambda a, b: a & b,
)

FUNCT3_TO_ALU = {
    '000': ALU_OPs.ADD,
    '010': ALU_OPs.ADD,
    '001': ALU_OPs.ADD,
    '100': ALU_OPs.XOR,
    '110': ALU_OPs.OR,
    '111': ALU_OPs.AND,
}