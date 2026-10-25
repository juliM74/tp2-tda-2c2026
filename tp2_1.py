def main(edificios, cantidad_visibles):
    n, k = edificios, cantidad_visibles
    if k < 0 or k > n:
        return 0
    if n == 0:
        return 1 if k == 0 else 0

    fila = [0] * (k + 1)
    fila[0] = 1 

    for i in range(1, n + 1):
        tope = min(i, k)
        for j in range(tope, 0, -1):
            fila[j] = fila[j - 1] + (i - 1) * fila[j]
        fila[0] = 0 

    return fila[k]


if __name__ == "__main__":
    print(main(3, 2))    
    print(main(10, 10))  
