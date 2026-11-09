# Código gerado automaticamente pelo compilador da linguagem fictícia/meme

# [ficadica] Programa completo demonstrando todas as capacidades da linguagem
def calcular_fatorial(n):
    if (n <= 1):
        return 1
    return (n * calcular_fatorial((n - 1)))
def classificar_numero(num):
    if (num > 0):
        return 'Positivo'
    elif (num < 0):
        return 'Negativo'
    else:
        return 'Zero'
        # Programa principal
print('=== Sistema de Calculo Meme ===')
valor = 5
fat = calcular_fatorial(valor)
print('Fatorial de', valor, 'eh', fat)
classificacao = classificar_numero(valor)
print('Classificacao:', classificacao)
print('Contagem de 1 ate 5:')
for i in range(1, (5) + 1):
    print('Passo', i)
print('Sucesso total! Receba!')
