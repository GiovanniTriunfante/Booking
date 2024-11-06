import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
import os

# Importe a classe GerenciamentoReservas do arquivo onde ela foi definida
from gerenciamento_reservas import GerenciamentoReservas 

# Função para exibir a página inicial do dashboard
def dashboard_home(reservas):
    st.title("Gerenciamento de Reserva - Home")
    st.write("Bem-vindo ao sistema de gerenciamento de reservas!")
    
    st.subheader("Tabela de Reservas")
    st.dataframe(reservas.df_reservas)  # Exibe a tabela de reservas

    st.subheader("Tabela de Parceiros")
    st.dataframe(reservas.df_parceiros)  # Exibe a tabela de parceiros

    st.subheader("Tabela de Proprietários")
    st.dataframe(reservas.df_proprietarios)  # Exibe a tabela de proprietários

# Função para exibir a página de relatórios
def relatorios(reservas):
    st.title("Relatórios")

    # Botão para recarregar dados
    if st.button("Recarregar Dados", key="recarregar_dados"):
        reservas.df_reservas = reservas.load_data(reservas.reservas_path)
        reservas.df_parceiros = reservas.load_data(reservas.parceiros_path)
        reservas.df_proprietarios = reservas.load_data(reservas.proprietarios_path)
        st.success("Dados recarregados com sucesso!")
    
    exibir_relatorio_semanal(reservas)
    exibir_relatorio_parceiros(reservas)

# Função para exibir a página de gestão de reservas
def gestao_reservas(reservas):
    st.title("Gestão de Reservas")
    adicionar_nova_reserva(reservas)
    editar_reservas(reservas)
    exibir_detalhamento_reservas(reservas)

# Função para exibir a página de gestão de parceiros
def gestao_parceiros(reservas):
    st.title("Gestão de Parceiros")
    adicionar_novo_parceiro(reservas)
    editar_parceiros(reservas)

# Função para exibir a página de gestão de proprietários
def gestao_proprietarios(reservas):
    st.title("Gestão de Proprietários")
    adicionar_novo_proprietario(reservas)
    editar_proprietarios(reservas)

# Funções para exibir relatórios, adicionar e editar dados:
def exibir_relatorio_semanal(reservas):
    st.subheader("Relatório Semanal")
    df_semanal, total_hospedagem, total_a_pagar, total_a_receber_parceiros, apartamentos_ocupados = reservas.calcular_totais_semanal()
    
    st.write("**Valor total da hospedagem:**", total_hospedagem)
    st.write("**Total a pagar ao proprietário:**", total_a_pagar)
    st.write("**Total a receber dos parceiros:**", total_a_receber_parceiros)
    st.write("**Número de apartamentos ocupados na semana:**", apartamentos_ocupados)

    grafico_df = pd.DataFrame({
        'Descrição': ['Total Hospedagem', 'Total a Pagar', 'Total a Receber'],
        'Valores': [total_hospedagem, total_a_pagar, total_a_receber_parceiros]
    })
    fig = px.bar(grafico_df, x='Descrição', y='Valores', title="Totais Semanais")
    st.plotly_chart(fig)

def exibir_relatorio_parceiros(reservas):
    st.subheader("Relatório de Parceiros")
    df_parceiros, total_a_receber, total_a_pagar = reservas.gerar_relatorio_parceiros()

    st.write("**Total a receber dos parceiros:**", total_a_receber)
    st.write("**Total a pagar aos parceiros:**", total_a_pagar)
    st.write("**Resumo por Parceiro:**")
    st.dataframe(df_parceiros)

    fig = px.bar(df_parceiros, x='Parceiro', y=['A receber', 'A pagar'], title="Valores a Receber e Pagar por Parceiro")
    st.plotly_chart(fig)

def exibir_detalhamento_reservas(reservas):
    st.subheader("Detalhes das Reservas Semanais")
    df_semanal, *_ = reservas.calcular_totais_semanal()
    st.dataframe(df_semanal[['Nome do hóspede', 'Data de entrada', 'Data de saída', 
                             'Número do apartamento', 'Valor da hospedagem',
                             'Nome do Condomínio', 'Bloco', 'Endereço']])

