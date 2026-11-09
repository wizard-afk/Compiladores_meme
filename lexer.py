"""
Módulo do analisador léxico (Lexer).
Converte o código-fonte da linguagem fictícia/meme em uma sequência de tokens.
Reconhece palavras-chave formais e referências meme da tabela oficial (readme.md),
diferenciando-as de identificadores, números, strings e comentários.
"""

from dataclasses import dataclass
from enum import Enum, auto
import re
from typing import List, Optional, Tuple

from errors import LexerError


class TokenType(Enum):
    # Palavras-chave de controle e estrutura
    DEF = auto()         # funcao / olha ela
    VAR = auto()         # variavel / receba / receba - luva de pedreiro
    PRINT = auto()       # imprimir / posso fala?
    INPUT = auto()       # entrada / hi lorena
    IF = auto()          # se / não acho que quem ganhar ou quem perder
    ELIF = auto()        # senao se / vai ganhar ou perder
    ELSE = auto()        # senao / nem quem ganhar nem perder
    WHILE = auto()       # enquanto / tuntuntuntuntuntuntunsahur
    FOR = auto()         # para / eita giovana, o forninho caiu!
    BREAK = auto()       # pare / calma calabreso
    CONTINUE = auto()    # continue / aham claudia, senta lá
    RETURN = auto()      # retorna / devolva / devolva - luva de pedreiro reverso

    # Literais booleanos e nulo
    TRUE = auto()        # verdadeiro / muehehe
    FALSE = auto()       # falso / nuquidito
    NONE = auto()        # nulo / nada pra comer nessa casa

    # Tipos e funções de conversão
    TYPE_INT = auto()    # inteiro / nazare tedesco -> int
    TYPE_FLOAT = auto()  # flutuante / alisa meu pelo -> float
    TYPE_STR = auto()    # string / joao de berro -> str
    TYPE_BOOL = auto()   # booleano / eu si lembro -> bool

    # Operadores lógicos auxiliares
    AND = auto()         # e / and
    OR = auto()          # ou / or
    NOT = auto()         # nao / não / not
    IN = auto()          # in / em
    RANGE_DE = auto()    # de (para laço for)
    RANGE_ATE = auto()   # ate / até (para laço for)
    RANGE_PASSO = auto() # passo (para laço for)

    # Identificadores e Literais
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()

    # Operadores aritméticos e relacionais
    OP_ASSIGN = auto()   # =
    OP_EQ = auto()       # ==
    OP_NEQ = auto()      # !=
    OP_LTE = auto()      # <=
    OP_GTE = auto()      # >=
    OP_LT = auto()       # <
    OP_GT = auto()       # >
    OP_PLUS = auto()     # +
    OP_MINUS = auto()    # -
    OP_POW = auto()      # **
    OP_MUL = auto()      # *
    OP_FLOORDIV = auto() # //
    OP_DIV = auto()      # /
    OP_MOD = auto()      # %

    # Delimitadores
    LPAREN = auto()      # (
    RPAREN = auto()      # )
    LBRACKET = auto()    # [
    RBRACKET = auto()    # ]
    COLON = auto()       # :
    COMMA = auto()       # ,

    # Estruturais
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    COMMENT = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: any
    line: int
    column: int
    raw: str = ""

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, linha={self.line}, col={self.column})"


