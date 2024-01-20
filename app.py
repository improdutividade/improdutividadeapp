import streamlit as st
import pandas as pd
import datetime
import pytz
import os
import base64
from io import BytesIO
import uuid
import io
import xlsxwriter

class RegistroAtividades:
    def __init__(self, user_id):
        self.user_id = user_id
        self.arquivo_dados = f'registros_atividades_{self.user_id}.xlsx'
        self.iniciar_arquivo_excel()
        self.iniciar_sessao()

    def iniciar_arquivo_excel(self):
        if not os.path.exists(self.arquivo_dados):
            df = pd.DataFrame(columns=['ID', 'Nome_Usuário', 'Frente_Serviço', 'Função', 'Atividade', 'Data', 'Início', 'Fim', 'Duração'])
            df.to_excel(self.arquivo_dados, index=False)

    def iniciar_sessao(self):
        if 'registro' not in st.session_state:
            st.session_state.registro = {
                'nome_usuario': '',
                'frente_servico': '',
                'df': pd.DataFrame(columns=['ID', 'Nome_Usuário', 'Frente_Serviço', 'Função', 'Atividade', 'Data', 'Início', 'Fim', 'Duração'])
            }

    def obter_informacoes_iniciais(self):
        st.session_state.registro['nome_usuario'] = st.text_input("Digite seu nome: ").upper()
        st.session_state.registro['frente_servico'] = st.text_input("Digite a frente de serviço: ").upper()

    def registrar_atividades(self):
        self.obter_informacoes_iniciais()

        quantidade_equipe = st.number_input("Digite a quantidade de membros da equipe: ", min_value=1, step=1, value=1)

        for i in range(1, quantidade_equipe + 1):
            self.registrar_atividade(i)

        # Adiciona botão para download do Excel preenchido
        if st.button("Baixar Relatório Excel"):
            self.gerar_relatorio_excel()

        # Adiciona botão para reiniciar os dados
        if st.button("Zerar Dados"):
            self.zerar_dados()

    def selecionar_atividade(self, funcionario_id):
        opcoes_atividades = [
           "Andando sem ferramenta", "Ao Celular / Fumando", "Aguardando Almoxarifado",
           "À disposição", "Necessidades Pessoais (Água/Banheiro)", "Operando",
           "Auxiliando", "Ajustando Ferramenta ou Equipamento", "Deslocando com ferramenta em mãos",
           "Em prontidão", "Conversando com Encarregado/Operários (Informações Técnicas)"]

        atividade = st.selectbox(f"Selecione a atividade para funcionário {funcionario_id}:", opcoes_atividades, key=f"atividade_{funcionario_id}")
        return atividade

    def registrar_atividade(self, funcionario_id):
        st.write(f"Funcionário {funcionario_id}:")
        nome_funcao = st.text_input(f"Informe a função para funcionário {funcionario_id}: ", key=f"funcao_{funcionario_id}").upper()

        atividade = self.selecionar_atividade(funcionario_id)
        iniciar = st.button(f"Iniciar atividade para funcionário {funcionario_id}")
        encerrar = st.button(f"Encerrar atividade para funcionário {funcionario_id}")

        if iniciar:
            self.iniciar_atividade(funcionario_id, nome_funcao, atividade)

        if encerrar:
            self.encerrar_atividade(funcionario_id)

    def iniciar_atividade(self, funcionario_id, nome_funcao, atividade):
        novo_registro = {
            'ID': funcionario_id,
            'Nome_Usuário': st.session_state.registro['nome_usuario'],
            'Frente_Serviço': st.session_state.registro['frente_servico'],
            'Função': nome_funcao,
            'Atividade': atividade,
            'Data': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime("%Y-%m-%d"),
            'Início': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime("%H:%M:%S"),
            'Fim': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime("%H:%M:%S"),
            'Duração': ''
        }

        df = st.session_state.registro['df']
        df = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
        st.session_state.registro['df'] = df

        st.success(f"Atividade '{atividade}' iniciada para funcionário {funcionario_id} ({nome_funcao})")

    def encerrar_atividade(self, funcionario_id):
        st.write(f"Encerrando atividade para funcionário {funcionario_id}...")

        df = st.session_state.registro['df']

        funcionario_df = df[df['ID'] == funcionario_id]

        if not funcionario_df.empty:
            inicio = funcionario_df.iloc[-1]['Início']
            if pd.isnull(inicio):
                st.error("Atividade ainda não iniciada para este funcionário.")
                return

            df.loc[(df['ID'] == funcionario_id) & (df.index == len(funcionario_df) - 1), 'Fim'] = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime("%H:%M:%S")
            fim = datetime.datetime.now()
            duracao = fim - pd.to_datetime(inicio)
            df.loc[(df['ID'] == funcionario_id) & (df.index == len(funcionario_df) - 1), 'Duração'] = duracao
            st.session_state.registro['df'] = df
            st.success(f"Atividade encerrada para funcionário {funcionario_id} às {fim.strftime('%H:%M:%S')}")

        else:
            st.error("ID do funcionário inválido.")

    def gerar_relatorio_excel(self):
        st.write(f"Dados salvos em '{self.arquivo_dados}'")

        df = st.session_state.registro['df']

        if not df.empty:
            df.to_excel(self.arquivo_dados, index=False)
            st.markdown(get_binary_file_downloader_html(self.arquivo_dados, 'Relatório Atividades'), unsafe_allow_html=True)
        else:
            st.warning("Nenhum dado disponível para exportação.")

    def zerar_dados(self):
        st.write("Zerando dados...")
        st.session_state.registro['df'] = pd.DataFrame(columns=['ID', 'Nome_Usuário', 'Frente_Serviço', 'Função', 'Atividade', 'Data', 'Início', 'Fim', 'Duração'])
        st.success("Dados zerados. Você pode iniciar novos registros.")

