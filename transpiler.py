"""
Módulo do gerador de código Python (Transpiler).
Percorre a Árvore Sintática Abstrata (AST) e gera código Python 3 executável,
legível e padronizado, com estratégia centralizada de indentação.
Valida o código resultante com a função interna `compile()`.
"""

from typing import List, Optional

from errors import TranspilerError
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


class Transpiler:
    """
    Tradutor da AST da linguagem fictícia/meme para código Python.
    Gerencia indentação de forma centralizada.
    """

    def __init__(self, indent_size: int = 4):
        self.indent_unit = " " * indent_size
        self.current_indent_level = 0
        self.lines: List[str] = []

    def transpile(self, program: Program, filename: str = "<gerado.py>") -> str:
        """
        Gera o código Python a partir do nó Program da AST
        e valida com compile().
        """
        self.lines = []
        self.current_indent_level = 0

        # Cabeçalho informativo
        self._emit("# Código gerado automaticamente pelo compilador da linguagem fictícia/meme")
        self._emit("")

        if not program.statements:
            self._emit("pass")
        else:
            for stmt in program.statements:
                self._generate_statement(stmt)

        generated_code = "\n".join(self.lines) + "\n"

        # Validação de sintaxe Python com compile()
        self._validate_python_code(generated_code, filename)

        return generated_code

    def _indent(self) -> str:
        return self.indent_unit * self.current_indent_level

    def _emit(self, text: str) -> None:
        if text == "":
            self.lines.append("")
        else:
            self.lines.append(f"{self._indent()}{text}")

    def _validate_python_code(self, code: str, filename: str) -> None:
        try:
            compile(code, filename, "exec")
        except SyntaxError as e:
            raise TranspilerError(
                f"Código Python gerado contém erro de sintaxe: {e.msg}",
                line=e.lineno,
                column=e.offset,
                source_line=e.text,
            )

    # --------------------------------------------------------------------------
    # Geração de comandos (Statements)
    # --------------------------------------------------------------------------

    def _generate_statement(self, stmt: ASTNode) -> None:
        if isinstance(stmt, CommentStmt):
            # Normaliza comentários do meme #ficadica para formato Python padrão
            text = stmt.text
            if text.startswith("#ficadica"):
                clean = text[len("#ficadica"):].strip()
                self._emit(f"# [ficadica] {clean}" if clean else "# [ficadica]")
            else:
                self._emit(text)

        elif isinstance(stmt, VarDecl):
            val_code = self._generate_expression(stmt.value) if stmt.value else "None"
            self._emit(f"{stmt.name} = {val_code}")

        elif isinstance(stmt, Assignment):
            val_code = self._generate_expression(stmt.value) if stmt.value else "None"
            self._emit(f"{stmt.name} = {val_code}")

        elif isinstance(stmt, PrintStmt):
            args_code = ", ".join(self._generate_expression(arg) for arg in stmt.args)
            self._emit(f"print({args_code})")

        elif isinstance(stmt, IfStmt):
            cond_code = self._generate_expression(stmt.condition) if stmt.condition else "True"
            self._emit(f"if {cond_code}:")
            self._generate_block(stmt.body)

            for elif_cond, elif_body in stmt.elif_branches:
                elif_code = self._generate_expression(elif_cond)
                self._emit(f"elif {elif_code}:")
                self._generate_block(elif_body)

            if stmt.else_body is not None:
                self._emit("else:")
                self._generate_block(stmt.else_body)

        elif isinstance(stmt, WhileStmt):
            cond_code = self._generate_expression(stmt.condition) if stmt.condition else "True"
            self._emit(f"while {cond_code}:")
            self._generate_block(stmt.body)

        elif isinstance(stmt, ForStmt):
            iter_code = self._generate_expression(stmt.iterable) if stmt.iterable else "[]"
            self._emit(f"for {stmt.variable} in {iter_code}:")
            self._generate_block(stmt.body)

        elif isinstance(stmt, FunctionDef):
            params_str = ", ".join(stmt.params)
            self._emit(f"def {stmt.name}({params_str}):")
            self._generate_block(stmt.body)

        elif isinstance(stmt, ReturnStmt):
            if stmt.value:
                self._emit(f"return {self._generate_expression(stmt.value)}")
            else:
                self._emit("return")

        elif isinstance(stmt, BreakStmt):
            self._emit("break")

        elif isinstance(stmt, ContinueStmt):
            self._emit("continue")

        elif isinstance(stmt, ExprStmt):
            if stmt.expr:
                self._emit(self._generate_expression(stmt.expr))

        else:
            raise TranspilerError(f"Tipo de nó AST não suportado pelo gerador: {type(stmt).__name__}")

    def _generate_block(self, statements: List[ASTNode]) -> None:
        self.current_indent_level += 1
        if not statements:
            self._emit("pass")
        else:
            for s in statements:
                self._generate_statement(s)
        self.current_indent_level -= 1

    # --------------------------------------------------------------------------
    # Geração de expressões (Expressions)
    # --------------------------------------------------------------------------

    def _generate_expression(self, expr: Optional[ASTNode]) -> str:
        if expr is None:
            return "None"

        if isinstance(expr, Literal):
            if expr.value is None:
                return "None"
            if isinstance(expr.value, bool):
                return "True" if expr.value else "False"
            if isinstance(expr.value, str):
                # Preserva string escapada com segurança
                return repr(expr.value)
            return str(expr.value)

        if isinstance(expr, Identifier):
            return expr.name

        if isinstance(expr, InputExpr):
            prompt_str = self._generate_expression(expr.prompt) if expr.prompt else ""
            return f"input({prompt_str})"

        if isinstance(expr, CallExpr):
            args_str = ", ".join(self._generate_expression(a) for a in expr.args)
            return f"{expr.callee}({args_str})"

        if isinstance(expr, RangeExpr):
            start = self._generate_expression(expr.start) if expr.start else "0"
            end = self._generate_expression(expr.end) if expr.end else "0"
            if expr.step:
                step = self._generate_expression(expr.step)
                return f"range({start}, ({end}) + 1, {step})"
            return f"range({start}, ({end}) + 1)"

        if isinstance(expr, UnaryOp):
            operand_str = self._generate_expression(expr.operand)
            if expr.op == "not":
                return f"(not {operand_str})"
            return f"({expr.op}{operand_str})"

        if isinstance(expr, BinaryOp):
            left_str = self._generate_expression(expr.left)
            right_str = self._generate_expression(expr.right)
            op = expr.op
            # Normaliza operadores lógicos
            if op in ("e", "and"):
                op = "and"
            elif op in ("ou", "or"):
                op = "or"
            return f"({left_str} {op} {right_str})"

        raise TranspilerError(f"Expressão AST desconhecida: {type(expr).__name__}")
