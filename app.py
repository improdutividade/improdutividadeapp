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
        self.arquivo_dados = "registro_atividades.xlsx"
        self.iniciar_arquivo_excel()

        self.id_sessao = st.session_state.id_sessao if "id_sessao" in st.session_state else st.session_state.__setitem__("id_sessao", st.session.id)
        self.nome_usuario = ''
        self.frente_servico = ''

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

        # Adiciona botão para download do Excel preenchido
        if st.button("Baixar Relatório Excel"):
            self.gerar_relatorio_excel()

        # Adiciona botão para reiniciar os dados
        if st.button("Zerar Dados"):
            self.zerar_dados()

    def selecionar_atividade(self, funcionario_id):
        opcoes_atividades = [
            'TRABALHANDO',
            'FORNECENDO APOIO',
            'EM TRÂNSITO AO LOCAL DE TRABALHO',
            'IDA AO BANHEIRO',
            'DESCANSANDO'
        ]

        atividade = st.selectbox(f"Selecione a atividade para funcionário {funcionario_id}:", opcoes_atividades, key=f"atividade_{funcionario_id}")
        return atividade

    def registrar_atividade(self, funcionario_id):
        # Exibir informações iniciais
        st.write(f"Funcionário {funcionario_id}:")
        nome_funcao = st.text_input(f"Informe a função para funcionário {funcionario_id}: ", key=f"funcao_{funcionario_id}").upper()

        # Exibir seletor de atividades, botões e processar a atividade
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
            'Nome_Usuário': self.nome_usuario,
            'Frente_Serviço': self.frente_servico,
            'Função': nome_funcao,
            'Atividade': atividade,
            'Data': datetime.now().strftime("%Y-%m-%d"),
            'Início': datetime.now().strftime("%H:%M:%S"),
            'Fim': '',
            'Duração': ''
        }

        df = pd.read_excel(self.arquivo_dados)

        # Verifica se há uma atividade em andamento para este funcionário
        atividade_em_andamento = df[(df['ID'] == funcionario_id) & (df['Fim'] == '')]

        if not atividade_em_andamento.empty:
            st.error(f"Atividade já iniciada para funcionário {funcionario_id}.")
        else:
            df = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
            df.to_excel(self.arquivo_dados, index=False)
            st.success(f"Atividade '{atividade}' iniciada para funcionário {funcionario_id} ({nome_funcao})")

    def encerrar_atividade(self, funcionario_id):
        df = pd.read_excel(self.arquivo_dados)

        # Localiza a atividade em andamento para este funcionário
        atividade_em_andamento = df[(df['ID'] == funcionario_id) & (df['Fim'] == '')]

        if atividade_em_andamento.empty:
            st.error(f"Nenhuma atividade em andamento para funcionário {funcionario_id}.")
        else:
            # Atualiza o registro com a data/hora de encerramento e calcula a duração
            df.loc[atividade_em_andamento.index, 'Fim'] = datetime.now().strftime("%H:%M:%S")
            df.loc[atividade_em_andamento.index, 'Duração'] = (datetime.now() - pd.to_datetime(atividade_em_andamento['Início'])).total_seconds() / 60.0
            df.to_excel(self.arquivo_dados, index=False)
            st.success(f"Atividade encerrada para funcionário {funcionario_id} às {datetime.now().strftime('%H:%M:%S')}")

    def gerar_relatorio_excel(self):
        st.write(f"Dados salvos em '{self.arquivo_dados}'")

    def zerar_dados(self):
        # Adiciona a confirmação para evitar exclusão acidental
        confirmacao = st.text_input("Para zerar os dados, digite 'CONFIRMAR':").upper()

        if confirmacao == 'CONFIRMAR':
            os.remove(self.arquivo_dados)
            st.success("Dados zerados com sucesso.")
        else:
            st.warning("Confirmação incorreta. Os dados não foram zerados.")

# Instancia a classe e executa o app
registro = RegistroAtividades()
registro.registrar_atividades_equipe()
