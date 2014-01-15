# encoding: utf-8
import os.path
try:
    from setuptools import setup
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup


# TODO: Replace example placeholders.
setup(
    name='pdef-example',
    version='1.0',
    license='Apache License 2.0',
    description='Pdef example generator',
    url='',

    author='Example author',
    author_email='example@example.com',

    packages=['pdef_example'],
    package_data={
        '': ['*.jinja2']
    },

    install_requires=[
        'pdef-compiler'
    ],
    
    # Replace with an actual entry point.
    entry_points={
        'pdefc.generators': [
            'example = pdef_example:ExampleGenerator',
        ]
    },

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Compilers'
    ]
)
