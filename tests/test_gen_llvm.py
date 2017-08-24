#
# Copyright: 2017 Red Hat, Inc.
# Author: Nathaniel McCallum <npmccallum@redhat.com>
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

from whitfield.gen.llvm import LLVMGenerator
from whitfield.math import ops
from whitfield import util
from pytest import mark

import itertools
import tempfile
import ctypes
import math
import sys
import os

lim = 2 ** 255 - 19
byt = util.bytes(lim)


def seq():
    "Yields interesting numbers to test. These are near various boundaries."
    # Near zero
    yield 0
    yield 1
    yield 2

    # Near register size boundaries
    for x in range(3, int(math.log2(util.bits(lim)))):
        yield 2 ** 2 ** x - 1
        yield 2 ** 2 ** x
        yield 2 ** 2 ** x + 1

    # Near the limit
    yield lim - 1


def run(func, runs):
    for l, r, v, e in runs:
        func(l, r, v)
        assert v == e


@mark.parametrize("o", ["+", "-", "*", "@"])
def test_gen_llvm(benchmark, o):
    ast = {
        "name": "foo",
        "limit": lim,
        "items": [{
            "name": "bar",
            "args": ["l", "r"],
            "rets": ["v"],
            "body": [["v", ["l", o, "r"]]]
        }]
    }

    runs = [[l.to_bytes(byt, sys.byteorder),
             r.to_bytes(byt, sys.byteorder),
             bytes(byt),
             ops(lim)[o](l, r).to_bytes(byt, sys.byteorder)]
             for l, r in itertools.product(seq(), seq())]

    with tempfile.NamedTemporaryFile(prefix="lib", suffix=".so") as lib:
        with tempfile.NamedTemporaryFile(suffix=".ll") as src:
            for chunk in LLVMGenerator()(ast):
                src.write((chunk + os.linesep).encode("utf8"))
            src.flush()

            cmd = (
                'clang',
                '-Wno-override-module',
                '-shared',
                '-o',
                f'"{lib.name}"',
                f'"{src.name}"'
            )
            assert os.system(" ".join(cmd)) == 0

        obj = ctypes.cdll.LoadLibrary(lib.name)
        benchmark(run, obj.wht_foo_bar, runs)
