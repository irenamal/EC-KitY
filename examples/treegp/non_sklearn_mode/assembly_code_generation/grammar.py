from examples.treegp.non_sklearn_mode.assembly_code_generation.assembly_parameters import *

terminal_set = [(reg, "reg") for reg in general_registers] + \
               [(reg, "half_reg") for reg in general_half_registers] + \
               [(reg, "address") for reg in addressing_registers] + \
               [(const, "const") for const in consts] + \
               [(reg, "push_reg") for reg in push_registers] + \
               [(reg, "pop_reg") for reg in pop_registers] + \
               [(opcode, "op_double") for opcode in opcodes_double] + \
               [(opcode, "op_single") for opcode in opcodes_single] + \
               [(opcode, "op_jmp") for opcode in opcodes_jump] + \
               [(opcode, "op") for opcode in opcodes_no_operands] + \
               [(opcode, "op_rep") for opcode in opcodes_repeats] + \
               [(opcode, "op_special") for opcode in opcodes_special] + \
               [(opcode, "op_function") for opcode in opcodes_function] + \
               [(opcode, "op_pointer") for opcode in opcodes_pointers] + \
               [(opcode, "op_ret") for opcode in opcode_ret] + \
               [(opcode, "op_push") for opcode in opcode_push] + \
               [(opcode, "op_pop") for opcode in opcode_pop] + \
               [(opcode, "op_double_no_const") for opcode in opcodes_double_no_cost] + \
               [(opcode, "op_shift") for opcode in opcodes_shift] + \
               [("", "section")]

function_set = [(section, ["label", "section", "backwards_jmp", "section"], "section")] + \
               [(section, ["label", "section", "backwards_jmp"], "section")] + \
               [(section, ["section", "forward_jmp", "section", "label", "section"], "section")] + \
               [(section, ["label", "section", "call_func", "backwards_jmp", "label", "section", "return"], "section")] + \
               [(func_opcode_two_operands, ["op_double", "reg", "reg", "section"], "section")] + \
               [(func_opcode_two_operands, ["op_double", "reg", "const", "section"], "section")] + \
               [(func_opcode_two_operands, ["op_double", "reg", "address", "section"], "section")] + \
               [(func_opcode_two_operands, ["op_double", "address", "reg", "section"], "section")] + \
               [(func_opcode_two_operands, ["op_double", "half_reg", "half_reg", "section"], "section")] + \
               [(func_opcode_two_operands, ["op_double", "half_reg", "const", "section"], "section")] + \
               [(func_opcode_two_operands, ["op_double", "half_reg", "address", "section"], "section")] + \
               [(func_opcode_two_operands, ["op_double", "address", "half_reg", "section"], "section")] + \
               [(func_opcode_two_operands, ["op_pointer", "reg", "address", "section"], "section")] + \
               [(func_opcode_two_operands, ["op_double_no_const", "reg", "reg", "section"], "section")] + \
               [(func_opcode_two_operands, ["op_double_no_const", "reg", "address", "section"], "section")] + \
               [(func_opcode_two_operands, ["op_double_no_const", "half_reg", "half_reg", "section"], "section")] + \
               [(func_opcode_two_operands, ["op_double_no_const", "half_reg", "address", "section"], "section")] + \
               [(func_opcode_two_operands_WORD, ["op_double", "address", "const", "section"], "section")] + \
               [(func_opcode_two_operands_BYTE, ["op_double", "address", "const", "section"], "section")] + \
               [(func_opcode_openrand, ["op_single", "reg", "section"], "section")] + \
               [(func_opcode_openrand, ["op_single", "half_reg", "section"], "section")] + \
               [(func_opcode_openrand, ["op_function", "address", "section"], "section")] + \
               [(func_opcode_openrand, ["op_rep", "op", "section"], "section")] + \
               [(func_opcode_openrand, ["op_push", "push_reg", "section"], "section")] + \
               [(func_opcode_openrand, ["op_pop", "pop_reg", "section"], "section")] + \
               [(func_opcode_operand_WORD, ["op_single", "address", "section"], "section")] + \
               [(func_opcode_operand_BYTE, ["op_single", "address", "section"], "section")] + \
               [(func_call, ["section"], "call_func")] + \
               [(func_opcode, ["op_ret", "section"], "return")] + \
               [(func_opcode, ["op", "section"], "section")] + \
               [(func_opcode, ["op_special", "section"], "section")] + \
               [(put_label, ["section"], "label")] + \
               [(func_forward_jmp, ["op_jmp", "section"], "forward_jmp")] + \
               [(func_backwords_jmp, ["op_jmp", "section"], "backwards_jmp")] + \
               [(func_jmp, ["reg", "section"], "section")] + \
               [(func_jmp, ["address", "section"], "section")] + \
               [(func_dw, ["const", "section"], "section")] + \
               [(func_addres, ["address", "const"], "address")] + \
               [(func_opcode_operand_cl, ["op_shift", "reg", "section"], "section")] + \
               [(func_opcode_operand_1, ["op_shift", "reg", "section"], "section")] + \
               [(func_opcode_operand_cl, ["op_shift", "half_reg", "section"], "section")] + \
               [(func_opcode_operand_1, ["op_shift", "half_reg", "section"], "section")] + \
               [(random_generator_lcg, ["reg", "section"], "section")] + \
               [(random_generator_xor_shift, ["reg", "reg", "section"], "section")]
