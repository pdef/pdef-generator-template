# encoding: utf-8
import io
import logging
import os
from pdefc.lang import TypeEnum
from pdefc.generators import Generator, Namespace, Templates, mkdir_p, upper_first


ENCODING = 'utf8'
ENUM_TEMPLATE = 'enum.jinja2'
MESSAGE_TEMPLATE = 'message.jinja2'
INTERFACE_TEMPLATE = 'interface.jinja2'
MODULE_TEMPLATE = 'module.jinja2'


class ExampleGenerator(Generator):
    '''Example pdef generator based on Jinja templates.

    @see Template engine documentation http://jinja.pocoo.org/
    '''

    def __init__(self, out, namespace=None, **kwargs):
        '''Create a new generator.

        @param out          Destination directory
        @param namespace    {pdef_module: language_module} name mapping,
                            for example, {"pdef.tests": "pdef_tests"}.
        '''
        super(ExampleGenerator, self).__init__(out, namespace=namespace, **kwargs)

        # Generator filters available in jinja templates.
        self.filters = ExampleFilters(self.namespace)

        # Jinja templates relative to this file.
        self.templates = Templates(__file__, filters=self.filters)

    def generate(self, package):
        '''Generate a package source code.'''
        for module in package.modules:
            self._generate_module(module)

    def _generate_module(self, module):
        '''Generate a module and its definitions source code and write the files.'''
        for definition in module.definitions:
            code = self._generate_definition(definition)
            filename = self._definition_filename(definition)
            self._write_file(filename, code)

        code = self.templates.render(MODULE_TEMPLATE, module=module)
        filename = self._module_filename(module)
        self._write_file(filename, code)

    def _generate_definition(self, definition):
        if definition.is_enum:
            return self.templates.render(ENUM_TEMPLATE, enum=definition)
        elif definition.is_message:
            return self.templates.render(MESSAGE_TEMPLATE, message=definition)
        elif definition.is_interface:
            return self.templates.render(INTERFACE_TEMPLATE, interface=definition)
        raise ValueError('Unsupported definition %r' % definition)

    def _definition_filename(self, definition):
        dirname = self._module_directory(definition.module)
        return '%s/%s.json' % (dirname, definition.name)

    def _module_directory(self, module):
        '''Return a module directory name from a module.name.'''
        name = self.namespace.map(module.name)
        return name.replace('.', '/')

    def _module_filename(self, module):
        '''Return a module filename.'''
        dirname = self._module_directory(module)
        return '%s.json' % dirname

    def _write_file(self, filename, code):
        # Join the filename with the destination directory.
        filepath = os.path.join(self.out, filename)

        # Create a directory with its children for a file.
        dirpath = os.path.dirname(filepath)
        mkdir_p(dirpath)

        # Write the file contents.
        with io.open(filepath, 'wt', encoding=ENCODING) as f:
            f.write(code)
        logging.info('Created %s', filename)


class ExampleFilters(object):
    '''Example filters which are available in jinja templates.

    A filter transforms a printed value in a template. For example (in a jinja template):
    {{ message.base|example_ref }}.

    '''
    def __init__(self, namespace):
        self.namespace = namespace

    def example_bool(self, expression):
        return 'true' if expression else 'false'

    def example_module(self, module):
        '''Map a module name using the namespace.'''
        return self.namespace.map(module.name)

    def example_ref(self, type0):
        '''Return an example language reference.'''
        type_name = type0.type

        if type_name in TypeEnum.PRIMITIVE_TYPES:
            # It's a simple primitive type, return its pdef enum type.
            return type_name

        elif type_name == TypeEnum.VOID:
            return 'void'

        elif type_name == TypeEnum.LIST:
            return self._list(type0)

        elif type_name == TypeEnum.SET:
            return self._set(type0)

        elif type_name == TypeEnum.MAP:
            return self._map(type0)

        elif type_name == TypeEnum.ENUM_VALUE:
            return self._enum_value(type0)

        # It's an enum, a message or an interface.
        return self._definition(type0)

    def _list(self, list0):
        '''Return a list reference, for example, list<TestEnum>.'''
        element = self.example_ref(list0.element)
        return 'list<%s>' % element

    def _set(self, set0):
        '''Return a set reference, for example, set<TestMessage>.'''
        element = self.example_ref(set0.element)
        return 'set<%s>' % element

    def _map(self, map0):
        '''Return a map reference, for example, map<int32, string>.'''
        key = self.example_ref(map0.key)
        value = self.example_ref(map0.value)
        return 'map<%s, %s>' % (key, value)

    def _enum_value(self, enum_value):
        '''Return an enum value reference, for example, package.module.Sex.MALE.'''
        enum = self.example_ref(enum_value.enum)
        return '%s.%s' % (enum, enum_value.name)

    def _definition(self, def0):
        '''Return a definition reference, for example, package.module.TestInterface.'''
        module_name = self.example_module(def0.module)
        return '%s.%s' % (module_name, def0.name)
