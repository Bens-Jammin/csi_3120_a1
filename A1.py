from operator import contains
import os
from typing import Union, List, Optional
from xml.etree.ElementTree import QName

alphabet_chars = list("abcdefghijklmnopqrstuvwxyz") + list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
numeric_chars = list("0123456789")
var_chars = alphabet_chars + numeric_chars
all_valid_chars = var_chars + ["(", ")", ".", "\\"]
valid_examples_fp = "./valid_examples.txt"
invalid_examples_fp = "./invalid_examples.txt"
extra_valid_example_fp = "./extra_valid_examples.txt"


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

def is_valid_var_name(s: str) -> tuple[bool, str]:
    """
    :param s: Candidate input variable name
    :return: True if the variable name starts with a character,
    and contains only characters and digits. Returns False otherwise.
    """

    if not alphabet_chars.__contains__(s[0]):
        return (False, f"SYNTAX ERROR: variables must start with a letter")
    
    for char in s:
        if not var_chars.__contains__(char):
            return (False, f"SYNTAX ERROR: variables cannot contain the character '{char}'")

    return (True, "")



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
    
    (valid, msg) = valid_syntax(s) 
    if not valid:
        print(msg)
        return False
    
    show_ambiguity = association_type is not None
    
    if association_type == "right":
        tokens = parse_expr(s, show_ambiguity)[::-1]
        return mirror_brackets(tokens)
    else:
        return parse_expr(s, show_ambiguity)

#   ======================
#   BEGIN CUSTOM FUNCTIONS
#   ======================


def parse_expr(s: str, show_ambiguity: bool = False) -> list[str]:
    """ 
    converts the string itself into the list of tokens
    """
    # some cases where there would be " <expr>", which makes
    # the program think theres two exprs
    s = s.strip()
    tokens = []
    
    if show_ambiguity: tokens.append("(")

    # case 1 : <expr> ::= '(' <expr> ')'
    # case 2 : <expr> ::= '\' <var> <expr> 
    if s[0] == '\\':
        var_end_idx = end_idx_of_var(s[1:]);
        # note: array indexing has an inclusive start
        # but an exclusive end
        var_str =  s[1:var_end_idx+1]
        expr_str = s[var_end_idx+1:]
        tokens.extend("\\")
        tokens.extend(var_str)
        tokens.extend(parse_expr(expr_str, show_ambiguity))
    # checks if this is either the only bracketed expr OR theres nested brackets
    elif (s[0] == '(' and ") " not in s) or (s.__contains__('(') and s.__contains__(')') and valid_syntax(s[1:-1])[0] ):
        closing_bracket_idx = find_closing_bracket(s)
        tokens.extend('(')
        tokens.extend( parse_expr(s[1:closing_bracket_idx], show_ambiguity) )
        tokens.extend(')')
    # case 3 : <expr> ::= <var>
    elif len(s.split(' ')) > 1:
        # if this expression is two '(<expr>)'s
        # split at the end of the first bracket expr
        if s[0] == '(' and s[-1] == ')':
            # re-add end bracket because the split() method
            # excludes the bracket for `expr1`
            expr1 = (s.split(") ", 1))[0] + ")"
            expr2 = (s.split(") ", 1))[1]
            tokens.extend( parse_expr(expr1) )
            tokens.extend( parse_expr(expr2) )
        else:
            expr1 = (s.split(" ", 1))[0]
            expr2 = (s.split(" ", 1))[1]
            tokens.extend( parse_expr(expr1, show_ambiguity) )
            tokens.extend( parse_expr(expr2, show_ambiguity) )   
    # case 4 : <expr> ::= <expr> <expr>
    elif alphabet_chars.__contains__(s[0]):
        # 'extend' takes an iterable as the argument, so if you give it a whole string,
        # itll split the string into its characters.
        # by giving it a list of a string, it just puts the whole string in as one object
        tokens.extend([s])


    if show_ambiguity: tokens.append(")")
    
    return tokens


def mirror_brackets(s: list[str]) -> list[str]:
    '''
    right associativity is done by flipping the expression, evaluating it as a
    left-associated tree, then reflipping it. Because of the way the brackets are added
    (done for left-associated parsing), the brackets need to be "mirrored" 
    (i.e. opening becomes closed, closed becomes opening) for a right associated parse
    to look correct  
    '''
    r = []
    for char in s:
        if char == "(":
            r.append(")")
        elif char == ")":
            r.append("(")
        else:
            r.append(char) 
    return r
    

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


def end_idx_of_var(s) -> int:
    '''
    given a string s where a variable starts at index 0,
    returns the index of the end of the variable
    example:
    "as(ds)" -> 2
    "mkdsaj (a v)" -> 6
    '''
    for idx, char in enumerate(s):
        if not var_chars.__contains__(char):
            return idx
    
    return len(s)
      

def find_closing_bracket(s) -> int:
    '''
    given a string with an opening bracket at index 0,
    returns the index of the associated closing bracket
    '''
    bracket_number = 0
    for idx, char in enumerate(s):
        if char == '(':
            bracket_number += 1
        elif char == ')':
            bracket_number -= 1
        if bracket_number == 0: 
            return idx
    return -1


