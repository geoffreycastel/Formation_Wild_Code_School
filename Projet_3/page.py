import streamlit as st
import pandas as pd
import seaborn as sns
from PIL import Image
import random
import folium
from streamlit_folium import folium_static

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Fonctions cache ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Définir la configuration de la page
st.set_page_config(layout="wide")

# DataFrame hôtels
@st.cache_data 
def create_df():
    data = pd.read_csv("https://raw.githubusercontent.com/geoffreycastel/Formation_Wild_Code_School/main/Projet_3/df_details.csv")
    df_details = pd.DataFrame(data)
    df_details = df_details.fillna('Non Renseigné')
    df_details = df_details.rename(columns = {'dc:identifier' : 'Identifiant', 'rdfs:label.fr' : 'Nom', 'schema:streetAddress' : 'Adresse', 'schema:addressLocality' : 'Ville', 'schema:postalCode' : 'Code_postal', 'schema:email' : 'Email', 'schema:telephone' : 'Telephone', 'foaf:homepage_x' : 'Site_web', 'schema:legalName' : 'Office_référente', 'foaf:homepage_y' : 'Site_web_office', 'type_stream' : 'Catégorie'})
    return df_details

df_details = create_df()


# DataFrame établissements sans commentaires
@st.cache_data 
def create_df_no_comments():
    data = pd.read_csv("https://raw.githubusercontent.com/geoffreycastel/Formation_Wild_Code_School/main/Projet_3/df_no_comment.csv")
    df_no_comment = pd.DataFrame(data)
    df_no_comment = df_no_comment[['dc:identifier', 'rdfs:label.fr', 'initial_type']].rename( columns = {'dc:identifier' : 'Identifiant', 'rdfs:label.fr' : 'Nom', 'initial_type' : 'Catégorie'})
    df_no_comment['Catégorie'] = df_no_comment['Catégorie'].replace('hotel', 'Hébergement').replace('restaurant', 'Restaurant')
    df_no_comment = df_no_comment.fillna('Non Renseigné')
    return df_no_comment

df_no_comment = create_df_no_comments()


# DataFrame prédictions catégories
@st.cache_data 
def create_df_proba():
    data = pd.read_csv("https://raw.githubusercontent.com/geoffreycastel/Formation_Wild_Code_School/main/Projet_3/df_prediction.csv")
    df_proba = pd.DataFrame(data)
    df_proba = df_proba[['dc:identifier', 'initial_type', 'rdfs:label.fr', 'prediction_Tfidf_2gram', 'proba_Tfidf_2gram_accomodation', 'proba_Tfidf_2gram_food']].rename( columns = {'dc:identifier' : 'Identifiant', 'initial_type' : 'Catégorie', 'rdfs:label.fr' : 'Nom', 'prediction_Tfidf_2gram' : 'Catégorie prédite', 'proba_Tfidf_2gram_accomodation' : 'Probabilité Hébergement', 'proba_Tfidf_2gram_food' : 'Probabilité Restaurant'})
    df_proba['Catégorie'] = df_proba['Catégorie'].replace('hotel', 'Hébergement').replace('restaurant', 'Restaurant').replace('hotel_restaurant', 'Hébergement & Restaurant')
    df_proba['Catégorie prédite'] = df_proba['Catégorie prédite'].replace({'food' : 'Restaurant', 'accomodation' : 'Hébergement'})
    df_proba['Probabilité Hébergement'] = df_proba['Probabilité Hébergement'].apply(lambda x : x * 100)
    df_proba['Probabilité Restaurant'] = df_proba['Probabilité Restaurant'].apply(lambda x : x * 100)
    df_proba = df_proba.fillna('Non Renseigné')
    return df_proba

df_proba = create_df_proba()


# DataFrame catégories google
@st.cache_data 
def create_df_google():
    data = pd.read_csv("https://raw.githubusercontent.com/geoffreycastel/Formation_Wild_Code_School/main/Projet_3/categorie_google.csv")
    df_google = pd.DataFrame(data)
    df_google = df_google.fillna('Non Renseigné')
    df_google = df_google.rename(columns = {'dc:identifier' : 'Identifiant', 'types' : 'Catégories Google'}).drop('Unnamed: 0', axis = 1)
    return df_google

