import base64
import io
import urllib.parse
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

# 1. Número de atendimento fixo (com código 55 do Brasil)
MEU_WHATSAPP = "5511939500631"

# 2. Configuração da página
st.set_page_config(
    page_title="Açaíteria & Pastéis Jireh", page_icon="🍇", layout="centered"
)


# 3. Estilo visual com contraste e legibilidade ajustados
def definir_fundo():
    try:
        with open("fundo.jpg.jpeg", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()

        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpeg;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
                background-repeat: no-repeat;
            }}
            div[data-baseweb="select"], 
            div[data-baseweb="input"], 
            .stMultiSelect, 
            .stNumberInput input, 
            .stTextInput input,
            .stTextArea textarea {{
                background-color: #FFFFFF !important;
                color: #000000 !important;
                border-radius: 8px !important;
            }}
            div[data-baseweb="select"] * {{
                color: #000000 !important;
            }}
            label, .stMarkdown p, h1, h2, h3, h4 {{
                color: #FFFFFF !important;
                text-shadow: 2px 2px 4px #000000 !important;
                font-weight: bold !important;
            }}
            .stSelectbox, .stMultiSelect, .stNumberInput, .stTextInput, .stTextArea {{
                background-color: rgba(0, 0, 0, 0.55);
                padding: 12px;
                border-radius: 10px;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )
    except Exception:
        pass


definir_fundo()


# -------------------------------------------------------------
# FUNÇÃO PARA GERAR O CUPOM PROFISSIONAL EM IMAGEM (PILLOW)
# -------------------------------------------------------------
def gerar_imagem_cupom(nome_cliente, observacoes, itens_carrinho, total_geral):
    # Largura fixa estilo recibo térmico e altura dinâmica baseada nos itens
    largura = 500
    altura = 300 + (len(itens_carrinho) * 45)
    if observacoes:
        altura += 60

    # Cria imagem com fundo branco
    imagem = Image.new("RGB", (largura, altura), color="#FFFFFF")
    desenho = ImageDraw.Draw(imagem)

    # Tenta carregar uma fonte padrão do sistema um pouco maior, se falhar usa a padrão
    try:
        fonte_titulo = ImageFont.truetype("arial.ttf", 22)
        fonte_texto = ImageFont.truetype("arial.ttf", 16)
        fonte_negrito = ImageFont.truetype("arialbd.ttf", 16)
    except:
        fonte_titulo = ImageFont.load_default()
        fonte_texto = ImageFont.load_default()
        fonte_negrito = ImageFont.load_default()

    y = 30
    # Cabeçalho
    desenho.text(
        (35, y), "AÇAITERIA & PASTÉIS JIREH", fill="#4A154B", font=fonte_titulo
    )
    y += 35
    desenho.text(
        (35, y), "========================================", fill="#888888", font=fonte_texto
    )
    y += 30

    # Dados do Cliente
    desenho.text(
        (35, y), f"Cliente / Mesa: {nome_cliente}", fill="#000000", font=fonte_negrito
    )
    y += 30

    if observacoes:
        desenho.text(
            (35, y), f"Obs: {observacoes}", fill="#D32F2F", font=fonte_texto
        )
        y += 35

    desenho.text(
        (35, y), "----------------------------------------", fill="#888888", font=fonte_texto
    )
    y += 25

    # Itens
    desenho.text((35, y), "ITENS DO PEDIDO:", fill="#333333", font=fonte_negrito)
    y += 30

    for i, item in enumerate(itens_carrinho, 1):
        texto_item = f"{i}. {item['descricao']}"
        preco_item = f"R$ {item['preco']:.2f}"

        desenho.text((35, y), texto_item, fill="#222222", font=fonte_texto)
        y += 22
        desenho.text((35, y), f"   Preço: {preco_item}", fill="#555555", font=fonte_texto)
        y += 30

    desenho.text(
        (35, y), "----------------------------------------", fill="#888888", font=fonte_texto
    )
    y += 30

    # Total Geral
    desenho.text(
        (35, y), f"TOTAL GERAL: R$ {total_geral:.2f}", fill="#000000", font=fonte_titulo
    )

    # Salva no buffer de memória
    buffer = io.BytesIO()
    imagem.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


# -------------------------------------------------------------
# CONTROLE DE ACESSO COM SENHA DE SEGURANÇA
# -------------------------------------------------------------
SENHA_CORRETA = "acai123"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔒 Acesso Restrito - Jireh")
    st.subheader("Digite a senha para acessar o sistema de pedidos:")

    senha_digitada = st.text_input("Senha de Acesso:", type="password")

    if st.button("🔑 Entrar no Sistema", type="primary"):
        if senha_digitada == SENHA_CORRETA:
            st.session_state.autenticado = True
            st.success("Acesso liberado!")
            st.rerun()
        else:
            st.error("Senha incorreta! Tente novamente.")
    st.stop()

# -------------------------------------------------------------
# DADOS DO CARDÁPIO E TABELAS DE PREÇOS
# -------------------------------------------------------------
if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

# Açaí Tradicional
ACAI_TRADICIONAL_TAMANHOS = {
    "Nenhum": 0.00,
    "180ml": 8.00,
    "300ml": 12.00,
    "500ml": 15.00,
    "700ml": 20.00,
}

# Açaí Trufado
ACAI_TRUFADO_TAMANHOS = {
    "Nenhum": 0.00,
    "300ml Trufado": 20.00,
    "500ml Trufado": 30.00,
    "700ml Trufado": 40.00,
}

RECHEIOS_TRUFADO = ["Nutella", "Creme Ninho", "Creme Ovomaltine", "Chocolate"]

FRUTAS = {
    "Banana": 3.00,
    "Morango": 3.50,
    "Uva": 3.50,
}

ADICIONAL = {
    "Leite condensado": 2.00,
    "Granola": 3.00,
    "Paçoca": 3.00,
    "Amendoim": 3.00,
    "Sucrilhos": 3.00,
    "Oreo": 3.00,
    "Confete": 3.50,
    "Biss": 3.00,
    "Granulado": 2.00,
    "Boll": 3.50,
    "Ovomaltine": 4.00,
    "Leite em pó": 3.50,
    "Nutella": 7.00,
    "Creme de Ovomaltine": 7.00,
    "Creme de Ninho": 6.00,
}

# Pastéis Salgados
PASTEL_TAMANHOS = {
    "Nenhum": 0.00,
    "Pastel P": 8.00,
    "Pastel M": 15.00,
    "Pastel G": 20.00,
}

PASTEL_ESPECIAL_TAMANHOS = {
    "Nenhum": 0.00,
    "Pastel P": 10.00,
    "Pastel M": 18.00,
    "Pastel G": 23.00,
}

sabores_pastel = [
    "Carne com queijo",
    "Frango com Catupiry",
    "Queijo",
    "Calabresa com queijo",
    "Presunto e queijo",
    "Pizza",
    "Carne seca com queijo",
]

# Cachorro Quente
CACHORRO_QUENTE_TAMANHOS = {
    "Nenhum": 0.00,
    "Cachorro Quente": 9.00,
    "Dogão": 15.00,
}

# Sorvete
preco_bola_sorvete = 2.50
sabores_sorvete = [
    "Chocolate",
    "Creme",
    "Morango",
    "Flocos",
    "Coco",
    "Napolitano",
]

# Título da Aplicação
st.title("🍇 Açaíteria & Pastéis Jireh")
st.subheader("📍 Lançamento de Pedidos")
st.divider()

# -------------------------------------------------------------
# 1. AÇAÍ
# -------------------------------------------------------------
st.header("1. Açaí")
tipo_acai = st.radio(
    "Escolha o tipo de Açaí:",
    ["Açaí Tradicional", "Açaí Trufado"],
    horizontal=True,
)

if tipo_acai == "Açaí Tradicional":
    tamanho_escolhido = st.selectbox(
        "Selecione o tamanho do Açaí Tradicional:",
        options=list(ACAI_TRADICIONAL_TAMANHOS.keys()),
        format_func=lambda x: (
            f"{x} - R$ {ACAI_TRADICIONAL_TAMANHOS[x]:.2f}"
            if x != "Nenhum"
            else "Não quero açaí"
        ),
    )
    preco_base_acai = ACAI_TRADICIONAL_TAMANHOS[tamanho_escolhido]

    if tamanho_escolhido != "Nenhum":
        frutas_escolhidas = st.multiselect(
            "Escolha as frutas (opcional):",
            options=list(FRUTAS.keys()),
            format_func=lambda x: f"{x} (+R$ {FRUTAS[x]:.2f})",
        )
        adicionais_escolhidos = st.multiselect(
            "Escolha os adicionais (opcional):",
            options=list(ADICIONAL.keys()),
            format_func=lambda x: f"{x} (+R$ {ADICIONAL[x]:.2f})",
        )

        preco_acai_total = (
                preco_base_acai
                + sum(FRUTAS[f] for f in frutas_escolhidas)
                + sum(ADICIONAL[item] for item in adicionais_escolhidos)
        )

        if st.button("➕ Adicionar Açaí Tradicional ao Carrinho"):
            txt_frutas = (
                ", ".join(frutas_escolhidas) if frutas_escolhidas else "Nenhuma"
            )
            txt_add = (
                ", ".join(adicionais_escolhidos)
                if adicionais_escolhidos
                else "Nenhum"
            )
            desc = (
                f"Açaí Tradicional ({tamanho_escolhido}) | Frutas: {txt_frutas} |"
                f" Adicionais: {txt_add}"
            )
            st.session_state.carrinho.append(
                {"descricao": desc, "preco": preco_acai_total}
            )
            st.success("Açaí adicionado ao carrinho!")

else:
    tamanho_escolhido = st.selectbox(
        "Selecione o tamanho do Açaí Trufado:",
        options=list(ACAI_TRUFADO_TAMANHOS.keys()),
        format_func=lambda x: (
            f"{x} - R$ {ACAI_TRUFADO_TAMANHOS[x]:.2f}"
            if x != "Nenhum"
            else "Não quero açaí"
        ),
    )
    preco_base_acai = ACAI_TRUFADO_TAMANHOS[tamanho_escolhido]

    if tamanho_escolhido != "Nenhum":
        recheio_trufado = st.selectbox(
            "Escolha 1 Recheio para a Trufa (Incluso):", options=RECHEIOS_TRUFADO
        )
        fruta_gratis = st.selectbox(
            "Escolha 1 Fruta (Inclusa - Grátis):", options=list(FRUTAS.keys())
        )

        adicionais_escolhidos = st.multiselect(
            "Escolha os adicionais extras (opcional):",
            options=list(ADICIONAL.keys()),
            format_func=lambda x: f"{x} (+R$ {ADICIONAL[x]:.2f})",
        )

        preco_acai_total = preco_base_acai + sum(
            ADICIONAL[item] for item in adicionais_escolhidos
        )

        if st.button("➕ Adicionar Açaí Trufado ao Carrinho"):
            txt_add = (
                ", ".join(adicionais_escolhidos)
                if adicionais_escolhidos
                else "Nenhum"
            )
            desc = (
                f"Açaí Trufado ({tamanho_escolhido}) | Recheio: {recheio_trufado} |"
                f" Fruta Grátis: {fruta_gratis} | Adicionais: {txt_add}"
            )
            st.session_state.carrinho.append(
                {"descricao": desc, "preco": preco_acai_total}
            )
            st.success("Açaí Trufado adicionado ao carrinho!")

st.divider()

# -------------------------------------------------------------
# 2. PASTÉIS SALGADOS
# -------------------------------------------------------------
st.header("2. Pastéis Salgados")
sabor_escolhido = st.selectbox(
    "Selecione o sabor do pastel:", options=sabores_pastel
)

if sabor_escolhido == "Carne seca com queijo":
    tabela_pastel_atual = PASTEL_ESPECIAL_TAMANHOS
else:
    tabela_pastel_atual = PASTEL_TAMANHOS

pastel_escolhido = st.selectbox(
    "Selecione o tamanho do pastel:",
    options=list(tabela_pastel_atual.keys()),
    format_func=lambda x: (
        f"{x} - R$ {tabela_pastel_atual[x]:.2f}"
        if x != "Nenhum"
        else "Não quero pastel"
    ),
)

if pastel_escolhido != "Nenhum":
    preco_p = tabela_pastel_atual[pastel_escolhido]
    if st.button("➕ Adicionar Pastel Salgado ao Carrinho"):
        desc_p = f"Pastel {pastel_escolhido} - Sabor: {sabor_escolhido}"
        st.session_state.carrinho.append({"descricao": desc_p, "preco": preco_p})
        st.success("Pastel salgado adicionado ao carrinho!")

st.divider()

# -------------------------------------------------------------
# 2.1 BORDAS DE CHOCOLATE
# -------------------------------------------------------------
st.header("🍫 Bordas de Chocolate / Doce")
borda_opcao = st.selectbox(
    "Escolha a Borda Doce de Chocolate:",
    options=[
        "Nenhum",
        "Chocolate ao Leite - R$ 4,00",
        "Nutella - R$ 7,00",
    ],
)

if borda_opcao != "Nenhum":
    preco_borda = 4.00 if "Chocolate ao Leite" in borda_opcao else 7.00
    nome_borda = (
        "Chocolate ao Leite" if "Chocolate ao Leite" in borda_opcao else "Nutella"
    )

    if st.button("➕ Adicionar Borda Doce ao Carrinho"):
        st.session_state.carrinho.append(
            {"descricao": f"Borda Doce: {nome_borda}", "preco": preco_borda}
        )
        st.success("Borda doce adicionada ao carrinho!")

st.divider()

# -------------------------------------------------------------
# 3. CACHORRO-QUENTE
# -------------------------------------------------------------
st.header("3. Cachorro-Quente")
dog_escolhido = st.selectbox(
    "Selecione o Cachorro-Quente:",
    options=list(CACHORRO_QUENTE_TAMANHOS.keys()),
    format_func=lambda x: (
        f"{x} - R$ {CACHORRO_QUENTE_TAMANHOS[x]:.2f}"
        if x != "Nenhum"
        else "Não quero cachorro-quente"
    ),
)

if dog_escolhido != "Nenhum":
    preco_d = CACHORRO_QUENTE_TAMANHOS[dog_escolhido]
    if st.button("➕ Adicionar Cachorro-Quente ao Carrinho"):
        st.session_state.carrinho.append(
            {"descricao": f"Cachorro-Quente: {dog_escolhido}", "preco": preco_d}
        )
        st.success("Cachorro-Quente adicionado ao carrinho!")

st.divider()

# -------------------------------------------------------------
# 4. SORVETE
# -------------------------------------------------------------
st.header("4. Sorvete")

sabores_sorvete_escolhidos = st.multiselect(
    "Escolha os sabores de sorvete:",
    options=sabores_sorvete,
)

total_bolas = 0
detalhes_quantidades = []

if sabores_sorvete_escolhidos:
    st.subheader("Defina as bolas por sabor:")
    for sabor in sabores_sorvete_escolhidos:
        qtd_sabor = st.number_input(
            f"Bolas de {sabor}:",
            min_value=1,
            max_value=10,
            value=1,
            step=1,
            key=f"qtd_sorvete_{sabor}",
        )
        total_bolas += qtd_sabor
        detalhes_quantidades.append(f"{qtd_sabor}x {sabor}")

quero_casquinha = st.checkbox("Adicionar Casquinha (+R$ 1,50)")

preco_s = (total_bolas * preco_bola_sorvete) + (
    1.50 if quero_casquinha else 0.00
)

if total_bolas > 0:
    st.info(
        f"Total de bolas: **{total_bolas}** | Subtotal: **R$ {preco_s:.2f}**"
    )

    if st.button("➕ Adicionar Sorvete ao Carrinho"):
        txt_sabores = ", ".join(detalhes_quantidades)
        desc_s = f"Sorvete ({total_bolas} bola(s) - {txt_sabores})"
        if quero_casquinha:
            desc_s += " [Com Casquinha]"

        st.session_state.carrinho.append({"descricao": desc_s, "preco": preco_s})
        st.success("Sorvete adicionado ao carrinho!")

st.divider()

# -------------------------------------------------------------
# 5. RESUMO E GERAÇÃO DO CUPOM EM IMAGEM
# -------------------------------------------------------------
st.header("🛒 Carrinho de Compras")

if st.session_state.carrinho:
    total_carrinho = 0.0
    for index, item in enumerate(st.session_state.carrinho, 1):
        st.write(f"**{index}.** {item['descricao']} - R$ {item['preco']:.2f}")
        total_carrinho += item["preco"]

    st.subheader(f"Total Geral: R$ {total_carrinho:.2f}")

    if st.button("🗑️ Limpar Carrinho"):
        st.session_state.carrinho = []
        st.rerun()
else:
    st.info("O carrinho está vazio. Adicione itens acima!")

st.divider()

st.header("5. Gerar Cupom do Pedido")
nome = st.text_input("Nome do Cliente / Mesa:", key="nome_cliente")
observacoes = st.text_area(
    "Observações Gerais (Ex: Cachorro-quente sem milho / Entregar na Mesa 2):",
    height=100,
    key="obs_gerais",
)

if st.session_state.carrinho and nome.strip():
    obs_limpa = observacoes.strip()
    total_geral = sum(item["preco"] for item in st.session_state.carrinho)

    # Gera o cupom limpo em imagem otimizada via Pillow
    buffer_imagem = gerar_imagem_cupom(
        nome.strip(), obs_limpa, st.session_state.carrinho, total_geral
    )

    st.success("✅ Cupom gerado com sucesso! Baixe a imagem abaixo:")

    # Botão único e direto de download da imagem do cupom
    st.download_button(
        label="📥 BAIXAR CUPOM DO PEDIDO (IMAGEM)",
        data=buffer_imagem,
        file_name=f"cupom_{nome.strip().replace(' ', '_')}.png",
        mime="image/png",
        use_container_width=True,
    )

elif not nome.strip() and st.session_state.carrinho:
    st.warning(
        "⚠️ Digite o nome do cliente/mesa para liberar a geração do cupom."
    )