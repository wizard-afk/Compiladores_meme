"""
Módulo do analisador sintático (Parser).
Transforma o fluxo de tokens gerado pelo Lexer em uma Árvore Sintática Abstrata (AST).
Suporta comandos formais e referências meme da especificação oficial.
"""

from typing import List, Optional, Tuple

from errors import ParserError
from lexer import Token, TokenType
from ast_nodes import (
    ASTNode,
    Assignment,
    BinaryOp,
    BreakStmt,
    CallExpr,
    CommentStmt,
    ContinueStmt,
    ExprStmt,
    ForStmt,
    FunctionDef,
    Identifier,
    IfStmt,
    InputExpr,
    Literal,
    PrintStmt,
    Program,
    RangeExpr,
    ReturnStmt,
    UnaryOp,
    VarDecl,
    WhileStmt,
)

# Mapeamento canônico dos tipos para equivalentes Python
TYPE_MAP = {
    TokenType.TYPE_INT: "int",
    TokenType.TYPE_FLOAT: "float",
    TokenType.TYPE_STR: "str",
    TokenType.TYPE_BOOL: "bool",
}


class Parser:
    """
    Analisador sintático descendente recursivo.
    Constrói a AST a partir dos tokens com verificação de erros sintáticos.
    """

    def __init__(self, tokens: List[Token], source_code: Optional[str] = None):
        self.tokens = tokens
        self.source_code = source_code or ""
        self.lines = self.source_code.splitlines() if self.source_code else []
        self.pos = 0

    def parse(self) -> Program:
        """Ponto de entrada do parser. Retorna o nó Program."""
        statements: List[ASTNode] = []
        while not self._is_at_end():
            self._skip_newlines()
            if self._is_at_end():
                break
            stmt = self._parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self._skip_newlines()
        first_token = self.tokens[0] if self.tokens else Token(TokenType.EOF, "", 1, 1)
        return Program(line=first_token.line, column=first_token.column, statements=statements)

    # --------------------------------------------------------------------------
    # Navegação de tokens
    # --------------------------------------------------------------------------

    def _peek(self, offset: int = 0) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1] if self.tokens else Token(TokenType.EOF, "", 1, 1)

    def _previous(self) -> Token:
        return self.tokens[self.pos - 1] if self.pos > 0 else self.tokens[0]

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return token_type == TokenType.EOF
        return self._peek().type == token_type

    def _match(self, *token_types: TokenType) -> bool:
        for t in token_types:
            if self._check(t):
                self._advance()
                return True
        return False

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.pos += 1
        return self._previous()

    def _consume(self, token_type: TokenType, error_msg: str) -> Token:
        if self._check(token_type):
            return self._advance()
        curr = self._peek()
        self._raise_error(f"{error_msg} (encontrado '{curr.value}' do tipo {curr.type.name})", curr)

    def _skip_newlines(self) -> None:
        while self._match(TokenType.NEWLINE):
            pass

    def _raise_error(self, message: str, token: Optional[Token] = None) -> None:
        t = token or self._peek()
        source_line = None
        if self.lines and 1 <= t.line <= len(self.lines):
            source_line = self.lines[t.line - 1]
        raise ParserError(message, line=t.line, column=t.column, source_line=source_line)

    # --------------------------------------------------------------------------
    # Regras de comandos (Statements)
    # --------------------------------------------------------------------------

    def _parse_statement(self) -> Optional[ASTNode]:
        curr = self._peek()

        # Comentários preservados
        if self._match(TokenType.COMMENT):
            tok = self._previous()
            return CommentStmt(line=tok.line, column=tok.column, text=tok.value)

        # Declaração de função (funcao / olha ela)
        if self._match(TokenType.DEF):
            return self._parse_function_def()

        # Declaração de variável (variavel / receba)
        if self._match(TokenType.VAR):
            return self._parse_var_decl()

        # Impressão (imprimir / posso fala?)
        if self._match(TokenType.PRINT):
            return self._parse_print_stmt()

        # Condicional (se / não acho que quem ganhar...)
        if self._match(TokenType.IF):
            return self._parse_if_stmt()

        # Laço enquanto (enquanto / tuntun...)
        if self._match(TokenType.WHILE):
            return self._parse_while_stmt()

        # Laço para (para / eita giovana...)
        if self._match(TokenType.FOR):
            return self._parse_for_stmt()

        # Retorno (retorna / devolva)
        if self._match(TokenType.RETURN):
            return self._parse_return_stmt()

        # Interrupção de laço (pare / calma calabreso)
        if self._match(TokenType.BREAK):
            tok = self._previous()
            self._match(TokenType.NEWLINE)
            return BreakStmt(line=tok.line, column=tok.column)

        # Continuação de laço (continue / aham claudia...)
        if self._match(TokenType.CONTINUE):
            tok = self._previous()
            self._match(TokenType.NEWLINE)
            return ContinueStmt(line=tok.line, column=tok.column)

        # Atribuição comum identificador = expressao
        if curr.type == TokenType.IDENTIFIER and self._peek(1).type == TokenType.OP_ASSIGN:
            return self._parse_assignment()

        # Caso geral: comando de expressão (chamadas de função avulsas, etc.)
        expr = self._parse_expression()
        self._match(TokenType.NEWLINE)
        return ExprStmt(line=expr.line, column=expr.column, expr=expr)

    def _parse_block(self) -> List[ASTNode]:
        """Analisa um bloco de comandos indentados."""
        self._consume(TokenType.COLON, "Esperado ':' no início do bloco de comandos")
        self._consume(TokenType.NEWLINE, "Esperada quebra de linha após ':'")

        # Verifica indentação
        self._consume(TokenType.INDENT, "Esperada indentação para início do bloco de comandos")

        statements: List[ASTNode] = []
        while not self._check(TokenType.DEDENT) and not self._is_at_end():
            self._skip_newlines()
            if self._check(TokenType.DEDENT) or self._is_at_end():
                break
            stmt = self._parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self._skip_newlines()

        self._consume(TokenType.DEDENT, "Esperado recuo (dedent) ao final do bloco de comandos")

        if not statements:
            self._raise_error("Bloco de comandos vazio não é permitido")
        return statements

    def _parse_function_def(self) -> FunctionDef:
        tok_def = self._previous()
        name_tok = self._consume(TokenType.IDENTIFIER, "Esperado nome da função após 'funcao'/'olha ela'")
        self._consume(TokenType.LPAREN, "Esperado '(' após o nome da função")

        params: List[str] = []
        if not self._check(TokenType.RPAREN):
            while True:
                p_tok = self._consume(TokenType.IDENTIFIER, "Esperado nome do parâmetro da função")
                params.append(p_tok.value)
                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RPAREN, "Esperado ')' após lista de parâmetros da função")
        body = self._parse_block()
        return FunctionDef(line=tok_def.line, column=tok_def.column, name=name_tok.value, params=params, body=body)

    def _parse_var_decl(self) -> VarDecl:
        tok_var = self._previous()
        name_tok = self._consume(TokenType.IDENTIFIER, "Esperado nome da variável após declaração 'variavel'/'receba'")

        value = None
        if self._match(TokenType.OP_ASSIGN):
            value = self._parse_expression()

        self._match(TokenType.NEWLINE)
        return VarDecl(line=tok_var.line, column=tok_var.column, name=name_tok.value, value=value)

    def _parse_assignment(self) -> Assignment:
        name_tok = self._advance()  # consome o IDENTIFIER
        self._advance()            # consome o OP_ASSIGN (=)
        value = self._parse_expression()
        self._match(TokenType.NEWLINE)
        return Assignment(line=name_tok.line, column=name_tok.column, name=name_tok.value, value=value)

    def _parse_print_stmt(self) -> PrintStmt:
        tok_print = self._previous()
        args: List[ASTNode] = []

        # Suporta impressão com parênteses: Posso fala?(...) ou sem: Posso fala? ...
        has_paren = self._match(TokenType.LPAREN)

        if has_paren:
            if not self._check(TokenType.RPAREN):
                while True:
                    args.append(self._parse_expression())
                    if not self._match(TokenType.COMMA):
                        break
            self._consume(TokenType.RPAREN, "Esperado ')' ao final dos argumentos de impressão")
        else:
            # Sem parênteses: lê expressões separadas por vírgula até fim da linha
            if not self._check(TokenType.NEWLINE) and not self._is_at_end():
                while True:
                    args.append(self._parse_expression())
                    if not self._match(TokenType.COMMA):
                        break

        self._match(TokenType.NEWLINE)
        return PrintStmt(line=tok_print.line, column=tok_print.column, args=args)

    def _parse_if_stmt(self) -> IfStmt:
        tok_if = self._previous()
        cond = self._parse_expression()
        body = self._parse_block()

        elif_branches: List[Tuple[ASTNode, List[ASTNode]]] = []
        else_body: Optional[List[ASTNode]] = None

        self._skip_newlines()
        while self._match(TokenType.ELIF):
            elif_cond = self._parse_expression()
            elif_body = self._parse_block()
            elif_branches.append((elif_cond, elif_body))
            self._skip_newlines()

        if self._match(TokenType.ELSE):
            else_body = self._parse_block()

        return IfStmt(
            line=tok_if.line,
            column=tok_if.column,
            condition=cond,
            body=body,
            elif_branches=elif_branches,
            else_body=else_body,
        )

    def _parse_while_stmt(self) -> WhileStmt:
        tok_while = self._previous()
        cond = self._parse_expression()
        body = self._parse_block()
        return WhileStmt(line=tok_while.line, column=tok_while.column, condition=cond, body=body)

    def _parse_for_stmt(self) -> ForStmt:
        tok_for = self._previous()
        var_tok = self._consume(TokenType.IDENTIFIER, "Esperado nome da variável iteradora após 'para'")

        # Duas sintaxes:
        # 1. para x in lista: / para x em lista:
        # 2. para i de 1 ate 10 [passo 2]:
        iterable: ASTNode
        if self._match(TokenType.IN):
            iterable = self._parse_expression()
        elif self._match(TokenType.RANGE_DE):
            start = self._parse_expression()
            self._consume(TokenType.RANGE_ATE, "Esperado 'ate' na definição de intervalo do laço 'para'")
            end = self._parse_expression()
            step = None
            if self._match(TokenType.RANGE_PASSO):
                step = self._parse_expression()
            iterable = RangeExpr(line=tok_for.line, column=tok_for.column, start=start, end=end, step=step)
        else:
            self._raise_error("Esperado 'in', 'em' ou 'de ... ate ...' no laço 'para'")

        body = self._parse_block()
        return ForStmt(line=tok_for.line, column=tok_for.column, variable=var_tok.value, iterable=iterable, body=body)

    def _parse_return_stmt(self) -> ReturnStmt:
        tok_ret = self._previous()
        value = None
        if not self._check(TokenType.NEWLINE) and not self._is_at_end():
            value = self._parse_expression()
        self._match(TokenType.NEWLINE)
        return ReturnStmt(line=tok_ret.line, column=tok_ret.column, value=value)

    # --------------------------------------------------------------------------
    # Expressões com precedência de operadores
    # --------------------------------------------------------------------------

    def _parse_expression(self) -> ASTNode:
        return self._parse_or()

    def _parse_or(self) -> ASTNode:
        expr = self._parse_and()
        while self._match(TokenType.OR):
            op_tok = self._previous()
            right = self._parse_and()
            expr = BinaryOp(line=op_tok.line, column=op_tok.column, left=expr, op="or", right=right)
        return expr

    def _parse_and(self) -> ASTNode:
        expr = self._parse_not()
        while self._match(TokenType.AND):
            op_tok = self._previous()
            right = self._parse_not()
            expr = BinaryOp(line=op_tok.line, column=op_tok.column, left=expr, op="and", right=right)
        return expr

    def _parse_not(self) -> ASTNode:
        if self._match(TokenType.NOT):
            tok = self._previous()
            operand = self._parse_not()
            return UnaryOp(line=tok.line, column=tok.column, op="not", operand=operand)
        return self._parse_comparison()

    def _parse_comparison(self) -> ASTNode:
        expr = self._parse_term()
        while self._match(
            TokenType.OP_EQ,
            TokenType.OP_NEQ,
            TokenType.OP_LT,
            TokenType.OP_LTE,
            TokenType.OP_GT,
            TokenType.OP_GTE,
        ):
            op_tok = self._previous()
            right = self._parse_term()
            expr = BinaryOp(line=op_tok.line, column=op_tok.column, left=expr, op=op_tok.value, right=right)
        return expr

    def _parse_term(self) -> ASTNode:
        expr = self._parse_factor()
        while self._match(TokenType.OP_PLUS, TokenType.OP_MINUS):
            op_tok = self._previous()
            right = self._parse_factor()
            expr = BinaryOp(line=op_tok.line, column=op_tok.column, left=expr, op=op_tok.value, right=right)
        return expr

    def _parse_factor(self) -> ASTNode:
        expr = self._parse_power()
        while self._match(TokenType.OP_MUL, TokenType.OP_DIV, TokenType.OP_FLOORDIV, TokenType.OP_MOD):
            op_tok = self._previous()
            right = self._parse_power()
            expr = BinaryOp(line=op_tok.line, column=op_tok.column, left=expr, op=op_tok.value, right=right)
        return expr

    def _parse_power(self) -> ASTNode:
        expr = self._parse_unary()
        while self._match(TokenType.OP_POW):
            op_tok = self._previous()
            right = self._parse_unary()
            expr = BinaryOp(line=op_tok.line, column=op_tok.column, left=expr, op="**", right=right)
        return expr

    def _parse_unary(self) -> ASTNode:
        if self._match(TokenType.OP_MINUS, TokenType.OP_PLUS):
            op_tok = self._previous()
            operand = self._parse_unary()
            return UnaryOp(line=op_tok.line, column=op_tok.column, op=op_tok.value, operand=operand)
        return self._parse_primary()

    def _parse_primary(self) -> ASTNode:
        curr = self._peek()

        # Literais booleanos
        if self._match(TokenType.TRUE):
            tok = self._previous()
            return Literal(line=tok.line, column=tok.column, value=True, raw=tok.value)
        if self._match(TokenType.FALSE):
            tok = self._previous()
            return Literal(line=tok.line, column=tok.column, value=False, raw=tok.value)

        # Literal nulo
        if self._match(TokenType.NONE):
            tok = self._previous()
            return Literal(line=tok.line, column=tok.column, value=None, raw=tok.value)

        # Números
        if self._match(TokenType.NUMBER):
            tok = self._previous()
            return Literal(line=tok.line, column=tok.column, value=tok.value, raw=tok.raw)

        # Strings
        if self._match(TokenType.STRING):
            tok = self._previous()
            return Literal(line=tok.line, column=tok.column, value=tok.value, raw=tok.raw)

        # Entrada de dados (entrada / Hi Lorena)
        if self._match(TokenType.INPUT):
            tok_in = self._previous()
            prompt = None
            if self._match(TokenType.LPAREN):
                if not self._check(TokenType.RPAREN):
                    prompt = self._parse_expression()
                self._consume(TokenType.RPAREN, "Esperado ')' ao fechar comando de entrada")
            return InputExpr(line=tok_in.line, column=tok_in.column, prompt=prompt)

        # Tipos primitivos usados como funções de conversão: inteiro(...), nazare tedesco(...)
        if curr.type in TYPE_MAP:
            type_tok = self._advance()
            py_type = TYPE_MAP[type_tok.type]
            if self._match(TokenType.LPAREN):
                args: List[ASTNode] = []
                if not self._check(TokenType.RPAREN):
                    args.append(self._parse_expression())
                self._consume(TokenType.RPAREN, f"Esperado ')' após conversão para {py_type}")
                return CallExpr(line=type_tok.line, column=type_tok.column, callee=py_type, args=args)
            return Identifier(line=type_tok.line, column=type_tok.column, name=py_type)

        # Identificador ou chamada de função genérica
        if self._match(TokenType.IDENTIFIER):
            name_tok = self._previous()
            if self._match(TokenType.LPAREN):
                args = []
                if not self._check(TokenType.RPAREN):
                    while True:
                        args.append(self._parse_expression())
                        if not self._match(TokenType.COMMA):
                            break
                self._consume(TokenType.RPAREN, f"Esperado ')' ao fechar chamada da função '{name_tok.value}'")
                return CallExpr(line=name_tok.line, column=name_tok.column, callee=name_tok.value, args=args)
            return Identifier(line=name_tok.line, column=name_tok.column, name=name_tok.value)

        # Expressão entre parênteses
        if self._match(TokenType.LPAREN):
            lparen = self._previous()
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "Parêntese não fechado: esperado ')' correspondente")
            return expr

        self._raise_error(f"Expressão inválida ou símbolo inesperado: '{curr.value}'", curr)
