from collections import defaultdict, namedtuple

from strfmt import argstr


class Result(namedtuple('Result', ['returned', 'raised'])):

    @classmethod
    def returning(cls, value):
        return cls(returned=value, raised=None)

    @classmethod
    def raising(cls, e: Exception):
        return cls(returned=None, raised=e)

    def __repr__(self):
        if self.raised is None:
            return 'Result.returning({!r})'.format(self.returned)
        return 'Result.raising({!r})'.format(self.raised)


class Case:

    def __init__(self, function, args, kwargs):
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return '{}({})'.format(
            self.function, argstr(*self.args, **self.kwargs))

    def result(self) -> Result:
        try:
            returned = self.function(*self.args, **self.kwargs)
        except Exception as e:
            return Result.raising(e)
        else:
            return Result.returning(returned)


class Test:

    def __init__(self, case: Case, expected: Result):
        self.case = case
        self.expected = expected

    @property
    def actual(self) -> Result:
        try:
            return self.__actual
        except AttributeError:
            self.__actual = actual = self.case.result()
            return actual

    def __bool__(self):
        # TODO: extend to arbitrary conditions
        return self.actual == self.expected

    def __repr__(self):
        if self:
            return '<✅ Test {self.case}: {self.expected}>'.format(self=self)
        return (
            '<❌ Test {self.case}: expected {self.expected}, got {actual}>'
            .format(self=self, actual=self.actual)
            )


class UnboundTest:

    def __init__(self, args, kwargs, expected: Result):
        self.args = args
        self.kwargs = kwargs
        self.expected = expected

    def __repr__(self):
        return 'UnboundTest({args}, {kwargs}, {expected})'.format_map(self.__dict__)

    def case(self, function) -> Case:
        return Case(function, self.args, self.kwargs)

    def bind(self, function) -> Test:
        return Test(self.case(function), self.expected)


class result:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    # TODO: extend to arbitrary conditions
    def __eq__(self, other):
        return UnboundTest(self.args, self.kwargs, Result.returning(other))

    def raises(self, e: Exception) -> UnboundTest:
        return UnboundTest(self.args, self.kwargs, Result.raising(e))


tested = defaultdict(list)


def test(*unbound_tests):
    def register_tests(f):
        tests = [t.bind(f) for t in unbound_tests]
        tested[f].extend(tests)
        return f
    return register_tests


# TODO: build into Tester class, keep track of tested functions, failures, etc
def run_tests(print_fails=True, print_passes=False):
    passed = False
    failed = False
    for function, tests in tested.items():
        for test in tests:
            if not test:
                passed = False
                if print_fails:
                    print(test)
            else:
                passed = True
                if print_passes:
                    print(test)
    return passed and not failed

