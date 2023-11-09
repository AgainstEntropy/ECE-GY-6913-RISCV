ALU_OPs = {
    ('0000000', '000'): lambda a, b: a + b,
    ('0100000', '000'): lambda a, b: a - b,
    ('0000000', '100'): lambda a, b: a ^ b,
    ('0000000', '100'): lambda a, b: a | b,
    ('0000000', '111'): lambda a, b: a & b,
}