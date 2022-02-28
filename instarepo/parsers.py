def quote():
    return one_char_if(lambda char: char == '"')


def not_quote():
    return many(one_char_if(lambda char: char != '"'))


def quoted_string():
    return combine_and(combine_and(quote(), not_quote()), quote())


def whitespace():
    return many(one_char_if(is_whitespace))


def surrounded_by_space(parser):
    def _surrounded_by_space(contents: str):
        _, remaining = whitespace()(contents)
        result, remaining = parser(remaining)
        if result:
            _, remaining = whitespace()(remaining)
            return result, remaining
        return "", contents

    return _surrounded_by_space


def is_symbol(char):
    return char in ",()="


def is_whitespace(char):
    return char == " " or char == "\t"


def any_char():
    def _any_char(contents: str):
        if len(contents) > 0:
            result = contents[0]
            remaining = contents[1:]
            return result, remaining
        else:
            return "", ""

    return _any_char


def one_char_if(predicate):
    def _one_char_if(contents: str):
        result, remaining = any_char()(contents)
        if predicate(result):
            return result, remaining
        else:
            return "", contents

    return _one_char_if


def many(parser):
    def _many(contents: str):
        eof = False
        remaining = contents
        total_result = ""
        while not eof:
            result, remaining = parser(remaining)
            total_result += result
            eof = not result
        return total_result, remaining

    return _many


def is_letter(char):
    return (char >= "a" and char <= "z") or (char >= "A" and char <= "Z")


def letter():
    return one_char_if(is_letter)


def word():
    return many(letter())


def combine_and(first, second):
    """
    Parser combinator where both first and second parser
    must return a successful result.
    """

    def _combine_and(contents: str):
        first_result, remaining = first(contents)
        if first_result:
            second_result, remaining = second(remaining)
            if second_result:
                return first_result + second_result, remaining
        return "", contents

    return _combine_and


def combine_and_opt(first, second):
    def _combine_and_opt(contents: str):
        first_result, remaining = first(contents)
        if first_result:
            second_result, remaining = second(remaining)
            return first_result + second_result, remaining
        return "", contents

    return _combine_and_opt


def combine_or(*parsers):
    def _combine_or(contents: str):
        for parser in parsers:
            result, remaining = parser(contents)
            if result:
                return result, remaining
        return "", contents

    return _combine_or


def is_cr_lf(char):
    return char == "\r" or char == "\n"


def until_eol_or_eof():
    def _until_eol_or_eof(contents: str):
        i = 0
        while i < len(contents) and not is_cr_lf(contents[i]):
            i = i + 1
        j = i
        while j < len(contents) and is_cr_lf(contents[j]):
            j = j + 1
        return contents[0:i], contents[j:]

    return _until_eol_or_eof
