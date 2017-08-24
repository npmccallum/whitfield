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

from . import Optimizer, after
from . import importer
from ..math import ops
from itertools import chain


def compile_time_math(expr, ops, constants={}):
    if isinstance(expr, int):
        return expr

    if isinstance(expr, str):
        return constants.get(expr, expr)

    expr = [compile_time_math(expr[0], ops, constants), expr[1],
            compile_time_math(expr[2], ops, constants)]
    if not isinstance(expr[0], int) or not isinstance(expr[2], int):
        return expr

    return ops[expr[1]](expr[0], expr[2])


@after(importer.Importer)
class LimitCondenser(Optimizer):
    "Condenses all compile-time operations in the field declaration."

    def __call__(self, ast):
        ast["limit"] = compile_time_math(ast["limit"], ops())
        assert isinstance(ast["limit"], int)


@after(LimitCondenser)
class ConstantCondenser(Optimizer):
    "Condenses all compile-time operations in constants."

    def __call__(self, ast):
        v = {}
        for i in ast["items"]:
            if not isinstance(i, list):
                continue

            v[i[0]] = i[1] = compile_time_math(i[1], ops(ast["limit"]), v)
            if not isinstance(i[1], int):
                raise SyntaxError("Constant '%s' not constant!", i[1])


@after(LimitCondenser, ConstantCondenser)
class FunctionCondenser(Optimizer):
    "Condenses all compile-time operations in functions."

    def _check_symbols(self, expr, ops, symbols=set()):
        if isinstance(expr, int):
            return

        if isinstance(expr, str):
            assert expr in symbols
            return

        self._check_symbols(expr[0], ops, symbols)
        assert expr[1] in ops
        self._check_symbols(expr[2], ops, symbols)

    def __call__(self, ast):
        # Constants
        c = {i[0]: i[1] for i in ast["items"] if isinstance(i, list)}

        for i in ast["items"]:
            if not isinstance(i, dict):
                continue

            s = set(c.keys()) | set(i["args"])  # Symbols
            v = c.copy()                        # Compile-time Values

            for a in i["body"]:
                assert a[0] not in c            # Cannot assign to constants
                assert a[0] not in i["args"]    # Cannot assign to arguments

                a[1] = compile_time_math(a[1], ops(ast["limit"]), v)
                if isinstance(a[1], int) and a[0] not in i["rets"]:
                    v.update([a])
                else:
                    s.add(a[0])
                    self._check_symbols(a[1], ops(ast["limit"]), s)

            i["body"] = [x for x in i["body"]
                         if not isinstance(x[1], int) or x[0] in i["rets"]]
