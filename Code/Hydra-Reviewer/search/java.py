def find_code_by_name(node, name):
    # 查找类和方法定义
    if node.type in ['class_declaration', 'method_declaration']:
        identifiers = [child for child in node.children]
        for identifier in identifiers:
            if identifier.text.decode('utf8') == name:
                return node.text.decode('utf8')

    # 递归查找所有子节点
    for child in node.children:
        result = find_code_by_name(child, name)
        if result:
            return result

    return None
