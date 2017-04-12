from hypothesis.stateful import RuleBasedStateMachine, rule, precondition, \
    invariant
import hypothesis.strategies as st
from hypothesis.internal.prioritymap import PriorityMap


class PriorityMapRules(RuleBasedStateMachine):
    def __init__(self):
        super(PriorityMapRules, self).__init__()
        self.__data = {}
        self.__target = PriorityMap()

    @rule(key=st.integers(), value=st.integers())
    def set_value(self, key, value):
        self.__data[key] = value
        self.__target[key] = value

    @rule()
    @precondition(lambda self: len(self.__target) > 0)
    def pop_value(self):
        k, v = self.__target.pop()
        assert v == min(self.__data.values())
        assert self.__data[k] == v
        del self.__data[k]

    @invariant()
    def check_agreement(self):
        assert len(self.__data) == len(self.__target)
        assert set(self.__data.keys()) == set(self.__target.keys())
        for k, v in self.__data.items():
            assert self.__target[k] == v


TestPriorityMap = PriorityMapRules.TestCase
