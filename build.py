# coding:utf-8
import codecs
import os
import re
import datetime

dir_auto = "auto/api"
dir_manual = "manual"
dir_script = "script"
file_auto_output = "snippets/auto.sublime-completions"
file_manual_output = "snippets/manual.sublime-completions"
file_script_output = "snippets/script.sublime-completions"

# --------------------------------------------------------------------------------
# for the dir_auto
# --------------------------------------------------------------------------------
# get the module name: jsb
# var jsb = jsb || {};
module_name_pattern = re.compile(r"var ([\w]+)")
# get the class name: Skeleton3D
# @class Skeleton3D
class_name_pattern = re.compile(r"@class\s*([\w]+)")
# get the method name And args: addBone (bone3d)
# addBone : function (
# bone3d 
# )
# {
# },
method_pattern = re.compile(r"([\w]+)\s*:\s*function\s*(\([^\)]*\))")

def CreateAutoSnippets():
    # 打开输出文件
    handle_output = codecs.open(file_auto_output, "w", "utf-8")
    # 遍历文件
    temp = "// Created On " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
    temp += "{\n"
    temp += "\"scope\": \"source.js\",\n"
    temp += "\"completions\":[\n"
    for file in os.listdir(dir_auto):
        if file.endswith("api.js"):
            handle_api_file = codecs.open(os.path.join(dir_auto, file), "r", "utf-8")
            content = handle_api_file.read()
            module_name_results = module_name_pattern.findall(content)
            module_name = module_name_results[0]
            print("******************************************************" )
            print("file:   %s" % file)
            print("module: %s" % module_name)
            # 把指针再次重新定位到文件开头
            handle_api_file.seek(0, 0)
            first_find = True
            class_name = ""
            class_content = ""
            class_count = 0
            lines = handle_api_file.readlines()
            line_count = len(lines)                            
            for i in range(line_count):
                line = lines[i]
                class_name_results = class_name_pattern.findall(line)
                # 匹配到下一个class_name或者到达文件尾
                if (len(class_name_results) > 0) or (i == (line_count - 1)):
                    if first_find:
                        first_find = False
                        class_content = line
                    else:
                        method_results = method_pattern.findall(class_content)
                        method_count = 0
                        for method_result in method_results:
                            method_name = method_result[0]
                            method_args = method_result[1]
                            # 去掉换行和最后的空格 再弄美观一点
                            method_args = method_args.replace("\n", "")
                            method_args = method_args.replace(" ", "")
                            method_args = method_args.replace(",", ", ")
                            # print(method_name + " " + method_args)
                            temp += "{ \"trigger\": \"%s.%s.%s%s\", \"contents\": \"%s%s\" },\n" % (module_name, class_name, method_name, method_args, method_name, method_args) 
                            method_count = method_count + 1
                        class_content = line
                        # print("@class %s methods:%d" % (class_name, method_count))             
                    if (len(class_name_results) > 0):
                        class_name = class_name_results[0]
                        class_count = class_count + 1
                else:
                    class_content = class_content + line
            print("classes:%d" % class_count)                
            handle_api_file.close()
    temp += "]\n}\n"
    # 写入结果
    handle_output.write(temp)
    # 关闭输出文件
    handle_output.close()

# --------------------------------------------------------------------------------
# for the dir_manual
# --------------------------------------------------------------------------------
# get each static extendXXX function
extend_function_pattern = re.compile(r"^static\s+[\w]+\s+extend[^\{]*\{[^\{]*\{[^\}]*\}[^\}]*\}", re.M)
# get each lua_pushstring
lua_pushstring_pattern = re.compile(r"lua_pushstring\([\w]+,\s*\"([\w\.]+)\"\);")
# get each tolua_function
tolua_function_pattern = re.compile(r"tolua_function\([\w]+,\s*\"([\w\.]+)\",[^;]+;")
# for lua_cocos2dx_physics_manual.cpp pattern
physics_module_pattern = re.compile(r"lua_pushstring\([\w]+,\s*\"([\w\.]*)\"\);[^\{]*\{[^\}]*\}")

