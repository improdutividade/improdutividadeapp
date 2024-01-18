import streamlit as st
import pandas as pd
import datetime
import pytz
import os
import base64
from io import BytesIO
import uuid

class RegistroAtividades:
    def __init__(self):
        self.uuid = str(uuid.uuid4())  # Adicionado identificador único para cada instância
        self.arquivo_dados = f'registros_atividades_{self.uuid}.xlsx'  # Utilizando UUID no nome do arquivo
        self.iniciar_arquivo_excel()

    # Restante do código permanece inalterado

    def iniciar_arquivo_excel(self):
        if not os.path.exists(self.arquivo_dados):
            df = pd.DataFrame(columns=['ID', 'Nome_Usuário', 'Frente_Serviço', 'Função', 'Atividade', 'Data', 'Início', 'Fim', 'Duração'])
            df.to_excel(self.arquivo_dados, index=False)

    # Restante do código permanece inalterado

    def iniciar_atividade(self, funcionario_id, nome_funcao, atividade):
        novo_registro = {
            'ID': funcionario_id,
            'Nome_Usuário': self.nome_usuario,
            'Frente_Serviço': self.frente_servico,
            'Função': nome_funcao,
            'Atividade': atividade,
            'Data': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime("%Y-%m-%d"),  # Utilizando fuso horário de Brasília
            'Início': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime("%H:%M:%S"),  # Utilizando fuso horário de Brasília
            'Fim': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime("%H:%M:%S"),  # Utilizando fuso horário de Brasília
            'Duração': ''
        }

        df = pd.read_excel(self.arquivo_dados)
        df = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
        df.to_excel(self.arquivo_dados, index=False)

        st.success(f"Atividade '{atividade}' iniciada para funcionário {funcionario_id} ({nome_funcao})")

    # Restante do código permanece inalterado

# Restante do código permanece inalterado

# Adicionado um botão para reiniciar o Streamlit e evitar conflitos entre usuários simultâneos
if st.button("Reiniciar"):
    os.execv(sys.executable, ['python'] + sys.argv)
