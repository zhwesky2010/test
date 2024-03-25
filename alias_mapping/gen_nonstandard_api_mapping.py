import json
import inspect
import paddle

from gen_standard_api import get_all_module

with open("standard_api.json", "r") as f:
    standard_api = json.load(f)

nonstandard_api_mapping = {}
def get_nonstandard_api_mapping(module):
    if not inspect.ismodule(module):
        return
    for api_name in dir(module):
        if getattr(module, "__all__", None):
            if api_name in module.__all__:
                continue

        api_full_name = module.__name__ + "." + api_name
        try:
            api = eval(api_full_name)
            if inspect.isfunction(api) or inspect.isclass(api):
                if api_name in standard_api:
                    nonstandard_api_mapping[api_full_name] = standard_api[api_name]
        except:
            pass

if __name__ == "__main__":
    for module in get_all_module():
        get_nonstandard_api_mapping(module)

    with open("nonstandard_api_mapping.json", "w") as f:
        json.dump(nonstandard_api_mapping, f, indent=4)
