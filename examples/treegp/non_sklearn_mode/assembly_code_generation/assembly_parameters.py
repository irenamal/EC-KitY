opcodes_no_operands = ["nop", "stosb", "stosw", "lodsb", "lodsw", "movsb", "movsw", "ret", "std", "cld", "cwd",
                       "cmpsb", "cmpsw"]
opcodes_special = ["wait\nwait\nwait\nwait", "wait\nwait", "int 0x86", "int 0x87"]  # "nrg"=wait wait
opcodes_repeats = ["rep", "repe", "repz"]  # , "repne", "repnz"]
opcodes_jump = ["jmp", "jcxz", "je", "jne", "jp", "jnp"]  # , "jo", "jno", "jc", "jnc"]
# , "ja", "jna", "js", "jns", "jl", "jnl", "jle", "jnle" ]
opcodes_double = ["cmp", "mov", "add", "sub", "and", "or", "xor"]
opcodes_single = ["div", "mul", "inc", "dec", "not", "neg", "push", "pop"]
opcodes_function = ["call", "call near", "call far"]
opcodes_pointers = ["lea", "les", "lds"]
# specials: xchg, sal, sar, lea
# not supported: jecxz, imul, idiv, push const, repnz and repnz with s/l/m
general_registers = ["ax", "bx", "cx"]  # sp, "dx"
pop_registers = ["ds", "es", "ss"]
push_registers = ["cs", "ss", "ds", "es"]
addressing_registers = ["[bx]", "[si]", "[di]", "[bp]"]
labels = []
consts = ["0x"+str(2*i) for i in range(-10, 100)] + ["(@start-@end)"]  # 65535, "0xcccc"


def put_label(*args):
    lb = len(labels)
    labels.append(lb)
    print("l{}:".format(lb))


def section(*args):
    return
