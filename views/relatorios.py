import streamlit as st
import pandas as pd

def render_relatorios(patrimonio_db, *args, **kwargs):
    st.title("Relatórios Patrimoniais")

    if not patrimonio_db:
        st.info("Nenhum patrimônio cadastrado para gerar relatórios.")
        return

    # Trata os dados para exibição na tabela (remove bytes de arquivos)
    dados_limpos = []
    for item in patrimonio_db:
        copia = item.copy()
        
        # Formata o arquivo NF para mostrar apenas o nome na tabela
        raw_nf = copia.get("arquivo_nf")
        if isinstance(raw_nf, dict):
            copia["arquivo_nf"] = raw_nf.get("nome_arquivo", "Anexado")
        elif not raw_nf:
            copia["arquivo_nf"] = "Não anexado"
            
        dados_limpos.append(copia)

    df = pd.DataFrame(dados_limpos)

    # Renomeia colunas para exibição amigável
    colunas_map = {
        "etiqueta": "Código/Etiqueta",
        "nome": "Descrição do Bem",
        "categoria": "Categoria",
        "setor": "Setor",
        "localizacao": "Localização",
        "responsavel": "Responsável",
        "estado": "Situação",
        "valor_unitario": "Valor (R$)",
        "numero_nf": "Nº NF",
        "fornecedor": "Fornecedor",
        "arquivo_nf": "Arquivo NF"
    }
    
    df_exibicao = df.rename(columns=colunas_map)

    st.subheader("Visão Geral do Acervo")
    st.dataframe(df_exibicao, use_container_width=True, hide_index=True)

    # Botão para exportar dados para CSV
    csv = df_exibicao.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Exportar Relatório em CSV",
        data=csv,
        file_name="relatorio_patrimonial.csv",
        mime="text/csv",
        type="primary"
    )
