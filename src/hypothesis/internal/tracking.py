from __future__ import division, print_function, absolute_import

import os
import sys

from hypothesis.errors import InvalidState

# Welcome to our old friend, global mutable state! This is the only way to
# write a trace function that performs remotely adequately, especially on pypy,
# so we define all the relevant tracing state as top level variables in the
# module. As trace functions are intrinsically global mutable state anyway this
# isn't really any worse than it would otherwise be, but it sure looks ugly
# doesn't it?

# The top entry of this is a filename: set(lines) mapping for the current
# active tracking. This will be merged into the next top entry when it gets
# popped.
tracking_state_stack = []

# We have to very carefully track whether we're in a Hypothesis function or
# not: We don't want to do tracking if we are, as this is a significant slow
# down for no benefit to the user.
in_hypothesis_call = False

# Whenever we start tracking we reset the value of whether we are in a
# hypothesis function or not to false. This stack lets us restore the
# correct value when we exit again.
in_hypothesis_call_stack = []

# We use a special local tracer function to reset the value of
# in_hypothesis_call on exit, but left to its own devices it will eagerly
# undo our restore code above. So we allow setting this flag to temporarily
# disable that for one reset.
do_not_reset = False


def start_tracking():
    existing_tracer = sys.gettrace()
    if existing_tracer not in (None, tracer, reset_on_return):
        raise InvalidState(
            'Cannot use state tracking when a trace function is alerady in '
            'place. Are you running under coverage or pdb?'
        )
    global do_not_reset
    do_not_reset = False
    global in_hypothesis_call
    in_hypothesis_call_stack.append(in_hypothesis_call)
    in_hypothesis_call = False
    tracking_state_stack.append({})
    sys.settrace(tracer)


def stop_tracking():
    global in_hypothesis_call
    global do_not_reset
    do_not_reset = True
    assert len(tracking_state_stack) == len(in_hypothesis_call_stack)
    result = tracking_state_stack.pop()
    in_hypothesis_call = in_hypothesis_call_stack.pop()
    if tracking_state_stack:
        parent = tracking_state_stack[-1]
        for k, v in result.items():
            try:
                parent[k].update(v)
            except KeyError:
                parent[k] = set(v)
    else:
        # Disabling the trace function here means we never get a return event.
        sys.settrace(None)
    return result


HYPOTHESIS_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..'))


FILE_PATH_CACHE = {}


def is_hypothesis_file(path):
    try:
        return FILE_PATH_CACHE[path]
    except KeyError:
        pass
    result = os.path.abspath(path).startswith(HYPOTHESIS_ROOT)
    FILE_PATH_CACHE[path] = result
    return result


def reset_on_return(frame, event, arg):
    global in_hypothesis_call
    global do_not_reset
    if event == 'return':
        if not do_not_reset:
            in_hypothesis_call = False
        do_not_reset = False


def tracer(frame, event, arg):
    global in_hypothesis_call
    global do_not_reset
    if in_hypothesis_call:
        return None
    if not tracking_state_stack:
        return None
    filepath = frame.f_code.co_filename
    if event == 'call':
        do_not_reset = False
        if is_hypothesis_file(filepath):
            in_hypothesis_call = True
            return reset_on_return
        else:
            return tracer
    elif event == 'line':
        try:
            target = tracking_state_stack[-1][filepath]
        except KeyError:
            target = set()
            tracking_state_stack[-1][filepath] = target
        target.add(frame.f_lineno)
