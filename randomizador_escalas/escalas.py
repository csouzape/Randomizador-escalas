import datetime
import random
import os
import glob
import logging
from typing import List, Dict, Tuple, Set

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

ARQUIVO_NOMES = "nomes.txt"
ARQUIVO_HISTORICO_ESCALAS = os.path.join("Escalas", "historico_escalas.txt")
DIAS_UTEIS = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira"]

PASTA_ESCALAS = "Escalas"
PASTA_MERENDA = os.path.join(PASTA_ESCALAS, "Escalas merenda")
PASTA_CHAVES = os.path.join(PASTA_ESCALAS, "Escalas chaves")
PASTA_CONTAGEM = os.path.join(PASTA_ESCALAS, "Escalas contagem")

def criar_pastas_se_nao_existem() -> None:
    for pasta in [PASTA_MERENDA, PASTA_CHAVES, PASTA_CONTAGEM]:
        os.makedirs(pasta, exist_ok=True)

def ler_nomes(arquivo: str = ARQUIVO_NOMES) -> Tuple[List[str], Dict[str, str]]:
    nomes_limpos = []
    nome_bruto_map = {}
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                if linha:
                    nome_limpo = linha.split(' - ')[0].strip()
                    if nome_limpo not in nome_bruto_map:
                        nomes_limpos.append(nome_limpo)
                        nome_bruto_map[nome_limpo] = linha
                    else:
                        logging.warning(f"Nome duplicado ignorado: {nome_limpo}")
        return nomes_limpos, nome_bruto_map
    except FileNotFoundError:
        logging.error(f"Arquivo {arquivo} não encontrado.")
        return [], {}
    except UnicodeDecodeError:
        logging.error(f"Erro de codificação ao ler {arquivo}.")
        return [], {}

def ler_historico_escalas(arquivo: str = ARQUIVO_HISTORICO_ESCALAS) -> List[str]:
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            return [linha.strip() for linha in f if linha.strip()]
    except FileNotFoundError:
        return []

def salvar_historico_geral(*escalas: Dict[str, List[str] or str]) -> None:
    protagonistas_trabalharam: Set[str] = set()
    for escala in escalas[:-1]:
        for protas_do_dia in escala.values():
            protagonistas_trabalharam.update(protas_do_dia)
    protagonistas_trabalharam.update(escalas[-1].values())
    with open(ARQUIVO_HISTORICO_ESCALAS, 'w', encoding='utf-8') as f_hist:
        for nome in sorted(protagonistas_trabalharam):
            f_hist.write(nome + "\n")
    logging.info(f"Histórico atualizado em: {ARQUIVO_HISTORICO_ESCALAS}")

def salvar_escala(data_segunda: datetime.date, data_fim: datetime.date, escala: Dict[str, List[str] or str], tipo: str, pasta: str, nome_bruto_map: Dict[str, str], datas_uteis: Dict[str, datetime.date]) -> None:
    data_formatada = f"{data_segunda.strftime('%d-%m-%Y')}_a_{data_fim.strftime('%d-%m-%Y')}"
    nome_arquivo_saida = os.path.join(pasta, f"escala_{tipo.lower()}_{data_formatada}.txt")
    with open(nome_arquivo_saida, 'w', encoding='utf-8') as f:
        f.write("="*40 + "\n")
        f.write(f"ESCALA {tipo.upper()} - SEMANA: {data_segunda.strftime('%d/%m')} A {data_fim.strftime('%d/%m')}\n")
        f.write("="*40 + "\n\n")
        for dia in escala:
            data = datas_uteis[dia].strftime('%d/%m')
            if tipo == "CHAVES":
                brutos = [nome_bruto_map[p] for p in escala[dia]]
                f.write(f"{dia} {data}\n1° andar: {brutos[0]} | {brutos[1]}\n2° andar: {brutos[2]}\n\n")
            elif tipo == "MERENDA":
                brutos = [nome_bruto_map[p] for p in escala[dia]]
                f.write(f"{dia} {data}\nfila: {brutos[0]}\napoio: {brutos[1]} | {brutos[2]}\n\n")
            elif tipo == "CONTAGEM":
                bruto = nome_bruto_map[escala[dia]]
                f.write(f"{dia} {data}\n{bruto}\n\n")
    logging.info(f"Escala {tipo} salva em: {nome_arquivo_saida}")

