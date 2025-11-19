import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="Dashboard Streaming",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def carregar_dados():
    df = pd.read_csv("Popular Movies TV shows from Prime Videos Netflix version_3.csv")
    
    # Limpeza e Conversão
    df['Rotten Tomatoes'] = pd.to_numeric(df['Rotten Tomatoes'], errors='coerce')
    df['IMDb'] = pd.to_numeric(df['IMDb'], errors='coerce')
    df['Rating'] = df['Rating'].fillna("Indisponível")
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    
    # Criar Décadas
    df['Década'] = (df['Year'] // 10) * 10
    df['Década'] = df['Década'].astype(str) + 's'
    
    def get_platform(row):
        if row['Netflix'] == 1 and row['Amazon Prime Video'] == 1:
            return 'Ambos'
        elif row['Netflix'] == 1:
            return 'Netflix'
        elif row['Amazon Prime Video'] == 1:
            return 'Prime Video'
        else:
            return 'Outros'
    
    df['Plataforma_Nome'] = df.apply(get_platform, axis=1)
    return df

df = carregar_dados()

st.sidebar.title("Menu Principal")
pagina = st.sidebar.radio(
    "Navegue por aqui:", 
    ["Visão Geral", "Batalha das Plataformas", "Encontrar o que Assistir", "Insights e Tendências", "Explorador de Dados", "Sobre o Dashboard"]
)

st.sidebar.markdown("---")
st.sidebar.info("Dashboard acadêmico v3.3\nBaseado no dataset Kaggle Popular Movies.")

# --- PÁGINA: VISÃO GERAL ---
if pagina == "Visão Geral":
    st.title("Panorama do Streaming")
    st.markdown("### Análise de catálogo da Netflix e Amazon Prime Video")
    
    min_year, max_year = int(df['Year'].min()), int(df['Year'].max())
    anos = st.slider("Filtrar Dados por Período de Lançamento:", min_year, max_year, (2000, max_year))
    df_filtrado = df[(df['Year'] >= anos[0]) & (df['Year'] <= anos[1])]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Títulos", f"{len(df_filtrado):,}")
    col2.metric("Média IMDb", f"{df_filtrado['IMDb'].mean():.1f}")
    col3.metric("Filmes/Séries Netflix", f"{df_filtrado['Netflix'].sum():,}")
    col4.metric("Filmes/Séries Prime", f"{df_filtrado['Amazon Prime Video'].sum():,}")

    st.markdown("---")

    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Top 10 Gêneros")
        top_generos = df_filtrado['Genre'].value_counts().head(10).reset_index()
        top_generos.columns = ['Gênero', 'Qtd']
        fig_bar = px.bar(top_generos, x='Qtd', y='Gênero', orientation='h', color='Qtd', color_continuous_scale='Viridis')
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with c2:
        st.subheader("Distribuição de Classificação Indicativa")
        fig_pie = px.pie(df_filtrado, names='Rating', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)

# --- PÁGINA: BATALHA DAS PLATAFORMAS ---
elif pagina == "Batalha das Plataformas":
    st.title("Netflix vs Prime Video: Quem vence?")
    
    st.subheader("Qualidade vs Quantidade")
    st.markdown("Cada ponto é um filme/série. A cor indica onde está disponível.")
    
    fig_scatter = px.scatter(
        df, 
        x="IMDb", 
        y="Rotten Tomatoes", 
        color="Plataforma_Nome",
        hover_data=['Title', 'Year', 'Genre'],
        color_discrete_map={'Netflix': '#E50914', 'Prime Video': '#00A8E1', 'Ambos': 'purple'},
        opacity=0.5,
        title="Dispersão de Notas (IMDb vs Rotten Tomatoes)"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Conteúdo Exclusivo vs Compartilhado")
        contagem = df['Plataforma_Nome'].value_counts().reset_index()
        contagem.columns = ['Plataforma', 'Total']
        fig_bar_plat = px.bar(contagem, x='Plataforma', y='Total', color='Plataforma', 
                              color_discrete_map={'Netflix': '#E50914', 'Prime Video': '#00A8E1', 'Ambos': 'purple', 'Outros': 'gray'})
        st.plotly_chart(fig_bar_plat, use_container_width=True)
        
    with col2:
        st.subheader("Evolução ao longo dos anos")
        df_evolucao = df[df['Year'] > 1990].groupby(['Year', 'Plataforma_Nome']).size().reset_index(name='Contagem')
        fig_line = px.line(df_evolucao, x='Year', y='Contagem', color='Plataforma_Nome',
                           color_discrete_map={'Netflix': '#E50914', 'Prime Video': '#00A8E1', 'Ambos': 'purple', 'Outros': 'gray'})
        st.plotly_chart(fig_line, use_container_width=True)

# --- PÁGINA: ENCONTRAR O QUE ASSISTIR ---
elif pagina == "Encontrar o que Assistir":
    st.title("Pesquisa Inteligente")
    st.markdown("Não sabe o que ver? Utilize os filtros abaixo para encontrar a melhor opção.")
    
    with st.expander("Configurar Filtros de Pesquisa", expanded=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            filtro_plat = st.multiselect("Onde você quer assistir?", ["Netflix", "Prime Video"], default=["Netflix", "Prime Video"])
            filtro_texto = st.text_input("Busca por Título (opcional):")
        
        with col_f2:
            todos_generos = sorted(df['Genre'].unique().tolist())
            filtro_genero = st.multiselect("Gêneros Favoritos:", todos_generos)
            
        with col_f3:
            min_imdb = st.slider("Nota Mínima IMDb:", 0.0, 10.0, 6.0)
            min_rotten = st.slider("Nota Mínima Rotten Tomatoes:", 0, 100, 50)

    df_search = df.copy()
    
    if "Netflix" in filtro_plat and "Prime Video" not in filtro_plat:
        df_search = df_search[df_search['Netflix'] == 1]
    elif "Prime Video" in filtro_plat and "Netflix" not in filtro_plat:
        df_search = df_search[df_search['Amazon Prime Video'] == 1]
    elif not filtro_plat:
        df_search = df_search.iloc[0:0]
        
    if filtro_genero:
        df_search = df_search[df_search['Genre'].isin(filtro_genero)]
        
    df_search = df_search[(df_search['IMDb'] >= min_imdb) & (df_search['Rotten Tomatoes'] >= min_rotten)]
    
    if filtro_texto:
        df_search = df_search[df_search['Title'].str.contains(filtro_texto, case=False, na=False)]

    st.subheader(f"Encontramos {len(df_search)} títulos para você")
    
    if st.button("Estou com sorte! (Escolher um aleatório dos filtrados)"):
        if len(df_search) > 0:
            escolhido = df_search.sample(1).iloc[0]
            st.success(f"Sugerimos: **{escolhido['Title']}** ({escolhido['Year']})")
            st.info(f"Gênero: {escolhido['Genre']} | IMDb: {escolhido['IMDb']} | Rotten: {escolhido['Rotten Tomatoes']}")
        else:
            st.warning("Ajuste os filtros para ter opções de sorteio!")

    st.markdown("---")
    
    display_cols = ['Title', 'Year', 'Genre', 'IMDb', 'Rotten Tomatoes', 'Plataforma_Nome', 'Rating']
    
    def highlight_high_rating(val):
        color = '#d4edda' if val >= 8.0 else ''
        return f'background-color: {color}'

    st.dataframe(
        df_search[display_cols].sort_values(by='IMDb', ascending=False).style.applymap(highlight_high_rating, subset=['IMDb']),
        use_container_width=True,
        height=500
    )

# --- PÁGINA: INSIGHTS E TENDÊNCIAS ---
elif pagina == "Insights e Tendências":
    st.title("Insights Avançados e Tendências")
    st.markdown("Análise estatística sobre o comportamento do cinema e TV ao longo do tempo.")

    st.header("A Evolução do Cinema por Décadas")
    st.markdown("Média de avaliação IMDb agrupada por décadas.")
    
    df_decada = df.groupby('Década')[['IMDb', 'Rotten Tomatoes']].mean().reset_index()
    
    fig_decada = px.bar(
        df_decada, 
        x='Década', 
        y='IMDb', 
        text_auto='.2s',
        color='IMDb',
        color_continuous_scale='Magma'
    )
    fig_decada.update_layout(xaxis_title="Década", yaxis_title="Nota Média IMDb")
    st.plotly_chart(fig_decada, use_container_width=True)
    
    st.markdown("---")
    st.header("Mapa de Calor de Densidade")
    st.markdown("Concentração de notas: Onde estão a maioria dos filmes?")
    
    fig_density = px.density_heatmap(
        df, 
        x="IMDb", 
        y="Rotten Tomatoes", 
        nbinsx=20, 
        nbinsy=20, 
        text_auto=True,
        marginal_x="histogram", 
        marginal_y="histogram"
    )
    st.plotly_chart(fig_density, use_container_width=True)

# --- PÁGINA: EXPLORADOR DE DADOS ---
elif pagina == "Explorador de Dados":
    st.title("Exploração de Dados Brutos")
    st.write("Veja o dataset completo sem filtros prévios.")
    st.dataframe(df)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Baixar Dataset CSV", csv, "dados_processados.csv", "text/csv")

# --- PÁGINA: SOBRE O DASHBOARD ---
elif pagina == "Sobre o Dashboard":
    st.title("Documentação do Projeto")
    
    st.markdown("""
    ### Objetivo
    Este dashboard interativo foi desenvolvido para analisar comparativamente os catálogos da Netflix e Amazon Prime Video,
    oferecendo insights sobre qualidade, quantidade e tendências ao longo do tempo.
    
    ### Guia de Navegação
    
    * **Visão Geral:** Apresenta os KPIs principais (Total de Títulos, Médias) e gráficos de distribuição por Gênero e Classificação Indicativa. Use o filtro de anos na barra lateral para ajustar este período.
    
    * **Batalha das Plataformas:** Compara diretamente as duas empresas. Inclui análise de dispersão (Scatter Plot) para identificar outliers e gráficos de evolução temporal.
    
    * **Encontrar o que Assistir:** Uma ferramenta de busca prática. Permite filtrar por Plataforma, Gênero e Notas mínimas. Inclui uma função aleatória ("Estou com sorte") para sugestões.
    
    * **Insights e Tendências:** Análises estatísticas mais profundas, focando na média de qualidade por décadas e na densidade de notas entre crítica e público.
    
    * **Explorador de Dados:** Acesso direto à tabela bruta (DataFrame) com opção de download em CSV.
    
    ### Fonte de Dados
    O dataset utilizado foi o "Popular Movies TV shows from Prime Videos Netflix", disponível no Kaggle, contendo mais de 24.000 registros.
    
    ### Tecnologias
    * Python (Linguagem Principal)
    * Streamlit (Frontend Web)
    * Pandas (Manipulação de Dados)
    * Plotly (Visualização Interativa)
    """)