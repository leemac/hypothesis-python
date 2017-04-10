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


def minimal(
        definition, condition=None,
        settings=None, timeout_after=10, random=None
):
    from hypothesis import settings as Settings
    from hypothesis.core import find

    settings = Settings(
        settings,
        max_examples=50000,
        max_iterations=100000,
        max_shrinks=5000,
        database=None,
        timeout=timeout_after,
    )

    condition = condition or (lambda x: True)

    return find(
        definition,
        condition,
        settings=settings,
        random=random,
    )


HYPOTHESIS_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..'))


def escalate_hypothesis_assertion():
    error_type, _, tb = sys.exc_info()
    if error_type != AssertionError:
        return
    import traceback
    filename = traceback.extract_tb(tb)[-1][0]
    traceback.print_exc()
    if os.path.abspath(filename).startswith(HYPOTHESIS_ROOT):
        raise