def gerar_escala_generica(nomes: List[str], protas_por_dia: int) -> Dict[str, List[str]]:
    escala = {}
    protas_disponiveis = nomes[:]
    random.shuffle(protas_disponiveis)
    for dia in DIAS_UTEIS:
        if len(protas_disponiveis) < protas_por_dia:
            protas_disponiveis.extend(nomes)
            random.shuffle(protas_disponiveis)
        escala[dia] = [protas_disponiveis.pop(0) for _ in range(protas_por_dia)]
    return escala

def gerar_escala_contagem(nomes: List[str], protas_anteriores: List[str]) -> Dict[str, str]:
    candidatos = [nome for nome in nomes if nome not in protas_anteriores]
    protas_disponiveis = candidatos if len(candidatos) >= len(DIAS_UTEIS) else nomes[:]
    random.shuffle(protas_disponiveis)
    escala = {}
    for dia in DIAS_UTEIS:
        if not protas_disponiveis:
            protas_disponiveis.extend(nomes)
            random.shuffle(protas_disponiveis)
        escala[dia] = protas_disponiveis.pop(0)
    return escala

def gerar_escalas_sem_sobreposicao(nomes: List[str], protas_anteriores: List[str]) -> Tuple[Dict[str, List[str]], Dict[str, List[str]], Dict[str, str]]:
    escala_merenda = {}
    escala_chaves = {}
    escala_contagem = {}

    for dia in DIAS_UTEIS:
        nomes_disponiveis = nomes[:]
        random.shuffle(nomes_disponiveis)

        # Merenda
        merenda = [nomes_disponiveis.pop(0) for _ in range(3)]
        escala_merenda[dia] = merenda

        # Chaves (sem os de merenda)
        nomes_restantes = [n for n in nomes_disponiveis if n not in merenda]
        if len(nomes_restantes) < 3:
            nomes_restantes = [n for n in nomes if n not in merenda]
            random.shuffle(nomes_restantes)
        chaves = [nomes_restantes.pop(0) for _ in range(3)]
        escala_chaves[dia] = chaves

        # Contagem (sem os de merenda e chaves)
        nomes_final = [n for n in nomes if n not in merenda and n not in chaves]
        candidatos_contagem = [n for n in nomes_final if n not in protas_anteriores]
        if not candidatos_contagem:
            candidatos_contagem = nomes_final if nomes_final else nomes[:]
        random.shuffle(candidatos_contagem)
        escala_contagem[dia] = candidatos_contagem[0] if candidatos_contagem else nomes[0]

    return escala_merenda, escala_chaves, escala_contagem

def proxima_segunda() -> datetime.date:
    hoje = datetime.date.today()
    dias_para_segunda = (7 - hoje.weekday()) % 7
    if hoje.weekday() == 0 and dias_para_segunda == 0:
        dias_para_segunda = 7
    return hoje + datetime.timedelta(days=dias_para_segunda)

def determinar_datas_uteis(data_inicio: datetime.date) -> Dict[str, datetime.date]:
    return {dia_semana: data_inicio + datetime.timedelta(days=i) for i, dia_semana in enumerate(DIAS_UTEIS)}

def validar_opcao_menu(opcao: str, opcoes_validas: List[str]) -> bool:
    return opcao in opcoes_validas

