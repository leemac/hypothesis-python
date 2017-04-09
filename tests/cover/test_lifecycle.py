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

import gc

import pytest

import hypothesis._lifecycle as _lifecycle
from hypothesis import strategies as st
from hypothesis import given, lifecycle, lifecycle_hook


def test_setup_and_teardown_are_called_on_lifecycle_hooks():
    class Test(object):
        bad = True

        @lifecycle_hook
        def setup_example(self):
            self.bad = False

        @lifecycle_hook
        def teardown_example(self):
            assert not self.bad
            self.bad = True
            self.torn_down = True

        @given(st.integers())
        def test(self, i):
            assert not self.bad

    x = Test()
    x.test()
    assert x.torn_down


def test_lifecycle_hooks_can_be_inherited():
    class Parent(object):
        bad = True

        @lifecycle_hook
        def setup_example(self):
            self.bad = False

        @lifecycle_hook
        def teardown_example(self):
            assert not self.bad
            self.bad = True
            self.torn_down = True

    class Test(Parent):

        @given(st.integers())
        def test(self, i):
            assert not self.bad

    x = Test()
    x.test()
    assert x.torn_down


@pytest.mark.xfail(
    reason='This test currently falls afoul of #493.'
)
def test_lifecycle_hooks_are_weak():
    _lifecycle.TYPE_TO_HOOK_CACHE.clear()
    assert not _lifecycle.TYPE_TO_HOOK_CACHE

    def run_locally():
        class Test(object):
            bad = True

            @lifecycle_hook
            def setup_example(self):
                pass

            @given(st.integers())
            def test(self, i):
                pass
        Test().test()
        assert _lifecycle.TYPE_TO_HOOK_CACHE
    run_locally()
    del run_locally
    gc.collect()
    assert not _lifecycle.TYPE_TO_HOOK_CACHE


def test_post_process_output():
    class Test(object):
        test_called = False

        @lifecycle_hook
        def execute_example_output(self, output):
            if output is not None:
                self.processed = True
            else:
                assert not self.test_called

        @given(st.integers())
        def test(self, i):
            self.test_called = True
            return i

    x = Test()
    x.test()
    assert x.processed


def test_can_specify_a_lifecycle_external():
    class Foo(object):

        @lifecycle_hook('setup_example')
        def a(self):
            self.setup_called = True

        @lifecycle_hook('teardown_example')
        def b(self):
            self.teardown_called = True

    x = Foo()

    @lifecycle(x)
    @given(st.integers())
    def test(i):
        pass
    test()
    assert x.setup_called
    assert x.teardown_called