# Função auxiliar para criar botão de download
def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">{file_label}</a>'
    return href

# Adicionado um identificador único para cada usuário usando o UUID
user_id = str(uuid.uuid4())
registro = RegistroAtividades(user_id)

class AnaliseAtividades:
    def __init__(self, user_id):
        self.user_id = user_id
        self.arquivo_dados = f'analise_atividades_{self.user_id}.xlsx'
        self.iniciar_arquivo_excel()
        self.iniciar_sessao()

    def iniciar_arquivo_excel(self):
        if not os.path.exists(self.arquivo_dados):
            df = pd.DataFrame(columns=['Nome_Usuario', 'Frente_Servico', 'Atividade', 'Quantidade'])
            df.to_excel(self.arquivo_dados, index=False)

    def iniciar_sessao(self):
        if 'analise' not in st.session_state:
            st.session_state.analise = {
                'nome_usuario': '',
                'frente_servico': '',
                'quantidade_equipe': 0,
                'atividades_quantidades': {},
                'df': pd.DataFrame(columns=['Nome_Usuario', 'Frente_Servico', 'Atividade', 'Quantidade'])
            }

def obter_informacoes_iniciais(self):
    if not st.session_state.analise['nome_usuario']:
        st.session_state.analise['nome_usuario'] = st.text_input("Digite seu nome:").upper()

    if not st.session_state.analise['frente_servico']:
        st.session_state.analise['frente_servico'] = st.text_input("Digite a frente de serviço:").upper()

    if not st.session_state.analise['quantidade_equipe']:
        st.session_state.analise['quantidade_equipe'] = st.number_input("Digite a quantidade de membros da equipe:", min_value=1, step=1, value=1)

    st.sidebar.subheader("Divisão da Equipe")
    analise.obter_informacoes_iniciais()
  
    def selecionar_atividades(self):
        opcoes_atividades = [
            "Andando sem ferramenta", "Ao Celular / Fumando", "Aguardando Almoxarifado",
            "À disposição", "Necessidades Pessoais (Água/Banheiro)", "Operando",
            "Auxiliando", "Ajustando Ferramenta ou Equipamento", "Deslocando com ferramenta em mãos",
            "Em prontidão", "Conversando com Encarregado/Operários (Informações Técnicas)"
        ]

        atividades_quantidades = {}

        for atividade in opcoes_atividades:
            key = f"{atividade}_{self.user_id}_{i}"
            quantidade = st.number_input(
                f"Quantidade de pessoas fazendo '{atividade}':",
                min_value=0, max_value=st.session_state.analise['quantidade_equipe'], step=1, value=0,
                key=key
            )
            if quantidade > 0:
                atividades_quantidades[atividade] = quantidade

        return atividades_quantidades

    def registrar_atividades_quantidades(self, atividades_quantidades):
        for atividade, quantidade in atividades_quantidades.items():
            registro_existente = st.session_state.analise['df'][
                (st.session_state.analise['df']['Nome_Usuario'] == st.session_state.analise['nome_usuario']) &
                (st.session_state.analise['df']['Frente_Servico'] == st.session_state.analise['frente_servico']) &
                (st.session_state.analise['df']['Atividade'] == atividade)
            ]

            if not registro_existente.empty:
                # Se o registro já existir, atualiza a quantidade
                st.session_state.analise['df'].loc[registro_existente.index, 'Quantidade'] = quantidade
            else:
                # Se o registro não existir, adiciona um novo
                novo_registro = {
                    'Nome_Usuario': st.session_state.analise['nome_usuario'],
                    'Frente_Servico': st.session_state.analise['frente_servico'],
                    'Atividade': atividade,
                    'Quantidade': quantidade
                }
                st.session_state.analise['df'] = pd.concat([st.session_state.analise['df'], pd.DataFrame([novo_registro])], ignore_index=True)

    def gerar_relatorio_excel(self):
        df = st.session_state.analise['df']

        # Cria um link para download do arquivo Excel
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        writer.save()
        excel_data = output.getvalue()
        output.seek(0)

        # Gera um link de download
        b64 = base64.b64encode(excel_data).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="analise_atividades_{self.user_id}.xlsx">Baixar Relatório Excel</a>'
        st.markdown(href, unsafe_allow_html=True)

    def zerar_analise(self):
        st.session_state.analise = {
            'nome_usuario': '',
            'frente_servico': '',
            'quantidade_equipe': 0,
            'atividades_quantidades': {},
            'df': pd.DataFrame(columns=['Nome_Usuario', 'Frente_Servico', 'Atividade', 'Quantidade'])
        }
        st.success("Análise zerada. Agora você pode iniciar uma nova análise.")

    def iniciar_analise(self):
        self.obter_informacoes_iniciais()

        quantidade_equipe = st.session_state.analise['quantidade_equipe']

        for i in range(1, quantidade_equipe + 1):
            st.write(f"Funcionário {i}:")

            # Obter atividades para o funcionário atual
            atividades_quantidades = self.selecionar_atividades()

            # Registrar atividades no dataframe
            self.registrar_atividades_quantidades(atividades_quantidades)

        st.write("Análise concluída para a equipe.")

        # Adiciona botões
        if st.button("Baixar Relatório Excel"):
            self.gerar_relatorio_excel()

        if st.button("Zerar Análise"):
            self.zerar_analise()
            
