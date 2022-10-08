# # Transfer operations
# transfer_pair = ("{opcode} {dst},{src}", {'opcode': transfer_opcodes_pair, 'dst': general_registers,
#                                           'src': general_registers + consts})
# # library.global_properties.add_checker(lambda **v: True)
#
# # Arithmetic operations
# arith_single = {"{opcode} {operand}", {'opcode': arithmetic_opcodes_single, 'operand': general_registers + consts}}
# arith_pair = ("{opcode} {dst},{src}", {'opcode': arithmetic_opcodes_pair, 'dst': general_registers,
#                                        'src': general_registers + consts})
#
# # Logical operations
# logic_single = {"{opcode} {operand}", {'opcode': logical_opcodes_single, 'operand': general_registers}}
# logic_pair = ("{opcode} {dst},{src}", {'opcode': logical_opcodes_pair, 'dst': general_registers,
#                                        'src': general_registers + consts})
#
# # Jump opcodes
# jmp = ("{opcode} {dst}", {'opcode': jump_opcodes, 'dst': labels})
#
# terminals = general_registers + consts
# functions = transfer_pair + arith_single + arith_pair + logic_single + logic_pair

# Assembly commands macros
transfer_opcodes_pair = ["mov", "xchg", "lea"]
arithmetic_opcodes_single = ["div", "idiv", "mul", "imul", "inc", "dec"]
arithmetic_opcodes_pair = ["add", "sub", "cmp"]
logical_opcodes_single = ["neg", "not"]
logical_opcodes_pair = ["and", "or", "xor", "mov"]
jump_opcodes = ["jmp", "je", "jz", "jcxz", "jp", "jpe", "jne", "jnz", "jecxz", "jnp", "jpo"]
# "ja", "jae", "jb", "jbe", "jna", "jnae", "jnb", "jnbe", "jc", "jnc"]
general_registers = ["ax", "bx", "cx", "dx"]  # "sp", "bp", "si", "di"]
labels = range(0, 10)
consts = range(0, 10)  # 65535

opcodes_with_one_operand = arithmetic_opcodes_single + logical_opcodes_single
opcodes_with_two_operands = transfer_opcodes_pair + arithmetic_opcodes_pair + logical_opcodes_pair

functions_with_one_operand = [lambda op, *args, opcode=opcode: print("{} {}".format(opcode, op))
                              for opcode in opcodes_with_one_operand]
labeled_functions_with_one_operand = [lambda lb, op, *args, opcode=opcode: print("l{}:\t{} {}".format(lb, opcode, op))
                                      for opcode in opcodes_with_one_operand]
functions_with_two_operands = [lambda dst, src, *args, opcode=opcode: print("{} {},{}".format(opcode, dst, src))
                               for opcode in opcodes_with_two_operands]
labeled_functions_with_two_operands = [lambda lb, dst, src, *args, opcode=opcode:
                                       print("l{}:\t{} {},{}".format(lb, opcode, dst, src))
                                       for opcode in opcodes_with_two_operands]
jumps = [lambda dst, *args, opcode=opcode: print("{} l{}".format(opcode, dst)) for opcode in jump_opcodes]

one_op_commands = ["{} {}", "{} [{}]"]
two_op_commands_regs = ["{} {},{}", "{} [{}],{}", "{} {},[{}]"]
two_op_commands_consts = ["{} {},{}", "{} [{}],{}"]

one_op = [lambda op, *args, opcode=opcode, command=command: print(command.format(opcode, op))
          for opcode in opcodes_with_one_operand
          for command in one_op_commands]

two_op_regs = [lambda dst, src, *args, opcode=opcode, command=command: print(command.format(opcode, dst, src))
               for opcode in opcodes_with_two_operands
               for command in two_op_commands_regs]

two_op_reg_const = [lambda dst, src, *args, opcode=opcode, command=command: print(command.format(opcode, dst, src))
                    for opcode in opcodes_with_two_operands
                    for command in two_op_commands_consts]


def put_label(lb, *args):
    print("l{}:".format(lb))

