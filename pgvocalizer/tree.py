class TreeNode:
    def __init__(self, val="", parent=None):
        self.child = []
        self.data = str(val)
        self.parent = parent

    def set_data(self, val):
        self.data = str(val)

    def add_child(self, val=""):
        child = TreeNode(val, self)
        self.child.append(child)
        return child
