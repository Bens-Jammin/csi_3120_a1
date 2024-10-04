from operator import contains
import os
from typing import Union, List, Optional

alphabet_chars = list("abcdefghijklmnopqrstuvwxyz") + list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
numeric_chars = list("0123456789")
var_chars = alphabet_chars + numeric_chars
all_valid_chars = var_chars + ["(", ")", ".", "\\"]
valid_examples_fp = "./valid_examples.txt"
invalid_examples_fp = "./invalid_examples.txt"


def read_lines_from_txt(fp: list[str, os.PathLike]) -> List[str]:
    """
    :param fp: File path of the .txt file.
    :return: The lines of the file path removing trailing whitespaces
    and newline characters.
    """
    
    with open(fp) as file:
        lines = [line.rstrip() for line in file]
        file.close()
    
    return lines

def is_valid_var_name(s: str) -> bool:
    """
    :param s: Candidate input variable name
    :return: True if the variable name starts with a character,
    and contains only characters and digits. Returns False otherwise.
    """

    if not alphabet_chars.__contains__(s[0]):
        print(f"SYNTAX ERROR: variables must start with a letter")

        return False
    
    for char in s:
        if not var_chars.__contains__(char):
            print(f"SYNTAX ERROR: variables cannot contain the character '{char}'")
            return False

    return True



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

    def print_tree(self, node: Optional[Node] = None, level: int = 0) -> None: #Using preorder traversal
        # TODO COMPLETE

        if node is None: 
            node = self.root

        indent = "----"*level
        print(indent + '_'.join(node.elem))

        level += 1
        for child in node.children: 
            self.print_tree(child, level)



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
    for idx,char in enumerate(s[::-1]):  # iter from right --> left
        if char == '.':
            dot_op = True
        if char == '\\':
            dot_op = False
    if dot_op == True:
        print(f"SYNTAX ERROR: dot operators must occur AFTER a lambda expression")
        return False
            
    # makes sure that if there is a dot operator, it has a variable beside it
    reversed_str = s[::-1]
    for (idx, char) in enumerate(reversed_str):
        if char == ".":
            if idx + 1 < len(s) and not var_chars.__contains__(reversed_str[idx+1]):
                print("SYNTAX ERROR: need a variable before a dot operator.")
                return False
    
    s = convert_dot_to_brackets(s_) 
    
    if not valid_brackets(s_):
        return False
    
    
    s = s.replace("_", " ")
    s = s.replace("  ", " ")
    s = add_correct_spacing(s=s)
    
    temp = s.split(" ")
    # next make sure any variables are valid
    for potential_var in s.split(' '):
        if ("(" in potential_var) or (")" in potential_var) or ("." in potential_var) or ("\\" in potential_var):
            continue
       
        # sometimes if you split between two spaces, it adds an empty string into the split
        if potential_var == "":
            continue
            
        if not is_valid_var_name(potential_var):
            return False
        
    # make sure lambda expressions are valid
    if not valid_lambda_expr(s_):
        return False
    
    # now that none of the rules are broken, we can begin
    # to parse the actual string into the tokens
    return parse(s)
    

#   ======================
#   BEGIN CUSTOM FUNCTIONS
#   ======================



def add_correct_spacing(s: str) -> str:
    """
    the parse_str function doesnt work for examples such as:
    a \\x(x b)
    because it parses "\\x(x" into one token. This function stops that from happening 
    """
    result = ""
    
    for idx, char in enumerate(s):
        if (char == "\\" or char == "(" or char == ")"):
            if (idx - 1 >= 0) and (s[idx - 1] != " "):
                result += " "      

        result += char

        if (char == "\\" or char == "(" or char == ")"):
            if (idx + 1 < len(s)) and (s[idx + 1] != " "):
                result += " "

    return result


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
            
    # add any remaining variable tokens that were parsed 
    if len(variable) > 0:
        tokens.append(variable)
    
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
            # spaces or brackets not allowed immediately after a slash
            if idx+1 < len(s) and (s[idx+1] == ' ' or s[idx+1] == '('):
                print(f"SYNTAX ERROR: spaces or brackets not allowed immediately after a lambda (index {idx})")
                return False    
        
        if char == ' ':
            # make sure there's another expression after the lambda token
            if all_valid_chars.__contains__(s[idx+1]):
                in_lambda_expr = False
            
        
    return not in_lambda_expr

    
