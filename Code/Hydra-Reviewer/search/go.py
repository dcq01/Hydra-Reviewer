# 函数：根据名称查找节点并返回代码片段
# 解析代码并查找函数定义
def find_code_by_name(node, name):
    # 查找类和方法定义
    if node.type in ['type_declaration', 'function_declaration', 'method_declaration']:
        identifiers = [child for child in node.children]
        for identifier in identifiers:
            if node.type == 'type_declaration' and identifier.type == 'type_spec':
                lines = identifier.text.decode('utf8').splitlines()
                if name in lines[0]:
                    return node.text.decode('utf8')
            if node.type == 'function_declaration' or node.type == 'method_declaration':
                if identifier.text.decode('utf8') == name:
                    return node.text.decode('utf8')

    # 递归查找所有子节点
    for child in node.children:
        result = find_code_by_name(child, name)
        if result:
            return result

    return None
