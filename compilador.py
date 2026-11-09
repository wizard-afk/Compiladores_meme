"""
Ponto de entrada do Compilador/Transpilador da Linguagem Fictícia/Meme para Python.
Permite compilar arquivos .fake via linha de comando, salvar o código Python gerado
e opcionalmente executá-lo (--run).
"""

import argparse
from pathlib import Path
import subprocess
import sys
from typing import Optional

from errors import CompilerError
from lexer import Lexer
from parser import Parser
from transpiler import Transpiler


def compilar_arquivo(
    caminho_entrada: Path,
    caminho_saida: Optional[Path] = None,
    executar: bool = False,
    verbose: bool = False,
    mostrar_tokens: bool = False,
    mostrar_ast: bool = False,
) -> int:
    """
    Executa o pipeline completo de compilação:
    Leitura -> Análise Léxica -> Análise Sintática -> Transpilação -> Escrita -> (Opcional) Execução.
    """
    if not caminho_entrada.exists():
        print(f"Erro: O arquivo de entrada '{caminho_entrada}' não foi encontrado.", file=sys.stderr)
        return 1

    try:
        codigo_fonte = caminho_entrada.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Erro ao ler arquivo '{caminho_entrada}': {e}", file=sys.stderr)
        return 1

    # Define caminho de saída padrão se não informado (substitui extensão por .py)
    if caminho_saida is None:
        caminho_saida = caminho_entrada.with_suffix(".py")

    try:
        # 1. Análise Léxica
        lexer = Lexer(codigo_fonte, filename=str(caminho_entrada))
        tokens = lexer.tokenize()

        if verbose or mostrar_tokens:
            print("\n=== TOKENS GERADOS ===")
            for t in tokens:
                print(f"  {t}")

        # 2. Análise Sintática
        parser = Parser(tokens, source_code=codigo_fonte)
        ast = parser.parse()

        if verbose or mostrar_ast:
            print("\n=== ÁRVORE SINTÁTICA ABSTRATA (AST) ===")
            print(f"  {ast}")

        # 3. Geração de Código Python (Transpilação)
        transpiler = Transpiler()
        codigo_python = transpiler.transpile(ast, filename=str(caminho_saida))

        # 4. Gravação do arquivo de saída
        caminho_saida.parent.mkdir(parents=True, exist_ok=True)
        caminho_saida.write_text(codigo_python, encoding="utf-8")
        print(f"[OK] Compilação bem-sucedida! Arquivo gerado: {caminho_saida}")

        # 5. Execução opcional do código gerado
        if executar:
            print(f"\n=== EXECUTANDO: {caminho_saida} ===")
            resultado = subprocess.run([sys.executable, str(caminho_saida)])
            return resultado.returncode

        return 0

    except CompilerError as ce:
        print("\n" + ce.format_error(), file=sys.stderr)
        return 1
    except Exception as ex:
        print(f"\n[Erro Inesperado]: {ex}", file=sys.stderr)
        return 1


def main() -> None:
    arg_parser = argparse.ArgumentParser(
        description="Compilador da Linguagem Fictícia/Meme para Python 3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python compilador.py exemplos/programa.fake
  python compilador.py exemplos/programa.fake -o saida.py
  python compilador.py exemplos/programa.fake --run
        """,
    )

    arg_parser.add_argument(
        "arquivo",
        type=Path,
        help="Caminho do arquivo de código-fonte (.fake) a ser compilado",
    )
    arg_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Caminho do arquivo Python de saída (.py). Padrão: mesmo nome com extensão .py",
    )
    arg_parser.add_argument(
        "--run",
        action="store_true",
        help="Executa o código Python gerado imediatamente após a compilação bem-sucedida",
    )
    arg_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Modo detalhado: exibe tokens e AST durante o processo",
    )
    arg_parser.add_argument(
        "--tokens",
        action="store_true",
        help="Exibe os tokens identificados pelo Lexer",
    )
    arg_parser.add_argument(
        "--ast",
        action="store_true",
        help="Exibe a estrutura da Árvore Sintática Abstrata (AST)",
    )

    args = arg_parser.parse_args()

    status = compilar_arquivo(
        caminho_entrada=args.arquivo,
        caminho_saida=args.output,
        executar=args.run,
        verbose=args.verbose,
        mostrar_tokens=args.tokens,
        mostrar_ast=args.ast,
    )
    sys.exit(status)


if __name__ == "__main__":
    main()