def CreateManualSnippets():
    # 打开输出文件
    handle_output = codecs.open(file_manual_output, "w", "utf-8")
    # 遍历cpp文件
    temp = "// Created On " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
    temp += "{\n"
    temp += "\"scope\": \"source.lua\",\n"
    temp += "\"completions\":[\n"
    for file in os.listdir(dir_manual):
        if file.startswith("lua_cocos2dx_") and file.endswith(".cpp"):           
            api_file = codecs.open(os.path.join(dir_manual, file), "r", "utf-8").read()
            if "lua_cocos2dx_deprecated.cpp" == file:
                # 不处理这个文件
                "" 
            elif "lua_cocos2dx_manual.cpp" == file:
                extends = extend_function_pattern.finditer(api_file)
                for extend in extends:
                    lua_pushstrings = lua_pushstring_pattern.finditer(extend.group())
                    module_name = lua_pushstrings.next().group(1)
                    for lua_pushstring in lua_pushstrings:
                        function_name = lua_pushstring.group(1)
                        # create a trigger, like this:
                        # { "trigger": "cc.Image:retain()", "contents": "retain()" },                           
                        temp += "{ \"trigger\": \"%s:%s(?)\", \"contents\": \"%s()\" },\n" % (module_name, function_name, function_name) 
                        # print("%s:%s()" % (module_name,function_name))
            elif "lua_cocos2dx_physics_manual.cpp" == file:
                modules = physics_module_pattern.finditer(api_file)
                for module in modules:
                    lua_pushstrings = lua_pushstring_pattern.finditer(module.group())
                    module_name = lua_pushstrings.next().group(1)
                    for lua_pushstring in lua_pushstrings:
                        function_name = lua_pushstring.group(1)
                        # create a trigger, like this:
                        # { "trigger": "cc.Image:retain()", "contents": "retain()" },                           
                        temp += "{ \"trigger\": \"%s:%s(?)\", \"contents\": \"%s()\" },\n" % (module_name, function_name, function_name) 
                        # print("%s:%s()" % (module_name,function_name))
                    # 这个文件最后有一个tolua_function的注册形式与前面的注册形式不同
                    tolua_functions = tolua_function_pattern.finditer(module.group())
                    for tolua_function in tolua_functions:
                        function_name = tolua_function.group(1)
                        # create a trigger, like this:
                        # { "trigger": "cc.Image:retain()", "contents": "retain()" },                           
                        temp += "{ \"trigger\": \"%s:%s(?)\", \"contents\": \"%s()\" },\n" % (module_name, function_name, function_name) 
                        # print("%s:%s()" % (module_name,function_name))
            else:
                extends = extend_function_pattern.finditer(api_file)
                for extend in extends:
                    lua_pushstrings = lua_pushstring_pattern.finditer(extend.group())
                    for lua_pushstring in lua_pushstrings:
                        module_name = lua_pushstring.group(1)
                        tolua_functions = tolua_function_pattern.finditer(extend.group())
                        for tolua_function in tolua_functions:
                            function_name = tolua_function.group(1)
                            # create a trigger, like this:
                            # { "trigger": "cc.Image:retain()", "contents": "retain()" },
                            temp += "{ \"trigger\": \"%s:%s(?)\", \"contents\": \"%s()\" },\n" % (module_name, function_name, function_name) 
    temp += "]\n}\n"
    # 写入结果
    handle_output.write(temp)
    # 关闭输出文件
    handle_output.close()

# --------------------------------------------------------------------------------
# for the dir_script
# --------------------------------------------------------------------------------
script_function_pattern = re.compile(r"function\s+([\w\.\:]+)\(([^\)]+)\)")
# \s*([\w\.]+)\s*=\s*function\s*(\([^\)]+\))
# Cocos2dConstants.lua中的cc.KeyCode含有很多特殊符号 无能为力
# 多了一个 KEY_SPACE = ' ', 筛选不掉，这一行应该在table_const_pattern里面才对
normal_const_pattern = re.compile(r"([\w\.]+)\s*\=\s*([\w\']+)\s+")
# KEY_RIGHT_BRACE       = '}', 整个匹配结束了，漏了末尾几条
table_const_pattern = re.compile(r"([\w\.]+)\s*\=\s*\{[^\}]+\}")
each_table_const_pattern = re.compile(r"([\w\.]+)\s*\=\s*([\w\']+)")

def CreateScriptSnippets():
    # 打开输出文件
    handle_output = codecs.open(file_script_output, "w", "utf-8")
    # 遍历lua文件
    temp = "// Created On " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
    temp += "{\n"
    temp += "\"scope\": \"source.js\",\n"
    temp += "\"completions\":[\n"
    for path, dir_names, file_names in os.walk(dir_script):
        for file_name in file_names:
            full_file_name = os.path.join(path, file_name)
            # print(full_file_name)
            if not full_file_name.startswith("Deprecated") and  full_file_name.endswith(".lua"):
                handle_api_file = codecs.open(full_file_name, "r", "utf-8")
                content = handle_api_file.read()
                if full_file_name.endswith("Constants.lua"):
                    # 查找单行行的常量 cc = XXX
                    normal_consts = normal_const_pattern.finditer(content)
                    for normal_const in normal_consts:
                        lhs = normal_const.group(1)
                        rhs = normal_const.group(2)
                        # print("%s = %s" % (lhs, rhs))
                        temp += "{ \"trigger\": \"%s = %s\", \"contents\": \"%s\" },\n" % (lhs, rhs, lhs)
                    table_consts = table_const_pattern.finditer(content)
                    # 查找常量是一个table的情况，找到之后再匹配单行
                    for table_const in table_consts:
                        table_name = table_const.group(1)
                        each_table_consts = each_table_const_pattern.finditer(table_const.group(0))
                        for each_table_const in each_table_consts:
                            lhs = each_table_const.group(1)
                            rhs = each_table_const.group(2)
                            # print("%s.%s = %s" % (table_name, lhs, rhs))
                            temp += "{ \"trigger\": \"%s.%s = %s\", \"contents\": \"%s.%s\" },\n" % (table_name, lhs, rhs, table_name, lhs)
                else:
                    script_functions = script_function_pattern.finditer(content)
                    for script_function in script_functions:
                        # print(script_function)
                        function_name = script_function.group(1)
                        params = script_function.group(2)
                        params = params.strip()
                        # print("%s(%s)" % (function_name, params))
                        # create a trigger, like this:
                        # { "trigger": "cc.Image:retain()", "contents": "retain()" },
                        temp += "{ \"trigger\": \"%s(%s)\", \"contents\": \"%s()\" },\n" % (function_name, params, function_name) 
                handle_api_file.close()
    temp += "]\n}\n"
    # 写入结果
    handle_output.write(temp)
    # 关闭输出文件
    handle_output.close()

# --------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------
if "__main__" == __name__:
    # CreateAutoSnippets()
    # CreateManualSnippets()
    CreateScriptSnippets()
    # if "nt" == os.name:
    #     print("*********")
    #     print("finish...")
    #     print("*********")
    #     os.system("pause")
