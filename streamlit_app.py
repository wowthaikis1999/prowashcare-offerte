import streamlit as st
from datetime import datetime
import io

st.set_page_config(page_title="ProWashCare Offerte", layout="centered")
st.title("🧼 ProWashCare – Offerte")

# ================== CONSTANTEN ==================
BTW_PERCENT = 0.21
OPRIT_MINIMUM = 299.0
VERVOERSKOST = 8.0

# ================== SESSION ==================
if "diensten" not in st.session_state:
    st.session_state.diensten = []

# ================== KLANTGEGEVENS ==================
st.subheader("👤 Klantgegevens")
klant_naam = st.text_input("Naam")
klant_adres = st.text_input("Adres")
klant_email = st.text_input("E-mail")

st.divider()

# ================== DIENST KIEZEN ==================
st.subheader("🧾 Dienst kiezen")
dienst = st.selectbox(
    "Kies een dienst",
    [
        "Ramen wassen",
        "Gevelreiniging",
        "Zonnepanelen reinigen",
        "Oprit / Terras / Bedrijfsterrein",
    ],
)

omschrijving = ""
eindbedrag = 0.0

# ================== RAMEN WASSEN ==================
if dienst == "Ramen wassen":
    st.write("### Ramen wassen")

    st.write("**Kleine ramen**")
    c1, c2 = st.columns(2)
    kb = c1.number_input("Binnen", 0, step=1, key="kb")
    kbui = c2.number_input("Buiten", 0, step=1, key="kbui")

    st.write("**Grote ramen**")
    c3, c4 = st.columns(2)
    gb = c3.number_input("Binnen", 0, step=1, key="gb")
    gbui = c4.number_input("Buiten", 0, step=1, key="gbui")

    st.write("**Dakramen / moeilijk te bereiken raam**")
    c5, c6 = st.columns(2)
    db = c5.number_input("Binnen", 0, step=1, key="db")
    dbui = c6.number_input("Buiten", 0, step=1, key="dbui")

    eindbedrag = (
        kb * 2.0 + kbui * 1.5 +
        gb * 2.5 + gbui * 2.0 +
        db * 2.5 + dbui * 2.5
    )

    omschrijving = (
        "Ramen wassen\n"
        f"- Kleine ramen: {kb} binnen, {kbui} buiten\n"
        f"- Grote ramen: {gb} binnen, {gbui} buiten\n"
        f"- Dakramen / moeilijk bereikbaar: {db} binnen, {dbui} buiten"
    )

    eindbedrag = max(50, eindbedrag)

# ================== GEVELREINIGING ==================
if dienst == "Gevelreiniging":
    st.write("### Gevelreiniging")

    m2 = st.number_input("Aantal m² gevel", 0, step=1)
    impregneren = st.checkbox("Impregneren (+ €5,00 / m²)")

    reiniging = m2 * 10.0
    impreg = m2 * 5.0 if impregneren else 0.0
    eindbedrag = reiniging + impreg

    omschrijving = f"Gevelreiniging\n- Reiniging: {m2} m² × €10,00"
    if impregneren:
        omschrijving += f"\n- Impregneren: {m2} m² × €5,00"

# ================== ZONNEPANELEN ==================
if dienst == "Zonnepanelen reinigen":
    st.write("### Zonnepanelen reinigen")

    aantal = st.number_input("Aantal zonnepanelen", 0, step=1)
    eindbedrag = aantal * 6.0

    omschrijving = f"Zonnepanelen reinigen\n- {aantal} panelen × €6,00"

# ================== OPRIT / TERRAS ==================
if dienst == "Oprit / Terras / Bedrijfsterrein":
    st.write("### Oprit / Terras / Bedrijfsterrein")

    m2 = st.number_input("Aantal m²", 0, step=1)

    col1, col2 = st.columns(2)
    zand = col1.checkbox("Zand invoegen (+ €3 / m²)")
    impreg = col2.checkbox("Impregneren (+ €5 / m²)")

    basis = m2 * 8.0
    zand_kost = m2 * 3.0 if zand else 0.0
    impreg_kost = m2 * 5.0 if impreg else 0.0

    eindbedrag = basis + zand_kost + impreg_kost

    if eindbedrag < OPRIT_MINIMUM and m2 > 0:
        eindbedrag = OPRIT_MINIMUM
        omschrijving = "Minimumtarief oprit / terras / bedrijfsterrein"
    else:
        omschrijving = f"Oprit / Terras / Bedrijfsterrein\n- {m2} m² × €8,00"
        if zand:
            omschrijving += f"\n- Zand invoegen: {m2} m² × €3,00"
        if impreg:
            omschrijving += f"\n- Impregneren: {m2} m² × €5,00"

# ================== TOEVOEGEN ==================
if st.button("➕ Dienst toevoegen"):
    if eindbedrag > 0:
        st.session_state.diensten.append((omschrijving, eindbedrag))
    else:
        st.warning("Geen geldige dienst ingevuld.")

# ================== VERVOERSKOST ==================
if st.button("🚚 Vervoerskosten toevoegen"):
    st.session_state.diensten.append(("Vervoerskosten", VERVOERSKOST))

# ================== OVERZICHT ==================
st.divider()
st.subheader("📋 Overzicht")

subtotaal = sum(d[1] for d in st.session_state.diensten)
btw = subtotaal * BTW_PERCENT
totaal = subtotaal + btw

for oms, prijs in st.session_state.diensten:
    st.write(oms)
    st.write(f"€ {prijs:.2f}")
    st.write("---")

st.write(f"**Subtotaal:** € {subtotaal:.2f}")
st.write(f"**BTW (21%):** € {btw:.2f}")
st.write(f"## **TOTAAL:** € {totaal:.2f}")
