import datetime
import random
import os
import glob # Novo módulo para manipulação de arquivos/caminhos

# --- Configurações ---
ARQUIVO_NOMES = "nomes.txt"
ARQUIVO_HISTORICO_ESCALAS = os.path.join("Escalas", "historico_escalas.txt") 
DIAS_UTEIS = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira"]

# Pastas de saída
PASTA_ESCALAS = "Escalas"
PASTA_MERENDA = os.path.join(PASTA_ESCALAS, "Escalas merenda")
PASTA_CHAVES = os.path.join(PASTA_ESCALAS, "Escalas chaves")
PASTA_CONTAGEM = os.path.join(PASTA_ESCALAS, "Escalas contagem")

# --- Funções de I/O de Arquivos e Histórico ---

def criar_pastas_se_nao_existem():
    """Cria as pastas de destino se não existirem."""
    os.makedirs(PASTA_MERENDA, exist_ok=True)
    os.makedirs(PASTA_CHAVES, exist_ok=True)
    os.makedirs(PASTA_CONTAGEM, exist_ok=True)

def ler_nomes(arquivo=ARQUIVO_NOMES):
    """
    Lê a lista de nomes e cria um mapeamento.
    ADICIONADO: Tratamento de exceção para codificação de arquivo.
    """
    nomes_limpos = []
    nome_bruto_map = {}
    try:
        # Tenta ler com a codificação padrão (utf-8)
        with open(arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                if linha:
                    nome_bruto = linha
                    # Assume que o nome limpo é tudo antes do primeiro ' - '
                    nome_limpo = linha.split(' - ')[0].strip()
                    
                    if nome_limpo in nome_bruto_map:
                        print(f"AVISO: Nome duplicado ignorado: {nome_limpo}")
                        continue
                        
                    nomes_limpos.append(nome_limpo)
                    nome_bruto_map[nome_limpo] = nome_bruto
                    
        return nomes_limpos, nome_bruto_map
    except FileNotFoundError:
        print(f"ERRO CRÍTICO: Arquivo {arquivo} não encontrado. Crie o arquivo e tente novamente.")
        return [], {}
    except UnicodeDecodeError:
        print(f"ERRO CRÍTICO: O arquivo {arquivo} não pôde ser lido (erro de codificação). Salve-o como UTF-8 e tente novamente.")
        return [], {}

def ler_historico_escalas(arquivo=ARQUIVO_HISTORICO_ESCALAS):
    """Lê todos os nomes que participaram de qualquer escala na semana anterior."""
    protas_anteriores = set()
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                nome = linha.strip()
                if nome:
                    protas_anteriores.add(nome)
    except FileNotFoundError:
        pass 
    return list(protas_anteriores)

def salvar_historico_geral(escala_merenda, escala_chaves, escala_contagem):
    """Salva todos os nomes que participaram das 3 escalas no arquivo de histórico."""
    protagonistas_trabalharam = set()
    
    for escala in [escala_merenda, escala_chaves]:
        for protas_do_dia in escala.values():
            for prota in protas_do_dia:
                protagonistas_trabalharam.add(prota)
                
    for prota in escala_contagem.values():
        protagonistas_trabalharam.add(prota)

    with open(ARQUIVO_HISTORICO_ESCALAS, 'w', encoding='utf-8') as f_hist:
        for nome in sorted(list(protagonistas_trabalharam)):
             f_hist.write(nome + "\n")
             
    print(f"-> Histórico de Escalas Geral atualizado em: {ARQUIVO_HISTORICO_ESCALAS}")


def salvar_escala(data_segunda, data_fim, escala, tipo, pasta, nome_bruto_map, datas_uteis):
    """Salva uma única escala em um arquivo TXT na pasta correta com a formatação solicitada."""
    
    data_formatada = f"{data_segunda.strftime('%d-%m-%Y')}_a_{data_fim.strftime('%d-%m-%Y')}"
    nome_arquivo_saida = os.path.join(pasta, f"escala_{tipo.lower()}_{data_formatada}.txt")
    
    with open(nome_arquivo_saida, 'w', encoding='utf-8') as f:
        f.write("="*40 + "\n")
        f.write(f"ESCALA {tipo.upper()} - SEMANA: {data_segunda.strftime('%d/%m')} A {data_fim.strftime('%d/%m')}\n")
        f.write("="*40 + "\n\n")

        dias_salvos = list(escala.keys())

        if tipo == "CHAVES":
            for i, dia in enumerate(dias_salvos):
                data = datas_uteis[dia].strftime('%d/%m')
                protas = escala[dia] 
                brutos = [nome_bruto_map[p] for p in protas]
                f.write(f"{dia} {data}\n")
                f.write(f"1° andar: {brutos[0]} | {brutos[1]}\n")
                f.write(f"2° andar: {brutos[2]}\n\n")

        elif tipo == "MERENDA":
            for i, dia in enumerate(dias_salvos):
                data = datas_uteis[dia].strftime('%d/%m')
                protas = escala[dia]
                brutos = [nome_bruto_map[p] for p in protas]
                f.write(f"{dia} {data}\n")
                f.write(f"fila: {brutos[0]}\n")
                f.write(f"apoio: {brutos[1]} | {brutos[2]}\n\n")

        elif tipo == "CONTAGEM":
            for i, dia in enumerate(dias_salvos):
                data = datas_uteis[dia].strftime('%d/%m')
                prota = escala[dia]
                bruto = nome_bruto_map[prota]
                f.write(f"{dia} {data}\n")
                f.write(f"{bruto}\n\n")
        
    print(f"-> Escala {tipo} salva em: {nome_arquivo_saida}")


# --- Lógica de Geração de Escalas ---

def gerar_escala_generica(nomes, protas_por_dia):
    """Gera uma escala genérica, garantindo distribuição uniforme."""
    escala = {}
    protas_disponiveis = nomes[:]
    random.shuffle(protas_disponiveis)
    
    for dia in DIAS_UTEIS:
        if len(protas_disponiveis) < protas_por_dia:
            protas_disponiveis.extend(nomes)
            random.shuffle(protas_disponiveis)
            
        prota_dia = [protas_disponiveis.pop(0) for _ in range(protas_por_dia)]
        escala[dia] = prota_dia
        
    return escala

def gerar_escala_merenda(nomes):
    return gerar_escala_generica(nomes, 3)

def gerar_escala_chaves(nomes):
    return gerar_escala_generica(nomes, 3)

def gerar_escala_contagem(nomes, protas_anteriores):
    """Gera a escala Contagem, priorizando quem NÃO trabalhou na semana anterior."""
    escala = {}
    
    # Cria uma lista de candidatos que NÃO trabalharam na semana anterior
    candidatos = [nome for nome in nomes if nome not in protas_anteriores]
    
    if len(candidatos) < len(DIAS_UTEIS):
        print("AVISO (Contagem): Poucos nomes livres. Repetição de semanas anteriores é inevitável.")
        protas_disponiveis = nomes[:] # Usa todos, se não houver candidatos suficientes
    else:
        protas_disponiveis = candidatos[:]
        
    random.shuffle(protas_disponiveis)
    
    for dia in DIAS_UTEIS:
        if not protas_disponiveis:
            protas_disponiveis.extend(nomes)
            random.shuffle(protas_disponiveis)
        
        prota_dia = protas_disponiveis.pop(0)
        escala[dia] = prota_dia
        
    return escala

# --- Funções de Data e Interface ---

def proxima_segunda():
    """Calcula a data da próxima Segunda-feira a partir de hoje."""
    hoje = datetime.date.today()
    dias_para_segunda = (7 - hoje.weekday()) % 7 
    if hoje.weekday() == 0 and dias_para_segunda == 0:
         dias_para_segunda = 7 
    
    proxima = hoje + datetime.timedelta(days=dias_para_segunda)
    return proxima

def determinar_datas_uteis(data_inicio):
    """Cria um dicionário {Dia_da_Semana: data_completa} para os dias úteis."""
    datas = {}
    for i, dia_semana in enumerate(DIAS_UTEIS):
        data = data_inicio + datetime.timedelta(days=i)
        datas[dia_semana] = data
    return datas

# NOVO: Função para exibir o histórico
def exibir_historico(protas_anteriores, total_protas):
    print("\n" + "~"*40)
    print("HISTÓRICO DA ÚLTIMA ESCALA GERADA")
    print("~"*40)
    
    if not protas_anteriores:
        print("Arquivo de histórico vazio ou não encontrado.")
        print("A próxima escala será gerada sem evitar nenhum protagonista.")
    else:
        print(f"Total de protagonistas: {total_protas}")
        print(f"Protagonistas que trabalharam na última semana: {len(protas_anteriores)}")
        
        protas_livres = total_protas - len(protas_anteriores)
        
        print(f"Protagonistas livres para prioridade na Contagem: {protas_livres}")
        print("-" * 40)
        print("Nomes que trabalharam (evitados na Opção 2):")
        
        # Exibe em colunas para melhor visualização
        colunas = 3
        sorted_protas = sorted(protas_anteriores)
        
        # Prepara os dados para impressão em colunas
        linhas = (len(sorted_protas) + colunas - 1) // colunas
        
        for i in range(linhas):
            linha = ""
            for j in range(colunas):
                idx = i + j * linhas
                if idx < len(sorted_protas):
                    linha += f"{sorted_protas[idx]:<25}"
            print(linha)

    print("~"*40)
    input("Pressione ENTER para voltar ao menu...")

# NOVO: Função para limpeza
def limpar_arquivos_antigos():
    """Exclui arquivos de escala gerados com mais de 90 dias."""
    print("\n" + "~"*40)
    print("INICIANDO LIMPEZA DE ARQUIVOS ANTIGOS")
    print("~"*40)
    
    # Define o limite de data (90 dias atrás)
    limite_data = datetime.date.today() - datetime.timedelta(days=90)
    pastas = [PASTA_MERENDA, PASTA_CHAVES, PASTA_CONTAGEM]
    arquivos_excluidos = 0
    
    for pasta in pastas:
        for arquivo_path in glob.glob(os.path.join(pasta, "escala_*.txt")):
            
            # Extrai a data do nome do arquivo (ex: escala_merenda_13-10-2025_a_17-10-2025.txt)
            nome_base = os.path.basename(arquivo_path)
            try:
                # Pega a primeira data (data de início)
                data_str = nome_base.split('_')[2] 
                data_arquivo = datetime.datetime.strptime(data_str, '%d-%m-%Y').date()
            except (IndexError, ValueError):
                print(f"AVISO: Não foi possível analisar a data do arquivo: {nome_base}")
                continue
                
            if data_arquivo < limite_data:
                try:
                    os.remove(arquivo_path)
                    print(f"EXCLUÍDO: {nome_base}")
                    arquivos_excluidos += 1
                except OSError as e:
                    print(f"ERRO ao excluir {nome_base}: {e}")

    if arquivos_excluidos == 0:
        print("Nenhum arquivo de escala com mais de 90 dias encontrado.")
    else:
        print(f"\nLimpeza concluída. Total de arquivos excluídos: {arquivos_excluidos}.")
        
    print("~"*40)
    input("Pressione ENTER para voltar ao menu...")


def menu_principal(nomes_limpos, nome_bruto_map):
    """Exibe o menu no terminal e executa a ação, permitindo geração sequencial."""
    if not nomes_limpos:
        print("Impossível rodar o menu. A lista de nomes está vazia.")
        return

    criar_pastas_se_nao_existem()
    
    data_inicio_escala_a_gerar = proxima_segunda()
    total_protas = len(nomes_limpos)
    
    while True:
        # Calcular os períodos para exibição no menu
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
        print("5 - Sair") # Sair agora é 5
        print("-" * 40)

        escolha = input("Selecione uma opção (1, 2, 3, 4 ou 5): ").strip()

        if escolha in ('1', '2'):
            
            protas_anteriores = ler_historico_escalas()
            
            if escolha == '1':
                print(f"\nGerando escalas para {periodo_proximo} (IGNORANDO histórico)...")
                protas_a_evitar = [] 
            else: # escolha == '2'
                print(f"\nGerando escalas para {periodo_proximo} (RECONHECENDO histórico)...")
                protas_a_evitar = protas_anteriores
                if not protas_a_evitar:
                     print("AVISO: Arquivo de histórico vazio. Gerando como 'nova'.")
                else:
                    protas_livres = total_protas - len(protas_a_evitar)
                    print(f"RESUMO: {len(protas_a_evitar)} protas trabalharam. Priorizando sorteio entre os {protas_livres} livres para a Contagem.")

            # --- GERAÇÃO ---
            escala_merenda = gerar_escala_merenda(nomes_limpos)
            escala_chaves = gerar_escala_chaves(nomes_limpos)
            escala_contagem = gerar_escala_contagem(nomes_limpos, protas_a_evitar)

            # --- SALVAMENTO ---
            salvar_escala(data_inicio_escala_a_gerar, data_fim, escala_merenda, "MERENDA", PASTA_MERENDA, nome_bruto_map, datas_uteis)
            salvar_escala(data_inicio_escala_a_gerar, data_fim, escala_chaves, "CHAVES", PASTA_CHAVES, nome_bruto_map, datas_uteis)
            salvar_escala(data_inicio_escala_a_gerar, data_fim, escala_contagem, "CONTAGEM", PASTA_CONTAGEM, nome_bruto_map, datas_uteis)
            
            salvar_historico_geral(escala_merenda, escala_chaves, escala_contagem)
            
            # CHAVE DA SEQUÊNCIA: AVANÇA A DATA DE INÍCIO DA PRÓXIMA ESCALA EM 7 DIAS
            data_inicio_escala_a_gerar += datetime.timedelta(days=7)
            
            print("\nTODAS AS ESCALAS FORAM GERADAS E SALVAS NAS SUAS PASTAS.")
            input(f"\nPressione ENTER para voltar ao menu e gerar a escala de {data_inicio_escala_a_gerar.strftime('%d/%m/%Y')}...")

        elif escolha == '3':
            protas_anteriores = ler_historico_escalas()
            exibir_historico(protas_anteriores, total_protas)

        elif escolha == '4':
            limpar_arquivos_antigos()

        elif escolha == '5':
            confirmacao = input("Tem certeza que deseja sair (S/N)? ").strip().lower()
            if confirmacao == 's':
                print("Saindo do programa.")
                break
        else:
            print("Opção inválida. Tente novamente.")

# --- Execução Principal ---
if __name__ == "__main__":
    nomes_limpos, nome_bruto_map = ler_nomes() 
    if nomes_limpos:
        menu_principal(nomes_limpos, nome_bruto_map)
    else:
        input("\nPressione ENTER para fechar o programa.")