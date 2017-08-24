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

import pkg_resources
import sys
import os

from . import ast


def main():
    name = os.path.basename(sys.argv[1]).split(".", 1)[0]
    assert ast.IDN.parseString(name)

    src = ast.WHT.parseFile(sys.argv[1], True).asList()[0]
    src["name"] = name

    dst = sys.argv[2]
    ext = dst.rsplit('.', 1)[-1]

    eps = pkg_resources.iter_entry_points(group="whitfield.opt.Optimizer")
    for opt in sorted([ep.load()() for ep in eps]):
        opt(src)

    eps = pkg_resources.iter_entry_points(group="whitfield.gen.Generator")
    eps = {ep.name: ep for ep in eps}
    gen = eps[ext].load()()

    with open(dst, "w") as f:
        for txt in gen(src):
            print(txt, file=f)


if __name__ == '__main__':
    main()
