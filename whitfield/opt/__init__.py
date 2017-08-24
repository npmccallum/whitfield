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

import abc
import functools


@functools.total_ordering
class Optimizer(abc.ABC):
    _before = set()
    _after = set()

    def __lt__(self, other):
        def lt(a, b):
            for x in b._after:
                if lt(a, x):
                    return True
            return b in a._before
        return lt(self.__class__, other.__class__)

    def __eq__(self, other):
        return not self < other and not self > other

    def __gt__(self, other):
        def gt(a, b):
            for x in b._before:
                if gt(a, x):
                    return True
            return b in a._after
        return gt(self.__class__, other.__class__)

    @abc.abstractmethod
    def __call__(self, ast):
        "Modifies the AST (in place)"


def after(*args):
    def inner(cls):
        cls._after = cls._after.union(args)
        for arg in args:
            arg._before = arg._before.union((cls,))

        return cls
    return inner


def before(*args):
    def inner(cls):
        cls._before = cls._before.union(args)
        for arg in args:
            arg._after = arg._after.union((cls,))
        return cls
    return inner
