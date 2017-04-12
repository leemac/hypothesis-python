# coding=utf-8
#
# This file is part of Hypothesis, which may be found at
# https://github.com/HypothesisWorks/hypothesis-python
#
# Most of this work is copyright (C) 2013-2016 David R. MacIver
# (david@drmaciver.com), but it contains contributions by others. See
# CONTRIBUTING.rst for a full list of people who may hold copyright, and
# consult the git log if you need to determine who owns an individual
# contribution.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.
#
# END HEADER

from __future__ import division, print_function, absolute_import

from hypothesis import given, settings, strategies as st
from hypothesis.database import InMemoryExampleDatabase
import pytest


def test_saves_examples_that_cover_different_branches_1():
    db = InMemoryExampleDatabase()

    @settings(database=db, use_coverage_information=True)
    @given(st.integers())
    def test(n):
        if n > 0:
            pass
        else:
            pass
    test()
    assert len(db.data) == 1
    vs = list(db.data.values())[0]
    assert len(vs) == 2


def test_saves_examples_that_cover_different_branches_2():
    db = InMemoryExampleDatabase()

    @settings(database=db, use_coverage_information=True)
    @given(st.lists(st.integers()))
    def test(ls):
        if len(ls) == 0:
            return
    test()
    assert len(db.data) == 1
    vs = list(db.data.values())[0]
    assert len(vs) == 2


def test_finds_obscure_edge_cases():
    @settings(
        database=None, use_coverage_information=True,
        max_examples=10**6,
        max_iterations=10**6,
        max_shrinks=0,
    )
    @given(st.binary(min_size=4, max_size=4))
    def test(block):
        if block[0] == 0:
            if block[1] == 10:
                if block[2] == 20:
                    if block[3] == 30:
                        raise ValueError("Oh noes")

    with pytest.raises(ValueError) as e:
        test()
    assert e.value.args[0] == "Oh noes"
