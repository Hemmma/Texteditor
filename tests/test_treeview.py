"""
Lab3新增: 树形结构显示模块单元测试
测试适配器模式实现的统一树形结构渲染
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import TreeView
import XmlEditor


class TestTreeNode(unittest.TestCase):
    """测试TreeNode接口"""
    
    def test_tree_node_interface(self):
        """测试TreeNode接口方法"""
        node = TreeView.TreeNode()
        with self.assertRaises(NotImplementedError):
            node.get_label()
        with self.assertRaises(NotImplementedError):
            node.get_children()


class TestXmlTreeAdapter(unittest.TestCase):
    """测试XmlTreeAdapter适配器"""
    
    def setUp(self):
        """准备测试数据"""
        self.root = XmlEditor.XmlElement('root', {'id': 'root1', 'type': 'main'})
        self.child1 = XmlEditor.XmlElement('child', {'id': 'child1'})
        self.child2 = XmlEditor.XmlElement('child', {'id': 'child2'}, 'Some text')
        self.root.add_child(self.child1)
        self.root.add_child(self.child2)
    
    def test_get_label(self):
        """测试获取XML元素标签"""
        adapter = TreeView.XmlTreeAdapter(self.root)
        label = adapter.get_label()
        self.assertEqual(label, 'root [id="root1", type="main"]')
    
    def test_get_label_no_attributes(self):
        """测试没有属性的XML元素"""
        element = XmlEditor.XmlElement('simple', {})
        adapter = TreeView.XmlTreeAdapter(element)
        label = adapter.get_label()
        self.assertEqual(label, 'simple []')
    
    def test_get_children_without_text(self):
        """测试获取子节点（无文本）"""
        adapter = TreeView.XmlTreeAdapter(self.root)
        children = adapter.get_children()
        self.assertEqual(len(children), 2)
        self.assertIsInstance(children[0], TreeView.XmlTreeAdapter)
        self.assertIsInstance(children[1], TreeView.XmlTreeAdapter)
    
    def test_get_children_with_text(self):
        """测试获取子节点（包含文本）"""
        adapter = TreeView.XmlTreeAdapter(self.child2)
        children = adapter.get_children()
        self.assertEqual(len(children), 1)
        self.assertIsInstance(children[0], TreeView.XmlTextNode)
        self.assertEqual(children[0].get_label(), '"Some text"')
    
    def test_has_children(self):
        """测试是否有子节点"""
        adapter = TreeView.XmlTreeAdapter(self.root)
        self.assertTrue(adapter.has_children())
        
        leaf_adapter = TreeView.XmlTreeAdapter(self.child1)
        self.assertFalse(leaf_adapter.has_children())


class TestXmlTextNode(unittest.TestCase):
    """测试XmlTextNode"""
    
    def test_get_label(self):
        """测试文本节点标签"""
        text_node = TreeView.XmlTextNode("Hello World")
        self.assertEqual(text_node.get_label(), '"Hello World"')
    
    def test_get_children(self):
        """测试文本节点无子节点"""
        text_node = TreeView.XmlTextNode("text")
        self.assertEqual(len(text_node.get_children()), 0)
    
    def test_has_children(self):
        """测试文本节点无子节点"""
        text_node = TreeView.XmlTextNode("text")
        self.assertFalse(text_node.has_children())


class TestDirectoryTreeAdapter(unittest.TestCase):
    """测试DirectoryTreeAdapter适配器"""
    
    def test_get_label(self):
        """测试获取目录标签"""
        adapter = TreeView.DirectoryTreeAdapter("folder")
        self.assertEqual(adapter.get_label(), "folder")
    
    def test_get_children_empty(self):
        """测试空目录"""
        adapter = TreeView.DirectoryTreeAdapter("empty", {})
        self.assertEqual(len(adapter.get_children()), 0)
        self.assertFalse(adapter.has_children())
    
    def test_get_children_with_subdirs(self):
        """测试有子目录的目录"""
        tree = {
            "subdir1": {},
            "subdir2": {"file.txt": {}}
        }
        adapter = TreeView.DirectoryTreeAdapter("parent", tree)
        children = adapter.get_children()
        self.assertEqual(len(children), 2)
        self.assertIsInstance(children[0], TreeView.DirectoryTreeAdapter)
        self.assertIsInstance(children[1], TreeView.DirectoryTreeAdapter)
    
    def test_has_children(self):
        """测试是否有子节点"""
        tree = {"subdir": {}}
        adapter = TreeView.DirectoryTreeAdapter("parent", tree)
        self.assertTrue(adapter.has_children())


class TestTreeRenderer(unittest.TestCase):
    """测试TreeRenderer渲染器"""
    
    def test_render_single_node(self):
        """测试渲染单节点"""
        element = XmlEditor.XmlElement('root', {'id': 'r1'})
        adapter = TreeView.XmlTreeAdapter(element)
        lines = TreeView.TreeRenderer.render(adapter, prefix="", is_last=True)
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], '└── root [id="r1"]')
    
    def test_render_with_children(self):
        """测试渲染带子节点的树"""
        root = XmlEditor.XmlElement('root', {'id': 'r1'})
        child1 = XmlEditor.XmlElement('child1', {'id': 'c1'})
        child2 = XmlEditor.XmlElement('child2', {'id': 'c2'})
        root.add_child(child1)
        root.add_child(child2)
        
        adapter = TreeView.XmlTreeAdapter(root)
        lines = TreeView.TreeRenderer.render(adapter, prefix="", is_last=True)
        
        self.assertEqual(len(lines), 3)
        self.assertTrue(lines[0].endswith('root [id="r1"]'))
        self.assertTrue(lines[1].endswith('child1 [id="c1"]'))
        self.assertTrue(lines[2].endswith('child2 [id="c2"]'))
        
        # 验证树形连接符
        self.assertIn('├── ', lines[1])
        self.assertIn('└── ', lines[2])
    
    def test_render_with_text(self):
        """测试渲染包含文本的XML元素"""
        element = XmlEditor.XmlElement('node', {'id': 'n1'}, 'Text content')
        adapter = TreeView.XmlTreeAdapter(element)
        lines = TreeView.TreeRenderer.render(adapter, prefix="", is_last=True)
        
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[0].endswith('node [id="n1"]'))
        self.assertTrue(lines[1].endswith('"Text content"'))
        self.assertIn('└── ', lines[1])
    
    def test_render_directory_tree(self):
        """测试渲染目录树"""
        tree = {
            "folder1": {"file1.txt": {}},
            "folder2": {}
        }
        root = TreeView.DirectoryTreeAdapter(".", tree)
        lines = TreeView.TreeRenderer.render(root, prefix="", is_last=True)
        
        self.assertEqual(len(lines), 4)
        self.assertTrue(lines[0].endswith('.'))
        # folder1 和 folder2 的顺序可能不确定（字典遍历）
        self.assertTrue(any('folder1' in line for line in lines))
        self.assertTrue(any('folder2' in line for line in lines))
        self.assertTrue(any('file1.txt' in line for line in lines))
    
    def test_render_deep_nesting(self):
        """测试深层嵌套结构"""
        root = XmlEditor.XmlElement('root', {'id': 'r1'})
        level1 = XmlEditor.XmlElement('level1', {'id': 'l1'})
        level2 = XmlEditor.XmlElement('level2', {'id': 'l2'})
        level3 = XmlEditor.XmlElement('level3', {'id': 'l3'})
        
        root.add_child(level1)
        level1.add_child(level2)
        level2.add_child(level3)
        
        adapter = TreeView.XmlTreeAdapter(root)
        lines = TreeView.TreeRenderer.render(adapter, prefix="", is_last=True)
        
        self.assertEqual(len(lines), 4)
        # 验证缩进
        self.assertTrue(lines[0].startswith('└── '))
        self.assertTrue(lines[1].startswith('    └── '))
        self.assertTrue(lines[2].startswith('        └── '))
        self.assertTrue(lines[3].startswith('            └── '))
    
    def test_render_with_prefix(self):
        """测试带前缀的渲染"""
        element = XmlEditor.XmlElement('node', {'id': 'n1'})
        adapter = TreeView.XmlTreeAdapter(element)
        lines = TreeView.TreeRenderer.render(adapter, prefix="    ", is_last=True)
        
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].startswith('    └── '))
    
    def test_render_mixed_last_positions(self):
        """测试混合位置的渲染（非最后节点）"""
        root = XmlEditor.XmlElement('root', {'id': 'r1'})
        child1 = XmlEditor.XmlElement('child1', {'id': 'c1'})
        child2 = XmlEditor.XmlElement('child2', {'id': 'c2'})
        child3 = XmlEditor.XmlElement('child3', {'id': 'c3'})
        root.add_child(child1)
        root.add_child(child2)
        root.add_child(child3)
        
        adapter = TreeView.XmlTreeAdapter(root)
        lines = TreeView.TreeRenderer.render(adapter, prefix="", is_last=True)
        
        # 验证连接符使用
        self.assertIn('├── ', lines[1])  # 第一个子节点
        self.assertIn('├── ', lines[2])  # 第二个子节点
        self.assertIn('└── ', lines[3])  # 最后一个子节点
    
    def test_render_empty_tree(self):
        """测试空树"""
        tree = {}
        root = TreeView.DirectoryTreeAdapter("empty", tree)
        lines = TreeView.TreeRenderer.render(root, prefix="", is_last=True)
        
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], '└── empty')


class TestIntegration(unittest.TestCase):
    """集成测试：验证适配器模式的完整工作流"""
    
    def test_xml_tree_consistency(self):
        """测试XML树显示的一致性"""
        # 构建一个完整的XML树
        root = XmlEditor.XmlElement('bookstore', {'version': '1.0'})
        book1 = XmlEditor.XmlElement('book', {'id': 'b1', 'category': 'fiction'})
        title1 = XmlEditor.XmlElement('title', {}, 'The Great Gatsby')
        author1 = XmlEditor.XmlElement('author', {}, 'F. Scott Fitzgerald')
        book1.add_child(title1)
        book1.add_child(author1)
        
        book2 = XmlEditor.XmlElement('book', {'id': 'b2', 'category': 'tech'})
        title2 = XmlEditor.XmlElement('title', {}, 'Clean Code')
        book2.add_child(title2)
        
        root.add_child(book1)
        root.add_child(book2)
        
        # 渲染树
        adapter = TreeView.XmlTreeAdapter(root)
        lines = TreeView.TreeRenderer.render(adapter, prefix="", is_last=True)
        
        # 验证结构
        self.assertGreater(len(lines), 5)
        self.assertTrue(lines[0].endswith('bookstore [version="1.0"]'))
        
        # 验证包含所有元素
        all_text = '\n'.join(lines)
        self.assertIn('book', all_text)
        self.assertIn('title', all_text)
        self.assertIn('author', all_text)
        self.assertIn('The Great Gatsby', all_text)
        self.assertIn('F. Scott Fitzgerald', all_text)
    
    def test_directory_tree_consistency(self):
        """测试目录树显示的一致性"""
        tree = {
            "src": {
                "main": {
                    "java": {}
                },
                "test": {}
            },
            "docs": {
                "README.md": {}
            }
        }
        
        root = TreeView.DirectoryTreeAdapter("project", tree)
        lines = TreeView.TreeRenderer.render(root, prefix="", is_last=True)
        
        # 验证结构
        self.assertGreater(len(lines), 3)
        all_text = '\n'.join(lines)
        self.assertIn('project', all_text)
        self.assertIn('src', all_text)
        self.assertIn('docs', all_text)


if __name__ == '__main__':
    unittest.main()
