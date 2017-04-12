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

import os
import sys

import hypothesis.internal.tracking as t
from hypothesis import strategies as st
from hypothesis import find

HERE = os.path.abspath(__file__)


def foo():
    x = 1
    y = 2
    return x + y


FOO_LINES = {30, 31, 32}


def test_is_empty_by_default():
    assert sys.gettrace() is None
    t.start_tracking()
    covered = t.stop_tracking()
    assert covered == {}


def test_can_track_lines():
    assert sys.gettrace() is None
    t.start_tracking()
    foo()
    covered = t.stop_tracking()
    covered_in_this_file = covered[HERE]
    assert covered_in_this_file == FOO_LINES


def test_does_not_cover_inside_hypothesis_functions():
    assert sys.gettrace() is None
    t.start_tracking()
    find(st.integers(), lambda x: x > 0)
    covered = t.stop_tracking()
    assert covered == {}


def call_foo_with_tracking(x):
    assert t.in_hypothesis_call
    t.start_tracking()
    was_in_call = t.in_hypothesis_call
    foo()
    covered = t.stop_tracking()
    assert not was_in_call
    assert t.in_hypothesis_call
    assert covered == {HERE: FOO_LINES}
    return x


def test_does_cover_inside_hypothesis_function_if_specifically_enabled():
    assert sys.gettrace() is None
    t.start_tracking()
    find(st.booleans(), call_foo_with_tracking)
    covered = t.stop_tracking()
    assert FOO_LINES.issubset(covered[HERE])
    covered.pop(HERE)
    assert not covered
