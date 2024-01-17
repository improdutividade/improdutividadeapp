import streamlit as st
import pandas as pd
import datetime
import os
import base64
from io import BytesIO
import pytz

class RegistroAtividades:
    def __init__(self):
        self.id_sessao = self.obter_id_sessao()
        self.arquivo_dados = f'registros_atividades_{self.id_sessao}.xlsx'
        self.iniciar_arquivo_excel()

    def obter_id_sessao(self):
        if 'id_sessao' not in st.session_state:
            st.session_state.id_sessao = st.session.get_session().id
        return st.session_state.id_sessao

    def iniciar_arquivo_excel(self):
        if not os.path.exists(self.arquivo_dados):
            df = pd.DataFrame(columns=['ID', 'Nome_Usuário', 'Frente_Serviço', 'Função', 'Atividade', 'Data', 'Início', 'Fim', 'Duração'])
            df.to_excel(self.arquivo_dados, index=False)

    def obter_informacoes_iniciais(self):
        self.nome_usuario = st.text_input("Digite seu nome: ").upper()
        self.frente_servico = st.text_input("Digite a frente de serviço: ").upper()

    def registrar_atividades_equipe(self):
        self.obter_informacoes_iniciais()

        quantidade_equipe = st.number_input("Digite a quantidade de membros da equipe: ", min_value=1, step=1, value=1)

        for i in range(1, quantidade_equipe + 1):
            self.registrar_atividade(i)

        if st.button("Baixar Relatório Excel"):
            self.gerar_relatorio_excel()

        if st.button("Zerar Dados"):
            self.zerar_dados()

    def selecionar_atividade(self, funcionario_id):
        opcoes_atividades = [
            'Andando sem ferramenta',
            'Ao Celular / Fumando',
            'Aguardando Almoxarifado',
            'À disposição',
            'Necessidades Pessoais (Água/Banheiro)',
            'Operando',
            'Auxiliando',
            'Ajustando Ferramenta ou Equipamento',
            'Deslocando com ferramenta em mãos',
            'Em prontidão',
            'Conversando com Encarregado/Operários (Informações Técnicas)'
        ]

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
        tz_brasilia = pytz.timezone('America/Sao_Paulo')
        agora_brasilia = datetime.datetime.now(tz_brasilia)

        novo_registro = {
            'ID': funcionario_id,
            'Nome_Usuário': self.nome_usuario,
            'Frente_Serviço': self.frente_servico,
            'Função': nome_funcao,
            'Atividade': atividade,
            'Data': agora_brasilia.strftime("%Y-%m-%d"),
            'Início': agora_brasilia.strftime("%H:%M:%S"),
            'Fim': agora_brasilia.strftime("%H:%M:%S"),
            'Duração': ''
        }

        df = pd.read_excel(self.arquivo_dados)
        df = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
        df.to_excel(self.arquivo_dados, index=False)

        st.success(f"Atividade '{atividade}' iniciada para funcionário {funcionario_id} ({nome_funcao})")

    def encerrar_atividade(self, funcionario_id):
        df = pd.read_excel(self.arquivo_dados)

        funcionario_df = df[df['ID'] == funcionario_id]

        if len(funcionario_df) > 0:
            inicio = funcionario_df.iloc[-1]['Início']
            if pd.isnull(inicio):
                st.error("Atividade ainda não iniciada para este funcionário.")
                return

            df.loc[(df['ID'] == funcionario_id) & (df.index == len(funcionario_df) - 1), 'Fim'] = datetime.datetime.now().strftime("%H:%M:%S")
            fim = datetime.datetime.now(tz_brasilia)
            duracao = fim - pd.to_datetime(inicio)
            df.loc[(df['ID'] == funcionario_id) & (df.index == len(funcionario_df) - 1), 'Duração'] = duracao
            df.to_excel(self.arquivo_dados, index=False)
            st.success(f"Atividade encerrada para funcionário {funcionario_id} às {fim.strftime('%H:%M:%S')}")
        else:
            st.error("ID do funcionário inválido.")

    def gerar_relatorio_excel(self):
        st.write(f"Dados salvos em '{self.arquivo_dados}'")
        df = pd.read_excel(self.arquivo_dados)

        if not df.empty:
            st.markdown(get_binary_file_downloader_html(self.arquivo_dados, 'Relatório Atividades'), unsafe_allow_html=True)
        else:
            st.warning("Nenhum dado disponível para exportação.")

    def zerar_dados(self):
        df = pd.DataFrame(columns=['ID', 'Nome_Usuário', 'Frente_Serviço', 'Função', 'Atividade', 'Data', 'Início', 'Fim', 'Duração'])
        df.to_excel(self.arquivo_dados, index=False)
        st.success("Dados zerados. Você pode iniciar novos registros.")

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">{file_label}</a>'
    return href

registro = RegistroAtividades()
registro.registrar_atividades_equipe()
