from os import path
import tempfile

import pytest
from testutils import Qit, init

init()

from qit import Range, Function, Product
from qit.base import qit
from qit.base.int import Int


def test_create_files_manual():
    tmp_dir = tempfile.gettempdir()
    file = path.join(tmp_dir, next(tempfile._get_candidate_names()))

    p = Product("p", Range(1), Range(1))
    f = Function("f").takes(p, "p").returns(Int()).from_file(file)

    c = Qit()
    c.create_source_files(f)

    assert path.isfile(file)


def test_create_files_auto():
    tmp_dir = tempfile.gettempdir()
    file = path.join(tmp_dir, next(tempfile._get_candidate_names()))

    p = Product("p", Range(1), Range(1))
    f = Function("f").takes(p, "p").returns(Int()).from_file(file)

    c = qit.Qit(True, True)

    with pytest.raises(Exception):
        c.run(p.iterate().map(f).collect())

    assert path.isfile(file)


def test_declaration():
    p = Product("P", Range(1), Range(1))
    f = Function("f").takes(p, "p").returns(Int())
    g = Function("g").takes(Int(), "x").returns(Int())

    q = Qit()

    assert q.declarations(f)[0] == "int f(const P &p)"
    assert q.declarations(g)[0] == "int g(const int &x)"
    assert len(q.declarations(p.iterate().map(f).map(g).map(g))) == 2

def test_existing_file():
    tmp_dir = tempfile.gettempdir()
    file = path.join(tmp_dir, next(tempfile._get_candidate_names()))

    with open(file, "w") as f:
        f.write("ahoj")

    p = Product("p", Range(1), Range(1))
    f = Function("f").takes(p, "p").returns(Int()).from_file(file)

    c = qit.Qit(True, True)

    with pytest.raises(Exception): # compile error
        c.run(p.iterate().map(f).collect())

    with open(file, "r") as f:
        assert f.read() == "ahoj"
