import streamlit as st

def render_formulario_patrimonio(item_edicao=None, save_callback=None):
    # Define valores padrão caso seja cadastro ou edição
    dados = item_edicao if item_edicao else {}

    st.subheader("📄 Dados da Nota Fiscal / Compra")
    
    col_nf1, col_nf2, col_nf3 = st.columns([1, 2, 1])
    with col_nf1:
        numero_nf = st.text_input("Nº NF", value=dados.get("numero_nf", ""))
    with col_nf2:
        fornecedor = st.text_input("Nome do Fornecedor", value=dados.get("fornecedor", ""))
    with col_nf3:
        valor_unitario = st.number_input(
            "Valor Unitário do Bem (R$)", 
            value=float(dados.get("valor_unitario", 0.0)), 
            min_value=0.0, 
            step=10.0,
            format="%.2f"
        )

    st.markdown("---")
    st.subheader("📦 Detalhes do Patrimônio")

    col_pat1, col_pat2 = st.columns(2)
    with col_pat1:
        etiqueta = st.text_input("Patrimônio (Código/Etiqueta) *", value=dados.get("etiqueta", ""))
        descricao = st.text_input("Descrição do bem *", value=dados.get("nome", ""))
        categoria = st.selectbox(
            "Categoria do bem", 
            ["Informática", "Mobiliário", "Veículos", "Eletrodomésticos", "Outros"],
            index=0
        )
    
    with col_pat2:
        localizacao = st.selectbox(
            "Localização / Cidade", 
            ["Santa Inês – MA", "Sede DF", "Campo - Cerrado", "Almoxarifado"]
        )
        responsavel = st.text_input("Responsável", value=dados.get("responsavel", "Equipe ISPN"))
        situacao = st.selectbox("Situação / Status", ["Em Uso", "Em Manutenção", "Inservível", "Baixado"])

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("💾 Cadastrar Patrimônio", type="primary", use_container_width=True):
        if not etiqueta or not descricao:
            st.error("Preencha os campos obrigatórios (*): Código/Etiqueta e Descrição do bem.")
        else:
            novo_patrimonio = {
                "etiqueta": etiqueta,
                "nome": descricao,
                "categoria": categoria,
                "numero_nf": numero_nf,
                "fornecedor": fornecedor,
                "valor_unitario": valor_unitario,
                "localizacao": localizacao,
                "responsavel": responsavel,
                "situacao": situacao
            }
            
            # Adiciona ao session state e salva na base de dados
            st.session_state.patrimonio_db.append(novo_patrimonio)
            
            if save_callback:
                save_callback()
                
            st.success("Patrimônio cadastrado com sucesso!")
            st.rerun()
