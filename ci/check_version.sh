#!/bin/bash
# Double check that the version in setup.cfg matches the version in instarepo.main
SETUP_CFG_VERSION=$(grep version setup.cfg | tr -d ' ' | cut -d= -f2)
MAIN_PY_VERSION=$(grep "VERSION =" instarepo/main.py | cut -d\" -f2)
if [[ "${SETUP_CFG_VERSION}" != "${MAIN_PY_VERSION}" ]]; then
    echo "Version in setup.cfg was ${SETUP_CFG_VERSION}"
    echo "Version in instarepo/main.py was ${MAIN_PY_VERSION}"
    exit 1
fi
