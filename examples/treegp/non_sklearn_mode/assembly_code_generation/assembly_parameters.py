import datetime
import random

opcodes_no_operands = ["nop", "stosw", "lodsw", "movsw", "cmpsw", "scasw", "pushf", "popf",
                       "lahf", "stosb", "lodsb", "movsb", "cmpsb", "scasb", "xlat", "xlatb",
                       "cwd", "cbw", "cmc", "clc", "stc", "cli", "sti", "cld", "std"]
opcodes_special = ["wait\nwait\nwait\nwait", "wait\nwait", "int 0x86", "int 0x87"]  # "nrg"=wait wait
opcodes_repeats = ["rep", "repe", "repz", "repne", "repnz"]
opcodes_jump = ["jmp", "jcxz", "je", "jne", "jp", "jnp", "jo", "jno", "jc", "jnc", "ja", "jna", "js", "jns", "jl",
                "jnl", "jle", "jnle", "loopnz", "loopne", "loopz", "loope", "loop"]
opcodes_double = ["cmp", "mov", "add", "sub", "and", "or", "xor", "adc", "sbb", "test"]
opcodes_single = ["div", "mul", "inc", "dec", "not", "neg"]
opcodes_function = ["call", "call near", "call far"]
opcodes_pointers = ["lea", "les", "lds"]
opcode_ret = ["ret", "retn", "retf", "iret"]
opcode_push = ["push"]
opcode_pop = ["pop"]
opcodes_double_no_cost = ["xchg"]
opcodes_shift = ["sal", "sar", "shl", "shr", "rol", "ror", "rcl", "rcr"]

# not supported: jecxz, imul, idiv, push const, repnz and repnz with s/l/m
general_registers = ["ax", "bx", "cx", "dx", "si", "di", "bp", "sp"]
general_half_registers = ["ah", "al", "bh", "bl", "ch", "cl", "dh", "dl"]
addressing_registers = ["[bx]", "[si]", "[di]", "[bp]"]
pop_registers = general_registers + ["WORD " + add_reg for add_reg in addressing_registers] + ["ds", "es"]  #+, "ss"]
push_registers = pop_registers + ["cs", "ss"]
labels = []
consts = ["0x"+str(2*i) for i in range(-10, 133)] + ["@start", "@end", "65535", "0xcccc"]


def func_opcode(f, opcode, *args):
    print("{}".format(opcode), file=f)


def func_opcode_openrand(f, opcode, op, *args):
    print("{} {}".format(opcode, op), file=f)


def func_opcode_two_operands(f, opcode, dst, src, *args):
    print("{} {}, {}".format(opcode, dst, src), file=f)


def func_opcode_operand_WORD(f, opcode, op, *args):
    print("{} {} {}".format(opcode, "WORD", op), file=f)


def func_opcode_two_operands_WORD(f, opcode, dst, src, *args):
    print("{} {} {}, {}".format(opcode, "WORD", dst, src), file=f)


def func_opcode_operand_BYTE(f, opcode, op, *args):
    print("{} {} {}".format(opcode, "BYTE", op), file=f)


def func_opcode_two_operands_BYTE(f, opcode, dst, src, *args):
    print("{} {} {}, {}".format(opcode, "BYTE", dst, src), file=f)


def func_opcode_operand_cl(f, opcode, dst, *args):
    func_opcode_two_operands(f, opcode, dst, "cl")


def func_opcode_operand_cl_WORD(f, opcode, dst, *args):
    func_opcode_two_operands_WORD(f, opcode, dst, "cl")


def func_opcode_operand_cl_BYTE(f, opcode, dst, *args):
    func_opcode_two_operands_BYTE(f, opcode, dst, "cl")


def func_opcode_operand_1(f, opcode, dst, *args):
    func_opcode_two_operands(f, opcode, dst, "1")


def func_opcode_operand_1_WORD(f, opcode, dst, *args):
    func_opcode_two_operands_WORD(f, opcode, dst, "1")


def func_opcode_operand_1_BYTE(f, opcode, dst, *args):
    func_opcode_two_operands_BYTE(f, opcode, dst, "1")


def func_call(f, *args):
    func_opcode_openrand(f, "call", "l"+str(len(labels)))


def func_addres(f, op, const, *args):
    return "{} + {}]".format(str(op)[:-1], const)


def func_dw(f, const, *args):
    func_opcode_openrand(f, "dw", const)


def func_jmp(f, op, *args):
    func_opcode_openrand(f, "jmp", op)


def func_backwords_jmp(f, opcode, *args):
    func_opcode_openrand(f, opcode, "l" + str(len(labels) - 1))


def func_forward_jmp(f, opcode, *args):
    func_opcode_openrand(f, opcode, "l" + str(len(labels)))


def random_generator_lcg(f, op, *args):
    func_opcode_two_operands(f, "mov", "ax", hex(int(datetime.datetime.now().timestamp())))
    func_opcode_two_operands(f, "mov", op, 1664525)
    func_opcode_openrand(f, "mul", op)
    func_opcode_two_operands(f, "add", "ax", 1013904223)


def random_generator_xor_shift(f, op1, op2, *args):
    func_opcode_two_operands(f, "mov", op1, random.randint(0, 65535))
    func_opcode_two_operands(f, "mov", op2, random.randint(0, 65535))
    func_opcode_two_operands(f, "xor", op1, op2)
    func_opcode_two_operands(f, "shl", op1, 7)
    func_opcode_two_operands(f, "shr", op2, 5)
    func_opcode_two_operands(f, "xor", op1, op2)


def put_label(f, *args):
    lb = len(labels)
    labels.append(lb)
    print("l{}:".format(lb), file=f)


def section(*args):
    return
