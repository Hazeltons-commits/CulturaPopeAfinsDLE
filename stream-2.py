import streamlit as st
import pandas as pd
import datetime


# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Culturapopeafinsdle", page_icon="🎮")

# --- CARREGAMENTO DE DADOS ---

@st.cache_data
def carregar_dados():
    
    data = pd.read_excel("DADOS.ods", header=None)
    
    return pd.DataFrame(data)

df = carregar_dados()

# --- LÓGICA DO JOGO ---

# s = datetime.datetime.now().day % len(df)
#s = datetime.date.today().day % 11 
s = 5
ans = df.iloc[s]

# Inicializar variáveis de estado (sessão) para manter os palpites ao recarregar a página
if 'tentativas' not in st.session_state:
    st.session_state.tentativas = []
if 'venceu' not in st.session_state:
    st.session_state.venceu = False

# --- INTERFACE ---
st.title("CULTURAPOPEAFINSDLE")

st.markdown("""
**Regras:**
- 🟩 **Verde**: Resposta correta
- 🟨 **Amarelo**: Resposta contém elementos corretos (parcial)
- 🟥 **Vermelho**: Resposta errada
- ⬆️/⬇️ **Setas**: Indicam se o valor numérico é maior ou menor
""")

st.markdown("""
**Cetegorias:**
- Os verificadores são os seguintes:
- Time, Cidade em que morou durante o curso, Estado civil, Atributos e Altura
- Obs: X e 0 representam falta de informações, que, no geral, carecem completamente de fontes
""")


# Inicializar o histórico de emojis no session_state
if 'emoji_history' not in st.session_state:
    st.session_state.emoji_history = ""

# --- DENTRO DA LÓGICA DE PROCESSAMENTO DO CHUTE ---
if not st.session_state.venceu:
    chute = st.selectbox("Chute um personagem:", [""] + list(df[0].unique()))

    if st.button("Enviar Chute") and chute != "":
        cl = df[df[0] == chute].iloc[0]
        
        linha_formatada = []
        linha_emojis = [] # Nova lista para guardar os emojis da tentativa atual

        for i in range(1, len(df.columns)):
            # Lógica Numérica (Última Coluna)
            # ... dentro do for i in range(1, len(df.columns)):

            # Lógica Numérica (Última Coluna)
            if i == (len(df.columns) - 1):
                if cl[i] > ans[i]:
                    status, emoji = "⬇️", "⬇️"
                    cor = "red"
                elif cl[i] < ans[i]:
                    status, emoji = "⬆️", "⬆️"
                    cor = "red"
                else:
                    status, emoji = "🟩", "🟩"
                    cor = "green"
                linha_formatada.append({"valor": cl[i], "cor": cor, "extra": status})
                linha_emojis.append(emoji)

            # Acerto Total Exacto
            elif str(cl[i]).strip().lower() == str(ans[i]).strip().lower():
                linha_formatada.append({"valor": cl[i], "cor": "green", "extra": ""})
                linha_emojis.append("🟩")

            # Acerto Parcial Baseado em Elementos Comuns
            else:
                # Transforma "Item 1, Item 2" em uma lista de termos limpos e em minúsculo
                elementos_chute = [elemento.strip().lower() for elemento in str(cl[i]).split(",")]
                elementos_resposta = [elemento.strip().lower() for elemento in str(ans[i]).split(",")]
                
                # Verifica se há alguma interseção entre as duas listas
                tem_intersecao = any(item in elementos_resposta for item in elementos_chute)
                
                if tem_intersecao:
                    linha_formatada.append({"valor": cl[i], "cor": "orange", "extra": ""})
                    linha_emojis.append("🟨")
                else:
                    linha_formatada.append({"valor": cl[i], "cor": "red", "extra": ""})
                    linha_emojis.append("🟥")
        # Registra a tentativa no histórico visual e no histórico de emojis
        st.session_state.tentativas.insert(0, {"personagem": cl[0], "detalhes": linha_formatada})
        
        # Monta a string de emojis para o compartilhamento (estilo Wordle)
        nova_linha_str = "".join(linha_emojis)
        st.session_state.emoji_history += nova_linha_str + "\n"
        
        if cl[0] == ans[0]:
            st.session_state.venceu = True
            st.balloons()


# --- EXIBIÇÃO DOS RESULTADOS ---
st.subheader("Histórico de Chutes")

for tentativa in st.session_state.tentativas:
    # Criamos as colunas para o Personagem + Atributos
    cols = st.columns(len(df.columns))
    
    # Nome do Personagem na primeira coluna
    cols[0].markdown(f"### {tentativa['personagem']}")
    
    # Itera sobre os atributos (detalhes)
    for i, item in enumerate(tentativa['detalhes']):
        # Mapeamento de cores sólidas e legíveis
        bg_color = {
            "green": "#28a745", 
            "orange": "#ffc107", 
            "red": "#dc3545"
        }.get(item['cor'], "#6c757d")
        
        # Texto sempre branco para contraste, exceto no amarelo (preto fica melhor)
        text_color = "black" if item['cor'] == "orange" else "white"
        
        # HTML para criar o "Card" colorido
        card_html = f"""
        <div style="
            background-color: {bg_color};
            color: {text_color};
            padding: 15px 5px;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
            font-family: sans-serif;
            margin-bottom: 5px;
            min-height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
        ">
            {item['valor']} {item['extra']}
        </div>
        """
        
        cols[i+1].markdown(card_html, unsafe_allow_html=True)

# --- EXIBIÇÃO DO RESULTADO FINAL E BOTÃO DE COPIAR ---
if st.session_state.venceu:
    st.success(f"Parabéns! Você acertou!")
    
    # Texto que será copiado
    texto_compartilhar = f"Joguei Culturapopeafinsdle\nTentativas: {len(st.session_state.tentativas)}\n\n{st.session_state.emoji_history}"
    
    st.text_area("Resultado para compartilhar:", value=texto_compartilhar, height=150)
    
    # Botão de Copiar (Usando a função nativa do Streamlit para copiar para área de transferência)
    st.button("Copiar Resultado 📋", on_click=lambda: st.write(f"Resultado copiado! (Use Ctrl+V)"))
    
    # Nota: Em versões recentes do Streamlit, st.copy_to_clipboard é a forma ideal:
    if hasattr(st, "copy_to_clipboard"):
        st.copy_to_clipboard(texto_compartilhar)
