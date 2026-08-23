import streamlit as st
import pandas as pd
import plotly.express as px

def render_dashboard(patrimonio_db):
    st.title("📊 Dashboard - Patrimônio ISPN")
    
    if not patrimonio_db:
        st.info("Nenhum patrimônio cadastrado para exibir no dashboard.")
        return

    df = pd.DataFrame(patrimonio_db)
    
    if df.empty:
        st.info("Nenhum patrimônio cadastrado para exibir no dashboard.")
        return

    # Mapeamento dinâmico de colunas
    col_status = 'status' if 'status' in df.columns else df.columns[0]
    col_categoria = 'categoria' if 'categoria' in df.columns else df.columns[0]
    col_local = 'localizacao' if 'localizacao' in df.columns else ('cidade' if 'cidade' in df.columns else df.columns[0])

    # Métricas
    total_bens = len(df)
    disponiveis = len(df[df[col_status].astype(str).str.lower() == 'disponível']) if col_status in df.columns else 0
    em_uso = len(df[df[col_status].astype(str).str.lower() == 'em uso']) if col_status in df.columns else 0
    manutencao = len(df[df[col_status].astype(str).str.lower() == 'manutenção']) if col_status in df.columns else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de Bens", total_bens)
    c2.metric("Disponíveis", disponiveis)
    c3.metric("Em Uso", em_uso)
    c4.metric("Em Manutenção", manutencao)

    st.markdown("<br>", unsafe_allow_html=True)

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("📍 Alocação por Localização")
        if col_local in df.columns:
            df_loc = df[col_local].value_counts().reset_index()
            df_loc.columns = ['Local', 'Quantidade']
            
            fig_loc = px.pie(
                df_loc, 
                names='Local', 
                values='Quantidade', 
                hole=0.5,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            
            fig_loc.update_layout(
                paper_bgcolor='#FFFFFF',
                plot_bgcolor='#FFFFFF',
                font=dict(color="#0F172A", size=13),
                legend=dict(font=dict(color="#0F172A")),
                margin=dict(t=30, b=30, l=30, r=30)
            )
            st.plotly_chart(fig_loc, use_container_width=True)

    with col_g2:
        st.subheader("📁 Distribuição por Categoria ISPN")
        if col_categoria in df.columns and col_status in df.columns:
            # Agrupamento seguro para evitar conflito de nomes no reset_index
            df_cat = df.groupby([col_categoria, col_status], as_index=False).size()
            df_cat.rename(columns={'size': 'Qtd'}, inplace=True)
            
            fig_cat = px.bar(
                df_cat, 
                x=col_categoria, 
                y='Qtd', 
                color=col_status,
                barmode='stack',
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            
            fig_cat.update_layout(
                paper_bgcolor='#FFFFFF',
                plot_bgcolor='#FFFFFF',
                font=dict(color="#0F172A", size=13),
                xaxis=dict(
                    title="Categoria",
                    title_font=dict(color="#0F172A"),
                    tickfont=dict(color="#0F172A"),
                    gridcolor="#E2E8F0"
                ),
                yaxis=dict(
                    title="Quantidade",
                    title_font=dict(color="#0F172A"),
                    tickfont=dict(color="#0F172A"),
                    gridcolor="#E2E8F0"
                ),
                legend=dict(font=dict(color="#0F172A")),
                margin=dict(t=30, b=30, l=30, r=30)
            )
            st.plotly_chart(fig_cat, use_container_width=True)
