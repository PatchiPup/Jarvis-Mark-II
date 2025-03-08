import pkgutil
import importlib
import command_modules

all_commands = {}
all_commands_str = ""
additional_info_str = ""

# Iterate over all modules in the handlers package
for _, module_name, _ in pkgutil.iter_modules(command_modules.__path__, command_modules.__name__ + "."):
    module = importlib.import_module(module_name)
    print(module_name)
    # Merge the command_handlers from each module
    if hasattr(module, "command_handlers"):
        all_commands.update(module.command_handlers)

    if hasattr(module, "commands_string"):
        all_commands_str += module.commands_string + '\n'

    if hasattr(module, "additional_info"):
        additional_info_str += module.additional_info + '\n'