def convert_dot_to_brackets(s: str) -> str:
    """ 
    checks to see if there are any dot operators,
    if there are, it converts it to the equivalent expression
    with brackets
    """
    s = s[::-1]
    
    modified_string = ""
    
    # looping over s backwards
    for char in s:
        if char == '.':
            modified_string = ''.join((')', modified_string))
            modified_string += '( '
        else:
            modified_string += char
    
    modified_string = modified_string[::-1]
    
    return modified_string


def valid_lambda_expr(s) -> tuple[bool, str]:
    """ 
    given the string s, determines if any lambda expressions in it are valid
    """
    in_lambda_expr = False
    for idx, char in enumerate(s):
        if char == '\\':
            in_lambda_expr = True
            # spaces or brackets not allowed immediately after a slash
            if idx+1 < len(s) and (s[idx+1] == ' ' or s[idx+1] == '('):
                return (False, f"SYNTAX ERROR: spaces or brackets not allowed immediately after a lambda (index {idx})")
                
        if char == ' ':
            # make sure there's another expression after the lambda token
            if all_valid_chars.__contains__(s[idx+1]):
                in_lambda_expr = False
            
    if not in_lambda_expr:
        return (True, "")
    else:
        return (False, "SYNTAX ERROR: lambda expression syntax is incorrect.")
    
    
def valid_brackets(s: str) -> tuple[bool, str]:    
    """
    returns true if the string has valid bracket syntax
    :param s_: the input string
    """
    s = s.replace(" ", "")
    bracket_count = 0
    for (idx,char) in enumerate(s):
        if char == '(':
            bracket_count += 1
            
            if idx + 1 < len(s) and s[idx+1] != '(':
                next_char = s[idx+1]
                # expression missing from the brackets
                if next_char == ')':
                    return (False, f"SYNTAX ERROR: expression missing inside brackets (index {idx})")
            
        if char == ')':
            bracket_count -= 1
        
        # bracket count can only be negative if a close bracket
        # appears before an opening
        if bracket_count < 0:
            return (False, f"SYNTAX ERROR: brackets are mismatched.")

    if bracket_count != 0:
        return (False, "SYNTAX ERROR: brackets are mismatched.")

    return (True, "")


def valid_syntax(s: str) -> tuple[bool, str]:
    
    (valid, err_msg) = valid_dot_op(s)
    if not valid:
        return (False, err_msg)
    
    modified_s = convert_dot_to_brackets(s) 
    
    (valid, err_msg) = valid_brackets(s)
    if not valid:
        return (False, err_msg)
   
    # standardize the string to make it easier to parse 
    modidifed_s = modified_s.replace("_", " ")
    modidifed_s = modified_s.replace("  ", " ")
    modidifed_s = add_correct_spacing(modified_s)
    
    # next make sure any variables are valid
    for potential_var in s.split(' '):
        if ("(" in potential_var) or (")" in potential_var) or ("." in potential_var) or ("\\" in potential_var):
            continue
       
        # sometimes if you split between two spaces, it adds an empty string into the split
        if potential_var == "":
            continue
            
        (valid, err_msg) = is_valid_var_name(potential_var)
        if not valid:
            return (False, err_msg)
        
    # make sure lambda expressions are valid
    (valid, err_msg) = valid_lambda_expr(s)
    if not valid:
        return (False, err_msg)
    
    return (True, "")


def valid_dot_op(s: str) -> tuple[bool, str]:   
    # make sure any dot operators happen AFTER a lambda expression
    dot_op = False
    for idx,char in enumerate(s[::-1]):  # iter from right --> left
        if char == '.':
            dot_op = True
        if char == '\\':
            dot_op = False
    if dot_op == True:
        return (False, f"SYNTAX ERROR: dot operators must occur AFTER a lambda expression")
            
    # makes sure that if there is a dot operator, it has a variable beside it   x
    reversed_str = s[::-1]
    for (idx, char) in enumerate(reversed_str):
        if char == ".":
            if idx + 1 <= len(s) and not var_chars.__contains__(reversed_str[idx+1]):
                return (False, "SYNTAX ERROR: need a variable before a dot operator.")
                
    return (True, "")


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
        # TODO: adding extra brackets for some reason ?
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
    
    if association_type == "right":
        s = s[::-1]
        s = " ".join(s)
    else:
        s = " ".join(s)
    
    return parse_tokens(s, association_type)




