import ast
from re import match
from numpy import arange, dtype
from collections import ChainMap

# Tree for parameter dependencies
class Tree(object):
    def __init__(self, name = None, expr = "", value = None, branches = None):
        self.name = name
        self.expr = expr
        self.value = value
        self.branches = [] if branches == None else branches

    @staticmethod
    def find_dependent_names(node):
        expr = node.expr
        dependents = []
        try:
            value = float(expr)
            node.value = value
        except ValueError:
            # Get variable names in expression
            names = []
            class GetNames(ast.NodeVisitor):
                def generic_visit(self, node):
                    if type(node).__name__ == "Name":
                        dependents.append(node.id)
                    ast.NodeVisitor.generic_visit(self, node)
            parsed = ast.parse(expr)
            ast.dump(parsed)
            GetNames().visit(parsed)
        return dependents

    # Recursively build dependencies tree for an entry in 
    # parameter dictionary
    @staticmethod
    def build_tree(p, parameters, dict_nodes, parent = "head"):
        # Create new node, attach to the head if no parent
        node = Tree(name = p, expr = parameters[p])
        if parent == "head":
            dict_nodes["head"].branches.append(node)
        # Add the node to the dictionary
        dict_nodes[p] = node
        # Find dependent parameters
        dependents = Tree.find_dependent_names(node)
        # If dependents, iterate recursively
        for d in dependents:
            # If d already in the tree, adjust the branch
            if d in dict_nodes:
                d_node = dict_nodes[d]
                # If d is attached to the head, remove link
                if d_node in dict_nodes["head"].branches:
                    dict_nodes["head"].branches.remove(d_node)
                # Update list for initial node
                node.branches.append(d_node)
            else:
                # If d not in the tree already, create new node
                node.branches.append(Tree.build_tree(d, parameters, 
                                                dict_nodes, parent = p))
        return node

    # Create dependencies tree from a parameter dictionary
    @staticmethod
    def tree_from_dict(parameters):
        param_tree = Tree(name = "head")
        dict_nodes = {}
        dict_nodes["head"] = param_tree
        for p in parameters:
            if p not in dict_nodes:
                Tree.build_tree(p, parameters, dict_nodes)
        return dict_nodes["head"]

    # Walk the tree and resolve dependencies
    def resolve_dependencies(self, value_dict = None):
        # Initialize dictionary
        if value_dict == None:
            value_dict = {}
        # Looks for value in dictionary (no multiple evaluations)
        if self.value != None:
            value_dict[self.name] = self.value
            return self.value, value_dict
        else:
            expr = self.expr
            for b in self.branches:
                expr = expr.replace(b.name, 
                                    str(b.resolve_dependencies(value_dict)[0]))
            # "Safely" evaluate arithmetic expression
            # You can still wreck the CPU but only 
            # numerical values and common operators are
            # allowed in the final expression
            if self.name != "head": 
                self.value = eval(expr)
                # Put value in dictionary
                value_dict[self.name] = self.value
            return self.value, value_dict
        return None

    # Convert all the expressions in parameter dict
    @staticmethod
    def convert_parameters(parameters):
        tree = Tree.tree_from_dict(parameters)
        return tree.resolve_dependencies()[1]
        

# Takes the input for each parameter name and returns
# a list of values
def make_list(yaml_arg):
    # If list, just return the value
    if isinstance(yaml_arg, list):
        return yaml_arg
    # If range, find intermediate values
    yaml_arg = str(yaml_arg).strip()
    range_pattern = r"[0-9.]*--[0-9.]*\s*[0-9.]*"
    if match(range_pattern, yaml_arg):
        bounds, step = yaml_arg.split()
        step = float(step)
        vmin, vmax = map(float, bounds.split('--'))
        vlist = list(arange(vmin, vmax, step)) + [vmax]
        return vlist
    # If not list, return list with 1 number or expression
    return [yaml_arg]


# If a formula is given instead of a number, evaluate
def convert_value(key, parameters):
    expr = parameters[key]
    try:
        return float(expr)
    except ValueError:
        # Get variable names in expression
        names = []
        class GetNames(ast.NodeVisitor):
            def generic_visit(self, node):
                if type(node).__name__ == "Name":
                    names.append(node.id)
                ast.NodeVisitor.generic_visit(self, node)
        parsed = ast.parse(expr)
        ast.dump(parsed)
        GetNames().visit(parsed)
        # Replace names by values
        for n in names:
            expr = expr.replace(n, str(parameters[n]))
        return "%.2f" % eval(expr)
    return None
