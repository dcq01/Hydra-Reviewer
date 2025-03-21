# 函数：根据名称查找节点并返回代码片段
def find_code_by_name(node, name):
    # 检查当前节点是否匹配
    if node.type in ['function_definition', 'method_definition', 'class_implementation']:
        identifiers = [child for child in node.children]
        for identifier in identifiers:
            if identifier.text.decode('utf8') == name or identifier.text.decode('utf8') == (name + "()"):
                return node.text.decode('utf8')

    # 递归查找子节点
    for child in node.children:
        result = find_code_by_name(child, name)
        if result:
            return result

    return None