def menu_principal(nomes_limpos: List[str], nome_bruto_map: Dict[str, str]) -> None:
    if not nomes_limpos:
        logging.error("Lista de nomes vazia.")
        return
    criar_pastas_se_nao_existem()
    data_inicio_escala_a_gerar = proxima_segunda()
    total_protas = len(nomes_limpos)
    while True:
        data_fim = data_inicio_escala_a_gerar + datetime.timedelta(days=4)
        periodo_proximo = f"{data_inicio_escala_a_gerar.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
        data_atual_segunda = data_inicio_escala_a_gerar - datetime.timedelta(days=7)
        data_atual_sexta = data_atual_segunda + datetime.timedelta(days=4)
        periodo_atual = f"{data_atual_segunda.strftime('%d/%m/%Y')} a {data_atual_sexta.strftime('%d/%m/%Y')}"
        datas_uteis = determinar_datas_uteis(data_inicio_escala_a_gerar)
        print("\n" + "="*40)
        print("Randomizador de escalas")
        print("="*40)
        print(f"Protagonistas carregados: {total_protas}")
        print(f"Escala dessa semana: {periodo_atual}")
        print(f"Período da Próxima Escala (A GERAR): {periodo_proximo}")
        print("-" * 40)
        print("1 - Gerar uma escala nova (Ignora histórico de trabalho)")
        print("2 - Gerar uma escala reconhecendo uma escala anterior (Prioriza não-trabalhados)")
        print("3 - Ver Histórico da Última Semana")
        print("4 - Limpar Arquivos de Escala Antigos (> 90 dias)")
        print("5 - Sair")
        print("-" * 40)
        escolha = input("Selecione uma opção (1, 2, 3, 4 ou 5): ").strip()
        if not validar_opcao_menu(escolha, ['1', '2', '3', '4', '5']):
            print("Opção inválida. Tente novamente.")
            continue
        if escolha in ('1', '2'):
            protas_anteriores = ler_historico_escalas()
            protas_a_evitar = protas_anteriores if escolha == '2' else []
            escala_merenda, escala_chaves, escala_contagem = gerar_escalas_sem_sobreposicao(nomes_limpos, protas_a_evitar)
            salvar_escala(data_inicio_escala_a_gerar, data_fim, escala_merenda, "MERENDA", PASTA_MERENDA, nome_bruto_map, datas_uteis)
            salvar_escala(data_inicio_escala_a_gerar, data_fim, escala_chaves, "CHAVES", PASTA_CHAVES, nome_bruto_map, datas_uteis)
            salvar_escala(data_inicio_escala_a_gerar, data_fim, escala_contagem, "CONTAGEM", PASTA_CONTAGEM, nome_bruto_map, datas_uteis)
            salvar_historico_geral(escala_merenda, escala_chaves, escala_contagem)
            data_inicio_escala_a_gerar += datetime.timedelta(days=7)
            input("\nPressione ENTER para continuar...")
        elif escolha == '3':
            protas_anteriores = ler_historico_escalas()
            print("\nHistórico da última escala:")
            for nome in sorted(protas_anteriores):
                print(nome)
            input("Pressione ENTER para voltar ao menu...")
        elif escolha == '4':
            limpar_arquivos_antigos()
        elif escolha == '5':
            confirmacao = input("Tem certeza que deseja sair (S/N)? ").strip().lower()
            if confirmacao == 's':
                print("Saindo do programa.")
                break

def limpar_arquivos_antigos() -> None:
    limite_data = datetime.date.today() - datetime.timedelta(days=90)
    pastas = [PASTA_MERENDA, PASTA_CHAVES, PASTA_CONTAGEM]
    arquivos_excluidos = 0
    for pasta in pastas:
        for arquivo_path in glob.glob(os.path.join(pasta, "escala_*.txt")):
            nome_base = os.path.basename(arquivo_path)
            try:
                data_str = nome_base.split('_')[2]
                data_arquivo = datetime.datetime.strptime(data_str, '%d-%m-%Y').date()
            except (IndexError, ValueError):
                logging.warning(f"Não foi possível analisar a data do arquivo: {nome_base}")
                continue
            if data_arquivo < limite_data:
                try:
                    os.remove(arquivo_path)
                    logging.info(f"Excluído: {nome_base}")
                    arquivos_excluidos += 1
                except OSError as e:
                    logging.error(f"Erro ao excluir {nome_base}: {e}")
    if arquivos_excluidos == 0:
        print("Nenhum arquivo antigo encontrado.")
    else:
        print(f"Total de arquivos excluídos: {arquivos_excluidos}.")
    input("Pressione ENTER para voltar ao menu...")

if __name__ == "__main__":
    nomes_limpos, nome_bruto_map = ler_nomes()
    if nomes_limpos:
        menu_principal(nomes_limpos, nome_bruto_map)
    else:
        input("\nPressione ENTER para fechar o programa.")