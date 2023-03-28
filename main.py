from typing import Optional, Callable, Tuple

Rule = Tuple[Callable[[str], bool], int]

def accept_char(char: str) -> Callable[[str], bool]:
    return lambda c: c == char


def accept_all() -> Callable[[str], bool]:
    return lambda _: True


class Matcher:

    def __init__(self, pattern: str) -> None:
        self.pattern = pattern

        self.state = 0
        self.state_1_buffer = ""

        self._pattern_iterator = iter(pattern)
        self._rules: list[Rule] = []

        self._get_rules()

    def _next_char(self) -> Optional[str]:
        """ Get the next character """

        try:
            return next(self._pattern_iterator)
        except:
            return None

    @property
    def rules(self) -> list[Rule]:
        """ Get match rules """
        return self._rules

    def _get_rules(self):
        """ Generate rules from pattern """

        while char := self._next_char():

            escaping = False

            if char == "\\":

                if not (char := self._next_char()):
                    raise

                escaping = True

            if self.state == 0:
                if char == "{" and not escaping:
                    self.state = 1

                elif char == "." and not escaping:
                    self._rules.append((accept_all(), 1))

                else:
                    self._rules.append((accept_char(char), 1))

            elif self.state == 1:
                if char == "}":
                    length = int(self.state_1_buffer)  # get wanted size for last rule

                    assert length >= 1

                    last_rule = self.rules[-1][0]  # get last rule function
                    self._rules = self.rules[:-1]  # remove last rule

                    self._rules.append((last_rule, length))
                    self.state_1_buffer = ""
                    self.state = 0

                else:
                    self.state_1_buffer += char

    def match(self, text: str) -> bool:
        """ Test if pattern matches string """

        idx = 0
        n = len(text)

        for rule, length in self.rules:
            for _ in range(length):
                if idx == n or not rule(text[idx]):
                    return False

                idx += 1

        return idx == n


pattern = Matcher(r"\.{5}")

assert pattern.match(".....")
assert not pattern.match("aaaaa")

pattern = Matcher(r"a{5}.c{2}")

assert pattern.match("aaaaa cc")
assert pattern.match("aaaaabcc")
assert not pattern.match("aaaaa cca")

pattern = Matcher(r"a{5} c{2}")

assert pattern.match("aaaaa cc")
assert not pattern.match("aaaaabcc")
assert not pattern.match("aaaaa cca")
