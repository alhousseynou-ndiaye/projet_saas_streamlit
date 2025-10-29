# mon_projet_saas.py
# ---------------------------------------------------------
# SaaS Starter — Dashboard Data (vendable à des PME)
# Features: Upload CSV/Excel, KPIs, filtres, charts, export
# ---------------------------------------------------------
import streamlit as st
import pandas as pd
import plotly.express as px
import io
from datetime import date

# --------- CONFIG PAGE ---------
st.set_page_config(page_title="Dashboard SaaS - Alhousseynou Ndiaye", page_icon="📊")

st.title("📊 Tableau de bord SaaS - Alhousseynou Ndiaye")
st.markdown("""
Cet outil permet d’analyser vos ventes ou vos performances en quelques clics.
Chargez vos données Excel/CSV et obtenez automatiquement :
- vos KPIs clés (CA, panier moyen, clients)
- des graphiques interactifs
- un export Excel prêt à partager
""")


# --------- SIDEBAR / BRANDING ---------
with st.sidebar:
    st.markdown("### 🧩 SaaS Starter")
    st.caption("Démo personnalisable pour PME")
    st.divider()
    st.markdown("#### ⚙️ Paramètres")
    monnaie = st.selectbox("Devise", ["€", "$", "£"], index=0)
    top_n = st.slider("Top N (classements)", 5, 20, 10, step=1)
    st.divider()
    st.markdown("#### 📥 Import de données")
    up = st.file_uploader("Charge un **CSV** ou **Excel**", type=["csv", "xlsx"])
    st.caption("Colonnes attendues (min): date, commande_id, client, pays, produit, categorie, quantite, prix_unitaire")
    st.divider()
    st.markdown("#### 🧪 Données de démonstration")
    demo = st.toggle("Utiliser un jeu de données démo", value=not bool(up))
    st.divider()
    page = st.radio("Navigation", ["🏠 Accueil", "📊 Dashboard", "🔎 Analyse détaillée", "⬇️ Export & Rapport", "📞 Contact"])



# --------- UTILITAIRES ---------
@st.cache_data
def load_demo():
    # jeu de données synthétique réaliste
    rng = pd.date_range("2024-01-01", periods=420, freq="D")
    import numpy as np
    df = pd.DataFrame({
        "date": np.random.choice(rng, 6000),
        "commande_id": [f"C-{100000+i}" for i in range(6000)],
        "client": np.random.choice([f"Client {i:03d}" for i in range(1, 260)], 6000),
        "pays": np.random.choice(["France","Belgique","Suisse","Espagne","Allemagne","Italie"], 6000, p=[.45,.08,.08,.15,.14,.10]),
        "produit": np.random.choice(["Clavier","Souris","Casque","Écran 24\"","Écran 27\"","Dock USB-C","Webcam","SSD 1To"], 6000),
        "categorie": None,
        "quantite": np.random.randint(1, 6, 6000),
        "prix_unitaire": np.random.choice([19.9,29.9,49,79,149,199,249,299], 6000)
    })
    cat_map = {"Clavier":"Périphériques","Souris":"Périphériques","Casque":"Audio","Écran 24\"":"Moniteurs",
               "Écran 27\"":"Moniteurs","Dock USB-C":"Accessoires","Webcam":"Vidéo","SSD 1To":"Stockage"}
    df["categorie"] = df["produit"].map(cat_map)
    df["date"] = pd.to_datetime(df["date"])
    df["ca"] = df["quantite"] * df["prix_unitaire"]
    return df

@st.cache_data
def read_any(file) -> pd.DataFrame:
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    df.columns = [c.strip().lower() for c in df.columns]
    # sécurité colonnes minimales
    needed = {"date","commande_id","client","pays","produit","quantite","prix_unitaire"}
    missing = [c for c in needed if c not in set(df.columns)]
    if missing:
        raise ValueError(f"Colonnes manquantes: {', '.join(missing)}")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    if "categorie" not in df.columns:
        df["categorie"] = "NA"
    df["ca"] = df["quantite"].astype(float) * df["prix_unitaire"].astype(float)
    return df

def fmt_money(x: float) -> str:
    s = f"{x:,.2f}".replace(",", " ").replace(".", ",")
    return f"{s} {monnaie}"

