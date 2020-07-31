'''via https://github.com/madrury/roguelike
'''

class Root:
    """The root node of a behaviour tree holds the namespace for the entire
    operation.
    """
    def __init__(self, child, namespace=None):
        if namespace is None:
            namespace = {}
        self.namespace = namespace
        self.child = child
        self.child.parent = self

    def tick(self, owner, game_map):
        self.namespace["decision_path"] = []
        return self.child.tick(owner, game_map)


class Node:
    """A mixin for all the nodes in a behaviour tree *except* the root node.
    Delegates namespace lookups to parent nodes.
    """
    @property
    def namespace(self):
        return self.parent.namespace

    def tick(self, owner, game_map):
        #print(self.__class__.__name__)
        self.namespace["decision_path"].append(self.__class__.__name__)
