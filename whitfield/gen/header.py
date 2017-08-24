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
from itertools import chain


class HeaderGenerator(Generator):
    def __call__(self, ast):
        bytes = util.bytes(ast['limit'])
        name = ast["name"]

        yield f"#pragma once"

        yield f"typedef unsigned char wht_{name}_t[{bytes}];"

        for i in sorted(ast["items"], key=lambda x: isinstance(x, dict)):
            if isinstance(i, list):
                yield f"extern wht_{name}_t wht_{name}_{i[0]};"
                continue

            elif isinstance(i, dict):
                args = [f"const wht_{name}_t {x}" for x in i["args"]]
                rets = [f"wht_{name}_t {x}" for x in i["rets"]]
                prms = ", ".join(chain(args, rets))
                yield f"void wht_{name}_{i['name']}({prms});"

            else:
                raise TypeError("Unknown item in AST!")

        yield f""
