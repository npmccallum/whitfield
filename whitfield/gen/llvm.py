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

from . import Generator
from .. import util
import abc


class Function(abc.ABC):
    name = None
    op = None

    @classmethod
    def find_class(cls, op):
        for c in cls.__subclasses__():
            if c.op == op:
                return c
        return None

    @abc.abstractmethod
    def body(self):
        pass

    def __call__(self):
        yield f"define internal i{self.bits}"
        yield f"@{self.name}(i{self.bits}, i{self.bits})"
        yield f"{{"
        yield from self.body()
        yield f"}}"

    def __init__(self, limit):
        self.limit = limit
        self.bits = util.bits(limit)


class AddFunction(Function):
    name = "add"
    op = "+"

    def body(self):
        yield f"%3 = add i{self.bits} %0, %1"
        yield f"%4 = sub i{self.bits} %3, {self.limit}"
        yield f"%5 = icmp ult i{self.bits} %3, {self.limit}"
        yield f"%6 = select i1 %5, i{self.bits} %3, i{self.bits} %4"
        yield f"ret i{self.bits} %6"


class SubFunction(Function):
    name = "sub"
    op = "-"

    def body(self):
        yield f"%3 = sub i{self.bits} %0, %1"
        yield f"%4 = add i{self.bits} %3, {self.limit}"
        yield f"%5 = icmp ult i{self.bits} %3, {self.limit}"
        yield f"%6 = select i1 %5, i{self.bits} %3, i{self.bits} %4"
        yield f"ret i{self.bits} %6"


class MulFunction(Function):
    name = "mul"
    op = "*"

    def body(self):
        bits = self.bits

        yield f"%3 = add i{bits} %0, 0"
        yield f"%4 = add i{bits} 0, 0"

        r = 4
        for o in range(bits - 1, -1, -1):
            yield f"%{r+1} = and i{bits} %1, {1 << o}"
            yield f"%{r+2} = icmp ne i{bits} %{r+1}, 0"
            yield f"%{r+3} = select i1 %{r+2}, i{bits} %{r-1}, i{bits} %{r-0}"
            yield f"%{r+4} = call i{bits} @add(i{bits} %{r-1}, i{bits} %{r-0})"
            yield f"%{r+5} = call i{bits} @add(i{bits} %{r+3}, i{bits} %{r+3})"
            yield f"%{r+6} = select i1 %{r+2}, i{bits} %{r+5}, i{bits} %{r+4}"
            yield f"%{r+7} = select i1 %{r+2}, i{bits} %{r+4}, i{bits} %{r+5}"
            r += 7

        yield f"ret i{bits} %{r-0}"


class ExpFunction(Function):
    name = "exp"
    op = "@"

    def body(self):
        bits = self.bits

        yield f"%3 = add i{bits} %0, 0"
        yield f"%4 = add i{bits} 1, 0"

        r = 4
        for o in range(bits - 1, -1, -1):
            yield f"%{r+1} = and i{bits} %1, {1 << o}"
            yield f"%{r+2} = icmp ne i{bits} %{r+1}, 0"
            yield f"%{r+3} = select i1 %{r+2}, i{bits} %{r-1}, i{bits} %{r-0}"
            yield f"%{r+4} = call i{bits} @mul(i{bits} %{r-1}, i{bits} %{r-0})"
            yield f"%{r+5} = call i{bits} @mul(i{bits} %{r+3}, i{bits} %{r+3})"
            yield f"%{r+6} = select i1 %{r+2}, i{bits} %{r+5}, i{bits} %{r+4}"
            yield f"%{r+7} = select i1 %{r+2}, i{bits} %{r+4}, i{bits} %{r+5}"
            r += 7

        yield f"ret i{bits} %{r-0}"


class LLVMGenerator(Generator):
    def _binop(self, bits, v, cnst, expr):
        if isinstance(expr, int):
            return f"{expr}"
        if isinstance(expr, str):
            try:
                return v[expr]
            except KeyError:
                return cnst[expr]
        elif isinstance(expr, list):
            l, o, r = expr
            l = yield from self._binop(bits, v, cnst, l)
            r = yield from self._binop(bits, v, cnst, r)
            n = Function.find_class(o).name
            r = yield f"call i{bits} @{n}(i{bits} {l}, i{bits} {r})"
            return f"%{r}"

        assert False

    def __call__(self, ast):
        bits = util.bits(ast["limit"])

        yield from AddFunction(ast["limit"])()
        yield from SubFunction(ast["limit"])()
        yield from MulFunction(ast["limit"])()
        yield from ExpFunction(ast["limit"])()

        cnst = {}
        for i in sorted(ast["items"], key=lambda x: isinstance(x, dict)):
            if isinstance(i, list):
                name = f"wht_{ast['name']}_{i[0]}"
                cnst[i[0]] = f"@{name}"
                yield f"@{name} = constant i{bits} {i[1]}"

            elif isinstance(i, dict):
                v = {}
                r = 0

                args = [f"i{bits}* %{n}" for n in i['args'] + i['rets']]
                args = ", ".join(args)
                yield f""
                yield f"define void @wht_{ast['name']}_{i['name']}({args}) {{"

                for n in i['args']:
                    r += 1
                    yield f"    %{r} = load i{bits}, i{bits}* %{n}"
                    v[n] = f"%{r}"

                for n, e in i['body']:
                    bo = self._binop(bits, v, cnst, e)
                    x = None
                    while True:
                        try:
                            line = bo.send(x)
                            x = r = r + 1
                            yield f"    %{r} = {line}"
                        except StopIteration:
                            v[n] = f"%{r}"
                            break

                for n in i['rets']:
                    yield f"    store i{bits} {v[n]}, i{bits}* %{n}"

        yield "    ret void"
        yield "}"