# --------- CHARGEMENT DONNÉES ---------
try:
    if demo:
        df = load_demo()
    elif up is not None:
        df = read_any(up)
    else:
        st.info("👉 Charge un fichier ou active *Données de démonstration* dans la barre latérale.")
        st.stop()
except Exception as e:
    st.error(f"Erreur au chargement des données : {e}")
    st.stop()

# --------- FILTRES COMMUNS ---------
min_d, max_d = df["date"].min().date(), df["date"].max().date()
c1, c2, c3, c4 = st.columns(4)
with c1:
    f_date_min = st.date_input("Date min", value=min_d, min_value=min_d, max_value=max_d)
with c2:
    f_date_max = st.date_input("Date max", value=max_d, min_value=min_d, max_value=max_d)
with c3:
    f_pays = st.multiselect("Pays", sorted(df["pays"].unique().tolist()))
with c4:
    f_cat = st.multiselect("Catégorie", sorted(df["categorie"].unique().tolist()))

mask = (df["date"].dt.date >= f_date_min) & (df["date"].dt.date <= f_date_max)
if f_pays:
    mask &= df["pays"].isin(f_pays)
if f_cat:
    mask &= df["categorie"].isin(f_cat)
data = df.loc[mask].copy()

if data.empty:
    st.warning("Aucune donnée pour ces filtres.")
    st.stop()

# --------- PAGES ---------
if page == "🏠 Accueil":
    st.title("📊 SaaS Starter — Dashboard Ventes")
    st.markdown("""
    Bienvenue ! Cette appli **prête à vendre** vous permet d'analyser vos ventes :
    - **Import** CSV/Excel, **KPIs** instantanés
    - Filtres par **dates / pays / catégorie**
    - Graphiques interactifs
    - **Export** du filtré (CSV) et **rapport** (Excel)
    - Personnalisable (logo, couleurs, devise)
    """)
    st.info("💡 Astuce vendeur : chargez un petit échantillon de données du client et montrez le dashboard en 5 minutes.")

    st.subheader("Aperçu rapide (KPIs)")
    col1, col2, col3, col4 = st.columns(4)
    ca_total = float(data["ca"].sum())
    nb_cmd = int(data["commande_id"].nunique())
    nb_clients = int(data["client"].nunique())
    panier = ca_total / nb_cmd if nb_cmd else 0.0

    col1.metric("Chiffre d'affaires", fmt_money(ca_total))
    col2.metric("Commandes", f"{nb_cmd:,}".replace(",", " "))
    col3.metric("Panier moyen", fmt_money(panier))
    col4.metric("Clients uniques", f"{nb_clients:,}".replace(",", " "))

elif page == "📊 Dashboard":
    st.title("📊 Dashboard")
    # Tendance
    ts = data.groupby(pd.Grouper(key="date", freq="W"))["ca"].sum().reset_index()
    st.plotly_chart(px.line(ts, x="date", y="ca", title="Tendance hebdomadaire du CA"), use_container_width=True)

    cA, cB = st.columns(2)
    # Top produits
    top_prod = data.groupby("produit")["ca"].sum().nlargest(top_n).reset_index()
    cA.plotly_chart(px.bar(top_prod, x="produit", y="ca", title=f"Top {top_n} produits"), use_container_width=True)
    # Top pays
    top_country = data.groupby("pays")["ca"].sum().nlargest(top_n).reset_index()
    cB.plotly_chart(px.bar(top_country, x="pays", y="ca", title=f"Top {top_n} pays"), use_container_width=True)

    cC, cD = st.columns(2)
    # Catégories
    top_cat = data.groupby("categorie")["ca"].sum().reset_index().sort_values("ca", ascending=False)
    cC.plotly_chart(px.pie(top_cat, names="categorie", values="ca", title="Répartition par catégorie"), use_container_width=True)
    # Évolution commandes
    cmd_ts = data.groupby(pd.Grouper(key="date", freq="W"))["commande_id"].nunique().reset_index()
    cD.plotly_chart(px.area(cmd_ts, x="date", y="commande_id", title="Commandes (hebdo)"), use_container_width=True)

    st.subheader("Tableau détaillé (filtré)")
    st.dataframe(data.sort_values("date", ascending=False), use_container_width=True)

