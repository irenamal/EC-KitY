opcodes_reg_reg = ["cmp", "mov", "xchg", "add", "sub", "and", "or", "xor"]
opcodes_reg_const = ["cmp", "mov", "add", "sub", "and", "or", "xor", "sal", "sar"]
opcodes_const_reg = []
opcodes_reg_address = ["cmp", "mov", "lea", "add", "sub", "and", "or", "xor"]
opcodes_address_reg = ["cmp", "mov", "add", "sub", "and", "or", "xor"]
opcodes_const_address = []
opcodes_address_const = ["mov WORD", "add WORD", "sub WORD", "and WORD", "or WORD", "xor WORD", "sal WORD", "sar WORD"]
opcodes_address_address = []
opcodes_reg = ["inc", "dec", "imul", "idiv", "not", "neg"]
opcodes_address = ["inc WORD", "dec WORD", "imul WORD", "idiv WORD", "not WORD", "neg WORD"]
opcodes_jump = ["jmp", "je", "jz", "jcxz", "jne", "jp", "jpe", "jnz"]  # , "jecxz", "jnp", "jpo"]
# "ja", "jae", "jb", "jbe", "jna", "jnae", "jnb", "jnbe", "jc", "jnc"]

general_registers = ["ax", "bx", "cx", "dx"]  # "sp", "bp", "ss", "cs", "ds", "es"
addressing_registers = ["abx", "asi", "adi"]  # bp
labels = []
consts = [0xCC, 512, 1024, 2048] + [i for i in range(0, 10)]  # 65535


def put_label(*args):
    lb = len(labels)
    labels.append(lb)
    print("l{}:".format(lb))


def section(*args):
    return
