# --- SEÇÃO DE IMPORTAÇÃO DE PLANILHA NA ABA GESTÃO ---
        with st.expander("📥 Importar Planilha de Patrimônio (Excel / CSV)", expanded=False):
            st.markdown("### 📋 Orientações sobre a Formatação da Planilha")
            st.markdown("""
            Para garantir que o sistema reconheça corretamente todas as informações, a primeira linha da sua planilha deve conter **exatamente os nomes de colunas (cabeçalho)** listados abaixo:
            """)
            
            # Exemplo estruturado de tabela atualizado (Sem valor, com placa opcional)
            exemplo_df = pd.DataFrame([
                {
                    "etiqueta": "PAT001",
                    "nome": "Notebook Dell Vostro",
                    "categoria": "Informática",
                    "localizacao": "Santa Inês – MA",
                    "responsavel": "João Silva",
                    "estado": "Bom",
                    "placa": ""
                },
                {
                    "etiqueta": "VEI001",
                    "nome": "Toyota Hilux 4x4",
                    "categoria": "Veículos",
                    "localizacao": "Sede DF",
                    "responsavel": "Maria Santos",
                    "estado": "Novo",
                    "placa": "ABC-1234"
                }
            ])
            st.dataframe(exemplo_df, use_container_width=True, hide_index=True)
            
            st.markdown("""
            **Detalhamento dos Campos Recomendados:**
            * **`etiqueta`** *(Obrigatório)*: Código único identificador do patrimônio (Ex: `PAT001`, `10025`).
            * **`nome`** *(Obrigatório)*: Descrição ou nome do item (Ex: `Impressora HP`, `Toyota Hilux`).
            * **`categoria`**: Categoria do bem (Ex: `Informática`, `Mobiliário`, `Veículos`).
            * **`localizacao`**: Local físico onde o bem se encontra (Ex: `Santa Inês – MA`, `Sede DF`).
            * **`responsavel`**: Pessoa responsável pelo bem.
            * **`estado`**: Condição do bem (Ex: `Novo`, `Bom`, `Manutenção`, `Inservível`).
            * **`placa`** *(Opcional)*: Placa do veículo (Recomendado para itens da categoria **Veículos**).
            
            ---
            """)
            
            # Modelo de download para o usuário
            buffer_modelo = io.BytesIO()
            with pd.ExcelWriter(buffer_modelo, engine='openpyxl') as writer:
                exemplo_df.to_excel(writer, index=False, sheet_name='Modelo')
            buffer_modelo.seek(0)

            st.download_button(
                label="📥 Baixar Planilha Modelo (.xlsx)",
                data=buffer_modelo,
                file_name="modelo_importacao_patrimonio.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            arquivo_upload = st.file_uploader("Carregue seu arquivo de planilha (.xlsx ou .csv):", type=["csv", "xlsx"])
            
            if arquivo_upload is not None:
                try:
                    if arquivo_upload.name.endswith('.csv'):
                        df_import = pd.read_csv(arquivo_upload)
                    else:
                        df_import = pd.read_excel(arquivo_upload)
                    
                    st.write("🔍 **Pré-visualização dos Dados Importados:**")
                    st.dataframe(df_import.head(10), use_container_width=True)
                    
                    mod_import = st.radio(
                        "Escolha a forma de importação:", 
                        ["Adicionar à base existente (Recomendado)", "Substituir base inteira"]
                    )
                    
                    if st.button("🚀 Confirmar Importação", type="primary"):
                        # Garantir substituição de valores nulos/NaN para evitar erros de renderização
                        df_import = df_import.fillna("")
                        novos_itens = df_import.to_dict(orient="records")
                        
                        if mod_import == "Substituir base inteira":
                            st.session_state.patrimonio_db = novos_itens
                        else:
                            st.session_state.patrimonio_db.extend(novos_itens)
                            
                        if save_all_data:
                            save_all_data(st.session_state.users_db, st.session_state.patrimonio_db, st.session_state.historico_db, st.session_state.cidades_db)
                        
                        st.success(f"✅ Importação realizada com sucesso! {len(novos_itens)} itens adicionados/atualizados.")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao ler e importar o arquivo: {str(e)}")