def valid_brackets(s: str) -> bool:    
    """
    returns true if the string has valid bracket syntax
    :param s_: the input string
    """
    bracket_count = 0
    for (idx,char) in enumerate(s):
        if char == '(':
            bracket_count += 1
            
            if idx + 1 < len(s) and s[idx+1] != '(':
                next_char = s[idx+1]
                # expression missing from the brackets
                if next_char == ' ' or next_char == ')':
                    print(f"SYNTAX ERROR: expression missing inside brackets (index {idx})")
                    return False
            
        if char == ')':
            bracket_count -= 1
        
        # bracket count can only be negative if a close bracket
        # appears before an opening
        if bracket_count < 0:
            print(f"SYNTAX ERROR: brackets are mismatched.")


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
    else:
        print(f"{len(valid_lines)} of {len(lines)} lines were correct")

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

    Example Input: ["\\", "x", "(", "x", "za", ")"]
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
    if node is None: 
        node = Node(tokens[:]) # Create root node

    while tokens:
        token = tokens.pop(0)

        if token == "(": 

            closingBracketIndex = findClosingBracket(tokens)

            exprString = ["("] + tokens[:closingBracketIndex + 1] # getting '(' <expr> ')'

            exprNode = Node(exprString)
            node.add_child_node(exprNode)

            exprNode.add_child_node(Node(["("]))

            subExprNode = Node(exprString[1:-1])
            exprNode.add_child_node(subExprNode)

            exprNode.add_child_node(Node([")"]))

            # if the subexpression node contains just a var, stop exploring
            if not len(subExprNode.elem) == 1: 
                
                build_parse_tree_rec(tokens[:closingBracketIndex], subExprNode) #Evaluates expr in '('<expr>')'
            
            # remove anything from tokens that we just parsed
            tokens = tokens[closingBracketIndex + 1:] 

        else: 
            node.add_child_node(Node([token])) # '\' or <var> into child node
    return node


def findClosingBracket(tokens: List[str]) -> int:

    stack = ["("] # THIS IS IMPORTANT: since the first "(" will have been popped when we call this function

    for index, token in enumerate(tokens):
        if token == "(": 
            stack.append(index)

        elif token == ")": 
            if stack:
                stack.pop()
                if not stack: # If stack is now empty, we've found corresponding closed bracket
                    return index
    return -1 # Closing bracket does not exist

def build_parse_tree(tokens: List[str]) -> ParseTree:
    """
    Build a parse tree from a list of tokens
    :param tokens: List of tokens
    :return: parse tree
    """
    pt = ParseTree(build_parse_tree_rec(tokens))
    return pt


if __name__ == "__main__":

#   ===========================
#   BEGIN TESTING OF PARSE TREE
#   ===========================
    
    testTokens1 = ["\\", "x", "(", "x", "za", ")"]
    testTokens2 = "(_a_)_(_b_)_(_c_)_(_d_)".split("_")
    testTokens3 = ['(', 'a', ')', '(', 'b', ')', '(', '\\', 'x', '(', 'x', 'b', ')', ')', '(', '\\', 'x', '(', 'x', 'yz', ')', ')']
    parseTree = build_parse_tree(testTokens3)
    parseTree.print_tree()

#   ===========================
#   END TESTING OF PARSE TREE
#   ===========================


    print("\n\nChecking valid examples...")
    read_lines_from_txt_check_validity(valid_examples_fp)
    read_lines_from_txt_output_parse_tree(valid_examples_fp)

    print("Checking invalid examples...")
    read_lines_from_txt_check_validity(invalid_examples_fp)

    # # Optional
    # print("\n\nAssociation Examples:")
    # sample = ["a", "b", "c"]
    # print("Right association")
    # associated_sample_r = add_associativity(sample, association_type="right")
    # print(associated_sample_r)
    # print("Left association")
    # associated_sample_l = add_associativity(sample, association_type="left")
    # print(associated_sample_l)