from typing import Any
var = {}

class token():
    typ: str
    val: str

    def __init__(self, typ, val):
        """
        >>> token('sym', '(')
        token('sym', '(')
        """
        self.typ = typ
        self.val = val

    def __repr__(self):
        return f'({self.typ!r} : {self.val!r})'
class Error :
    pass
def lex(s : str):

    tokens = []
    i = 0
    while i < len(s):
        if s[i].isspace():
            i += 1
        elif s[i].isalpha():
            end = i + 1
            while end < len(s) and (s[end].isalnum() or s[end] == '_'):
                end += 1
            assert end >= len(s) or not (s[end].isalnum() or s[end] == '_')

            word = s[i:end]

            if word in ['true', 'false','print']:
                tokens.append(token('kw', word))
            else:
                tokens.append(token('var', word))

            i = end
        elif s[i].isdigit():
            end = i + 1
            while end < len(s) and (s[end].isdigit() or s[end] == '.'):
                end += 1
            assert end >= len(s) or not (s[end].isdigit()or s[end] == '.')

            if '.' in s[i:end]:
                tokens.append(token('float', s[i:end]))
            else:
                tokens.append(token('int', s[i:end]))

            i = end

        elif s[i:i+2] == '>=' :
            tokens.append(token('greater_equal', s[i:i+2]))
            i += 2
        elif s[i:i+2] == '<=' :
            tokens.append(token('less_equal', s[i:i+2]))
            i += 2
        elif s[i:i+2] == '==' :
            tokens.append(token('equalizer', s[i:i+2]))
            i += 2
        elif s[i:i+2] == '--':
            tokens.append(token('decrement', s[i:i+2]))
            i += 2
        elif s[i:i+2] == '++':
            tokens.append(token('increment', s[i:i+2]))
            i += 2
        elif s[i] == '=':
            tokens.append(token('equal', s[i]))
            i += 1
        elif s[i] == '+':
            tokens.append(token('addition', s[i]))
            i += 1
        elif s[i] == '-':
            tokens.append(token('minus_sign', s[i]))
            i += 1
        elif s[i] == '*':
            tokens.append(token('multiplication', s[i]))
            i += 1
        elif s[i] == '/':
            tokens.append(token('division', s[i]))
            i += 1
        elif s[i] == '%':
            tokens.append(token('binary_modulus', s[i]))
            i += 1
        elif s[i] == '^':
            tokens.append(token('exponentiation', s[i]))
            i += 1
        elif s[i] == '(':
            tokens.append(token('left_parentheses', s[i]))
            i += 1
        elif s[i] == ')':
            tokens.append(token('right_parentheses', s[i]))
            i += 1
        elif s[i] == '>':
            tokens.append(token('greater', s[i]))
            i += 1
        elif s[i] == '<':
            tokens.append(token('lesser', s[i]))
            i += 1

        else:
            raise SyntaxError(f'unexpected character {s[i]}')

    return tokens


