# Compilador da Linguagem Fictícia/Meme para Python 3

Projeto completo de um compilador simplificado (transpilador) de nível intermediário que traduz programas escritos em uma linguagem fictícia/meme para código Python 3 executável, legível e sintaticamente válido.

---

## 1. Tabela Oficial de Referência da Linguagem

A especificação da linguagem  define a relação entre palavras-chave, equivalentes em Python e referências de memes da cultura brasileira:

| Palavra | Python | Referência |
|---|---|---|
| `funcao` | `def` | olha ela |
| `variavel` | `x = 10` | receba - luva de pedreiro |
| `imprimir` | `PRINT` | Posso fala? |
| `entrada` | `INPUT` | Hi Lorena |
| `se` | `IF` | Não acho que quem ganhar ou quem perder |
| `senao` | `ELSE` | Nem quem ganhar nem perder |
| `senao se` | `ELIF` | Vai ganhar ou perder |
| `enquanto` | `WHILE` | tuntuntuntuntuntuntunsahur |
| `pare` | `BREAK` | calma calabreso |
| `para` | `FOR` | Eita Giovana, o FORninho caiu! |
| `continue` | `CONTINUE` | Aham Claudia, senta lá |
| `retorna` | `RETURN` | devolva - luva de pedreiro reverso |
| | | |
| `verdadeiro` | `TRUE` | Muehehe |
| `falso` | `FALSE` | Nuquidito |
| `booleano` | `bool` | eu si lembro |
| `flutuante` | `float` | alisa meu pelo |
| `inteiro` | `int` | nazare tedesco |
| `string` | `str` | joao de berro |
| `nulo` | `none` | nada pra comer nessa casa |
| | | |
| `Comentario` | `#` | #ficadica |

### Decisões de Projeto e Tratamento de Ambiguidades
1. **Dualidade de Sintaxe (Palavras Formais vs. Referências Meme):** O compilador aceita tanto os nomes formais (`funcao`, `imprimir`, `se`, `retorna`) quanto as frases meme (`olha ela`, `Posso fala?`, `Não acho que quem ganhar ou quem perder`, `devolva`). Ambas podem inclusive ser combinadas livremente.
2. **Atribuição e Declaração de Variáveis:** Aceita as formas `variavel x = 10`, `receba - luva de pedreiro x = 10`, `receba x = 10` e atribuições diretas `x = 10`.
3. **Frases com Pontuação e Espaços:** Expressões como `Posso fala?` e `Eita Giovana, o FORninho caiu!` são reconhecidas atomicamente pelo analisador léxico sem colidir com identificadores ou pontuações de controle.
4. **Preservação de Literais:** Palavras-chave ou frases meme dentro de strings (ex.: `"Não acho que quem ganhar..."`) são preservadas como dados puros e não são convertidas em tokens de controle.

---

## 2. Arquitetura do Compilador

O projeto foi estruturado em módulos independentes com responsabilidades bem definidas:

```text
Compiladores_meme/
├── compilador.py         # Interface CLI (argparse) e orquestrador do pipeline
├── lexer.py              # Analisador léxico: tokenização, controle de indentação e memes
├── ast_nodes.py          # Definição dos nós da Árvore Sintática Abstrata (AST)
├── parser.py             # Analisador sintático: descendente recursivo com AST
├── transpiler.py         # Gerador de código Python e validador via compile()
├── errors.py             # Hierarquia de erros com mensagens amigáveis e apontadores
├── README.md             # Esta documentação completa
├── exemplos/             # Exemplos progressivos na sintaxe .fake
│   ├── programa.fake           # Saída simples de texto
│   ├── variaveis_entrada.fake  # Variáveis, tipos e entrada de dados
│   ├── condicionais.fake       # Condicionais se, senao se e senao
│   ├── repeticao.fake          # Laços enquanto e para com pare e continue
│   ├── funcoes.fake            # Declaração e chamada de funções com retorno
│   └── completo.fake           # Programa completo integrando todos os recursos
└── testes/               # Suíte completa de testes automatizados (unittest)
    ├── test_lexer.py           # Testes do analisador léxico
    ├── test_parser.py          # Testes do parser e construção da AST
    ├── test_transpiler.py      # Testes do gerador de código Python
    └── test_integration.py     # Testes de ponta a ponta e linha de comando
```

### Papel de Cada Módulo