# Tabela ordenada de palavras-chave e memes para correspondência léxica.
# Expressões com mais palavras ou caracteres específicos são casadas primeiro.
KEYWORDS_TABLE: List[Tuple[str, TokenType]] = [
    # Condicionais memes (Dilma)
    (r"n[aã]o\s+acho\s+que\s+quem\s+ganhar\s+ou\s+quem\s+perder\b", TokenType.IF),
    (r"nem\s+quem\s+ganhar\s+nem\s+perder\b", TokenType.ELSE),
    (r"vai\s+ganhar\s+ou\s+perder\b", TokenType.ELIF),

    # Laço for meme (Giovana)
    (r"eita\s+giovana,?\s+o\s+forninho\s+caiu(!|\b)", TokenType.FOR),

    # Break / Continue memes
    (r"calma\s+calabreso\b", TokenType.BREAK),
    (r"aham\s+claudia,?\s+senta\s+l[aá]\b", TokenType.CONTINUE),

    # Retorno memes
    (r"devolva\s*-\s*luva\s+de\s+pedreiro\s+reverso\b", TokenType.RETURN),
    (r"devolva\b", TokenType.RETURN),

    # Variável memes
    (r"receba\s*-\s*luva\s+de\s+pedreiro\b", TokenType.VAR),
    (r"receba\b", TokenType.VAR),

    # Saída e Entrada memes
    (r"posso\s+fala\?", TokenType.PRINT),
    (r"hi\s+lorena\b", TokenType.INPUT),

    # Função meme
    (r"olha\s+ela\b", TokenType.DEF),

    # Laço while meme
    (r"tuntuntuntuntuntuntunsahur\b", TokenType.WHILE),

    # Nulo meme
    (r"nada\s+pra\s+comer\s+nessa\s+casa\b", TokenType.NONE),

    # Tipos memes
    (r"alisa\s+meu\s+pelo\b", TokenType.TYPE_FLOAT),
    (r"nazar[eé]\s+tedesco\b", TokenType.TYPE_INT),
    (r"jo[aã]o\s+de\s+berro\b", TokenType.TYPE_STR),
    (r"eu\s+si\s+lembro\b", TokenType.TYPE_BOOL),

    # Literais booleanos memes
    (r"muehehe\b", TokenType.TRUE),
    (r"nuquidito\b", TokenType.FALSE),

    # Palavras-chave formais da tabela
    (r"fun[cç][aã]o\b", TokenType.DEF),
    (r"vari[aá]vel\b", TokenType.VAR),
    (r"imprimir\b", TokenType.PRINT),
    (r"entrada\b", TokenType.INPUT),
    (r"sen[aã]o\s+se\b", TokenType.ELIF),
    (r"sen[aã]ose\b", TokenType.ELIF),
    (r"sen[aã]o\b", TokenType.ELSE),
    (r"se\b", TokenType.IF),
    (r"enquanto\b", TokenType.WHILE),
    (r"pare\b", TokenType.BREAK),
    (r"para\b", TokenType.FOR),
    (r"continue\b", TokenType.CONTINUE),
    (r"retorna\b", TokenType.RETURN),
    (r"verdadeiro\b", TokenType.TRUE),
    (r"falso\b", TokenType.FALSE),
    (r"booleano\b", TokenType.TYPE_BOOL),
    (r"flutuante\b", TokenType.TYPE_FLOAT),
    (r"inteiro\b", TokenType.TYPE_INT),
    (r"string\b", TokenType.TYPE_STR),
    (r"nulo\b", TokenType.NONE),

    # Palavras lógicas auxiliares
    (r"and\b", TokenType.AND),
    (r"e\b", TokenType.AND),
    (r"or\b", TokenType.OR),
    (r"ou\b", TokenType.OR),
    (r"not\b", TokenType.NOT),
    (r"n[aã]o\b", TokenType.NOT),
    (r"in\b", TokenType.IN),
    (r"em\b", TokenType.IN),
    (r"de\b", TokenType.RANGE_DE),
    (r"at[eé]\b", TokenType.RANGE_ATE),
    (r"passo\b", TokenType.RANGE_PASSO),
]

# Compila as expressões de palavras-chave
COMPILED_KEYWORDS = [
    (re.compile(f"^{pattern}", re.IGNORECASE), token_type)
    for pattern, token_type in KEYWORDS_TABLE
]

OPERATORS_TABLE: List[Tuple[str, TokenType]] = [
    ("==", TokenType.OP_EQ),
    ("!=", TokenType.OP_NEQ),
    ("<=", TokenType.OP_LTE),
    (">=", TokenType.OP_GTE),
    ("<", TokenType.OP_LT),
    (">", TokenType.OP_GT),
    ("=", TokenType.OP_ASSIGN),
    ("**", TokenType.OP_POW),
    ("//", TokenType.OP_FLOORDIV),
    ("+", TokenType.OP_PLUS),
    ("-", TokenType.OP_MINUS),
    ("*", TokenType.OP_MUL),
    ("/", TokenType.OP_DIV),
    ("%", TokenType.OP_MOD),
]

DELIMITERS_TABLE: List[Tuple[str, TokenType]] = [
    ("(", TokenType.LPAREN),
    (")", TokenType.RPAREN),
    ("[", TokenType.LBRACKET),
    ("]", TokenType.RBRACKET),
    (":", TokenType.COLON),
    (",", TokenType.COMMA),
]


