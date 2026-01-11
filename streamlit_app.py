import streamlit as st

st.set_page_config(page_title="ProWashCare Offerte", layout="centered")
st.title("🧼 ProWashCare – Offerte")

BTW = 0.21
OPRIT_MINIMUM = 299.0
VERVOERSKOST = 8.0

# ================= SESSION =================
if "diensten" not in st.session_state:
    st.session_state.diensten = []

# ================= KLANT =================
st.subheader("👤 Klantgegevens")
klant_naam = st.text_input("Naam", key="klant_naam")
klant_adres = st.text_input("Adres", key="klant_adres")
klant_email = st.text_input("E-mail", key="klant_email")

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
    key="dienst_select",
)

omschrijving = ""
eindbedrag = 0.0

# ================= RAMEN =================
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

    m2 = st.number_input("Oppervlakte (m²)", 0.0, step=1.0, key="gevel_m2")
    impreg = st.checkbox("Impregneren (+ €4 / m²)", key="gevel_impreg")

    eindbedrag = m2 * 5.0 + (m2 * 4.0 if impreg else 0.0)
    eindbedrag = max(299, eindbedrag)

    omschrijving = f"Gevelreiniging\n{m2} m²"
    if impreg:
        omschrijving += "\nImpregneren"

# ================= PANELEN =================
elif dienst == "Zonnepanelen":
    aantal = st.number_input("Aantal zonnepanelen", 0, step=1, key="panelen")
    eindbedrag = max(79, aantal * 5.0)
    omschrijving = f"Zonnepanelen reinigen\n{aantal} panelen"

# ================= OPRIT / TERRAS =================
elif dienst == "Oprit / Terras / Bedrijfsterrein":
    st.write("### Oprit / Terras / Bedrijfsterrein")

    type_keuze = st.radio(
        "Type",
        ["Oprit", "Terras", "Bedrijfsterrein"],
        horizontal=True,
        key="oprit_type",
    )

    m2 = st.number_input("Oppervlakte (m²)", 0.0, step=1.0, key="oprit_m2")

    c1, c2, c3, c4 = st.columns(4)
    reinigen = c1.checkbox("Reinigen", key="op_reinigen")
    zand = c2.checkbox("Zand invegen", key="op_zand")
    onkruid = c3.checkbox("Onkruidmijdend voegzand", key="op_onkruid")
    coating = c4.checkbox("Coating", key="op_coating")

    opties = []
    eindbedrag = 0.0

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
            omschrijving = f"{type_keuze}\n{m2} m² ({', '.join(opties)})"

# ================= TOEVOEGEN =================
if st.button("➕ Dienst toevoegen", key="add_dienst"):
    if eindbedrag > 0:
        st.session_state.diensten.append((omschrijving, eindbedrag))
    else:
        st.warning("Selecteer minstens één optie.")

# ================= VERVOER =================
if st.button("🚚 Vervoerskosten toevoegen", key="add_vervoer"):
    st.session_state.diensten.append(("Vervoerskosten", VERVOERSKOST))

# ================= OVERZICHT =================
st.divider()
st.subheader("📋 Overzicht diensten")

subtotaal = 0.0

for i, (oms, prijs) in enumerate(st.session_state.diensten):
    col1, col2 = st.columns([6, 2])

    # Omschrijving (meerdere regels mooi onder elkaar)
    col1.markdown(oms.replace("\n", "  \n"))

    # Prijs duidelijk zichtbaar
    col2.markdown(f"**€ {prijs:.2f}**")

    subtotaal += prijs

btw = subtotaal * BTW
totaal = subtotaal + btw

st.divider()
st.write(f"**Subtotaal:** € {subtotaal:.2f}")
st.write(f"**BTW (21%):** € {btw:.2f}")
st.write(f"## **Totaal:** € {totaal:.2f}")
