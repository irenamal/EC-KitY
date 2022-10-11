# Assembly commands macros
transfer_opcodes_pair = ["mov", "lea"]
arithmetic_opcodes_single = ["div", "idiv", "mul", "imul", "inc", "dec"]
arithmetic_opcodes_pair = ["add", "sub", "cmp"]
logical_opcodes_single = ["neg", "not"]
logical_opcodes_pair = ["and", "or", "xor", "mov"]
opcodes_between_regs = ["xchg"]  # TODO
jump_opcodes = ["jmp", "je", "jz", "jcxz", "jp", "jpe", "jne", "jnz", "jecxz", "jnp", "jpo"]
# "ja", "jae", "jb", "jbe", "jna", "jnae", "jnb", "jnbe", "jc", "jnc"]
general_registers = ["ax", "bx", "cx", "dx"]  # "sp", "bp", "si", "di"]
labels = []
consts = range(0, 10)  # 65535

opcodes_with_one_operand = arithmetic_opcodes_single + logical_opcodes_single
opcodes_with_two_operands = transfer_opcodes_pair + arithmetic_opcodes_pair + logical_opcodes_pair

functions_with_one_operand = [lambda op, *args, opcode=opcode: print("{} {}".format(opcode, op))
                              for opcode in opcodes_with_one_operand]

functions_with_two_operands = [lambda dst, src, *args, opcode=opcode: print("{} {},{}".format(opcode, dst, src))
                               for opcode in opcodes_with_two_operands]

one_op_commands = ["{} {}"]  # , "{} [{}]"]
two_op_commands_regs = ["{} {},{}"]  # , "{} [{}],{}", "{} {},[{}]"]
two_op_commands_consts = ["{} {},{}"]  # , "{} [{}],{}"]

one_op = [lambda op, *args, opcode=opcode, command=command: print(command.format(opcode, op))
          for opcode in opcodes_with_one_operand
          for command in one_op_commands]

two_op_regs = [lambda dst, src, *args, opcode=opcode, command=command: print(command.format(opcode, dst, src))
               for opcode in opcodes_with_two_operands
               for command in two_op_commands_regs]

two_op_reg_const = [lambda dst, src, *args, opcode=opcode, command=command: print(command.format(opcode, dst, src))
                    for opcode in opcodes_with_two_operands
                    for command in two_op_commands_consts]

forward_jumps = [lambda *args, opcode=opcode: print("{} l{}".format(opcode, len(labels))) for opcode in jump_opcodes]
backwards_jumps = [lambda *args, opcode=opcode: print("{} l{}".format(opcode, len(labels)-1)) for opcode in jump_opcodes]


def put_label(*args):
    lb = len(labels)
    labels.append(lb)
    print("l{}:".format(lb))
    return lb


INSTRUCTION = one_op + two_op_regs + two_op_reg_const
LABEL = put_label()
JMP = forward_jumps + backwards_jumps
STATEMENT1 = (LABEL, INSTRUCTION, JMP)
STATEMENT2 = (JMP, INSTRUCTION, LABEL)
STATEMENT3 = (INSTRUCTION)
STATEMENT = [STATEMENT1, STATEMENT2, STATEMENT3]


def statement1(label, *args):
    return


def statement2(label, *args):
    return


def statement3(*args):
    return


def statement4(*args):
    return
