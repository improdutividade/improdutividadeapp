import streamlit as st
import pandas as pd
import datetime
import pytz
import os
import base64
from io import BytesIO

class RegistroAtividades:
    def __init__(self):
        self.arquivo_dados = 'dados.xlsx'
        self.nome_usuario = st.text_input("Digite o seu nome de usuário:")
        self.frente_servico = st.text_input("Digite a frente de serviço:")
        self.id_sessao = st.session_state.id_sessao if "id_sessao" in st.session_state else st.session_state.__setitem__("id_sessao", st.session.id) or st.session.id

    def obter_id_sessao(self):
        return st.session.get_session().id

    def iniciar_atividade(self, funcionario_id, nome_funcao, atividade):
        novo_registro = {
            'ID': funcionario_id,
            'Nome_Usuário': self.nome_usuario,
            'Frente_Serviço': self.frente_servico,
            'Função': nome_funcao,
            'Atividade': atividade,
            'Data': datetime.datetime.now(pytz.timezone('America/Sao_Paulo')).strftime("%Y-%m-%d"),
            'Início': datetime.datetime.now(pytz.timezone('America/Sao_Paulo')).strftime("%H:%M:%S"),
            'Fim': datetime.datetime.now(pytz.timezone('America/Sao_Paulo')).strftime("%H:%M:%S"),
            'Duração': ''
        }

        df = pd.DataFrame([novo_registro])
        df.to_excel(self.arquivo_dados, index=False, header=not st.session_state.get('dados_carregados', False))
        st.session_state.dados_carregados = True
        st.success("Atividade iniciada com sucesso!")

    def encerrar_atividade(self, funcionario_id):
        df = pd.read_excel(self.arquivo_dados)

        funcionario_df = df[df['ID'] == funcionario_id]

        if len(funcionario_df) > 0:
            inicio = funcionario_df.iloc[-1]['Início']
            if pd.isnull(inicio):
                st.error("Atividade ainda não iniciada para este funcionário.")
                return

            fim = datetime.datetime.now(pytz.timezone('America/Sao_Paulo'))
            df.loc[(df['ID'] == funcionario_id) & (df.index == len(funcionario_df) - 1), 'Fim'] = fim.strftime("%H:%M:%S")
            duracao = fim - pd.to_datetime(inicio)
            df.loc[(df['ID'] == funcionario_id) & (df.index == len(funcionario_df) - 1), 'Duração'] = duracao
            df.to_excel(self.arquivo_dados, index=False)
            st.success(f"Atividade encerrada para funcionário {funcionario_id} às {fim.strftime('%H:%M:%S')}")
        else:
            st.error("ID do funcionário inválido.")

# Utilização
registro = RegistroAtividades()

# Botões para interação do usuário
if st.button("Iniciar Atividade"):
    registro.iniciar_atividade(registro.id_sessao, "Função Padrão", "Atividade Padrão")

if st.button("Encerrar Atividade"):
    registro.encerrar_atividade(registro.id_sessao)