def build_parse_tree_rec(tokens: List[str], node: Optional[Node] = None, isInnerExpression: bool = False) -> Node:
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

        if isInnerExpression and token == '\\':  # in case of '\' <var> <expr> sub expression
          
            if is_valid_var_name(tokens[1])[0]: 
                innerExprTokens = [token, tokens.pop(0), tokens.pop(0)] # Getting '\' <var> <var>
                innerExprNode = Node(innerExprTokens[:])
                node.add_child_node(innerExprNode)
                build_parse_tree_rec(innerExprTokens, innerExprNode)

                

            elif tokens[1] == "\\":
                innerExprTokens = [token]
                while True:
                    innerExprTokens.append(tokens.pop(0)) #To capture an expr that looks like '\' 'x' '\' 'y' '\' 'z'...
                    innerExprTokens.append(tokens.pop(0))
                    innerExprTokens.append(tokens.pop(0))
                    token = tokens.pop(0)

                    if token == '\\' and tokens[1] == '\\': 
                        innerExprTokens.append(token)
                        continue

                    elif token == '\\' and not tokens[1] == '\\': 
                        innerExprTokens.append(token)
                        innerExprTokens.append(tokens.pop(0))
                        token = tokens.pop(0)
                        innerExprTokens.append(token)
                        break

                    else: 
                        innerExprTokens.append(token)
                        break

                if token == '(': 
                    closingBracketIndex = findClosingBracket(tokens)
                    innerExprTokens += tokens[:closingBracketIndex + 1]
                    tokens = tokens[closingBracketIndex + 1:]

                innerExprNode = Node(innerExprTokens[:])
                node.add_child_node(innerExprNode)
                build_parse_tree_rec(innerExprTokens, innerExprNode)



            else:
                closingBracketIndex = findClosingBracket(tokens[2:]) + 2
                innerExprTokens = [token] + tokens[:closingBracketIndex + 1] # \ <var> '(' <expr> ')'
                innerExprNode = Node(innerExprTokens[:])

                node.add_child_node(innerExprNode)

                tokens = tokens[closingBracketIndex + 1:]  # removeing the inner expression we're about to parse

                build_parse_tree_rec(innerExprTokens, innerExprNode) # building parse tree on \ <var> '(' <expr> ')' treeting it as an <expr>



        elif token == "(": 

            closingBracketIndex = findClosingBracket(tokens)

            innerExprTokens = [token] + tokens[:closingBracketIndex + 1] # getting '(' <expr> ')'

            innerExprNode = Node(innerExprTokens)
            node.add_child_node(innerExprNode)

            innerExprNode.add_child_node(Node(["("]))

            innerInnerExprNode = Node(innerExprTokens[1:-1])
            innerExprNode.add_child_node(innerInnerExprNode)

            innerExprNode.add_child_node(Node([")"]))

           
            if not len(innerInnerExprNode.elem) == 1:  # if the subexpression node contains just a var, stop exploring
                build_parse_tree_rec(tokens[:closingBracketIndex], innerInnerExprNode, isInnerExpression = True) #Evaluates expr in '('<expr>')'
            
            tokens = tokens[closingBracketIndex + 1:] # remove tokens we've parsed

        else: 
            node.add_child_node(Node([token]))

        isInnerExpression = True

    return node

#<expr> ::= <var> | '(' <expr> ')' | '\' <var> <expr> | <expr> <expr> 


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
    
    # testTokens1 = ["\\", "x", "(", "x", "za", ")"]
    # testTokens2 = "(_a_)_(_b_)_(_c_)_(_d_)".split("_")
    # testTokens3 = ['(', 'a', ')', '(', 'b', ')', '(', '\\', 'x', '(', 'x', 'b', ')', ')', '(', '\\', 'x', '(', 'x', 'yz', ')', ')']
    # testTokens4 = ['a','a', '\\', 'x', '(', 'x', 'b', ')', '(', 'a', 'b', ')', 'ab']
    # testTokens5 = ['a', 'a', '\\', 'ab', 'ab', '\\', 'x', '(', 'x', 'y', ')', 'a', 'b']
    # testTokens6 = ['a', '\\', 'x', '(', 'x', 'b', ')']
    # testTokens7 = ['a', 'a', '\\', 'ab', 'ab', '\\', 'x', '(', 'x', '\\', 'x', '(', 'x', 'y', ')', ')', 'a', 'b']
    # testTokens8 = ['a', '\\', 'x', '\\', 'y', '\\', 'z', '(', 'x', 'y', ')', 'a']
    #testTokens8 = "\\_x_(_x_(_b_c_)_)".split("_")
    # testTokens9 = ['\\', '(', 'x', 'z', ')']

    # parseTree = build_parse_tree(testTokens9)
    # parseTree.print_tree()


#   ===========================
#   END TESTING OF PARSE TREE
#   ===========================


    print("\n\nChecking valid examples...")
    read_lines_from_txt_check_validity(valid_examples_fp)
    read_lines_from_txt_output_parse_tree(valid_examples_fp)

    print("Checking invalid examples...")
    read_lines_from_txt_check_validity(invalid_examples_fp)

    # # Optional
    print("\n\nAssociation Examples:")
    sample = ["a", "b", "c"]
    print("Right association")
    associated_sample_r = add_associativity(sample, association_type="right")
    print(associated_sample_r)
    print("Left association")
    associated_sample_l = add_associativity(sample, association_type="left")
    print(associated_sample_l)