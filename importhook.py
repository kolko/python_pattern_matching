import sys
import imp
import ast

# def load_module(self, fullname):
#     print(111)
#     print(fullname)
#     code = self.get_code(fullname)
#     ispkg = self.is_package(fullname)
#     mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
#     mod.__file__ = "<%s>" % self.__class__.__name__
#     mod.__loader__ = self
#     if ispkg:
#         mod.__path__ = []
#         mod.__package__ = fullname
#     else:
#         mod.__package__ = fullname.rpartition('.')[0]
#     exec(code, mod.__dict__)
#     return mod
#
# sys.meta_path.append(load_module)


class MacroFinder(object):
    def find_module(self, module_name, package_path):
        print(1)
        return 1

    def load_module(self, fullname):
        print(2)
        code = self.get_code(fullname)
        ispkg = self.is_package(fullname)
        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod.__file__ = "<%s>1111111111112131111213131111111" % self.__class__.__name__
        mod.__loader__ = self
        if ispkg:
            mod.__path__ = []
            mod.__package__ = fullname
        else:
            mod.__package__ = fullname.rpartition('.')[0]
        exec(code, mod.__dict__)
        return mod

sys.meta_path.append(MacroFinder)
sys.path_hooks.append(MacroFinder)