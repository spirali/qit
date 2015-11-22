from os import path

import pytest
from testutils import Qit, init, get_filename_in_build_dir
from testutils import make_file_in_build_dir

init()

from qit import Range, Function, Product
from qit.base.int import Int
from qit.base.exception import MissingFiles

def test_extern_function():
    q = Qit()

    make_file_in_build_dir("f.hxx", "int f(int x) { return x * 10; }")

    i = Int()
    f = Function("f").takes(i, "x").returns(i).from_file("f.hxx")

    result = q.run(Range(6).iterate().map(f))
    assert result == [ 0, 10, 20, 30, 40, 50 ]

def test_create_files_direct_call():
    c = Qit()
    p = Product("p", Range(1), Range(1))
    f = Function("f").takes(p, "p").returns(Int()).from_file("myfile.hxx")
    c.create_files(f)
    assert path.isfile(get_filename_in_build_dir("myfile.hxx"))

def test_create_files_auto():
    f = Function("f").takes(Int(), "p").returns(Int()).from_file("fg.hxx")
    g = Function("g").takes(Int(), "p").returns(Int()).from_file("fg.hxx")
    h = Function("h").takes(Int(), "p").returns(Int()).from_file("h.hxx")

    c = Qit()
    with pytest.raises(MissingFiles):
        c.run(Range(10).iterate().map(f).map(g).map(h).map(f))

    assert not path.isfile(get_filename_in_build_dir("fg.hxx"))
    assert not path.isfile(get_filename_in_build_dir("h.hxx"))

    c = Qit(create_files=True)
    with pytest.raises(MissingFiles):
        c.run(Range(10).iterate().map(f).map(g).map(h).map(f))

    assert path.isfile(get_filename_in_build_dir("fg.hxx"))
    assert path.isfile(get_filename_in_build_dir("h.hxx"))

def test_qit_declaration():
    p = Product("P", Range(1), Range(1))
    f = Function("f").takes(p, "p").returns(Int())
    g = Function("g").takes(Int(), "x").returns(Int())

    q = Qit()

    assert q.declarations(f, False) == ["int f(const P &p)"]
    assert q.declarations(g, False) == ["int g(const int &x)"]
    assert len(q.declarations(p.iterate().map(f).map(g).map(g), False)) == 2
