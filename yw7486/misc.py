from functools import partial

from constants import SYS_BIT, BIAS, UPPER_BOUND


binary_str_to_int = partial(int, base=2)

def sign_ext(x: str, length: int = SYS_BIT) -> str:
    if len(x) > length:
        raise ValueError("x is longer than length")
    return x[0] * (length - len(x)) + x

def signed_binary_str_to_int(x: str) -> int:
    x = binary_str_to_int(x)
    return (x - BIAS) if (x > UPPER_BOUND) else x
