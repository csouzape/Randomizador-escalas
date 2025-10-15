import random
from datetime import datetime

nomes = [
    "Bruno Gabriel - 3C",
    "Carlos Gabriel - 2C",
    "Clara Gomes - 1C",
    "Héber Micael - 3C",
    "Isabela Monteiro - 1B",
    "Joyce Maria - 1C",
    "Kayki Keven - 2C",
    "Lays Lorena - 3B",
    "Maria Clara - 3C",
    "Maria Julia - 3A",
    "Rhaquel de Souza - 1C",
    "Sabrina - 3A",
    "Sara Rogério - 1A",
    "Vítor Gabriel - 1C",
    "Matheus Henrique - 1C"
]

dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]

def gerar_escalas(nomes, dias):
    escala_merenda = {}
    escala_chaves = {}
    escala_contagem = {}

    for dia in dias:
        nomes_disponiveis = nomes[:]
        random.shuffle(nomes_disponiveis)
        merenda = [nomes_disponiveis.pop(0) for _ in range(3)]
        escala_merenda[dia] = merenda

        nomes_restantes = [n for n in nomes_disponiveis if n not in merenda]
        random.shuffle(nomes_restantes)
        chaves = [nomes_restantes.pop(0) for _ in range(3)]
        escala_chaves[dia] = chaves

        nomes_final = [n for n in nomes if n not in merenda and n not in chaves]
        random.shuffle(nomes_final)
        contagem = nomes_final[0] if nomes_final else nomes[0]
        escala_contagem[dia] = contagem

    return escala_merenda, escala_chaves, escala_contagem

def salvar_escalas_txt(merenda, chaves, contagem):
    hoje = datetime.now().strftime("%Y-%m-%d")
    nome_arquivo = f"escalas_{hoje}.txt"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(f"ESCALA GERADA EM {hoje}\n\n")
        f.write("ESCALA MERENDA:\n")
        for dia, nomes in merenda.items():
            f.write(f"{dia}: {', '.join(nomes)}\n")
        f.write("\nESCALA CHAVES:\n")
        for dia, nomes in chaves.items():
            f.write(f"{dia}: {', '.join(nomes)}\n")
        f.write("\nESCALA CONTAGEM:\n")
        for dia, nome in contagem.items():
            f.write(f"{dia}: {nome}\n")
    print(f"\nEscalas salvas em {nome_arquivo}")

if __name__ == "__main__":
    merenda, chaves, contagem = gerar_escalas(nomes, dias)
    print("ESCALA MERENDA:")
    for dia, nomes in merenda.items():
        print(f"{dia}: {', '.join(nomes)}")
    print("\nESCALA CHAVES:")
    for dia, nomes in chaves.items():
        print(f"{dia}: {', '.join(nomes)}")
    print("\nESCALA CONTAGEM:")
    for dia, nome in contagem.items():
        print(f"{dia}: {nome}")
    salvar_escalas_txt(merenda, chaves, contagem)
