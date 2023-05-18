# Starter SConstruct for enscons

import enscons
import setuptools_scm
import pytoml


def build_cl(target, source, env):
    assert len(source) == 1
    assert len(target) == 1
    rv = compile_clvm(
        str(source[0]), str(target[0]), search_paths=env.get("CL_INCLUDE", "")
    )


cl_builder = Builder(action=build_cl, suffix=".clsp.hex")


metadata = dict(pytoml.load(open("pyproject.toml")))["tool"]["enscons"]
metadata["version"] = setuptools_scm.get_version(local_scheme="no-local-version")

full_tag = "py3-none-any"  # pure Python packages compatible with 2+3

env = Environment(
    tools=["default", "packaging", enscons.generate],
    PACKAGE_METADATA=metadata,
    WHEEL_TAG=full_tag,
    ROOT_IS_PURELIB=full_tag.endswith("-any"),
)
env["BUILDERS"]["Chialisp"] = cl_builder
env["CL_INCLUDE"] = ["hsms/puzzles"]


# Only *.py is included automatically by setup2toml.
# Add extra 'purelib' files or package_data here.
py_source = Glob("hsms/*.py") + Glob("hsms/*/*.py")

clsp_source = Glob("hsms/puzzles/*.clsp")
clsp_includes = Glob("hsms/puzzles/*.cl") + Glob("hsms/puzzles/*.clvm")
clvm = [env.Chialisp(_) for _ in clsp_source]

sdist_source = (
    File(["PKG-INFO", "README.md", "SConstruct", "pyproject.toml"])
    + py_source
    + clsp_source
    + clsp_includes
)
sdist = env.SDist(source=sdist_source)

wheel_source = env.Whl("purelib", py_source + clvm, root="")
whl = env.WhlFile(source=wheel_source)
env.NoClean(sdist)
env.Alias("sdist", sdist)

# needed for pep517 (enscons.api) to work
env.Default(whl, sdist)
