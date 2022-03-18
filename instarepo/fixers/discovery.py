from typing import List

import instarepo.fixers.base
import instarepo.fixers.changelog
import instarepo.fixers.ci
import instarepo.fixers.config
import instarepo.fixers.context
import instarepo.fixers.dotnet
import instarepo.fixers.license
import instarepo.fixers.maven
import instarepo.fixers.missing_files
import instarepo.fixers.pascal
import instarepo.fixers.readme
import instarepo.fixers.repo_description
import instarepo.fixers.vb6

from .naming import FIXER_SUFFIX, fixer_class_to_fixer_key


def try_get_fixer_order(fixer_class):
    return fixer_class.order if hasattr(fixer_class, "order") else 0


def select_fixer_classes(
    only_fixers: List[str] = None, except_fixers: List[str] = None
):
    if only_fixers:
        if except_fixers:
            raise ValueError("Cannot use only_fixers and except_fixers together")
        unsorted_iterable = filter(
            lambda fixer_class: _fixer_class_starts_with_prefix(
                fixer_class, only_fixers
            ),
            all_fixer_classes(),
        )
    elif except_fixers:
        unsorted_iterable = filter(
            lambda fixer_class: not _fixer_class_starts_with_prefix(
                fixer_class, except_fixers
            ),
            all_fixer_classes(),
        )
    else:
        unsorted_iterable = all_fixer_classes()
    result = list(unsorted_iterable)
    result.sort(key=try_get_fixer_order)
    return result


def _fixer_class_starts_with_prefix(fixer_class, prefixes: List[str]):
    """
    Checks if the friendly name of the given fixer class starts with any of the given prefixes.
    """
    fixer_key = fixer_class_to_fixer_key(fixer_class)
    for prefix in prefixes:
        if fixer_key.startswith(prefix):
            return True
    return False


def all_fixer_classes():
    """Gets all fixer classes"""
    my_modules = [
        instarepo.fixers.changelog,
        instarepo.fixers.ci,
        instarepo.fixers.dotnet,
        instarepo.fixers.license,
        instarepo.fixers.maven,
        instarepo.fixers.missing_files,
        instarepo.fixers.pascal,
        instarepo.fixers.readme,
        instarepo.fixers.repo_description,
        instarepo.fixers.vb6,
    ]
    for my_module in my_modules:
        my_classes = classes_in_module(my_module)
        for clz in my_classes:
            if clz.__name__.endswith(FIXER_SUFFIX):
                yield clz


def classes_in_module(module):
    """
    Gets the classes defined in the given module
    """
    module_dict = module.__dict__
    return (
        module_dict[c]
        for c in module_dict
        if (
            isinstance(module_dict[c], type)
            and module_dict[c].__module__ == module.__name__
        )
    )
