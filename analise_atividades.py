import streamlit as st
import pandas as pd
import datetime
import pytz
import os
import base64
from io import BytesIO

class AnaliseAtividades:
    def __init__(self, user_id):
        self.user_id = user_id
        self.arquivo_dados = f'analise_atividades_{self.user_id}.xlsx'
        self.iniciar_sessao()

    def iniciar_sessao(self):
        if 'analise' not in st.session_state:
            st.session_state.analise = {
                'df': pd.DataFrame(columns=['Nome_Usuário', 'Frente_Serviço', 'Atividade', 'Início', 'Fim', 'Quantidade']),
                'nome_usuario': '',
                'frente_servico': '',
                'equipe_quantidade': 0,
                'equipe_distribuicao': {}
            }

    def obter_informacoes_iniciais(self):
        st.session_state.analise['nome_usuario'] = st.text_input("Digite seu nome: ").upper()
        st.session_state.analise['frente_servico'] = st.text_input("Digite a frente de serviço: ").upper()
        st.session_state.analise['equipe_quantidade'] = st.number_input("Digite a quantidade de membros da equipe: ", min_value=1, step=1, value=1)

    def distribuir_equipe_atividades(self):
        self.iniciar_sessao()

        opcoes_atividades = [
            "Andando sem ferramenta", "Ao Celular / Fumando", "Aguardando Almoxarifado",
            "À disposição", "Necessidades Pessoais (Água/Banheiro)", "Operando",
            "Auxiliando", "Ajustando Ferramenta ou Equipamento", "Deslocando com ferramenta em mãos",
            "Em prontidão", "Conversando com Encarregado/Operários (Informações Técnicas)"
        ]

        # Certifique-se de inicializar a chave 'equipe_distribuicao' no estado da sessão
        if 'equipe_distribuicao' not in st.session_state.analise:
            st.session_state.analise['equipe_distribuicao'] = {}

        st.write("Distribua a quantidade de membros da equipe entre as atividades:")
        for atividade in opcoes_atividades:
            quantidade_input = st.text_input(f"Quantidade para '{atividade}':")
            quantidade = int(quantidade_input) if quantidade_input.strip() else 0

            st.session_state.analise['equipe_distribuicao'][atividade] = quantidade

    def registrar_atividades_quantidades(self):
        # Inicializa o DataFrame df se não existir no estado da sessão
        if 'df' not in st.session_state.analise:
            st.session_state.analise['df'] = pd.DataFrame(columns=['Nome_Usuário', 'Frente_Serviço', 'Atividade', 'Início', 'Fim', 'Quantidade'])

        df = st.session_state.analise['df']

        # Verifica se há alguma atualização nas atividades
        if any(st.session_state.analise['equipe_distribuicao'].values()):
            for atividade, quantidade in st.session_state.analise['equipe_distribuicao'].items():
                # Obtemos o horário atual no fuso horário de Brasília
                horario_brasilia = datetime.datetime.now(pytz.timezone('America/Sao_Paulo')).strftime("%H:%M:%S")

                novo_registro = {
                    'Nome_Usuário': st.session_state.analise['nome_usuario'],
                    'Frente_Serviço': st.session_state.analise['frente_servico'],
                    'Atividade': atividade,
                    'Início': horario_brasilia,
                    'Fim': '',
                    'Quantidade': quantidade
                }

                df = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
                st.session_state.analise['df'] = df

                st.success(f"Atividade '{atividade}' registrada com {quantidade} pessoa(s).")

            # Zera a equipe_distribuicao após o registro
            st.session_state.analise['equipe_distribuicao'] = {}

    def gerar_relatorio_excel(self):
        st.write(f"Dados salvos em '{self.arquivo_dados}'")

        df = st.session_state.analise['df']

        if not df.empty:
            df.to_excel(self.arquivo_dados, index=False)
            st.markdown(get_binary_file_downloader_html(self.arquivo_dados, 'Relatório Atividades'), unsafe_allow_html=True)
        else:
            st.warning("Nenhum dado disponível para exportação.")

    def zerar_dados(self):
        # Zera todos os dados da sessão e exclui o arquivo Excel
        st.session_state.analise = {}
        if os.path.exists(self.arquivo_dados):
            os.remove(self.arquivo_dados)

# Função auxiliar para criar botão de download
def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">{file_label}</a>'
    return href
