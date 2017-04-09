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

from weakref import WeakKeyDictionary

from hypothesis.errors import InvalidArgument
from hypothesis.internal.compat import callable
from hypothesis.utils.conventions import UniqueIdentifier

THIS_IS_REALLY_A_HOOK = UniqueIdentifier('THIS_IS_REALLY_A_HOOK')

HYPOTHESIS_HOOK_IDENTIFIER = 'hypothesi_internal_lifecycle_hook'

TYPE_TO_HOOK_CACHE = WeakKeyDictionary()

VALID_HOOKS = {}


def default_hook(fn):
    VALID_HOOKS[fn.__name__] = fn
    return fn


def is_hook(fn, name):
    if not callable(fn):
        return False
    try:
        label = getattr(fn, HYPOTHESIS_HOOK_IDENTIFIER)
    except AttributeError:
        return False

    if type(label) != tuple:
        return False

    return (name, THIS_IS_REALLY_A_HOOK) == label


def define_lifecycle_hook(function, name):
    setattr(function, HYPOTHESIS_HOOK_IDENTIFIER, (
        name, THIS_IS_REALLY_A_HOOK))
    return function


def lifecycle_hook(fn_or_name):
    if callable(fn_or_name):
        return define_lifecycle_hook(fn_or_name, fn_or_name.__name__)
    else:
        def accept(fn):
            return define_lifecycle_hook(fn, fn_or_name)
        return accept


def has_hooks(target):
    return any(
        get_hook(target, name) != default
        for name, default in VALID_HOOKS.items()
    )


def get_hook(target, name):
    try:
        default_hook = VALID_HOOKS[name]
    except KeyError:
        raise InvalidArgument('%r is not a valid hook name' % (name,))

    try:
        cache = TYPE_TO_HOOK_CACHE[target]
    except KeyError:
        cache = {}
        TYPE_TO_HOOK_CACHE[target] = cache

    try:
        cached_name = cache[name]
    except KeyError:
        pass
    else:
        if cached_name is None:
            return default_hook
        hook = getattr(target, cached_name)
        assert is_hook(hook, name)
        return hook

    hook_of_canonical_name = getattr(target, name, None)

    if is_hook(hook_of_canonical_name, name):
        hook_name = name
        hook = hook_of_canonical_name
    else:
        for k in dir(target):
            v = getattr(target, k)
            if is_hook(v, name):
                hook_name = k
                hook = v
                break
        else:
            hook_name = None
            hook = default_hook
    cache[name] = hook_name
    return hook


@default_hook
def setup_example(self):
    pass


@default_hook
def teardown_example(self):
    pass


@default_hook
def execute_example_output(self, output):
    return output
