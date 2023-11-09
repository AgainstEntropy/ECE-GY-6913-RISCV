from functools import partial

from constants import SYS_BIT, BIAS, UPPER_BOUND


binary_str_to_int = partial(int, base=2)

def sign_ext(x: str, prefix: str = None, length: int = SYS_BIT) -> str:
    if len(x) > length:
        raise ValueError("x is longer than length")
    prefix = prefix or x[0]
    return prefix * (length - len(x)) + x

def signed_binary_str_to_int(x: str) -> int:
    x = binary_str_to_int(x)
    return (x - BIAS) if (x > UPPER_BOUND) else x

def signed_int_to_binary_str(x: int) -> str:
    if x < 0:
        x += BIAS
        return format(x, 'b')[:32]
    return sign_ext(format(x, 'b')[:32], prefix='0')
