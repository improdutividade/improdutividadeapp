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
        self.arquivo_dados = 'dados.xlsx'
        self.nome_usuario = st.text_input("Digite o seu nome de usuário:")
        self.frente_servico = st.text_input("Digite a frente de serviço:")
        self.quantidade_equipe = st.number_input("Digite a quantidade da equipe:", min_value=1, value=1)
        self.funcao_funcionario = st.text_input("Digite a função do funcionário:")
        self.atividades_disponiveis = ["Andando sem ferramenta", "Ao Celular / Fumando", "Aguardando Almoxarifado",
                                       "À disposição", "Necessidades Pessoais (Água/Banheiro)", "Operando",
                                       "Auxiliando", "Ajustando Ferramenta ou Equipamento", "Deslocando com ferramenta em mãos",
                                       "Em prontidão", "Conversando com Encarregado/Operários (Informações Técnicas)"]
        self.escolha_atividade = st.selectbox("Escolha a atividade:", self.atividades_disponiveis)
        self.id_sessao = self.obter_id_sessao()

    def obter_id_sessao(self):
        if "id_sessao" not in st.session_state:
            # Gera um UUID único para a sessão
            st.session_state.id_sessao = str(uuid.uuid4())
        return st.session_state.id_sessao

    def iniciar_atividade(self, id_sessao, funcao, atividade):
        # Lógica para iniciar atividade
        pass

    def encerrar_atividade(self, id_sessao, quantidade_equipe, funcao_funcionario, escolha_atividade):
        # Lógica para encerrar atividade
        # Aqui você precisa ajustar a leitura e manipulação do DataFrame conforme a sua necessidade
        df = pd.read_excel(self.arquivo_dados)
        
        for _ in range(quantidade_equipe):
            # Simulando o encerramento para cada membro da equipe
            funcionario_id = id_sessao  # Use o ID da sessão como identificador único do funcionário (ajuste conforme necessário)
            funcionario_df = df[df['ID'] == funcionario_id]

            # Atualizar o DataFrame conforme necessário
            # ...

            # Após a atualização, você pode salvar novamente o DataFrame no arquivo
            # df.to_excel(self.arquivo_dados, index=False)

    def exportar_para_excel(self):
        # Lógica para exportar dados para Excel
        # Aqui você precisa ajustar conforme a estrutura do seu DataFrame
        pass

# Utilização
registro = RegistroAtividades()

# Botões para interação do usuário
if st.button("Iniciar Atividade"):
    registro.iniciar_atividade(registro.id_sessao, registro.funcao_funcionario, registro.escolha_atividade)

if st.button("Encerrar Atividade"):
    registro.encerrar_atividade(registro.id_sessao, registro.quantidade_equipe, registro.funcao_funcionario, registro.escolha_atividade)

# Botão para exportar para Excel
if st.button("Exportar para Excel"):
    registro.exportar_para_excel()

# Botão para zerar dados
if st.button("Zerar Dados"):
    # Lógica para zerar dados
    pass
