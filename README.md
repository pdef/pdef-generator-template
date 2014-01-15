Pdef generator template
=======================

This is a [pdef](http://pdef.io/) code generator example based on 
[Jinja2](http://jinja.pocoo.org/) template engine. The preferred way to write 
a custom generator is to clone and modify this one.

How to use
----------
Clone this repository.

```bash
git clone git@github.com:pdef/pdef-generator-template.git
```

Setup a python sandbox with [virtualenv](http://www.virtualenv.org/en/latest/).
```bash
virtualenv env
```

Activate the sandbox.
```bash
source env/bin/activate
```

Install the pdef compiler in the sandbox (`pip` is already available there).
```bash
pip install pdef-compiler
```

Cd into the `generator` directory and activate the development mode.
```bash
cd generator
python setup.py develop
```

From now on `generate-example` will be available as a `pdefc` command.
Generate the test pdef package.
```bash
pdefc -v generate-example https://raw.github.com/pdef/pdef/1.1/test/test.yaml \
    --out generated-files
```

Or use the `generate-test-package.sh` script (it also specifies some example module and prefix 
mappings).
```
./generate-test-package.sh
```

Update `setup.py` with custom information and license, and a correct entry point 
(there is a special comment about it inside). The entry point is a generator name 
which is used as the `generate-` command suffix.

See [The Python Package Index](http://docs.python.org/3.3/distutils/packageindex.html)
docs on how to upload the package to PyPI.
