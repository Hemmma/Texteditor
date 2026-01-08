"""
Lab3新增: 树形结构显示模块
使用适配器模式(Adapter Pattern)统一不同数据结构的树形显示
"""


class TreeNode:
    """树节点接口 - 适配器的目标接口"""
    
    def get_label(self) -> str:
        """获取节点显示标签"""
        raise NotImplementedError
    
    def get_children(self) -> list:
        """获取子节点列表"""
        raise NotImplementedError
    
    def has_children(self) -> bool:
        """判断是否有子节点"""
        return len(self.get_children()) > 0


class XmlTreeAdapter(TreeNode):
    """XML元素树适配器"""
    
    def __init__(self, xml_element):
        self.element = xml_element
    
    def get_label(self) -> str:
        """返回格式: "tag [id="xxx", ...]" """
        attrs_str = ", ".join([f'{k}="{v}"' for k, v in self.element.attributes.items()])
        return f"{self.element.tag} [{attrs_str}]"
    
    def get_children(self) -> list:
        """将 xml_element.children 和 text 转换为 TreeNode 列表"""
        children = []
        
        # 如果有文本内容，先添加为子节点
        if self.element.text and self.element.text.strip():
            children.append(XmlTextNode(self.element.text))
        
        # 再添加子元素
        for child in self.element.children:
            children.append(XmlTreeAdapter(child))
        
        return children


class XmlTextNode(TreeNode):
    """XML文本内容节点（叶子节点）"""
    
    def __init__(self, text):
        self.text = text
    
    def get_label(self) -> str:
        return f'"{self.text}"'
    
    def get_children(self) -> list:
        return []


class DirectoryTreeAdapter(TreeNode):
    """目录/文件树适配器"""
    
    def __init__(self, name, children_dict=None):
        self.name = name
        self.children_dict = children_dict or {}
    
    def get_label(self) -> str:
        return self.name
    
    def get_children(self) -> list:
        """将 children_dict 转换为 DirectoryTreeAdapter 列表"""
        children = []
        for name, sub_dict in self.children_dict.items():
            children.append(DirectoryTreeAdapter(name, sub_dict))
        return children


class TreeRenderer:
    """统一的树形结构渲染器"""
    
    @staticmethod
    def render(node: TreeNode, prefix="", is_last=True) -> list:
        """
        渲染树形结构
        返回: 字符串列表，每个元素是一行输出
        """
        lines = []
        connector = "└── " if is_last else "├── "
        lines.append(prefix + connector + node.get_label())
        
        children = node.get_children()
        extension = "    " if is_last else "│   "
        new_prefix = prefix + extension
        
        for i, child in enumerate(children):
            child_is_last = (i == len(children) - 1)
            lines.extend(TreeRenderer.render(child, new_prefix, child_is_last))
        
        return lines