df_google = create_df_google()


# DataFrame latitude longitude
@st.cache_data 
def create_df_lat_lon():
    data = pd.read_csv("https://raw.githubusercontent.com/geoffreycastel/Formation_Wild_Code_School/main/Projet_3/df_lat_lon.csv")
    df_lat_lon = pd.DataFrame(data)
    df_lat_lon = df_lat_lon.fillna('Non Renseigné')
    df_lat_lon = df_lat_lon.rename(columns = {'dc:identifier' : 'Identifiant', 'schema:geo.schema:latitude' : 'latitude', 'schema:geo.schema:longitude': 'longitude'})
    df_lat_lon['Coordonnées'] = df_lat_lon.apply(lambda x: [x['latitude'], x['longitude']], axis = 1)
    return df_lat_lon

df_lat_lon = create_df_lat_lon()

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# SIDEBAR ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

logo_adn_tourisme = "https://raw.githubusercontent.com/geoffreycastel/Formation_Wild_Code_School/main/Projet_3/logo_adn_tourisme.png"

st.sidebar.image(logo_adn_tourisme, use_column_width=True)

list_regions = ['Auvergne-Rhône-Alpes', 'Bourgogne-Franche-Comté', 'Bretagne', 'Centre-Val de Loire', 'Corse', 'Grand Est', 'Hauts-de-France',
'Normandie', 'Nouvelle-Aquitaine', 'Occitanie', 'Pays de la Loire', "Provence-Alpes-Côte d'Azur", 'Île-de-France', 'DOM/TOM']

region_index = 6

st.sidebar.write("Choix de la région :")

# Afficher les options sous forme de boutons avec la sélection par défaut
for indice, region in enumerate(list_regions):

    if indice == region_index:

        st.sidebar.markdown(f'<input type="radio" name="region" value="{region}" checked disabled> {region}', unsafe_allow_html=True)

    else:

        st.sidebar.markdown(f'<input type="radio" name="region" value="{region}" disabled> {region}', unsafe_allow_html=True)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# HEADER + BODY ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

st.header("Bienvenue sur l'application web d':red[A]:green[D]:orange[N] Tour:red[_i_]sme :round_pushpin: :world_map:")
st.write('')

