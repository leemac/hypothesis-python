from __future__ import division, print_function, absolute_import

from collections import Counter
from hypothesis.utils.conventions import UniqueIdentifier


UNIVERSAL_TAG = UniqueIdentifier("UNIVERSAL_TAG")


class NegatedTag(object):
    def __init__(self, tag):
        self.tag = tag

    def __hash__(self):
        return ~hash(self.tag)

    def __eq__(self, other):
        if not isinstance(other, NegatedTag):
            return NotImplemented
        return self.tag == other.tag

    def __ne__(self, other):
        if not isinstance(other, NegatedTag):
            return NotImplemented
        return self.tag != other.tag

    def __repr__(self):
        return "~%r" % (self.tag,)


class Corpus(object):
    def __init__(self, add_callback=None, remove_callback=None):
        self.__add_callback = add_callback or (lambda s: None)
        self.__remove_callback = remove_callback or (lambda s: None)
        self.__tags_to_values = {}
        self.__refcounts = Counter()
        self.__corpus = []
        self.__value_to_index = {}
        self.__all_tags = set()

    def for_tag(self, t):
        return self.__corpus[
            self.__value_to_index[self.__tags_to_values[t]]][1]

    def __check_invariants(self):
        assert len(self.__refcounts) == len(self.__corpus) == len(
            self.__value_to_index)

    def __len__(self):
        self.__check_invariants()
        return len(self.__corpus)

    def __getitem__(self, i):
        self.__check_invariants()
        return self.__corpus[i][1]

    def __contains__(self, value):
        self.__check_invariants()
        try:
            i = self.__value_to_index[value]
        except KeyError:
            return False
        assert self.__corpus[i] == value
        return True

    def __patch_tags(self, tags):
        for t in tags:
            if t not in self.__all_tags:
                if UNIVERSAL_TAG in self.__tags_to_values:
                    v = self.__tags_to_values[UNIVERSAL_TAG]
                    k = NegatedTag(t)
                    self.__tags_to_values[k] = v
                    self.__refcounts[v] += 1
                self.__all_tags.add(t)
            yield t

        for s in self.__all_tags - tags:
            yield NegatedTag(s)

        yield UNIVERSAL_TAG

    def add(self, value, payload, tags):
        self.__check_invariants()
        for tag in self.__patch_tags(tags):
            try:
                existing = self.__tags_to_values[tag]
            except KeyError:
                pass
            else:
                if shortlex(value) >= shortlex(existing):
                    continue
                assert self.__refcounts[existing] > 0
                self.__refcounts[existing] -= 1
                if self.__refcounts[existing] == 0:
                    del self.__refcounts[existing]
                    i = self.__value_to_index.pop(existing)
                    assert self.__corpus[i][0] == existing
                    if i + 1 < len(self.__corpus):
                        self.__corpus[i] = self.__corpus.pop()
                        self.__value_to_index[self.__corpus[i][0]] = i
                    else:
                        self.__corpus.pop()
                    self.__remove_callback(existing)
            self.__refcounts[value] += 1
            if self.__refcounts[value] == 1:
                i = len(self.__corpus)
                self.__corpus.append((value, payload))
                self.__value_to_index[value] = i
                self.__add_callback(value)
            self.__tags_to_values[tag] = value
        self.__check_invariants()


def shortlex(s):
    return (len(s), s)
