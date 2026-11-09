"""
Módulo de tratamento e formatação de erros do compilador.
Define exceções específicas para as etapas de análise léxica,
sintática e de geração de código (transpilação).
"""

from typing import Optional


class CompilerError(Exception):
    """Classe base para erros do compilador."""

    def __init__(
        self,
        message: str,
        line: Optional[int] = None,
        column: Optional[int] = None,
        source_line: Optional[str] = None,
        stage: str = "Erro Geral",
    ):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column
        self.source_line = source_line
        self.stage = stage

    def format_error(self) -> str:
        """Formata a mensagem de erro de forma amigável com indicador visual."""
        header = f"[{self.stage}]"
        pos_info = []
        if self.line is not None:
            pos_info.append(f"Linha {self.line}")
        if self.column is not None:
            pos_info.append(f"Coluna {self.column}")

        if pos_info:
            header += f" ({', '.join(pos_info)})"

        lines = [f"{header}: {self.message}"]

        if self.source_line is not None:
            clean_line = self.source_line.rstrip("\r\n")
            lines.append(f"    > {clean_line}")
            if self.column is not None and self.column >= 1:
                pointer = " " * (4 + 2 + self.column - 1) + "^"
                lines.append(pointer)

        return "\n".join(lines)

    def __str__(self) -> str:
        return self.format_error()


class LexerError(CompilerError):
    """Erro ocorrido durante a análise léxica (tokenização)."""

    def __init__(
        self,
        message: str,
        line: Optional[int] = None,
        column: Optional[int] = None,
        source_line: Optional[str] = None,
    ):
        super().__init__(message, line, column, source_line, stage="Erro Léxico")


class ParserError(CompilerError):
    """Erro ocorrido durante a análise sintática (parser/AST)."""

    def __init__(
        self,
        message: str,
        line: Optional[int] = None,
        column: Optional[int] = None,
        source_line: Optional[str] = None,
    ):
        super().__init__(message, line, column, source_line, stage="Erro Sintático")


class TranspilerError(CompilerError):
    """Erro ocorrido durante a geração de código Python."""

    def __init__(
        self,
        message: str,
        line: Optional[int] = None,
        column: Optional[int] = None,
        source_line: Optional[str] = None,
    ):
        super().__init__(message, line, column, source_line, stage="Erro de Transpilação")