- **[`errors.py`](file:///c:/Users/user/Documents/GitHub/Compiladores_meme/errors.py):** Define `CompilerError`, `LexerError`, `ParserError` e `TranspilerError`. Formata mensagens exibindo a linha, coluna e um cursor visual (`^`) indicando a causa do erro.
- **[`lexer.py`](file:///c:/Users/user/Documents/GitHub/Compiladores_meme/lexer.py):** Varre o texto fonte gerando objetos `Token`. Mantém uma pilha de indentação para produzir tokens `INDENT`, `DEDENT` e `NEWLINE` (estilo Python).
- **[`ast_nodes.py`](file:///c:/Users/user/Documents/GitHub/Compiladores_meme/ast_nodes.py):** Contém nós em `@dataclass` (`Program`, `VarDecl`, `IfStmt`, `WhileStmt`, `ForStmt`, `FunctionDef`, `ReturnStmt`, `BinaryOp`, etc.).
- **[`parser.py`](file:///c:/Users/user/Documents/GitHub/Compiladores_meme/parser.py):** Implementa um parser descendente recursivo com tabela de precedência para operadores matemáticos, lógicos e relacionais.
- **[`transpiler.py`](file:///c:/Users/user/Documents/GitHub/Compiladores_meme/transpiler.py):** Percorre os nós da AST e gera código Python 3 perfeitamente indentado. Antes de concluir, invoca a função embutida `compile(codigo, filename, "exec")` para certificar a validade sintática do código gerado.
- **[`compilador.py`](file:///c:/Users/user/Documents/GitHub/Compiladores_meme/compilador.py):** Interface de linha de comando que aceita o caminho de entrada, caminho de saída customizado (`-o`), opção de execução imediata (`--run`) e modo detalhado (`-v`, `--tokens`, `--ast`).

---

## 3. Preparação do Ambiente

O compilador foi desenvolvido para funcionar com a biblioteca padrão do Python 3 (Python 3.10 ou superior). **Nenhuma biblioteca externa de terceiros é necessária.**

Para verificar a instalação do Python:

```bash
python --version
```

---

## 4. Como Executar o Compilador

### 4.1. Compilação Básica
Para compilar um arquivo `.fake` gerando o respectivo arquivo `.py` no mesmo diretório:

```bash
python compilador.py exemplos/programa.fake
```

Saída:
```text
[OK] Compilação bem-sucedida! Arquivo gerado: exemplos/programa.py
```

### 4.2. Definir Arquivo de Saída Customizado (`-o`)
Para escolher onde o arquivo `.py` será gerado:

```bash
python compilador.py exemplos/programa.fake -o saida.py
```

### 4.3. Compilar e Executar Imediatamente (`--run`)
Para compilar e, caso não haja erros, executar o código Python gerado:

```bash
python compilador.py exemplos/programa.fake --run
```

### 4.4. Visualizar Tokens e AST (`--tokens`, `--ast` ou `-v`)
```bash
python compilador.py exemplos/programa.fake --tokens --ast
```

---

## 5. Como Executar o Código Traduzido

Caso tenha compilado sem a flag `--run`, o arquivo Python gerado pode ser executado a qualquer momento com o interpretador Python padrão:

```bash
python exemplos/programa.py
```

---

## 6. Como Rodar os Testes Automatizados

A suíte de testes utiliza o módulo padrão `unittest` do Python.

Para executar todos os testes automatizados:

```bash
python -m unittest discover -s testes -p "test_*.py"
```

Os testes cobrem:
- Reconhecimento de todos os tokens formais e referências de meme.
- Preservação de palavras-chave dentro de literais de texto.
- Avaliação de precedência de operadores aritméticos e lógicos.
- Construção correta da AST em laços, condicionais e funções.
- Testes negativos com lançamento de `LexerError` e `ParserError`.
- Validação do código Python gerado via `compile()`.
- Testes de integração de leitura/escrita de arquivos e execução de scripts gerados.

---

## 7. Construções Suportadas com Exemplos

### 7.1. Saída de Texto e Comentários
```fake
#ficadica Comentário oficial
Posso fala?("Olá, Mundo!")
imprimir("Mensagem padrão")
```
Python gerado:
```python
# [ficadica] Comentário oficial
print('Olá, Mundo!')
print('Mensagem padrão')
```

### 7.2. Variáveis, Tipos e Entrada
```fake
receba nome = "Alice"
receba idade = nazare tedesco("30")
receba salario = alisa meu pelo("3500.50")
receba online = Muehehe
receba vazio = nada pra comer nessa casa
```
Python gerado:
```python
nome = 'Alice'
idade = int('30')
salario = float('3500.50')
online = True
vazio = None
```

### 7.3. Estruturas Condicionais
```fake
Não acho que quem ganhar ou quem perder nota >= 90:
    Posso fala?("Excelente")
Vai ganhar ou perder nota >= 60:
    Posso fala?("Aprovado")
Nem quem ganhar nem perder:
    Posso fala?("Reprovado")
```
Python gerado:
```python
if (nota >= 90):
    print('Excelente')
elif (nota >= 60):
    print('Aprovado')
else:
    print('Reprovado')
```

### 7.4. Laços de Repetição
```fake
# Laço enquanto
receba c = 1
tuntuntuntuntuntuntunsahur c <= 3:
    Posso fala?("Contagem:", c)
    c = c + 1

# Laço para (intervalo)
Eita Giovana, o FORninho caiu! i de 1 ate 5:
    Não acho que quem ganhar ou quem perder i == 3:
        calma calabreso
    Posso fala?(i)
```
Python gerado:
```python
c = 1
while (c <= 3):
    print('Contagem:', c)
    c = (c + 1)

for i in range(1, (5) + 1):
    if (i == 3):
        break
    print(i)
```

### 7.5. Funções e Retornos
```fake
olha ela fatorial(n):
    Não acho que quem ganhar ou quem perder n <= 1:
        devolva 1
    devolva n * fatorial(n - 1)

receba res = fatorial(5)
Posso fala?("Resultado:", res)
```
Python gerado:
```python
def fatorial(n):
    if (n <= 1):
        return 1
    return (n * fatorial((n - 1)))

res = fatorial(5)
print('Resultado:', res)
```

---

## 8. Limitações Conhecidas

- **Tipagem Dinâmica:** A linguagem é dinamicamente tipada no runtime Python. As palavras de tipo (`inteiro`/`nazare tedesco`, `flutuante`/`alisa meu pelo`, etc.) funcionam como funções de conversão (cast).
- **Escopo e Sintaxe de Blocos:** Os blocos utilizam o delimitador `:` e controle rigoroso de indentação. Blocos sem comandos devem conter instruções válidas (como em Python).
- **Sem Otimizações de Máquina:** O compilador foca em fins didáticos e transpilacão limpa de código fonte para código fonte (Source-to-Source / Transpiler).