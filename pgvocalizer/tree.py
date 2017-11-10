class TreeNode:
    def __init__(self, val="", parent=None):
        self.children = []
        self.data = str(val)
        self.parent = parent

    def add_child(self, val=""):
        child = TreeNode(val, self)
        self.children.append(child)
        return child
