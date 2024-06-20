import importlib.util

async def load_command(command_name):
    spec = importlib.util.spec_from_file_location(f"command.{command_name}", f"command/{command_name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    command_func = getattr(module, command_name)
    return command_func