# Adicionado um identificador único para cada usuário usando o UUID
user_id = str(uuid.uuid4())
registro = RegistroAtividades(user_id)
analise = AnaliseAtividades(user_id)

def descricao_app1():
    st.title("App 1 - Registro de Atividades (AtividadeTracker)")
    st.write(
        "O AtividadeTracker é uma aplicação projetada para simplificar o registro "
        "de atividades individuais de membros de uma equipe. Com essa ferramenta intuitiva, "
        "os usuários podem facilmente monitorar e documentar as atividades realizadas durante um determinado período.\n\n"
        "Principais recursos do AtividadeTracker:\n"
        "- Registro Individual: Permite que cada membro da equipe registre suas atividades de maneira personalizada.\n"
        "- Controle de Tempo: Registra automaticamente o início e o fim de cada atividade, calculando a duração total.\n"        
        "Seja para equipes de construção civil, escritórios ou outros setores, "
        "o AtividadeTracker simplifica o processo de rastreamento de atividades, "
        "promovendo uma gestão mais eficiente do tempo e recursos."
    )

def descricao_app2():
    st.title("App 2 - Análise de Atividades (ConstruData Insights)")
    st.write(
        "O ConstruData Insights é uma aplicação especializada na análise e visualização da distribuição "
        "de pessoas em diferentes atividades no setor da construção civil. Esta ferramenta foi desenvolvida "
        "para oferecer insights valiosos sobre a produtividade da equipe e otimizar a alocação de recursos.\n\n"
        "Principais recursos do ConstruData Insights:\n"
        "- Análise de Atividades: Permite aos usuários selecionar e quantificar diversas atividades com base em critérios específicos.\n"
        "- Tempo Real: Oferece informações em tempo real sobre a distribuição de equipe em diferentes tarefas.\n"
        "Seja para gestores de projeto, supervisores ou tomadores de decisão, "
        "o ConstruData Insights é uma ferramenta valiosa para melhorar a eficiência operacional e a produtividade "
        "na indústria da construção civil."
    )

def informacoes():
    st.title("Informações")
    st.write("Bem-vindo à página de informações. Aqui você encontrará detalhes sobre os aplicativos.")

    st.header("Sobre o App 1:")
    descricao_app1()

    st.header("Sobre o App 2:")
    descricao_app2()

# Gráficos
def graficos():
    st.title("Gráficos")
    st.write("Bem-vindo à página de gráficos. Aqui você encontrará representações visuais baseadas nos dados coletados.")

# Função principal
def main():
    st.sidebar.title("Menu de Navegação")
    app_choice = st.sidebar.radio("Selecione uma opção:", ("App 1 - AtividadeTracker", "App 2 - ConstruData Insights", "Informações", "Gráficos"))

    if app_choice == "App 1 - AtividadeTracker":
        registro.registrar_atividades()

    elif app_choice == "App 2 - ConstruData Insights":
        # Implementando a lógica do App 2
        analise.iniciar_analise()

    elif app_choice == "Informações":
        informacoes()  # Adicione a lógica do App de Informações aqui

    elif app_choice == "Gráficos":
        graficos()  # Adicione a lógica do App de Gráficos aqui

if __name__ == "__main__":
    main()