def adicionar_nova_reserva(reservas):
    with st.expander("Adicionar Nova Reserva"):
        # Dados básicos da reserva
        nome = st.text_input("Nome do Hóspede", key="nome_hospede_novo")
        data_entrada = st.date_input("Data de Entrada", date.today(), key="data_entrada_novo")
        data_saida = st.date_input("Data de Saída", date.today() + timedelta(days=1), key="data_saida_novo")
        numero_apartamento = st.number_input("Número do Apartamento", min_value=1, step=1, key="numero_apartamento_novo")
        valor_hospedagem = st.number_input("Valor da Hospedagem", min_value=0.0, step=0.01, key="valor_hospedagem_novo")
        valor_proprietario = st.number_input("Valor para o Proprietário", min_value=0.0, step=0.01, key="valor_proprietario_novo")
        quantidade_pessoas = st.number_input("Quantidade de Pessoas", min_value=1, step=1, key="quantidade_pessoas_novo")
        condominio = st.text_input("Nome do Condomínio", key="condominio_novo")
        bloco = st.text_input("Bloco", key="bloco_novo")
        endereco = st.text_input("Endereço", key="endereco_novo")
        
        # Campo de valor do pagamento
        valor_pagamento = st.number_input("Valor do Pagamento", min_value=0.0, step=0.01, key="valor_pagamento_novo")
        
        # Seletor de status do pagamento com uma `key` única
        status_pagamento = st.selectbox("Status do Pagamento", ["Paga", "A Pagar"], key="status_pagamento_novo")

        # Exibe o campo "Valor Faltante para Pagar" se o status for "A Pagar"
        valor_faltante = 0.0  # Valor padrão
        if status_pagamento == "A Pagar":
            valor_faltante = st.number_input("Valor Faltante para Pagar", min_value=0.0, step=0.01, key="valor_faltante_novo")

        # Informações de valores com parceiros
        a_receber_parceiros = st.number_input("A Receber de Parceiros", min_value=0.0, step=0.01, key="a_receber_parceiros_novo")
        a_pagar_parceiros = st.number_input("A Pagar para Parceiros", min_value=0.0, step=0.01, key="a_pagar_parceiros_novo")

        # Informações do proprietário
        nome_proprietario = st.text_input("Nome do Proprietário", key="nome_proprietario_novo")

        # Informações do responsável
        email_responsavel = st.text_input("Email do Responsável", key="email_responsavel_novo")
        telefone_responsavel = st.text_input("Telefone do Responsável", key="telefone_responsavel_novo")
        documento_responsavel = st.text_input("Documento do Responsável", key="documento_responsavel_novo")

        # Botão para adicionar a reserva com as novas informações
        if st.button("Adicionar Reserva", key="botao_adicionar_reserva"):
            # Usa o valor do pagamento e o valor faltante para atualizar a reserva
            reservas.adicionar_reserva(
                nome, data_entrada, data_saida, numero_apartamento, valor_hospedagem, 
                valor_proprietario, nome_proprietario, quantidade_pessoas,
                condominio, bloco, endereco, status_pagamento, 
                a_receber_parceiros, a_pagar_parceiros,
                email_responsavel=email_responsavel, telefone_responsavel=telefone_responsavel, documento_responsavel=documento_responsavel,
                pago=valor_pagamento if status_pagamento == "Paga" else 0.0,
                a_pagar=valor_faltante if status_pagamento == "A Pagar" else 0.0
            )
            st.success("Nova reserva adicionada com sucesso!")


