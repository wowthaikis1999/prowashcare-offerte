import streamlit as st
from datetime import datetime

st.set_page_config(page_title="ProWashCare Offerte", layout="centered")
st.title("🧼 ProWashCare – Offerte")

BTW_PERCENT = 0.21
OPRIT_MINIMUM = 299.0
VERVOERSKOST = 8.0

if "diensten" not in st.session_state:
    st.session_state.diensten = []

# ================= KLANT =================
st.subheader("👤 Klantgegevens")
klant_naam = st.text_input("Naam")
klant_adres = st.text_input("Adres")
klant_email = st.text_input("E-mail")

st.divider()

# ================= DIENST =================
st.subheader("🧾 Dienst kiezen")
dienst = st.selectbox(
    "Dienst",
    [
        "Ramen wassen",
        "Gevelreiniging",
        "Zonnepanelen",
        "Oprit / Terras / Bedrijfsterrein",
    ],
)

omschrijving = ""
eindbedrag = 0.0

# ================= RAMEN =================
if dienst == "Ramen wassen":
    st.write("### Ramen wassen")

    st.write("**Kleine ramen**")
    c1, c2 = st.columns(2)
    kb = c1.number_input("Binnen", 0, step=1)
    kbui = c2.number_input("Buiten", 0, step=1)

    st.write("**Grote ramen**")
    c3, c4 = st.columns(2)
    gb = c3.number_input("Binnen", 0, step=1)
    gbui = c4.number_input("Buiten", 0, step=1)

    st.write("**Dakramen / moeilijk te bereiken raam**")
    c5, c6 = st.columns(2)
    db = c5.number_input("Binnen", 0, step=1)
    dbui = c6.number_input("Buiten", 0, step=1)

    eindbedrag = (
        kb * 2.0 + kbui * 1.5 +
        gb * 2.5 + gbui * 2.0 +
        db * 2.5 + dbui * 2.5
    )

    eindbedrag = max(50, eindbedrag)

    omschrijving = (
        "Ramen wassen\n"
        f"Kleine ramen: {kb} binnen, {kbui} buiten\n"
        f"Grote ramen: {gb} binnen, {gbui} buiten\n"
        f"Dakramen / moeilijk bereikbaar: {db} binnen, {dbui} buiten"
    )

# ================= GEVEL =================
elif dienst == "Gevelreiniging":
    st.write("### Gevelreiniging")

    m2 = st.number_input("Oppervlakte (m²)", 0.0, step=1.0)
    impreg = st.checkbox("Impregneren (+ €4 / m²)")

    eindbedrag = m2 * 5.0 + (m2 * 4.0 if impreg else 0.0)

    omschrijving = f"Gevelreiniging\n{m2} m²"
    if impreg:
        omschrijving += "\nImpregneren"

    eindbedrag = max(299, eindbedrag)

# ================= PANELEN =================
elif dienst == "Zonnepanelen":
    aantal = st.number_input("Aantal zonnepanelen", 0, step=1)
    eindbedrag = max(79, aantal * 5)

    omschrijving = f"Zonnepanelen reinigen\n{aantal} panelen"

# ================= OPRIT / TERRAS =================
elif dienst == "Oprit / Terras / Bedrijfsterrein":
    st.write("### Oprit / Terras / Bedrijfsterrein")

    type_keuze = st.radio(
        "Type",
        ["Oprit", "Terras", "Bedrijfsterrein"],
        horizontal=True
    )

    m2 = st.number_input("Oppervlakte (m²)", 0.0, step=1.0)

    col1, col2, col3, col4 = st.columns(4)
    reinigen = col1.checkbox("Reinigen")
    zand = col2.checkbox("Zand invegen")
    onkruid = col3.checkbox("Onkruidmijdend voegzand")
    coating = col4.checkbox("Coating")

    eindbedrag = 0.0
    opties = []

    if reinigen:
        eindbedrag += m2 * 3.5
        opties.append("Reinigen")
    if zand:
        eindbedrag += m2 * 1.0
        opties.append("Zand invegen")
    if onkruid:
        eindbedrag += m2 * 2.0
        opties.append("Onkruidmijdend voegzand")
    if coating:
        eindbedrag += m2 * 3.5
        opties.append("Coating")

    if opties:
        if eindbedrag < OPRIT_MINIMUM:
            eindbedrag = OPRIT_MINIMUM
            omschrijving = "Minimumtarief oprit / terras / bedrijfsterrein"
        else:
            omschrijving = (
                f"{type_keuze}\n"
                f"{m2} m² ({', '.join(opties)})"
            )

# ================= TOEVOEGEN =================
if st.button("➕ Dienst toevoegen"):
    if eindbedrag > 0:
        st.session_state.diensten.append((omschrijving, eindbedrag))
    else:
        st.warning("Selecteer minstens één optie.")

# ================= VERVOER =================
if st.button("🚚 Vervoerskosten toevoegen"):
    st.session_state.diensten.append(("Vervoerskosten", VERVOERSKOST))

# ================= OVERZICHT =================
st.divider()
st.subheader("📋 Overzicht")

subtotaal = sum(p for _, p in st.session_state.diensten)
btw = subtotaal * BTW_PERCENT
totaal = subtotaal + btw

for oms, prijs in st.session_state.diensten:
    st.write(oms.replace("\n", "  \n"))
    st.write(f"€ {prijs:.2f}")
    st.write("---")

st.write(f"**Subtotaal:** € {subtotaal:.2f}")
st.write(f"**BTW (21%):** € {btw:.2f}")
st.write(f"## **Totaal:** € {totaal:.2f}")
