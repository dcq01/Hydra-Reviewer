# 函数：根据名称查找节点并返回代码片段
def find_code_by_name(node, name):
    # 检查当前节点是否匹配
    if node.type in ['function_definition', 'type_definition']:
        identifiers = [child for child in node.children]
        for identifier in identifiers:
            if node.type == 'function_definition':
                if identifier.type == 'pointer_declarator':
                    identifier_text = identifier.text.decode('utf8')
                    index = identifier_text.find('(')
                    if index != -1:
                        identifier_text = identifier_text[:index]
                    if name in identifier_text:
                        return node.text.decode('utf8')
                if identifier.type == 'function_declarator':
                    identifier_text = identifier.text.decode('utf8')
                    index = identifier_text.find('(')
                    if index != -1:
                        identifier_text = identifier_text[:index]
                    if name in identifier_text:
                        return node.text.decode('utf8')
            if node.type == 'type_definition':
                if identifier.text.decode('utf8') == name:
                    return node.text.decode('utf8')

    # 递归查找子节点
    for child in node.children:
        result = find_code_by_name(child, name)
        if result:
            return result

    return None
