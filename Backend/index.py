def mulheres():
    mulieres2 = 0
    mulieresmais2 = 0
    for i in range(0,10):
        pergunta = input("Você tem mais de 2 filhos? (S/N)").capitalize()

        if pergunta[0] == "S":
            mulieresmais2+=1
        elif pergunta[0] == "N":
            mulieres2+=1   
    print(f"Mulheres com mais de 2 filhos: {mulieresmais2}\nMulheres com 2 ou Menos filhos: {mulieres2}")

def compras():
    while True:
        valor_total = float(input("Valor total? "))
        if valor_total>100:
            print(f"valor total com desconto: {valor_total-(valor_total*0.1)}")
        else:
            print(f"valor total: {valor_total}")
        op = input("Deseja continuar? (sim ou não)").upper()
        
        if op[0] == "S":
            pass
        elif op[0] == "N":
            break
compras()
