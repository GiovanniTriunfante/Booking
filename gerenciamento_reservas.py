import pandas as pd
from datetime import datetime, timedelta
import os


class GerenciamentoReservas:
    def __init__(self, reservas_path, parceiros_path, proprietarios_path):
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Caminhos para os arquivos
        self.reservas_path = os.path.join(current_dir, reservas_path)
        self.parceiros_path = os.path.join(current_dir, parceiros_path)
        self.proprietarios_path = os.path.join(current_dir, proprietarios_path)
        
        # Carregar dados das planilhas
        self.df_reservas = self.load_data(self.reservas_path)
        self.df_parceiros = self.load_data(self.parceiros_path)
        self.df_proprietarios = self.load_data(self.proprietarios_path)

        # Verificar e adicionar colunas faltantes para as informações do responsável na tabela de reservas
        self.ensure_responsavel_columns()

    def ensure_responsavel_columns(self):
        """Verifica se as colunas do responsável estão presentes no DataFrame de reservas e as adiciona, se necessário."""
        required_columns = ['Email do responsável', 'Telefone do responsável', 'Documento do responsável']
        for col in required_columns:
            if col not in self.df_reservas.columns:
                self.df_reservas[col] = None  # Adiciona a coluna com valores nulos se não existir

    

    def calcular_totais_semanal(self):
     today = datetime.today().date()
     start_week = today - timedelta(days=today.weekday())  # Início da semana
     end_week = start_week + timedelta(days=6)  # Fim da semana

     # Converte as colunas 'Data de entrada' e 'Data de saída' para o tipo 'date'
     self.df_reservas['Data de entrada'] = pd.to_datetime(self.df_reservas['Data de entrada']).dt.date
     self.df_reservas['Data de saída'] = pd.to_datetime(self.df_reservas['Data de saída']).dt.date

     # Filtra as reservas da semana atual
     reservas_semanal = self.df_reservas[
        (self.df_reservas['Data de entrada'] <= end_week) &
        (self.df_reservas['Data de saída'] >= start_week)
     ]

     # Calcula totais incluindo novas colunas
     total_hospedagem = reservas_semanal['Valor da hospedagem'].sum()
     total_a_pagar = reservas_semanal['A pagar'].sum()
     total_a_receber_parceiros = reservas_semanal['A receber de parceiros'].sum()
     valor_para_proprietario = reservas_semanal['Valor para o proprietário'].sum()

     apartamentos_ocupados = reservas_semanal['Número do apartamento'].nunique()

     return reservas_semanal, total_hospedagem, total_a_pagar, total_a_receber_parceiros, valor_para_proprietario, apartamentos_ocupados

    def load_data(self, file_path):
        """Carrega dados de uma planilha Excel e retorna um DataFrame."""
        try:
            df = pd.read_excel(file_path)
            print(f"Colunas carregadas de {file_path}: {df.columns.tolist()}")
            return df
        except FileNotFoundError:
            print(f"Erro: Arquivo '{file_path}' não encontrado.")
            return pd.DataFrame()
        except Exception as e:
            print(f"Erro ao carregar '{file_path}': {e}")
            return pd.DataFrame()

    def save_to_excel(self, df, file_path):
        """Salva DataFrames no formato Excel."""
        try:
            df.to_excel(file_path, index=False)
            print(f"Arquivo salvo com sucesso em: {file_path}")
        except Exception as e:
            print(f"Erro ao salvar arquivo Excel: {e}")

    


    # Métodos para gerenciar parceiros
    def gerar_relatorio_parceiros(self):
        """Gera um relatório dos parceiros com totais a receber e a pagar."""
        if not self.check_columns(self.df_parceiros, ['A receber', 'A pagar']):
            return pd.DataFrame(), 0, 0

        total_a_receber = self.df_parceiros['A receber'].sum()
        total_a_pagar = self.df_parceiros['A pagar'].sum()
        return self.df_parceiros, total_a_receber, total_a_pagar

    def adicionar_parceiro(self, parceiro, a_receber, a_pagar):
        """Adiciona um novo parceiro e salva no arquivo Excel diretamente no DataFrame."""
        new_data = pd.DataFrame({
            'Parceiro': [parceiro],
            'A receber': [a_receber],
            'A pagar': [a_pagar]
        })
        self.df_parceiros = pd.concat([self.df_parceiros, new_data], ignore_index=True)
        self.save_to_excel(self.df_parceiros, self.parceiros_path)

    def atualizar_parceiro(self, id_parceiro, parceiro, a_receber, a_pagar):
        """Atualiza um parceiro específico no DataFrame e salva no Excel."""
        if id_parceiro in self.df_parceiros.index:
            self.df_parceiros.at[id_parceiro, 'Parceiro'] = parceiro
            self.df_parceiros.at[id_parceiro, 'A receber'] = a_receber
            self.df_parceiros.at[id_parceiro, 'A pagar'] = a_pagar
            self.save_to_excel(self.df_parceiros, self.parceiros_path)
        else:
            print(f"Parceiro com ID {id_parceiro} não encontrado.")

    # Métodos para gerenciar proprietários
    def adicionar_proprietario(self, nome, email, telefone, documento):
        """Adiciona um novo proprietário e salva no arquivo Excel diretamente no DataFrame."""
        new_data = pd.DataFrame({
            'Nome Completo': [nome],
            'Email': [email],
            'Telefone': [telefone],
            'Documento': [documento]
        })
        self.df_proprietarios = pd.concat([self.df_proprietarios, new_data], ignore_index=True)
        self.save_to_excel(self.df_proprietarios, self.proprietarios_path)

    def atualizar_proprietario(self, id_proprietario, nome, email, telefone, documento):
        """Atualiza um proprietário específico no DataFrame e salva no Excel."""
        if id_proprietario in self.df_proprietarios.index:
            self.df_proprietarios.at[id_proprietario, 'Nome Completo'] = nome
            self.df_proprietarios.at[id_proprietario, 'Email'] = email
            self.df_proprietarios.at[id_proprietario, 'Telefone'] = telefone
            self.df_proprietarios.at[id_proprietario, 'Documento'] = documento
            self.save_to_excel(self.df_proprietarios, self.proprietarios_path)
        else:
            print(f"Proprietário com ID {id_proprietario} não encontrado.")

    # Métodos para gerenciar reservas
    def adicionar_reserva(self, nome, data_entrada, data_saida, numero_apartamento, 
                      valor_hospedagem, valor_proprietario, nome_proprietario, quantidade_pessoas,
                      condominio, bloco, endereco, status, 
                      a_receber_parceiros=0.0, a_pagar_parceiros=0.0,
                      email_responsavel=None, telefone_responsavel=None, documento_responsavel=None,
                      pago=0.0, a_pagar=0.0):
    # Dados da nova reserva com todas as colunas incluídas
     new_data = pd.DataFrame({
        'Nome do hóspede': [nome],
        'Data de entrada': [data_entrada],
        'Data de saída': [data_saida],
        'Número do apartamento': [numero_apartamento],
        'Valor da hospedagem': [valor_hospedagem],
        'Valor para o proprietário': [valor_proprietario],
        'Nome do proprietário': [nome_proprietario],
        'Quantidade de pessoas': [quantidade_pessoas],
        'Nome do Condomínio': [condominio],
        'Bloco': [bloco],
        'Endereço': [endereco],
        'Status': [status],
        'Pago': [pago],
        'A pagar': [a_pagar],
        'A receber de parceiros': [a_receber_parceiros],
        'A pagar para parceiros': [a_pagar_parceiros],
        'Email do responsável': [email_responsavel],
        'Telefone do responsável': [telefone_responsavel],
        'Documento do responsável': [documento_responsavel]
    })

    # Adiciona a nova reserva ao DataFrame e salva no Excel
     self.df_reservas = pd.concat([self.df_reservas, new_data], ignore_index=True)
     self.save_to_excel(self.df_reservas, self.reservas_path)

    def atualizar_reserva(self, id_reserva, nome, data_entrada, data_saida, numero_apartamento, 
                      valor_hospedagem, valor_proprietario, nome_proprietario, quantidade_pessoas,
                      condominio, bloco, endereco, status, 
                      a_receber_parceiros, a_pagar_parceiros, pago, a_pagar, 
                      email_responsavel=None, telefone_responsavel=None, documento_responsavel=None):
     """Atualiza uma reserva específica no DataFrame e salva no Excel."""
     if id_reserva in self.df_reservas.index:
        # Atualiza as informações da reserva, incluindo as novas colunas
        self.df_reservas.at[id_reserva, 'Nome do hóspede'] = nome
        self.df_reservas.at[id_reserva, 'Data de entrada'] = data_entrada
        self.df_reservas.at[id_reserva, 'Data de saída'] = data_saida
        self.df_reservas.at[id_reserva, 'Número do apartamento'] = numero_apartamento
        self.df_reservas.at[id_reserva, 'Valor da hospedagem'] = valor_hospedagem
        self.df_reservas.at[id_reserva, 'Valor para o proprietário'] = valor_proprietario
        self.df_reservas.at[id_reserva, 'Nome do proprietário'] = nome_proprietario
        self.df_reservas.at[id_reserva, 'Quantidade de pessoas'] = quantidade_pessoas
        self.df_reservas.at[id_reserva, 'Nome do Condomínio'] = condominio
        self.df_reservas.at[id_reserva, 'Bloco'] = bloco
        self.df_reservas.at[id_reserva, 'Endereço'] = endereco
        self.df_reservas.at[id_reserva, 'Status'] = status
        self.df_reservas.at[id_reserva, 'A receber de parceiros'] = a_receber_parceiros
        self.df_reservas.at[id_reserva, 'A pagar para parceiros'] = a_pagar_parceiros
        self.df_reservas.at[id_reserva, 'Pago'] = pago
        self.df_reservas.at[id_reserva, 'A pagar'] = a_pagar

        # Atualiza as informações do responsável, se fornecidas
        if email_responsavel is not None:
            self.df_reservas.at[id_reserva, 'Email do responsável'] = email_responsavel
        if telefone_responsavel is not None:
            self.df_reservas.at[id_reserva, 'Telefone do responsável'] = telefone_responsavel
        if documento_responsavel is not None:
            self.df_reservas.at[id_reserva, 'Documento do responsável'] = documento_responsavel

        # Salva as alterações no arquivo Excel
        self.save_to_excel(self.df_reservas, self.reservas_path)
        print(f"Reserva com ID {id_reserva} foi atualizada com sucesso.")
     else:
        print(f"Reserva com ID {id_reserva} não encontrada.")


    def check_columns(self, df, required_columns):
        """Verifica se as colunas necessárias estão presentes no DataFrame."""
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Erro: Colunas ausentes: {missing_columns}")
            return False
        return True
