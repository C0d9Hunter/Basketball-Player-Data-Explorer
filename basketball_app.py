import streamlit as st 
import pandas as pd 
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np 
import datetime


st.set_page_config(page_title="BasketBall Data Explorer",page_icon="image/icon.jpg", layout="wide", initial_sidebar_state="collapsed")

#app header logo
st.markdown(
        f"""
        <div class="container">
            <img class="logo-img" style="width:300px; margin-bottom:10px" src="data:image/png;base64,{base64.b64encode(open("./image/image.jpg", "rb").read()).decode()}">
        </div>
        """,
        unsafe_allow_html=True
    )

st.title('NBA Player Stats Explorer')

st.markdown("""
Cette application effectue un simple collecte des données(webscrapping) des statistiques des joueurs de la NBA!
""")

st.sidebar.header('User Input Features')

#selectionner l'annee entre 1950 et l'annee actuelle
current_year = int(datetime.datetime.now().year) #exemple 2021
selected_year = st.sidebar.selectbox('Année', list(reversed(range(1950,current_year+1))))

# Web scraping of NBA player stats
@st.cache
def load_data(year):
    url = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_per_game.html"
    html = pd.read_html(url, header = 0)
    df = html[0]
    raw = df.drop(df[df.Age == 'Age'].index) # Deletes repeating headers in content
    raw = raw.fillna(0)
    playerstats = raw.drop(['Rk'], axis=1)
    return playerstats
playerstats = load_data(selected_year)

# st.write(playerstats)
# Sidebar - Team selection
#regrouper les joueurs en equipes
sorted_unique_team = sorted(playerstats.Tm.unique())
#selectionner les equipes voulues
selected_team = st.sidebar.multiselect('Equipe', sorted_unique_team, sorted_unique_team)

# Sidebar - Position selection
unique_pos = ['C','PF','SF','PG','SG']
selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)

# filtrer les donnees afin d'obtenir les equipes selectionnés ayant les positions selectionnés au sein de leurs equipes
df_selected_team = playerstats[(playerstats.Tm.isin(selected_team)) & (playerstats.Pos.isin(selected_pos))]

st.header('Afficher les statistiques des joueurs des équipes sélectionnées')
st.write('Dimension du dataset: ' + str(df_selected_team.shape[0]) + ' lignes et ' + str(df_selected_team.shape[1]) + ' colonne.')
st.dataframe(df_selected_team)

# Download NBA player stats data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
#Fonction permettant de telecharger un fichier
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Telecharger le fichier CSV</a>'
    return href

#telechargement du dataset en csv en fonction des parametres equipes selectionnés et position selectionné
st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

# Heatmap
if st.button('Intercorrelation Heatmap'):
    st.header('Intercorrelation Matrix Heatmap')
    df_selected_team.to_csv('output.csv',index=False)
    df = pd.read_csv('output.csv')

    corr = df.corr()
    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True
    with sns.axes_style("white"):
        f, ax = plt.subplots(figsize=(10,10))
        ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
        st.pyplot(f)
