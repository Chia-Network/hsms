from clvm_rs.program import Program

from hsms.clvm.disasm import disassemble


def check_disassemble(h, s):
    p = Program.fromhex(h)
    output = disassemble(p)
    print(output)
    assert output == s


def test_disassemble():
    # one-byte encodings
    check_disassemble("80", "0")
    check_disassemble("01", "1")
    check_disassemble("3f", "63")

    check_disassemble("8140", "64")
    check_disassemble("817f", "127")
    check_disassemble("8180", "-128")
    check_disassemble("8181", "-127")
    check_disassemble("81fe", "-2")
    check_disassemble("81ff", "-1")
    check_disassemble("8100", "0x00")
    check_disassemble("8101", "1")
    check_disassemble("8102", "2")

    check_disassemble("820000", "0x0000")
    check_disassemble("820001", "0x0001")
    check_disassemble("820002", "0x0002")
    check_disassemble("82007f", "0x007f")
    check_disassemble("820080", "128")
    check_disassemble("820081", "129")
    check_disassemble("827fff", "32767")
    check_disassemble("828000", "-32768")
    check_disassemble("828001", "-32767")
    check_disassemble("82ff7f", "-129")
    check_disassemble("82ff80", "0xff80")
    check_disassemble("82ff81", "0xff81")
    check_disassemble("82fffe", "0xfffe")
    check_disassemble("82ffff", "0xffff")

    check_disassemble("83000000", "0x000000")
    check_disassemble("83000001", "0x000001")
    check_disassemble("83000002", "0x000002")
    check_disassemble("83007fff", "0x007fff")
    check_disassemble("83008000", "0x008000")
    check_disassemble("83008001", "0x008001")
    check_disassemble("837fffff", "0x7fffff")
    check_disassemble("83008000", "0x008000")
    check_disassemble("83008001", "0x008001")
    check_disassemble("8300ff7f", "0x00ff7f")
    check_disassemble("8300ff80", "0x00ff80")
    check_disassemble("8300ff81", "0x00ff81")
    check_disassemble("8300fffe", "0x00fffe")
    check_disassemble("8300ffff", "0x00ffff")

    check_disassemble("83666f6f", '"foo"')

    check_disassemble("ff8080", "(0)")
    check_disassemble("ff83666f6fff8362617280", '("foo" "bar")')
    check_disassemble(
        "ff83666f6fff83626172ff8362617a836a6f62", '("foo" "bar" "baz" . "job")'
    )
    check_disassemble(
        "ff83666f6fffff83626172ff8362617a80836a6f62", '("foo" ("bar" "baz") . "job")'
    )
    check_disassemble("ff64ff8200c880", "(100 200)")
    check_disassemble("ff01ff02ff05ff0d80", "(q 2 5 13)")
    check_disassemble("ff02ff05ff0d80", "(a 5 13)")

    sq, dq = "'", '"'
    # sq = single quote; dq = double quote
    ev = f"{sq}{dq}foo{dq}{sq}"
    check_disassemble("8522666f6f22", ev)

    # we now do the seven character string "'foo'"
    check_disassemble("872227666f6f2722", "0x2227666f6f2722")
