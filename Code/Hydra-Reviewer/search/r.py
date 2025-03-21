# 函数：根据名称查找节点并返回代码片段
def find_code_by_name(node, name):
    # 查找函数、方法或类定义
    if node.type in ['call', 'binary_operator', 'argument']:
        identifiers = [child for child in node.children]
        set_class_flag = 0
        for identifier in identifiers:
            if node.type == 'call':
                if identifier.text.decode('utf8') == 'setClass':
                    set_class_flag = 1
                if identifier.type == 'arguments':
                    if set_class_flag == 1 and name in identifier.text.decode('utf8'):
                        return node.text.decode('utf8')
            if node.type == 'binary_operator':
                if identifier.text.decode('utf8') == name:
                    return node.text.decode('utf8')
            if node.type == 'argument':
                if identifier.text.decode('utf8') == name:
                    return node.text.decode('utf8')

    # 递归查找所有子节点
    for child in node.children:
        result = find_code_by_name(child, name)
        if result:
            return result
    return None
