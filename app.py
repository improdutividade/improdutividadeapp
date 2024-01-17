import streamlit as st
import pandas as pd
import datetime
import pytz
import os
import base64
from io import BytesIO
import uuid

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">{file_label}</a>'
    return href

class RegistroAtividades:
    def __init__(self):
        self.arquivo_dados = 'dados.xlsx'
        self.nome_usuario = st.text_input("Digite o seu nome de usuário:")
        self.frente_servico = st.text_input("Digite a frente de serviço:")
        self.quantidade_equipe = st.number_input("Digite a quantidade da equipe:", min_value=1, value=1)
        self.atividades_disponiveis = ["Andando sem ferramenta", "Ao Celular / Fumando", "Aguardando Almoxarifado",
                                       "À disposição", "Necessidades Pessoais (Água/Banheiro)", "Operando",
                                       "Auxiliando", "Ajustando Ferramenta ou Equipamento", "Deslocando com ferramenta em mãos",
                                       "Em prontidão", "Conversando com Encarregado/Operários (Informações Técnicas)"]
        self.id_sessao = self.obter_id_sessao()
        self.dados_equipe = []

    def obter_id_sessao(self):
        if "id_sessao" not in st.session_state:
            st.session_state.id_sessao = str(uuid.uuid4())
        return st.session_state.id_sessao

    def iniciar_atividade(self, id_sessao, funcao, atividade):
        data_hora_inicio = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        dados_membro = {'id': id_sessao, 'funcao': funcao, 'atividade': atividade, 'inicio': data_hora_inicio}
        self.dados_equipe.append(dados_membro)

    def encerrar_atividade(self, id_sessao, funcao_funcionario, escolha_atividade):
        for membro_equipe in self.dados_equipe:
            funcionario_id = membro_equipe['id']
            if funcionario_id == id_sessao:
                data_hora_fim = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                membro_equipe['fim'] = data_hora_fim
                break

    def exportar_para_excel(self):
        df = pd.DataFrame(self.dados_equipe)
        df.to_excel(self.arquivo_dados, index=False, header=True)

# Utilização
registro = RegistroAtividades()

for i in range(registro.quantidade_equipe):
    st.subheader(f"Informações do Funcionário {i + 1}")
    prefixo = f"funcionario_{i + 1}"
    funcao_funcionario = st.text_input(f"{prefixo} - Digite a função do funcionário:")
    escolha_atividade = st.selectbox(f"{prefixo} - Escolha a atividade:", registro.atividades_disponiveis)

    if st.button(f"{prefixo} - Iniciar Atividade"):
        registro.iniciar_atividade(registro.id_sessao, funcao_funcionario, escolha_atividade)

    if st.button(f"{prefixo} - Encerrar Atividade"):
        registro.encerrar_atividade(registro.id_sessao, funcao_funcionario, escolha_atividade)

# Botão para exportar para Excel
if st.button("Exportar para Excel"):
    registro.exportar_para_excel()
    st.success("Dados exportados para Excel.")

    # Criar link de download
    st.markdown(get_binary_file_downloader_html(registro.arquivo_dados, 'Baixar Excel'), unsafe_allow_html=True)

# Botão para zerar dados
if st.button("Zerar Dados"):
    registro.dados_equipe = []
    st.success("Dados zerados.")