class Parser:
    def __init__(self,tokens) -> None:
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self, ):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        
        return self.current_tok

    def parse(self):
        res = self.expr()
        if self.current_tok.typ == 'EOF':
            raise SyntaxError(f'Expected EOF')
        return res
    
    def expr(self):
        if self.current_tok.typ == 'var': 
            var_name = self.current_tok
            self.advance()
        if self.current_tok.typ == 'equal':
            self.advance()
            expr = self.expr()
            
            result = VarAssignNode(var_name, expr)
            return result
        if self.current_tok.typ == 'kw' and self.current_tok.val == 'print':
            self.advance()
            expr = self.expr()
            result = PrintNode(expr)
            return result
            
            
        res = self.term()
        while self.current_tok.typ in ('addition', 'minus_sign'):
            if self.current_tok.typ == 'addition':
                op_tok = self.current_tok
                self.advance()
                res = BinaryNode(res, op_tok, self.term())
            elif self.current_tok.typ == 'minus_sign':
                op_tok = self.current_tok
                self.advance()
                res = BinaryNode(res, op_tok, self.term())
        return res
    
    def atom(self):
        tok = self.current_tok

        if tok.typ in ('int', 'float'):
            self.advance()
            return NumberNode(tok)
        elif tok.typ == 'var':
            self.advance()
            return VarAccessNode(tok)
        elif tok.typ == 'left_parentheses':
            self.advance()
            res = self.expr()
            if self.current_tok.typ != 'right_parentheses':
                raise SyntaxError(f'Expected )')
            self.advance()
            return res
    
    def power(self):
        res = self.atom()
        while self.current_tok.typ == 'exponentiation':
            if self.current_tok.typ == 'exponentiation':
                op_tok = self.current_tok
                self.advance()
                res = BinaryNode(res, op_tok, self.atom())
        return res

    def factor(self):
        tok = self.current_tok
        if tok.typ == 'minus_sign':
            self.advance()
            return UnaryNode(tok, self.factor())
        elif tok.typ == 'addition':
            self.advance()
            return UnaryNode(tok, self.factor())
        return self.power()
    
    def term(self):
        res = self.factor()
        while self.current_tok.typ in ('multiplication', 'division', 'binary_modulus', 'exponentiation'):
            if self.current_tok.typ == 'multiplication':
                op_tok = self.current_tok
                self.advance()
                res = BinaryNode(res, op_tok, self.factor())
            elif self.current_tok.typ == 'division':
                op_tok = self.current_tok
                self.advance()
                res = BinaryNode(res, op_tok, self.factor())
            elif self.current_tok.typ == 'binary_modulus':
                op_tok = self.current_tok
                self.advance()
                res = BinaryNode(res, op_tok, self.factor())
            elif self.current_tok.typ == 'exponentiation':
                op_tok = self.current_tok
                self.advance()
                res = BinaryNode(res, op_tok, self.atom())
        return res
    
class VarAssignNode():
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node
    
    def __repr__(self):
        return f'({self.var_name_tok}, {self.value_node})'
  

class VarAccessNode():
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok
    
    def __repr__(self):
        return f'({self.var_name_tok})'
    
class Variables():
    def __init__(self) -> None:
        
        self.globe = None

    def get(self,name):
        value = var.get(name,None)
        if value == None and self.globe:
            return self.globe.get(name)
        return value
     
    def set(self,name,value):
        var.update({name : value}) 

    def remove(self,name):
        del var[name]


class NumberNode:
	def __init__(self, tok):
		self.tok = tok

	def __repr__(self):
		return f'{self.tok}'

class BinaryNode:
	def __init__(self, left_node, op_tok, right_node):
		self.left_node = left_node
		self.op_tok = op_tok
		self.right_node = right_node

	def __repr__(self):
		return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class PrintNode:
    def __init__(self, node):
        self.node = node

    def __repr__(self):
        return f'({self.node})'

class UnaryNode:
	def __init__(self, op_tok, node):
		self.op_tok = op_tok
		self.node = node

	def __repr__(self):
		return f'({self.op_tok}, {self.node})'

