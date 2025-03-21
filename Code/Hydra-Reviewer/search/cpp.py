# 函数：根据名称查找节点并返回代码片段
def find_code_by_name(node, name):
    # 查找函数、方法或类定义
    if node.type in ['function_definition', 'class_specifier']:
        identifiers = [child for child in node.children]
        for identifier in identifiers:
            if (identifier.type == 'function_declarator' and name in identifier.text.decode('utf8')) or (
                    node.type == 'class_specifier' and identifier.text.decode('utf8') == name):
                return node.text.decode('utf8')

    # 递归查找所有子节点
    for child in node.children:
        result = find_code_by_name(child, name)
        if result:
            return result
    return None