elif page == "🔎 Analyse détaillée":
    st.title("🔎 Analyse détaillée")
    tab1, tab2, tab3 = st.tabs(["Cohortes clients", "Pareto 80/20", "Saisonnalité"])

    with tab1:
        # Cohortes simples par mois d'acquisition (approximé par 1ère commande)
        first_order = data.groupby("client")["date"].min().dt.to_period("M")
        tmp = data.assign(cohorte=data["client"].map(first_order))
        coh = tmp.assign(mois=tmp["date"].dt.to_period("M")).groupby(["cohorte","mois"])["client"].nunique().reset_index()
        coh["delta"] = (coh["mois"].astype(int) - coh["cohorte"].astype(int))
        pivot = coh.pivot(index="cohorte", columns="delta", values="client").fillna(0)
        st.dataframe(pivot, use_container_width=True)
        st.caption("Nombre de clients actifs par mois depuis l'acquisition (cohortes).")

    with tab2:
        agg_client = data.groupby("client")["ca"].sum().sort_values(ascending=False).reset_index()
        agg_client["cum_pct"] = agg_client["ca"].cumsum() / agg_client["ca"].sum()
        st.plotly_chart(px.line(agg_client, x=agg_client.index, y="cum_pct", title="Courbe de Pareto (CA cumulé)"), use_container_width=True)
        st.caption("Identifie rapidement les ~20% de clients générant ~80% du CA.")

    with tab3:
        by_month = data.groupby(data["date"].dt.to_period("M"))["ca"].sum().reset_index()
        by_month["date"] = by_month["date"].dt.to_timestamp()
        st.plotly_chart(px.bar(by_month, x="date", y="ca", title="Saisonnalité mensuelle du CA"), use_container_width=True)

elif page == "⬇️ Export & Rapport":
    st.title("⬇️ Exports")
    dview = data.sort_values("date", ascending=False)
    csv = dview.to_csv(index=False).encode("utf-8")
    st.download_button("Télécharger le CSV filtré", csv, "ventes_filtrees.csv", "text/csv")

    # Rapport Excel en mémoire
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        dview.to_excel(writer, index=False, sheet_name="Données")
        (data.groupby("produit")["ca"].sum().nlargest(20)
         .reset_index().to_excel(writer, index=False, sheet_name="Top_Produits"))
        (data.groupby(pd.Grouper(key="date", freq="W"))["ca"].sum()
         .reset_index().to_excel(writer, index=False, sheet_name="Tendance_CA"))
    st.download_button("Télécharger le Rapport Excel", buf.getvalue(), "rapport_dashboard.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.success("✅ Prêt à envoyer à un client.")

elif page == "📞 Contact":
    st.title("📞 Contact & À propos")
    st.markdown("""
    - **Prestations** : mise en place du dashboard, adaptation KPI métier, formation 1h.
    - **Délai** : 2–5 jours selon périmètre.
    - **Contact** : envoyez vos données d'exemple et vos besoins.
    """)
    with st.form("contact"):
        c1, c2 = st.columns(2)
        nom = c1.text_input("Nom")
        email = c2.text_input("Email")
        msg = st.text_area("Message / besoin")
        ok = st.form_submit_button("Envoyer")
    if ok:
        if email and msg:
            st.success("Merci ! Je vous recontacte rapidement. (Démo — branchement email à faire côté serveur)")
        else:
            st.warning("Renseignez au minimum votre email et un message.")

# --------- FOOTER ---------
st.markdown("---")
st.caption(f"© {date.today().year} — SaaS Starter (Streamlit). Personnalisation sur demande.")

# =========================================
# 📬 SECTION CONTACT
# =========================================
st.subheader("📬 Me contacter")

with st.form(key="contact_form"):
    name = st.text_input("Nom complet")
    email = st.text_input("Adresse e-mail")
    message = st.text_area("Votre message")

    submitted = st.form_submit_button("Envoyer ✉️")

    if submitted:
        if name and email and message:
            st.success("✅ Merci ! Votre message a été enregistré.")
            st.info("👉 Vous pouvez aussi me contacter directement à : **alhousseynoundiaye8@gmail.com**")
        else:
            st.warning("⚠️ Veuillez remplir tous les champs avant d’envoyer.")