class Lexer:
    """
    Analisador léxico para a linguagem fictícia/meme.
    Processa linha a linha controlando indentação (INDENT/DEDENT/NEWLINE)
    estilo Python.
    """

    def __init__(self, source_code: str, filename: Optional[str] = None):
        self.source_code = source_code
        self.filename = filename or "<entrada>"
        self.lines = source_code.splitlines(keepends=True)
        self.tokens: List[Token] = []
        self.indent_stack: List[int] = [0]
        self.paren_depth: int = 0  # Evita quebras de linha dentro de parênteses/colchetes

    def tokenize(self) -> List[Token]:
        self.tokens = []
        self.indent_stack = [0]
        self.paren_depth = 0

        for line_idx, raw_line in enumerate(self.lines, start=1):
            self._tokenize_line(raw_line, line_idx)

        # Emite DEDENTs pendentes ao final do arquivo
        last_line_num = len(self.lines) if self.lines else 1
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, "", last_line_num, 1, ""))

        self.tokens.append(Token(TokenType.EOF, "", last_line_num, 1, ""))
        return self.tokens

    def _tokenize_line(self, line: str, line_num: int) -> None:
        # Analisa a indentação inicial se a linha tiver conteúdo útil
        stripped = line.strip()

        # Linha em branco ou apenas comentário
        if not stripped or stripped.startswith("#"):
            # Preserva comentários caso estejam presentes
            if stripped.startswith("#"):
                comment_col = line.find("#") + 1
                # Comentário oficial #ficadica ou padrão #
                comment_text = stripped
                self.tokens.append(Token(TokenType.COMMENT, comment_text, line_num, comment_col, stripped))
                self.tokens.append(Token(TokenType.NEWLINE, "\n", line_num, len(line), "\n"))
            return

        # Calcula nível de indentação (espaços e tabs normalizados para 4 espaços)
        indent_level = 0
        indent_chars = 0
        for ch in line:
            if ch == " ":
                indent_level += 1
                indent_chars += 1
            elif ch == "\t":
                indent_level += 4
                indent_chars += 1
            else:
                break

        # Apenas ajusta indentação fora de parênteses
        if self.paren_depth == 0:
            current_indent = self.indent_stack[-1]
            if indent_level > current_indent:
                self.indent_stack.append(indent_level)
                self.tokens.append(Token(TokenType.INDENT, indent_level, line_num, indent_chars + 1, ""))
            elif indent_level < current_indent:
                while self.indent_stack[-1] > indent_level:
                    self.indent_stack.pop()
                    self.tokens.append(Token(TokenType.DEDENT, indent_level, line_num, indent_chars + 1, ""))
                if self.indent_stack[-1] != indent_level:
                    raise LexerError(
                        f"Nível de indentação inconsistente (esperado {self.indent_stack[-1]}, encontrado {indent_level})",
                        line=line_num,
                        column=indent_chars + 1,
                        source_line=line,
                    )

        # Tokenização dos elementos da linha
        idx = indent_chars
        line_len = len(line)

        while idx < line_len:
            ch = line[idx]

            # Ignora espaços internos
            if ch in (" ", "\t", "\r"):
                idx += 1
                continue

            # Quebra de linha no final
            if ch == "\n":
                idx += 1
                break

            # Comentário no meio ou final da linha (#ficadica ou #)
            if ch == "#":
                comment_text = line[idx:].rstrip("\r\n")
                self.tokens.append(Token(TokenType.COMMENT, comment_text, line_num, idx + 1, comment_text))
                idx = line_len
                break

            # Strings delimitadas por aspas simples ou duplas
            if ch in ('"', "'"):
                str_val, raw_str, new_idx = self._consume_string(line, idx, line_num)
                self.tokens.append(Token(TokenType.STRING, str_val, line_num, idx + 1, raw_str))
                idx = new_idx
                continue

            # Números (inteiros e decimais/flutuantes)
            if ch.isdigit():
                num_val, raw_num, new_idx = self._consume_number(line, idx, line_num)
                self.tokens.append(Token(TokenType.NUMBER, num_val, line_num, idx + 1, raw_num))
                idx = new_idx
                continue

            # Tenta casar palavras-chave ou frases memes
            matched_kw = False
            sub_line = line[idx:]
            for regex, token_type in COMPILED_KEYWORDS:
                match = regex.match(sub_line)
                if match:
                    raw_text = match.group(0)
                    self.tokens.append(Token(token_type, raw_text, line_num, idx + 1, raw_text))
                    idx += len(raw_text)
                    matched_kw = True
                    break

            if matched_kw:
                continue

            # Identificadores comuns (variáveis, nomes de funções)
            if ch.isalpha() or ch == "_":
                ident_val, raw_ident, new_idx = self._consume_identifier(line, idx)
                self.tokens.append(Token(TokenType.IDENTIFIER, ident_val, line_num, idx + 1, raw_ident))
                idx = new_idx
                continue

            # Operadores
            matched_op = False
            for op_str, op_type in OPERATORS_TABLE:
                if line.startswith(op_str, idx):
                    self.tokens.append(Token(op_type, op_str, line_num, idx + 1, op_str))
                    idx += len(op_str)
                    matched_op = True
                    break

            if matched_op:
                continue

            # Delimitadores
            matched_delim = False
            for delim_str, delim_type in DELIMITERS_TABLE:
                if line.startswith(delim_str, idx):
                    if delim_type in (TokenType.LPAREN, TokenType.LBRACKET):
                        self.paren_depth += 1
                    elif delim_type in (TokenType.RPAREN, TokenType.RBRACKET):
                        self.paren_depth = max(0, self.paren_depth - 1)

                    self.tokens.append(Token(delim_type, delim_str, line_num, idx + 1, delim_str))
                    idx += len(delim_str)
                    matched_delim = True
                    break

            if matched_delim:
                continue

            # Caractere inválido
            raise LexerError(
                f"Caractere inválido ou não reconhecido: {ch!r}",
                line=line_num,
                column=idx + 1,
                source_line=line,
            )

        # Emite NEWLINE após linha com conteúdo (apenas se fora de parênteses)
        if self.paren_depth == 0:
            self.tokens.append(Token(TokenType.NEWLINE, "\n", line_num, line_len, "\n"))

    def _consume_string(self, line: str, start_idx: int, line_num: int) -> Tuple[str, str, int]:
        quote_char = line[start_idx]
        idx = start_idx + 1
        chars = []
        line_len = len(line)

        while idx < line_len:
            ch = line[idx]
            if ch == "\\":
                idx += 1
                if idx >= line_len:
                    break
                esc = line[idx]
                if esc == "n":
                    chars.append("\n")
                elif esc == "t":
                    chars.append("\t")
                elif esc == "\\":
                    chars.append("\\")
                elif esc == quote_char:
                    chars.append(quote_char)
                else:
                    chars.append("\\" + esc)
                idx += 1
                continue

            if ch == quote_char:
                idx += 1
                raw_str = line[start_idx:idx]
                return "".join(chars), raw_str, idx

            if ch == "\n":
                break

            chars.append(ch)
            idx += 1

        raise LexerError(
            f"String não fechada (aspas {quote_char} sem fechamento na mesma linha)",
            line=line_num,
            column=start_idx + 1,
            source_line=line,
        )

    def _consume_number(self, line: str, start_idx: int, line_num: int) -> Tuple[any, str, int]:
        idx = start_idx
        line_len = len(line)
        has_dot = False

        while idx < line_len:
            ch = line[idx]
            if ch.isdigit():
                idx += 1
            elif ch == "." and not has_dot:
                # Verifica se o próximo caractere é dígito (evita casar ponto de chamada de método)
                if idx + 1 < line_len and line[idx + 1].isdigit():
                    has_dot = True
                    idx += 1
                else:
                    break
            else:
                break

        raw_num = line[start_idx:idx]
        if has_dot:
            val = float(raw_num)
        else:
            val = int(raw_num)

        return val, raw_num, idx

    def _consume_identifier(self, line: str, start_idx: int) -> Tuple[str, str, int]:
        idx = start_idx
        line_len = len(line)
        while idx < line_len:
            ch = line[idx]
            if ch.isalnum() or ch == "_":
                idx += 1
            else:
                break
        raw_ident = line[start_idx:idx]
        return raw_ident, raw_ident, idx
