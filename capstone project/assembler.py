import sys
import os

# Predefined Hack symbols
PREDEFINED_SYMBOLS = {
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
    "R0": 0, "R1": 1, "R2": 2, "R3": 3, "R4": 4, "R5": 5, "R6": 6, "R7": 7,
    "R8": 8, "R9": 9, "R10": 10, "R11": 11, "R12": 12, "R13": 13, "R14": 14, "R15": 15,
    "SCREEN": 16384, "KBD": 24576
}

COMP_TABLE = {
    "0":   "0101010", "1":   "0111111", "-1":  "0111010",
    "D":   "0001100", "A":   "0110000", "M":   "1110000",
    "!D":  "0001101", "!A":  "0110001", "!M":  "1110001",
    "-D":  "0001111", "-A":  "0110011", "-M":  "1110011",
    "D+1": "0011111", "A+1": "0110111", "M+1": "1110111",
    "D-1": "0001110", "A-1": "0110010", "M-1": "1110010",
    "D+A": "0000010", "A+D": "0000010",
    "D+M": "1000010", "M+D": "1000010",
    "D-A": "0010011", "D-M": "1010011",
    "A-D": "0000111", "M-D": "1000111",
    "D&A": "0000000", "A&D": "0000000",
    "D&M": "1000000", "M&D": "1000000",
    "D|A": "0010101", "A|D": "0010101",
    "D|M": "1010101", "M|D": "1010101"
}

DEST_TABLE = {
    "":    "000", "M":   "001", "D":   "010", "MD":  "011",
    "A":   "100", "AM":  "101", "AD":  "110", "AMD": "111"
}

JUMP_TABLE = {
    "":    "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"
}

def clean_lines(raw_lines):
    cleaned = []
    for line in raw_lines:
        no_comment = line.split("//")[0].strip()
        if no_comment:
            cleaned.append(no_comment)
    return cleaned

def assemble(asm_path):
    with open(asm_path, "r", encoding="utf-8") as f:
        lines = clean_lines(f.readlines())

    symbol_table = dict(PREDEFINED_SYMBOLS)
    labels = {}
    variables = {}

    # First Pass: Record label ROM addresses
    rom_address = 0
    instructions = []
    for line in lines:
        if line.startswith("(") and line.endswith(")"):
            label_name = line[1:-1].strip()
            symbol_table[label_name] = rom_address
            labels[label_name] = rom_address
        else:
            instructions.append(line)
            rom_address += 1

    # Second Pass: Translate instructions to 16-bit binary
    next_ram_address = 16
    binary_output = []

    for inst in instructions:
        if inst.startswith("@"):
            symbol = inst[1:].strip()
            if symbol.isdigit():
                val = int(symbol)
            else:
                if symbol not in symbol_table:
                    symbol_table[symbol] = next_ram_address
                    variables[symbol] = next_ram_address
                    next_ram_address += 1
                val = symbol_table[symbol]
            binary_output.append(f"0{val:015b}")
        else:
            dest_part = ""
            jump_part = ""
            comp_part = inst

            if "=" in comp_part:
                dest_part, comp_part = comp_part.split("=", 1)
            if ";" in comp_part:
                comp_part, jump_part = comp_part.split(";", 1)

            dest_bits = DEST_TABLE[dest_part.strip()]
            comp_bits = COMP_TABLE[comp_part.strip()]
            jump_bits = JUMP_TABLE[jump_part.strip()]

            binary_output.append(f"111{comp_bits}{dest_bits}{jump_bits}")

    # Write .hack output
    base_name = os.path.splitext(asm_path)[0]
    hack_path = f"{base_name}.hack"
    with open(hack_path, "w", encoding="utf-8") as f:
        f.write("\n".join(binary_output) + "\n")

    # K mod 3 == 0 Extra Feature: Save all labels and variables with addresses in symbols.txt
    symbols_path = os.path.join(os.path.dirname(os.path.abspath(asm_path)), "symbols.txt")
    with open(symbols_path, "w", encoding="utf-8") as f:
        f.write("=== LABELS (ROM Addresses) ===\n")
        if labels:
            for name, addr in labels.items():
                f.write(f"{name}: {addr}\n")
        else:
            f.write("(None)\n")

        f.write("\n=== VARIABLES (RAM Addresses) ===\n")
        if variables:
            for name, addr in variables.items():
                f.write(f"{name}: {addr}\n")
        else:
            f.write("(None)\n")

    print(f"Assembled {asm_path} -> {hack_path}")
    print(f"Saved symbols to {symbols_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python assembler.py <Program.asm>")
        sys.exit(1)
    assemble(sys.argv[1])