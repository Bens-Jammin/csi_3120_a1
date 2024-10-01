from operator import contains
import os
from typing import Union, List, Optional

alphabet_chars = list("abcdefghijklmnopqrstuvwxyz") + list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
numeric_chars = list("0123456789")
var_chars = alphabet_chars + numeric_chars
all_valid_chars = var_chars + ["(", ")", ".", "\\"]
valid_examples_fp = "./valid_examples.txt"
invalid_examples_fp = "./invalid_examples.txt"


def read_lines_from_txt(fp: [str, os.PathLike]) -> List[str]:
    """
    :param fp: File path of the .txt file.
    :return: The lines of the file path removing trailing whitespaces
    and newline characters.
    """
    
    with open(fp) as file:
        lines = [line.rstrip() for line in file]
        file.close()
    
    return 

def is_valid_var_name(s: str) -> bool:
    """
    :param s: Candidate input variable name
    :return: True if the variable name starts with a character,
    and contains only characters and digits. Returns False otherwise.
    """
    # TODO

    if s[0] in alphabet_chars and all(char in var_chars for char in s): 
        return True

    return False



class Node:
    """
    Nodes in a parse tree
    Attributes:
        elem: a list of strings
        children: a list of child nodes
    """
    def __init__(self, elem: List[str] = None):
        self.elem = elem
        self.children = []


    def add_child_node(self, node: 'Node') -> None:
        self.children.append(node)


class ParseTree:
    """
    A full parse tree, with nodes
    Attributes:
        root: the root of the tree
    """
    def __init__(self, root):
        self.root = root

    def print_tree(self, node: Optional[Node] = None, level: int = 0) -> None:
        # TODO
        print("")



def parse_tokens(s_: str, association_type: Optional[str] = None) -> Union[List[str], bool]:
    """
    Gets the final tokens for valid strings as a list of strings, only for valid syntax,
    where tokens are (no whitespace included)
    \\ values for lambdas
    valid variable names
    opening and closing parenthesis
    Note that dots are replaced with corresponding parenthesis
    :param s_: the input string
    :param association_type: If not None, add brackets to make expressions non-ambiguous
    :return: A List of tokens (strings) if a valid input, otherwise False
    """

    s = s_[:]  #  Don't modify the original input string
    
    # make sure any dot operators happen AFTER a lambda expression
    dot_op = False
    for char in s[::-1]:  # iter from right --> left
        if char == '.':
            dot_op = True
        if char == '\\':
            dot_op = False
    if dot_op == True:
        print("[DEBUG] dot operation is wrong in '{}'".format(s))
        return False
            
    
    s = convert_dot_to_brackets(s_) 
    
    if valid_brackets(s_) == False:
        print("[DEBUG] brackets are wrong in '{}'".format(s))
        return False
    
    # next make sure any variables are valid
    for potential_var in s_.split(' '):
        if potential_var in ['(', ')', '.', '\\']:
            continue
        
        if not is_valid_var_name(potential_var):
            print("[DEBUG] variable names are wrong in '{}'".format(s))
            return False
        
    # make sure lambda expressions are valid
    if not valid_lambda_expr(s_):
        print("[DEBUG] lambda expressions are wrong in '{}'".format(s))
        return False
    
    print("[DEBUG] '{}' is valid expr".format(s))
    # now that none of the rules are broken, we can begin
    # to parse the actual string into the tokens
    return parse(s)
    

#   ======================
#   BEGIN CUSTOM FUNCTIONS
#   ======================


def parse(s) -> list[str]:
    """ 
    converts the string itself into the list of tokens
    """
    tokens = []
    variable = ""
    for char in s:
        if char in ['(', ')', '.', '\\']:
            tokens.append(char)
        if char in alphabet_chars:
            variable += char
        if char == ' ' and len(variable) != 0:
            tokens.append(variable)
            variable = ""
    
    return tokens


def convert_dot_to_brackets(s: str) -> str:
    """ 
    checks to see if there are any dot operators,
    if there are, it converts it to the equivalent expression
    with brackets
    """
    s = s[::-1]
    
    modified_string = ""
    
    for char in s:
        if char == '.':
            modified_string = ''.join((')', modified_string))
            modified_string += '( '
        else:
            modified_string += char
    
    modified_string = modified_string[::-1]
    
    return modified_string


def valid_lambda_expr(s) -> bool:
    """ 
    given the string s, determines if any lambda expressions in it are valid
    """
    in_lambda_expr = False
    for idx, char in enumerate(s):
        if char == '\\':
            in_lambda_expr = True
        
        if char == ' ':
            # make sure there's something else after the space
            if alphabet_chars.contains(s[idx+1]):
                in_lambda_expr = False
            
        
        
    return in_lambda_expr == False

    
