import json
import inspect
import os
from collections import defaultdict
import paddle

temp_standard_api = defaultdict(list)

def get_all_module():
    module_list = []
    for root, dirs, files in os.walk("/workspace/Paddle1/python/paddle"):
        for file in files:
            file_path = os.path.join(root, file)
            file_path_list = []
            if file_path.endswith("__init__.py"):
                file_path_list = file_path.split("/")[4:-1]
            elif file_path.endswith(".py"):
                file_path_list = file_path[:-3].split("/")[4:]

            if len(file_path_list) > 0:
                if file_path_list[-1].startswith("_"):
                    continue
                if file_path_list[-1].startswith("__"):
                    continue
                module_name = ".".join(file_path_list)
                try:
                    # import的范围比eval大
                    # import: 任意文件都可以import，例如 import paddle.check_import_scipy
                    # eval: 只有在paddle/__init__.py中import过的才可以eval，例如 无法直接 eval(paddle.check_import_scipy)，
                    # 只有 import paddle.check_import_scipy，才可以eval调到
                    module = eval(module_name)
                    if inspect.ismodule(module):
                        skip_module_list = ['quant', 'sparse', 'incubate', 'decomposition', 'pir', 'fleet', 'distributed.passes', 
                            'distributed.auto_parallel', 'distributed.ps.the_one_ps', 'gast']
                        skip = False
                        for skip_module in skip_module_list:
                            if skip_module in module_name:
                                skip = True
                                break
                        if not skip:
                            module_list.append(module)
                except:
                    pass
    

    return module_list

def get_standard_api(module):
    """
    获取模块中存储在__all__中的标准推荐API，并将其存储在字典中。

    Args:
        module (Any): 任意模块

    Returns:
        Optional[Dict[str, str]]: 包含API名称和完整API路径的字典。
    """
    if not inspect.ismodule(module):
        return
    if getattr(module, "__all__", None):
        for api_name in module.__all__:
            api_full_name = module.__name__ + "." + api_name
            try:
                api = eval(api_full_name)
                if inspect.isfunction(api) or inspect.isclass(api):
                    temp_standard_api[api_name].append(api_full_name)
            except:
                pass

if __name__ == "__main__":
    for module in get_all_module():
        if 'lazy_init' in module.__name__:
            continue
        if 'fleet.base.topology' in module.__name__:
            continue
        if 'paddle.distribution.transform' in module.__name__:
            continue
        get_standard_api(module)


    standard_api = {}
    for k, v in temp_standard_api.items():
        if len(v) == 1:
            standard_api[k] = v[0]


    with open("standard_api.json", "w") as f:
        json.dump(standard_api, f, indent=4)
