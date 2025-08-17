#!/bin/bash
source venv/bin/activate
cd docs/

sphinx-apidoc -o source/ ../src/pydessem/

make html
deactivate