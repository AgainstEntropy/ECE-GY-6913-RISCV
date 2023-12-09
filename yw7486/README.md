# ECE-GY-6913-RISCV

RISC-V simulator with Python.

- [x] Single Stage Core

- [ ] Five Stage Core

## Create Environment

### with `Conda`

    conda env create -n risc-v -f requirements.txt

    conda activate risc-v

### with vanilla `pip`

    pip install -r requirements.txt

## Run

### with default arguments

    python ./yw7486/main.py

This will automatically create an output folder called `output_yw7486`.

### with specified input path

    python ./yw7486/main.py --iodir=/path/to/input/folder/

### with debug mode

When `debug` is activated, the output folder will be `output_yw7486_debug` instead of `output_yw7486`.

    python ./yw7486/main.py --debug