def editar_reservas(reservas):
    st.subheader("Editar Reservas")
    id_reserva = st.selectbox("Selecione a Reserva para Editar", reservas.df_reservas.index, key="reserva_edit")
    reserva_selecionada = reservas.df_reservas.loc[id_reserva]

    # Campos para editar informações da reserva
    nome = st.text_input("Nome do Hóspede", reserva_selecionada['Nome do hóspede'], key="nome_hospede")
    data_entrada = st.date_input("Data de Entrada", reserva_selecionada['Data de entrada'], key="data_entrada")
    data_saida = st.date_input("Data de Saída", reserva_selecionada['Data de saída'], key="data_saida")
    numero_apartamento = st.number_input("Número do Apartamento", value=int(reserva_selecionada['Número do apartamento']), key="numero_apartamento")
    valor_hospedagem = st.number_input("Valor da Hospedagem", value=float(reserva_selecionada['Valor da hospedagem']), key="valor_hospedagem")
    valor_proprietario = st.number_input("Valor para o Proprietário", value=float(reserva_selecionada['Valor para o proprietário']), key="valor_proprietario")
    quantidade_pessoas = st.number_input("Quantidade de Pessoas", value=int(reserva_selecionada['Quantidade de pessoas']), key="quantidade_pessoas")
    condominio = st.text_input("Nome do Condomínio", reserva_selecionada['Nome do Condomínio'], key="condominio")
    bloco = st.text_input("Bloco", reserva_selecionada['Bloco'], key="bloco")
    endereco = st.text_input("Endereço", reserva_selecionada['Endereço'], key="endereco")
    
    # Campos de valores pagos e a pagar para parceiros
    a_receber_parceiros = st.number_input("A Receber de Parceiros", value=float(reserva_selecionada.get('A receber de parceiros', 0)), key="a_receber_parceiros")
    a_pagar_parceiros = st.number_input("A Pagar para Parceiros", value=float(reserva_selecionada.get('A pagar para parceiros', 0)), key="a_pagar_parceiros")
    
    # Campos de pagamento
    pago = st.number_input("Pago", value=float(reserva_selecionada.get('Pago', 0)), key="pago")
    a_pagar = st.number_input("A Pagar", value=float(reserva_selecionada.get('A pagar', 0)), key="a_pagar")

    # Campo de status do pagamento
    status_lista = ["Paga", "A Pagar"]
    status_atual = reserva_selecionada.get("Status", "Paga")
    index_status = status_lista.index(status_atual) if status_atual in status_lista else 0
    status = st.selectbox("Status do Pagamento", status_lista, index=index_status, key="status_pagamento")

    # Informações do proprietário
    nome_proprietario = st.text_input("Nome do Proprietário", reserva_selecionada.get('Nome do proprietário', ''), key="nome_proprietario")
    
    # Campos para as informações do responsável
    email_responsavel = st.text_input("Email do Responsável", reserva_selecionada.get('Email do responsável', ''), key="email_responsavel")
    telefone_responsavel = st.text_input("Telefone do Responsável", reserva_selecionada.get('Telefone do responsável', ''), key="telefone_responsavel")
    documento_responsavel = st.text_input("Documento do Responsável", reserva_selecionada.get('Documento do responsável', ''), key="documento_responsavel")

    # Salva as alterações com todos os argumentos necessários, incluindo as novas informações
    if st.button("Salvar Alterações", key="salvar_alteracoes_reserva"):
        reservas.atualizar_reserva(
            id_reserva, nome, data_entrada, data_saida, numero_apartamento, 
            valor_hospedagem, valor_proprietario, nome_proprietario, quantidade_pessoas,
            condominio, bloco, endereco, status, 
            a_receber_parceiros, a_pagar_parceiros, pago, a_pagar, 
            email_responsavel=email_responsavel, 
            telefone_responsavel=telefone_responsavel, 
            documento_responsavel=documento_responsavel
        )
        st.success("Reserva atualizada com sucesso!")


