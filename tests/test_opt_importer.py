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

from whitfield.opt.importer import Importer


def test_importer():
    ast = {"prime": 7, "items": ["tests/importer"]}
    Importer()(ast)

    assert ast == {
        "prime": 7,
        "items": [{
            'name': 'foo',
            'args': ['a', 'b', 'c'],
            'rets': ['x', 'y', 'z'],
            'body': [['x', [['a', '+', 'b'], '+', 'A']],
                     ['y', [['b', '+', 'c'], '+', 'A']],
                     ['z', [['a', '+', 'c'], '+', 'A']]],
        }]
    }
