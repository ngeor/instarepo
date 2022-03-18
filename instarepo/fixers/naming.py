FIXER_PREFIX = "instarepo.fixers."
FIXER_SUFFIX = "Fix"


def fixer_class_to_fixer_key(clz):
    """
    Derives the unique fixer identifier out of a fixer class.
    The identifier is shorter and can be used to dynamically
    turn fixers on/off via the CLI.
    """
    full_module_name: str = clz.__module__
    expected_prefix = FIXER_PREFIX
    if not full_module_name.startswith(expected_prefix):
        raise ValueError(
            f"Module {full_module_name} did not start with prefix {expected_prefix}"
        )
    expected_suffix = FIXER_SUFFIX
    if not clz.__name__.endswith(expected_suffix):
        raise ValueError(
            f"Module {clz.__name__} did not end with suffix {expected_suffix}"
        )
    my_module = full_module_name[len(expected_prefix) :]
    return (
        my_module
        + "."
        + _pascal_case_to_underscore_case(clz.__name__[0 : -len(expected_suffix)])
    )


def _pascal_case_to_underscore_case(value: str) -> str:
    """
    Converts a pascal case string (e.g. MyClass)
    into a lower case underscore separated string (e.g. my_class).
    """
    result = ""
    state = "initial"
    partial = ""
    for char in value:
        if "A" <= char <= "Z":
            if state == "initial":
                state = "upper"
            elif state == "upper":
                state = "multi-upper"
            else:
                if result:
                    result += "_"
                result += partial
                partial = ""
                state = "upper"
            partial += char.lower()
        else:
            if state == "multi-upper":
                if result:
                    result += "_"
                result += partial
                partial = ""
            partial += char
            state = "lower"

    if result:
        result += "_"
    result += partial
    return result
