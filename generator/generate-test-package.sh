#!/bin/sh
pdefc -v generate-example https://raw.github.com/pdef/pdef/1.1/test/test.yaml \
    --module pdef_test:test \
    --prefix pdef:Example \
    --out generated-files
