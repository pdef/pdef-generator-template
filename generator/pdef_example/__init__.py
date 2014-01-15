# encoding: utf-8
from pdefc.lang import TypeEnum
from pdefc.generators import Generator, Templates, GeneratorCli, ModuleMapper, PrefixMapper


ENCODING = 'utf8'
ENUM_TEMPLATE = 'enum.jinja2'
MESSAGE_TEMPLATE = 'message.jinja2'
INTERFACE_TEMPLATE = 'interface.jinja2'
MODULE_TEMPLATE = 'module.jinja2'


class ExampleGeneratorCli(GeneratorCli):
    '''Generator command-line interface which adds command to the compiler arg parser.'''

    def build_parser(self, parser):
        self._add_module_args(parser)
        self._add_prefix_args(parser)

    def create_generator(self, out, args):
        module_names = self._parse_module_args(args)
        prefixes = self._parse_prefix_args(args)
        return ExampleGenerator(out, module_names, prefixes)


class ExampleGenerator(Generator):
    '''Example generator template.'''

    @classmethod
    def create_cli(cls):
        '''Create and return a generator command-line interface.'''
        return ExampleGeneratorCli()

    def __init__(self, out, module_names=None, prefixes=None):
        '''Create a new generator.'''
        super(ExampleGenerator, self).__init__(out)
        self.module_mapper = ModuleMapper(module_names)
        self.prefix_mapper = PrefixMapper(prefixes)

        # Generator filters available in jinja templates.
        self.filters = ExampleFilters(self.module_mapper, self.prefix_mapper)

        # Jinja templates relative to this file.
        self.templates = Templates(__file__, filters=self.filters)

    def generate(self, package):
        '''Generate a package source code.'''
        for module in package.modules:
            for definition in module.definitions:
                code = self._generate_definition(definition)
                filename = self._definition_filename(definition)
                self.write_file(filename, code)

            code = self.templates.render(MODULE_TEMPLATE, module=module)
            filename = self._module_filename(module)
            self.write_file(filename, code)

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
        name = self.filters.example_name(definition)
        return '%s/%s.json' % (dirname, name)

    def _module_directory(self, module):
        '''Return a module directory name from a module.fullname.'''
        name = self.filters.example_module(module)
        return name.replace('.', '/')

    def _module_filename(self, module):
        '''Return a module filename.'''
        dirname = self._module_directory(module)
        return '%s.json' % dirname


class ExampleFilters(object):
    '''Example filters which are available in jinja templates.

    A filter transforms a printed value in a template. For example (in a jinja template):
    {{ message.base|example_ref }}.

    '''

    def __init__(self, module_mapper, prefix_mapper):
        self.module_mapper = module_mapper
        self.prefix_mapper = prefix_mapper

    def example_bool(self, expression):
        return 'true' if expression else 'false'

    def example_module(self, module):
        '''Map a module name using the module_mapper.'''
        return self.module_mapper(module.fullname)

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

    def example_name(self, def0):
        '''Return a definition name with an optional prefix without a module name.'''
        prefix = self.prefix_mapper.get_prefix(def0.namespace)
        return prefix + def0.name if prefix else def0.name

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
        def_name = self.example_name(def0)
        return '%s.%s' % (module_name, def_name)
