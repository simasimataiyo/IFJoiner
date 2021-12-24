
import importlib
import pathlib
import os
cop_path = pathlib.Path("./custom_operators")
file_path_list = list(cop_path.glob("**/*.py"))
file_name_list = []

for pname in file_path_list:
    file_name = os.path.basename(pname)
    if(file_name != "__init__.py"):
        file_name = file_name.replace(".py", "")
        file_name_list.append(file_name)

__all__ = file_name_list