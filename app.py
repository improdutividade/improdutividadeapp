import streamlit as st
import pandas as pd
import datetime
import os

class RegistroAtividades:
    def __init__(self):
        self.arquivo_dados = 'registros_atividades.xlsx'
        self.iniciar_arquivo_excel()

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

    def selecionar_atividade(self, funcionario_id):
        opcoes_atividades = [
            '- TRABALHANDO',
            '- FORNECENDO APOIO',
            '- EM TRÂNSITO AO LOCAL DE TRABALHO',
            '- IDA AO BANHEIRO',
            '- DESCANSANDO'
        ]

        atividade = st.selectbox(f"Selecione a atividade para funcionário {funcionario_id}:", opcoes_atividades, key=f"atividade_{funcionario_id}")
        return atividade

    def registrar_atividade(self, funcionario_id):
        nome_funcao = st.text_input(f"Informe a função do funcionário {funcionario_id}: ", key=f"funcao_{funcionario_id}").upper()

        iniciar = st.button(f"Iniciar atividade para funcionário {funcionario_id}")
        if iniciar:
            atividade = self.selecionar_atividade(funcionario_id)

            novo_registro = {
                'ID': funcionario_id,
                'Nome_Usuário': self.nome_usuario,
                'Frente_Serviço': self.frente_servico,
                'Função': nome_funcao,
                'Atividade': atividade,
                'Data': datetime.datetime.now().strftime("%Y-%m-%d"),
                'Início': datetime.datetime.now().strftime("%H:%M:%S"),
                'Fim': '',
                'Duração': ''
            }

            df = pd.read_excel(self.arquivo_dados)
            df = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
            df.to_excel(self.arquivo_dados, index=False)

            st.success(f"Atividade '{atividade}' iniciada para funcionário {funcionario_id} ({nome_funcao})")

        encerrar = st.button(f"Encerrar atividade para funcionário {funcionario_id}")
        if encerrar:
            self.encerrar_atividade(funcionario_id)

    def encerrar_atividade(self, funcionario_id):
        df = pd.read_excel(self.arquivo_dados)

        funcionario_df = df[df['ID'] == funcionario_id]

        if len(funcionario_df) > 0:
            inicio = funcionario_df.iloc[-1]['Início']
            if pd.isnull(inicio):
                st.error("Atividade ainda não iniciada para este funcionário.")
                return

            df.loc[(df['ID'] == funcionario_id) & (df.index == len(funcionario_df) - 1), 'Fim'] = datetime.datetime.now().strftime("%H:%M:%S")
            fim = datetime.datetime.now()
            duracao = fim - pd.to_datetime(inicio)
            df.loc[(df['ID'] == funcionario_id) & (df.index == len(funcionario_df) - 1), 'Duração'] = duracao
            df.to_excel(self.arquivo_dados, index=False)
            st.success(f"Atividade encerrada para funcionário {funcionario_id} às {fim.strftime('%H:%M:%S')}")
        else:
            st.error("ID do funcionário inválido.")

    def gerar_relatorio_excel(self):
        st.write(f"Dados salvos em '{self.arquivo_dados}'")

# Criar instância da classe RegistroAtividades
registro = RegistroAtividades()

# Registrar atividades da equipe
registro.registrar_atividades_equipe()

# Gerar relatório em Excel
registro.gerar_relatorio_excel()
