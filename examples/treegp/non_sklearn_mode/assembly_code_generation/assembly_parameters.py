opcodes_no_operands = ["nop", "stosw", "lodsw", "movsw", "std", "cld", "cwd", "cmpsw"] #"stosb", "lodsb","movsb", "cmpsb",
opcodes_special = ["wait\nwait\nwait\nwait", "wait\nwait", "int 0x86", "int 0x87"]  # "nrg"=wait wait
opcodes_repeats = ["rep", "repe", "repz", "repne", "repnz"]
opcodes_jump = ["jmp", "jcxz", "je", "jne", "jp", "jnp"]  # , "jo", "jno", "jc", "jnc", "ja", "jna", "js", "jns", "jl", "jnl", "jle", "jnle" ]
opcodes_double = ["cmp", "mov", "add", "sub", "and", "or", "xor"]
opcodes_single = ["div", "mul", "inc", "dec", "not", "neg"]
opcodes_function = ["call", "call near", "call far"]
opcodes_pointers = ["lea", "les", "lds"]
opcode_ret = ["ret"]
opcodes_double_no_cost = ["xchg"]
opcodes_shift = ["sal", "sar", "shl", "shr"]

# not supported: jecxz, imul, idiv, push const, repnz and repnz with s/l/m
general_registers = ["ax", "bx", "cx", "dx", "si", "di", "bp"]
addressing_registers = ["[bx]", "[si]", "[di]", "[bp]"]
pop_registers = general_registers + ["WORD " + add_reg for add_reg in addressing_registers] #+ ["ds", "es", "ss"]
push_registers = pop_registers + ["cs", "ds", "es", "ss"]
labels = []
consts = ["0x"+str(2*i) for i in range(-10, 130)] + ["@start", "@end", "65535", "0xcccc"]


def put_label(f, *args):
    lb = len(labels)
    labels.append(lb)
    print("l{}:".format(lb), file=f)


def section(*args):
    return