# Création des 2 tabs
tab_mauvaise_categorie, tab_no_desc = st.tabs(['Etablissements mal catégorisés', 'Etablissements sans description'])

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ETABLISSEMENTS MAL CATÉGORISÉS --------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Sélection des établissements mal catégorisés
with tab_mauvaise_categorie:

    # Création de la liste des catégories d'établissements
    list_categories_tmc = ['Hébergement', 'Restaurant', 'Hébergement & Restaurant']

    st.write('')

    # Choix de la catégorie dans la liste
    choix_categorie = st.selectbox("Veuillez choisir un type d'établissement", (list_categories_tmc), key = 'tmc')

    # Si l'utilisateur sélectionne Hébergement
    if choix_categorie == 'Hébergement':

        st.write('')
        st.write('')

        proba_choisie = st.slider("Définissez la probabilité à partir de laquelle un Hébergement est considéré comme bien catégorisé", 51, 75, 65)

        st.write("Un", choix_categorie, 'est considéré comme mal catégorisé lorsque sa probabilité est inférieure ou égale à', str(proba_choisie), "%")

        st.write('')
        st.write('')

        df_hebergement = df_proba[df_proba['Catégorie'] == 'Hébergement']
        df_hebergement = df_hebergement[df_hebergement['Probabilité Hébergement'] <= proba_choisie]
        df_hebergement.drop('Catégorie', axis = 1, inplace = True)

        st.write('> Un Hébergement devrait devenir un **Restaurant** lorsque sa probabilité est inférieure à', str(100 - proba_choisie), '%')
        df_hebergement_to_restaurant = df_hebergement[df_hebergement['Probabilité Hébergement'] <= 100 - proba_choisie]
        st.dataframe(df_hebergement_to_restaurant, use_container_width=True)

        st.write('')

        st.write('> Un Hébergement devrait avoir la catégorie **Hébergement & Restaurant** lorsque sa probabilité est comprise entre', str(100 - proba_choisie), 'et', str(proba_choisie), '%')
        df_hebergement_to_mixte = df_hebergement[df_hebergement['Probabilité Hébergement'] < proba_choisie]
        df_hebergement_to_mixte = df_hebergement_to_mixte[df_hebergement_to_mixte['Probabilité Hébergement'] > 100 - proba_choisie]
        st.dataframe(df_hebergement_to_mixte, use_container_width=True)

        st.write('')

        # Saisie d'un identifiant par l'utilisateur
        id_etablissement = st.text_input(label = "Veuillez renseigner l'identifiant de l'établissement", key = 'id_heb_tmc')


        # Si l'identifiant saisi est présent dans les valeurs de la colonne Identifiant
        if id_etablissement in df_hebergement['Identifiant'].values:

            st.write('')

            # Filtrer le DataFrame pour n'afficher que l'établissement avec l'id correspondant
            etablissement = df_details[df_details['Identifiant'] == id_etablissement]
            
            # Création de 2 colonnes
            left_column, right_column = st.columns([3.5, 3])

            # Colonne de gauche
            with left_column:

                st.write('')
                st.write('')
                st.write('')

                # Affichez les informations correspondants à l'établissement
                st.write('**Identifiant :**', str(id_etablissement))
                st.write('**Nom :**', str(etablissement['Nom'].iloc[0]))
                st.write('**Code postal :**', str(etablissement['Code_postal'].iloc[0]))
                st.write('**Ville :**', str(etablissement['Ville'].iloc[0]))
                st.write('**Adresse :**', str(etablissement['Adresse'].iloc[0]))
                st.write('**Email :**', str(etablissement['Email'].iloc[0]))

                if len(etablissement['Telephone'].iloc[0]) < 20:
                    st.write('**Téléphone(s) :**', str(etablissement['Telephone'].iloc[0]))
                else:
                    st.write('**Téléphone(s) :**', str(etablissement['Telephone'].iloc[0][0:18]), '//', str(etablissement['Telephone'].iloc[0][18:]))

                st.write('**Site web :**', str(etablissement['Site_web'].iloc[0]))
                st.write('**Site web Office de Tourisme Référente:**', str(etablissement['Site_web_office'].iloc[0])) 

            # Colonne de droite
            with right_column:

                emplacement = df_lat_lon[df_lat_lon['Identifiant'] == id_etablissement]

                m = folium.Map(location = emplacement['Coordonnées'].iloc[0], zoom_start = 12)

                folium.Marker(location = emplacement['Coordonnées'].iloc[0], popup = str(etablissement['Nom'].iloc[0]) ).add_to(m)

                folium_static(m)


        else:

            st.write("Aucun établissement n'a été trouvé avec cet identifiant.")


    # Si l'utilisateur sélectionne Restaurant
    if choix_categorie == 'Restaurant':

        st.write('')
        st.write('')

        proba_choisie = st.slider("Définissez la probabilité à partir de laquelle un Restaurant est considéré comme bien catégorisé", 51, 75, 65)

        st.write("Un", choix_categorie, 'est considéré comme mal catégorisé lorsque sa probabilité est inférieure ou égale à', str(proba_choisie), "%")

        st.write('')
        st.write('')

        df_restaurants = df_proba[df_proba['Catégorie'] == 'Restaurant']
        df_restaurants = df_restaurants[df_restaurants['Probabilité Restaurant'] <= proba_choisie]
        df_restaurants.drop('Catégorie', axis = 1, inplace = True)


        st.write('> Un Restaurant devrait devenir un **Hébergement** lorsque sa probabilité est inférieure à', str(100 - proba_choisie), '%')
        df_restaurant_to_hebergement = df_restaurants[df_restaurants['Probabilité Restaurant'] <= 100 - proba_choisie]
        st.dataframe(df_restaurant_to_hebergement, use_container_width=True)

        st.write('')

        st.write('> Un Restaurant devrait avoir la catégorie **Hébergement & Restaurant** lorsque sa probabilité est comprise entre', str(100 - proba_choisie), 'et', str(proba_choisie), '%')
        df_restaurant_to_mixte = df_restaurants[df_restaurants['Probabilité Restaurant'] < proba_choisie]
        df_restaurant_to_mixte = df_restaurant_to_mixte[df_restaurant_to_mixte['Probabilité Restaurant'] > 100 - proba_choisie]
        st.dataframe(df_restaurant_to_mixte, use_container_width=True)

        st.write('')

        # Saisie d'un identifiant par l'utilisateur
        id_etablissement = st.text_input("Veuillez renseigner l'identifiant de l'établissement", key = 'id_rest_tmc')

        # Si l'identifiant est présent dans les valeurs de la colonne Identifiant
        if id_etablissement in df_restaurants['Identifiant'].values:

            st.write('')

            # Filtrer le DataFrame pour n'afficher que l'établissement avec l'id correspondant
            etablissement = df_details[df_details['Identifiant'] == id_etablissement]

            left_column, right_column = st.columns([3.5, 3])

            with left_column:

                st.write('')
                st.write('')
                st.write('')

                # Affichez les informations correspondants à l'établissement
                st.write('**Identifiant :**', str(id_etablissement))
                st.write('**Nom :**', str(etablissement['Nom'].iloc[0]))
                st.write('**Code postal :**', str(etablissement['Code_postal'].iloc[0]))
                st.write('**Ville :**', str(etablissement['Ville'].iloc[0]))
                st.write('**Adresse :**', str(etablissement['Adresse'].iloc[0]))
                st.write('**Email :**', str(etablissement['Email'].iloc[0]))
                if len(etablissement['Telephone'].iloc[0]) < 20:
                    st.write('**Téléphone(s) :**', str(etablissement['Telephone'].iloc[0]))
                else:
                    st.write('**Téléphone(s) :**', str(etablissement['Telephone'].iloc[0][0:18]), '//', str(etablissement['Telephone'].iloc[0][18:]))
                st.write('**Site web :**', str(etablissement['Site_web'].iloc[0]))
                st.write('**Site web Office de Tourisme Référente:**', str(etablissement['Site_web_office'].iloc[0]))            

            with right_column:

                emplacement = df_lat_lon[df_lat_lon['Identifiant'] == id_etablissement]

                m = folium.Map(location = emplacement['Coordonnées'].iloc[0], zoom_start = 12)

                folium.Marker(location = emplacement['Coordonnées'].iloc[0], popup = str(etablissement['Nom'].iloc[0]) ).add_to(m)

                folium_static(m)

        else:

            st.write("Aucun établissement n'a été trouvé avec cet identifiant.")




        # Si l'utilisateur sélectionne Hébergement & Restaurant
    if choix_categorie == 'Hébergement & Restaurant':

        st.write('')
        st.write('')

        proba_choisie = st.slider("Définissez l'intervalle de probabilité pour laquelle un Hébergement & Restaurant est considéré comme bien catégorisé", 25, 75, (35, 65))

        st.write("Un ", choix_categorie, "est considéré comme mal catégorisé lorsque la probabilité qu'il soit un Hébergement ou un Restaurant est comprise en dehors de l'intervalle ")

        st.write('')
        st.write('')

        df_hebergements_restaurants = df_proba[df_proba['Catégorie'] == 'Hébergement & Restaurant']
        df_hebergements_restaurants.drop('Catégorie', axis = 1, inplace = True)

        st.write('> Un Hébergement & Restaurant devrait devenir un **Hébergement** lorsque sa probabilité est supérieure à', str(proba_choisie[1]), '%')
        df_hebergements_restaurants_to_hebergement = df_hebergements_restaurants[df_hebergements_restaurants['Probabilité Hébergement'] > proba_choisie[1]]
        st.dataframe(df_hebergements_restaurants_to_hebergement, use_container_width=True)

        st.write('')

        st.write('> Un Hebergement & Restaurant devrait devenir un **Restaurant** lorsque sa probabilité est supérieure à', str(proba_choisie[1]), '%')
        df_hebergements_restaurants_to_restaurant = df_hebergements_restaurants[df_hebergements_restaurants['Probabilité Restaurant'] > proba_choisie[1]]
        st.dataframe(df_hebergements_restaurants_to_restaurant, use_container_width=True)



        # Saisie d'un identifiant par l'utilisateur
        id_etablissement = st.text_input("Veuillez renseigner l'identifiant de l'établissement", key = 'id_rest_heb_tmc')

        # Si l'identifiant est présent dans les valeurs de la colonne Identifiant
        if id_etablissement in df_hebergements_restaurants['Identifiant'].values:

            st.write('')

            # Filtrer le DataFrame pour n'afficher que l'établissement avec l'id correspondant
            etablissement = df_details[df_details['Identifiant'] == id_etablissement]

            left_column, right_column = st.columns([3.5, 3])

            with left_column:

                st.write('')
                st.write('')
                st.write('')

                # Affichez les informations correspondants à l'établissement
                st.write('**Identifiant :**', str(id_etablissement))
                st.write('**Nom :**', str(etablissement['Nom'].iloc[0]))
                st.write('**Code postal :**', str(etablissement['Code_postal'].iloc[0]))
                st.write('**Ville :**', str(etablissement['Ville'].iloc[0]))
                st.write('**Adresse :**', str(etablissement['Adresse'].iloc[0]))
                st.write('**Email :**', str(etablissement['Email'].iloc[0]))
                if len(etablissement['Telephone'].iloc[0]) < 20:
                    st.write('**Téléphone(s) :**', str(etablissement['Telephone'].iloc[0]))
                else:
                    st.write('**Téléphone(s) :**', str(etablissement['Telephone'].iloc[0][0:18]), '//', str(etablissement['Telephone'].iloc[0][18:]))
                st.write('**Site web :**', str(etablissement['Site_web'].iloc[0]))
                st.write('**Site web Office de Tourisme Référente:**', str(etablissement['Site_web_office'].iloc[0]))            

            with right_column:

                emplacement = df_lat_lon[df_lat_lon['Identifiant'] == id_etablissement]

                m = folium.Map(location = emplacement['Coordonnées'].iloc[0], zoom_start = 12)

                folium.Marker(location = emplacement['Coordonnées'].iloc[0], popup = str(etablissement['Nom'].iloc[0]) ).add_to(m)

                folium_static(m)

        else:

            st.write("Aucun établissement n'a été trouvé avec cet identifiant.")

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ETABLISSEMENTS SANS DESCRIPTION ------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Sélection des établissements sans description
with tab_no_desc:

    st.write('')

    df_no_comment_google = pd.merge(left = df_no_comment, right = df_google, on = 'Identifiant', how = 'left')

    # Création de la liste des catégories d'établissements
    list_categories_tnd = ['Hébergement', 'Restaurant']


    # Choix de la catégorie dans la liste
    choix_categorie = st.selectbox("Veuillez choisir un type d'établissement", (list_categories_tnd), key = 'tnd')

    st.write('')
    st.write('')

    # Si l'utilisateur sélectionne Hébergement
    if choix_categorie == 'Hébergement':

        df_hebergement_no_comment = df_no_comment_google[df_no_comment_google['Catégorie'] == 'Hébergement']

        st.dataframe(df_hebergement_no_comment, use_container_width=True)

        st.write('')

        # Saisie d'un identifiant par l'utilisateur
        id_etablissement = st.text_input("Veuillez renseigner l'identifiant de l'établissement", key = 'id_heb_tnd')

        # Si l'identifiant est présent dans les valeurs de la colonne Identifiant
        if id_etablissement in df_hebergement_no_comment['Identifiant'].values:

            st.write('')

            # Filtrer le DataFrame pour n'afficher que l'établissement avec l'id correspondant
            etablissement = df_details[df_details['Identifiant'] == id_etablissement]

            left_column, right_column = st.columns([3.5, 3])

            with left_column:

                st.write('')
                st.write('')
                st.write('')

                # Affichez les informations correspondants à l'établissement
                st.write('**Identifiant :**', str(id_etablissement))
                st.write('**Nom :**', str(etablissement['Nom'].iloc[0]))
                st.write('**Code postal :**', str(etablissement['Code_postal'].iloc[0]))
                st.write('**Ville :**', str(etablissement['Ville'].iloc[0]))
                st.write('**Adresse :**', str(etablissement['Adresse'].iloc[0]))
                st.write('**Email :**', str(etablissement['Email'].iloc[0]))
                if len(etablissement['Telephone'].iloc[0]) < 20:
                    st.write('**Téléphone(s) :**', str(etablissement['Telephone'].iloc[0]))
                else:
                    st.write('**Téléphone(s) :**', str(etablissement['Telephone'].iloc[0][0:18]), '//', str(etablissement['Telephone'].iloc[0][18:]))
                st.write('**Site web :**', str(etablissement['Site_web'].iloc[0]))
                st.write('**Site web Office de Tourisme Référente:**', str(etablissement['Site_web_office'].iloc[0]))            

            with right_column:

                emplacement = df_lat_lon[df_lat_lon['Identifiant'] == id_etablissement]

                m = folium.Map(location = emplacement['Coordonnées'].iloc[0], zoom_start = 12)

                folium.Marker(location = emplacement['Coordonnées'].iloc[0], popup = str(etablissement['Nom'].iloc[0]) ).add_to(m)

                folium_static(m)

        else:

            st.write("Aucun établissement n'a été trouvé avec cet identifiant.")




    # Si l'utilisateur sélectionne Restaurant
    if choix_categorie == 'Restaurant':

        df_restaurants_no_comment = df_no_comment_google[df_no_comment_google['Catégorie'] == 'Restaurant']

        st.dataframe(df_restaurants_no_comment, use_container_width=True)

        # Saisie d'un identifiant par l'utilisateur
        id_etablissement = st.text_input("Veuillez renseigner l'identifiant de l'établissement", key = 'id_rest_tnd')

        # Si l'identifiant est présent dans les valeurs de la colonne Identifiant
        if id_etablissement in df_restaurants_no_comment['Identifiant'].values:

            st.write('')

            # Filtrer le DataFrame pour n'afficher que l'établissement avec l'id correspondant
            etablissement = df_details[df_details['Identifiant'] == id_etablissement]

            left_column, right_column = st.columns([3.5, 3])

            with left_column:

                st.write('')
                st.write('')
                st.write('')

                # Affichez les informations correspondants à l'établissement
                st.write('**Identifiant :**', str(id_etablissement))
                st.write('**Nom :**', str(etablissement['Nom'].iloc[0]))
                st.write('**Code postal :**', str(etablissement['Code_postal'].iloc[0]))
                st.write('**Ville :**', str(etablissement['Ville'].iloc[0]))
                st.write('**Adresse :**', str(etablissement['Adresse'].iloc[0]))
                st.write('**Email :**', str(etablissement['Email'].iloc[0]))
                if len(etablissement['Telephone'].iloc[0]) < 20:
                    st.write('**Téléphone(s) :**', str(etablissement['Telephone'].iloc[0]))
                else:
                    st.write('**Téléphone(s) :**', str(etablissement['Telephone'].iloc[0][0:18]), '//', str(etablissement['Telephone'].iloc[0][18:]))
                st.write('**Site web :**', str(etablissement['Site_web'].iloc[0]))
                st.write('**Site web Office de Tourisme Référente:**', str(etablissement['Site_web_office'].iloc[0]))            

            with right_column:

                emplacement = df_lat_lon[df_lat_lon['Identifiant'] == id_etablissement]

                m = folium.Map(location = emplacement['Coordonnées'].iloc[0], zoom_start = 12)

                folium.Marker(location = emplacement['Coordonnées'].iloc[0], popup = str(etablissement['Nom'].iloc[0]) ).add_to(m)

                folium_static(m)

        else:

            st.write("Aucun établissement n'a été trouvé avec cet identifiant.")