def valid_brackets(s: str) -> bool:    
    """
    returns true if the string has valid bracket syntax
    :param s_: the input string
    """
    bracket_count = 0
    for char in s:
        if char == '(':
            bracket_count += 1
        if char == ')':
            bracket_count -= 1
            if bracket_count == -1:
                return False 

    return bracket_count == 0


#   ====================
#   END CUSTOM FUNCTIONS
#   ====================

def read_lines_from_txt_check_validity(fp: [str, os.PathLike]) -> None:
    """
    Reads each line from a .txt file, and then
    parses each string  to yield a tokenized list of strings for printing, joined by _ characters
    In the case of a non-valid line, the corresponding error message is printed (not necessarily within
    this function, but possibly within the parse_tokens function).
    :param lines: The file path of the lines to parse
    """
    lines = read_lines_from_txt(fp)
    valid_lines = []
    for l in lines:
        tokens = parse_tokens(l)
        if tokens:
            valid_lines.append(l)
            print(f"The tokenized string for input string {l} is {'_'.join(tokens)}")
    if len(valid_lines) == len(lines):
        print(f"All lines are valid")

def read_lines_from_txt_output_parse_tree(fp: [str, os.PathLike]) -> None:
    """
    Reads each line from a .txt file, and then
    parses each string to yield a tokenized output string, to be used in constructing a parse tree. The
    parse tree should call print_tree() to print its content to the console.
    In the case of a non-valid line, the corresponding error message is printed (not necessarily within
    this function, but possibly within the parse_tokens function).
    :param fp: The file path of the lines to parse
    """
    lines = read_lines_from_txt(fp)
    for l in lines:
        tokens = parse_tokens(l)
        if tokens:
            print("\n")
            parse_tree2 = build_parse_tree(tokens)
            parse_tree2.print_tree()


def add_associativity(s_: List[str], association_type: str = "left") -> List[str]:
    """
    :param s_: A list of string tokens
    :param association_type: a string in [`left`, `right`]
    :return: List of strings, with added parenthesis that disambiguates the original expression
    """

    # TODO Optional
    s = s_[:]  # Don't modify original string
    return []




def build_parse_tree_rec(tokens: List[str], node: Optional[Node] = None) -> Node:
    """

    Example Input: ["\", "x", "(", "x", "za", ")"]
    Expected output: 
    ----\
    ----x
    ----(_x_za_)
    --------(
    --------x_za
    ------------x
    ------------za
    --------)
    An inner recursive inner function to build a parse tree
    :param tokens: A list of token strings
    :param node: A Node object
    :return: a node with children whose tokens are variables, parenthesis, slashes, or the inner part of an expression
    """

    #TODO
    if node is None: 
        node = Node()

    while tokens: # Not sure about this while loop yet
        token = tokens.pop(0)

        if token == "\\": # we have '\' <var> <expr>
            backSlashNode = Node([token])
            node.add_child_node(backSlashNode) # '\' into a child node.
            varNode = Node([tokens.pop(0)])
            node.add_child_node(varNode) # <var> into a child node
            exprNode = Node([tokens])
            node.add_child_node(exprNode) # <expr> into a child node
            build_parse_tree_rec(tokens, exprNode) # recusively calling our tree builder on the <expr> child node


        elif token == "(": 
            openBracketNode = Node(["("])
            node.add_child_node(openBracketNode)

            subExprNode = Node(tokens)
            node.add_child_node(subExprNode)

            closedBracketNode = Node([")"])
            node.add_child_node(closedBracketNode)

            build_parse_tree_rec(tokens, subExprNode)

        elif token == ")":
            return node # Terminate and retrun the evaluation of the sub expression

        else: 
            node.add_child_node(Node[token]) # <var> into child node


    return Node()



def build_parse_tree(tokens: List[str]) -> ParseTree:
    """
    Build a parse tree from a list of tokens
    :param tokens: List of tokens
    :return: parse tree
    """
    pt = ParseTree(build_parse_tree_rec(tokens))
    return pt


if __name__ == "__main__":

    examples = [
        "\\x. x y z", 
        "\\x. \\x. x y z",
        "(A B)",
        "abc",
        "a (b c)"
    ]
    for x in examples:
        print(parse_tokens(x))


    print("\n\nChecking valid examples...")
# read_lines_from_txt_check_validity(valid_examples_fp)
#     read_lines_from_txt_output_parse_tree(valid_examples_fp)

#     print("Checking invalid examples...")
#     read_lines_from_txt_check_validity(invalid_examples_fp)

#     # Optional
#     print("\n\nAssociation Examples:")
#     sample = ["a", "b", "c"]
#     print("Right association")
#     associated_sample_r = add_associativity(sample, association_type="right")
#     print(associated_sample_r)
#     print("Left association")
#     associated_sample_l = add_associativity(sample, association_type="left")
#     print(associated_sample_l)