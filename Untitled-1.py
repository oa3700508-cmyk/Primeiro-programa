while True:
    n1 = int(input("digite seu primeiro número: "))
    n2 = int(input("digite seu segundo número: "))

    resp = int (input("1 - soma \n" \
    "2 - subtração \n" \
    "3 - multiplicação \n" \
    "4 - divisão \nR: "))

    if resp == 1:
        cal = n1 + n2
    elif resp == 2:
        cal = n1 - n2
    elif resp == 3:
        cal = n1 * n2
    elif resp == 4:
        cal = n1 / n2
    else:
        print("essa opção não existe ")                                  
        continue
    break
print(f"o resultado é: {cal}")