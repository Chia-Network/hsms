import pathlib

import pkg_resources
from clvm_rs import Program
from clvm_tools_rs import compile_clvm


def load_clvm(clvm_filename, package_or_requirement=__name__) -> Program:
    """
    This function takes a .clvm file in the given package and compiles it to a
    .clvm.hex file if the .hex file is missing or older than the .clvm file, then
    returns the contents of the .hex file as a `Program`.

    clvm_filename: file name
    package_or_requirement: usually `__name__` if the clvm file is in the same package
    """

    hex_filename = f"{clvm_filename}.hex"

    try:
        if pkg_resources.resource_exists(package_or_requirement, clvm_filename):
            full_path = pathlib.Path(
                pkg_resources.resource_filename(package_or_requirement, clvm_filename)
            )
            output = full_path.parent / hex_filename
            compile_clvm(
                str(full_path),
                str(output),
                search_paths=[
                    str(full_path.parent),
                    str(full_path.parent.joinpath("include")),
                ],
            )
    except NotImplementedError:
        # pyinstaller doesn't support `pkg_resources.resource_exists`
        # so we just fall through to loading the hex clvm
        pass

    clvm_hex = pkg_resources.resource_string(
        package_or_requirement, hex_filename
    ).decode("utf8")
    clvm_blob = bytes.fromhex(clvm_hex)
    return Program.from_bytes(clvm_blob)
