"""
Definições dos nós da Árvore Sintática Abstrata (AST).
Representação intermediária que desacopla o parser da geração de código Python.
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple


@dataclass
class ASTNode:
    """Nó base da AST com rastreamento de linha e coluna."""
    line: int = 1
    column: int = 1


@dataclass
class Program(ASTNode):
    """Nó raiz representando o programa completo."""
    statements: List[ASTNode] = field(default_factory=list)


@dataclass
class CommentStmt(ASTNode):
    """Comentário preservado (# ou #ficadica)."""
    text: str = ""


@dataclass
class VarDecl(ASTNode):
    """Declaração explícita de variável (variavel x = 10 / receba x = 10)."""
    name: str = ""
    value: Optional[ASTNode] = None


@dataclass
class Assignment(ASTNode):
    """Atribuição simples ou reatribuição (x = 10)."""
    name: str = ""
    value: Optional[ASTNode] = None


@dataclass
class PrintStmt(ASTNode):
    """Comando de impressão (imprimir(...) / Posso fala?(...))."""
    args: List[ASTNode] = field(default_factory=list)


@dataclass
class InputExpr(ASTNode):
    """Expressão de entrada de dados (entrada(...) / Hi Lorena(...))."""
    prompt: Optional[ASTNode] = None


@dataclass
class IfStmt(ASTNode):
    """
    Estrutura condicional (se / Não acho que quem ganhar ou quem perder).
    Suporta múltiplos 'senao se' e 'senao' opcional.
    """
    condition: Optional[ASTNode] = None
    body: List[ASTNode] = field(default_factory=list)
    elif_branches: List[Tuple[ASTNode, List[ASTNode]]] = field(default_factory=list)
    else_body: Optional[List[ASTNode]] = None


@dataclass
class WhileStmt(ASTNode):
    """Laço de repetição enquanto (enquanto / tuntuntuntuntuntuntunsahur)."""
    condition: Optional[ASTNode] = None
    body: List[ASTNode] = field(default_factory=list)


@dataclass
class ForStmt(ASTNode):
    """
    Laço de repetição para (para / Eita Giovana, o FORninho caiu!).
    Pode iterar sobre uma sequência ou intervalo (de ... ate ...).
    """
    variable: str = ""
    iterable: Optional[ASTNode] = None
    body: List[ASTNode] = field(default_factory=list)


@dataclass
class FunctionDef(ASTNode):
    """Declaração de função (funcao nome(...) / olha ela nome(...))."""
    name: str = ""
    params: List[str] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)


@dataclass
class ReturnStmt(ASTNode):
    """Comando de retorno (retorna / devolva)."""
    value: Optional[ASTNode] = None


@dataclass
class BreakStmt(ASTNode):
    """Interrupção de laço (pare / calma calabreso)."""
    pass


@dataclass
class ContinueStmt(ASTNode):
    """Continuação de laço (continue / Aham Claudia, senta lá)."""
    pass


@dataclass
class ExprStmt(ASTNode):
    """Expressão executada como comando isolado."""
    expr: Optional[ASTNode] = None


@dataclass
class BinaryOp(ASTNode):
    """Operação binária (aritmética, relacional ou lógica)."""
    left: Optional[ASTNode] = None
    op: str = ""
    right: Optional[ASTNode] = None


@dataclass
class UnaryOp(ASTNode):
    """Operação unária (-x, not x)."""
    op: str = ""
    operand: Optional[ASTNode] = None


@dataclass
class CallExpr(ASTNode):
    """Chamada de função ou conversão de tipo."""
    callee: str = ""
    args: List[ASTNode] = field(default_factory=list)


@dataclass
class RangeExpr(ASTNode):
    """Intervalo para repetição (de inicio ate fim [passo p])."""
    start: Optional[ASTNode] = None
    end: Optional[ASTNode] = None
    step: Optional[ASTNode] = None


@dataclass
class Literal(ASTNode):
    """Literal de valor primitivo (número, string, booleano, nulo)."""
    value: Any = None
    raw: str = ""


@dataclass
class Identifier(ASTNode):
    """Identificador de variável ou função."""
    name: str = ""