class Interpreter :

    
    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name)
        value_t = method(node)

        return value_t
    
    def visit_VarAccessNode(self,node):

        variable_name = node.var_name_tok.val
        value = Variables.get(self, variable_name)
        if value == None:
            raise NameError(repr(variable_name))
        return value

    def visit_VarAssignNode(self, node):
        variable_name = node.var_name_tok.val
        value = self.visit(node.value_node)
        if variable_name in var :
            op_token = node.value_node.op_tok.typ
            if op_token == 'addition':
                Variables.set(self,variable_name, Number.add_num(value, var[variable_name]))
            elif op_token == 'minus_sign':
                Variables.set(self,variable_name, Number.sub_num(var[variable_name], value))
            elif op_token == 'multiplication':
                Variables.set(self,variable_name, Number.mul_num(value, var[variable_name]))
            elif op_token == 'division':
                Variables.set(self,variable_name, Number.div_num(value, var[variable_name]))
            elif op_token == 'binary_modulus':
                Variables.set(self,variable_name, Number.mod_num(value, var[variable_name]))
            elif op_token == 'exponentiation':
                Variables.set(self,variable_name, Number.pow_num(value, var[variable_name]))
            
        else :
            Variables.set(self,variable_name, value)
        
        return value

    def visit_NumberNode(self, node):
        return Number(node.tok.val)
    
    def visit_BinaryNode(self, node):
        left = self.visit(node.left_node)
        right = self.visit(node.right_node)
        if node.op_tok.typ == 'addition':
            return left.add(right)
        elif node.op_tok.typ == 'minus_sign':
            return left.sub(right)
        elif node.op_tok.typ == 'multiplication':
            return left.mul(right)
        elif node.op_tok.typ == 'division':
            return left.truediv(right)
        elif node.op_tok.typ == 'binary_modulus':
            return left.mod(right)
        elif node.op_tok.typ == 'exponentiation':
            return left.pow(right)
    
    
    def visit_UnaryNode(self, node):
        number = self.visit(node.node)
        if node.op_tok.typ == 'minus_sign':
            number = number.mul(Number(-1))
        return number
    
    def visit_PrintNode(self, node):
        value = self.visit(node.node)
        # print(value)
        return value

class Number:
    def __init__(self, value):
        self.value = value

    
    def __repr__(self):
        return f'{self.value}'
    
    def add_num(self, other):
        if  (isinstance(self,Number)):
            return Number(float(self.value)+ float(other.value))
    
    def add(self, other):
        if isinstance(other, Number):
            return Number(float(self.value) + float(other.value))
        elif isinstance(other, str):
            return Number(float(self.value) + float(other))
        else:
            raise TypeError(f'Expected Number, got {type(other)}')
        
    def sub(self, other):
        if isinstance(other, Number):
            return Number(float(self.value) - float(other.value))
        elif isinstance(other, str):
            return Number(float(self.value) - float(other))
        else:
            raise TypeError(f'Expected Number, got {type(other)}')
    
    def sub_num(self, other):
        if  (isinstance(self,Number)):
            return Number(float(self.value) + float(other.value))
            
    
    def mul(self, other):
        if isinstance(other, Number):
            return Number(float(self.value) * float(other.value))
        elif isinstance(other, str):
            return Number(float(self.value) * float(other))
        else:
            raise TypeError(f'Expected Number, got {type(other)}')
    
    def mul_num(self, other):
        if  (isinstance(self,Number)):
            return Number(float(self.value) * float(other.value))
           
    def truediv(self, other):
        if isinstance(other, Number):
            return Number(float(self.value) / float(other.value))
        elif isinstance(other, str):
            return Number(float(self.value) / float(other))
        else:
            raise TypeError(f'Expected Number, got {type(other)}')
    
    def div_num(self, other):
        if  (isinstance(self,Number)):
            return Number(float(self.value)/ float(other.value))
    
    def mod(self, other):
        if isinstance(other, Number):
            return Number(float(self.value) % float(other.value))
        elif isinstance(other, str):
            return Number(float(self.value) % float(other))
        else:
            raise TypeError(f'Expected Number, got {type(other)}')
    
    def mod_num(self, other):
        if  (isinstance(self,Number)):
            return Number(float(self.value) % float(other.value))
        
        
    def pow(self, other):
        if isinstance(other, Number):
            return Number(float(self.value) ** float(other.value))
        elif isinstance(other, str):
            return Number(float(self.value) ** float(other))
        else:
            raise TypeError(f'Expected Number, got {type(other)}')
    
    def pow_num(self, other):
        if  (isinstance(self,Number)):
            return Number(float(self.value) ** float(other.value))
            
     
if __name__ == "__main__" :


    inputlist = []
   
    while True:
        try:
            line = input()
            value = lex(line)
            print(value)
            value2 = Parser(value)
            value3 = value2.parse()
            print(value3)
            print(Interpreter().visit(value3))
            # print(var)

            if len(line.strip()) == 0:
                break
        except EOFError:
            break
        