def adicionar_novo_parceiro(reservas):
    with st.expander("Adicionar Novo Parceiro"):
        parceiro = st.text_input("Nome do Parceiro", key="nome_parceiro_novo")
        a_receber = st.number_input("A Receber", min_value=0.0, step=0.01, key="a_receber_parceiro_novo")
        a_pagar = st.number_input("A Pagar", min_value=0.0, step=0.01, key="a_pagar_parceiro_novo")

        if st.button("Adicionar Parceiro", key="botao_adicionar_parceiro"):
            reservas.adicionar_parceiro(parceiro, a_receber, a_pagar)
            st.success("Novo parceiro adicionado com sucesso!")

def editar_parceiros(reservas):
    st.subheader("Editar Parceiros")
    id_parceiro = st.selectbox("Selecione o Parceiro para Editar", reservas.df_parceiros.index, key="parceiro_edit")
    parceiro_selecionado = reservas.df_parceiros.loc[id_parceiro]

    parceiro = st.text_input("Nome do Parceiro", parceiro_selecionado['Parceiro'], key="nome_parceiro")
    a_receber = st.number_input("A Receber", value=float(parceiro_selecionado['A receber']), key="a_receber_parceiro")
    a_pagar = st.number_input("A Pagar", value=float(parceiro_selecionado['A pagar']), key="a_pagar_parceiro")

    if st.button("Salvar Alterações no Parceiro", key="salvar_alteracoes_parceiro"):
        reservas.atualizar_parceiro(id_parceiro, parceiro, a_receber, a_pagar)
        st.success("Parceiro atualizado com sucesso!")

# Funções para adicionar e editar proprietários
def adicionar_novo_proprietario(reservas):
    with st.expander("Adicionar Novo Proprietário"):
        nome = st.text_input("Nome Completo", key="nome_proprietario_novo")
        email = st.text_input("Email", key="email_proprietario_novo")
        telefone = st.text_input("Telefone", key="telefone_proprietario_novo")
        documento = st.text_input("Documento", key="documento_proprietario_novo")

        if st.button("Adicionar Proprietário", key="botao_adicionar_proprietario"):
            reservas.adicionar_proprietario(nome, email, telefone, documento)
            st.success("Novo proprietário adicionado com sucesso!")

def editar_proprietarios(reservas):
    st.subheader("Editar Proprietários")
    id_proprietario = st.selectbox("Selecione o Proprietário para Editar", reservas.df_proprietarios.index, key="proprietario_edit")
    proprietario_selecionado = reservas.df_proprietarios.loc[id_proprietario]

    nome = st.text_input("Nome Completo", proprietario_selecionado['Nome Completo'], key="nome_proprietario")
    email = st.text_input("Email", proprietario_selecionado['Email'], key="email_proprietario")
    telefone = st.text_input("Telefone", proprietario_selecionado['Telefone'], key="telefone_proprietario")
    documento = st.text_input("Documento", proprietario_selecionado['Documento'], key="documento_proprietario")

    if st.button("Salvar Alterações no Proprietário", key="salvar_alteracoes_proprietario"):
        reservas.atualizar_proprietario(id_proprietario, nome, email, telefone, documento)
        st.success("Proprietário atualizado com sucesso!")

# Mapeamento das páginas
pages = {
    "Dashboard Home": lambda: dashboard_home(reservas),
    "Relatórios": lambda: relatorios(reservas),
    "Gestão de Reservas": lambda: gestao_reservas(reservas),
    "Gestão de Parceiros": lambda: gestao_parceiros(reservas),
    "Gestão de Proprietários": lambda: gestao_proprietarios(reservas),
}

# Criação do seletor de páginas na barra lateral
st.sidebar.title("Navegação")
selected_page = st.sidebar.selectbox("Escolha uma página", list(pages.keys()))

# Inicialização do objeto de gerenciamento de reservas
current_dir = os.path.dirname(os.path.abspath(__file__))
reservas_path = os.path.join(current_dir, "reservas.xlsx")
parceiros_path = os.path.join(current_dir, "parceiros.xlsx")
proprietarios_path = os.path.join(current_dir, "proprietarios.xlsx")
reservas = GerenciamentoReservas(reservas_path, parceiros_path, proprietarios_path)

# Chamada da função correspondente à página selecionada
pages[selected_page]()
