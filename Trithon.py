# Trithon (Tribes & Python) Hybrid Scripts
# -|DF|- Link
# Communication DLL by Bovidi

# Use telnet to communicate back and forth using TRIBES and python functions and execute different commands outside of the game.

#   Examples:
#        SpotifyHUD  --  Get spotify info directly into TRIBES if Spotify is found to be open and                               playing.

#        WeatherHUD  --  Get local weather, or from anywhere, in an instant with data uploaded right                            to the weatherHUD in TRIBES.

# from types import SimpleNamespace
# from registered_functions import registered_functions
import json, os


class ValueMissing(Exception):
    def __init__(self, message="You are missing a value."):
        super().__init__(message)


class Trithon:
    def __init__(self, func_dict=None):
        self.func_dict = func_dict if func_dict is not None else dict()
        self._json = None

    def add_variable(self, var: str = None, association: str = None):
        "Cycle all checks to make sure there are values"

        if var is None and association is None or var == "" and association == "":
            return "Please add a TRIBES variable name and association."
        elif var == "":
            return "Please add a TRIBES variable name."
        elif association == "" or association is None:
            return "Please add a TRIBES association."

        return f'$pref::{var} = "{association}"; \n'

    def add_function(self, func: str = None):
        if func is not None:
            return func + "\n"

        return "Please add a TRIBES function."

    def add_to_dict(self, **kwargs):
        """
        Add a TRIBES and Python function to the dictionary so
        telnet can differentiate between commands.
        """

        for key, value in kwargs.items():
            self.func_dict[key] = str(value)

    def read_dict(self, tribes_func: str):
        """
        Read's the dictionary to find any key:value pairs for TRIBES
        and Python commands.
        """

        return self.func_dict.get(tribes_func, 'None')
   
    def eval(self, func, *args: str):
        arg_lst = []
        for arg in args:
            arg_lst.append(f'"{arg}"')

        the_args = ", ".join(arg_lst)

        end = ");"

        return(str(f'eval("{func}({the_args}' + end))

    def write_to_file(self, filename):
        pass

    def write_json(self, filename, json_data=None):
        if filename:
            if os.path.isfile(filename) and json_data is not None:
                with open(filename, "w") as file:
                    file.write(filename, json_data)

    def read_json(self, json_str=None, filename=None, *args):
        if json_str is not None:
            if validate_json(json_str):
                self._json = json.loads(json_str)
        elif filename is not None:
            if os.path.isfile(filename):
                with open(filename, "r") as file:
                    self._json = file.read()
        else:
            return False


def validate_json(data):
    try:
        json.loads(data)
    except ValueError:
        return False
    return True
