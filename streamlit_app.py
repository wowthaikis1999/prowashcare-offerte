import streamlit as st

# ---------------- CONFIG ----------------
st.set_page_config(page_title="ProWashCare Offerte", layout="centered")
st.title("🧼 ProWashCare – Offerte Tool")

BTW = 0.21
VERVOERSKOSTEN = 8.0

# ---------------- SESSION STATE ----------------
if "diensten" not in st.session_state:
    st.session_state.diensten = []

# ---------------- HULPFUNCTIES ----------------
def bereken_totalen():
    subtotaal = sum(d["totaal"] for d in st.session_state.diensten)
    btw = subtotaal * BTW
    totaal = subtotaal + btw
    return subtotaal, btw, totaal

# ---------------- KLANTGEGEVENS ----------------
st.subheader("👤 Klantgegevens")
col1, col2 = st.columns(2)

with col1:
    klant_naam = st.text_input("Naam")
    klant_email = st.text_input("E-mail")

with col2:
    klant_adres = st.text_area("Adres", height=80)

# ---------------- DIENST SELECTIE ----------------
st.divider()
st.subheader("➕ Dienst toevoegen")

dienst = st.selectbox(
    "Kies een dienst",
    ["Ramen wassen", "Zonnepanelen", "Gevelreiniging", "Oprit / Terras / Bedrijfsterrein"]
)

# ---------------- RAMEN WASSEN ----------------
if dienst == "Ramen wassen":
    st.markdown("### Ramen wassen")

    c1, c2, c3 = st.columns(3)
    with c1:
        kb = st.number_input("Kleine ramen – Binnen\n", 0, step=1)
        kbui = st.number_input("Kleine ramen – Buiten\n", 0, step=1)
    with c2:
        gb = st.number_input("Grote ramen – Binnen\n", 0, step=1)
        gbui = st.number_input("Grote ramen – Buiten\n", 0, step=1)
    with c3:
        db = st.number_input("Dakramen / moeilijk bereikbaar – Binnen", 0, step=1)
        dbui = st.number_input("Dakramen / moeilijk bereikbaar – Buiten", 0, step=1)

    if st.button("Dienst toevoegen", key="ramen"):
        regels = []
        if kb: regels.append(("Kleine ramen binnen", kb, kb * 2.0))
        if kbui: regels.append(("Kleine ramen buiten", kbui, kbui * 1.5))
        if gb: regels.append(("Grote ramen binnen", gb, gb * 2.5))
        if gbui: regels.append(("Grote ramen buiten", gbui, gbui * 2.0))
        if db: regels.append(("Dakramen / moeilijk bereikbaar binnen", db, db * 2.5))
        if dbui: regels.append(("Dakramen / moeilijk bereikbaar buiten", dbui, dbui * 2.5))

        totaal = max(50, sum(r[2] for r in regels))

        st.session_state.diensten.append({
            "titel": "Ramen wassen",
            "regels": regels,
            "totaal": totaal
        })
        st.success("Ramen wassen toegevoegd")

# ---------------- ZONNEPANELEN ----------------
elif dienst == "Zonnepanelen":
    aantal = st.number_input("Aantal zonnepanelen", 1, step=1)

    if st.button("Dienst toevoegen", key="panelen"):
        regels = [("Zonnepanelen reinigen", aantal, aantal * 5)]
        totaal = max(79, aantal * 5)

        st.session_state.diensten.append({
            "titel": "Zonnepanelen",
            "regels": regels,
            "totaal": totaal
        })
        st.success("Zonnepanelen toegevoegd")

# ---------------- GEVEL ----------------
elif dienst == "Gevelreiniging":
    m2 = st.number_input("Oppervlakte (m²)", 0.1, step=0.1)
    impregneren = st.checkbox("Impregneren (+ €4/m²)")

    if st.button("Dienst toevoegen", key="gevel"):
        regels = [("Gevel reinigen", m2, m2 * 5)]
        if impregneren:
            regels.append(("Impregneren", m2, m2 * 4))

        totaal = max(299, sum(r[2] for r in regels))

        st.session_state.diensten.append({
            "titel": "Gevelreiniging",
            "regels": regels,
            "totaal": totaal
        })
        st.success("Gevelreiniging toegevoegd")

# ---------------- OPRIT / TERRAS ----------------
elif dienst == "Oprit / Terras / Bedrijfsterrein":
    type_keuze = st.radio("Type", ["Oprit", "Terras", "Bedrijfsterrein"], horizontal=True)
    m2 = st.number_input("Oppervlakte (m²)", 0.1, step=0.1)

    c1, c2, c3, c4 = st.columns(4)
    reinigen = c1.checkbox("Reinigen")
    zand = c2.checkbox("Zand invegen")
    onkruid = c3.checkbox("Onkruidmijdend voegzand")
    coating = c4.checkbox("Coating")

    if st.button("Dienst toevoegen", key="oprit"):
        regels = []
        if reinigen: regels.append(("Reinigen", m2, m2 * 3.5))
        if zand: regels.append(("Zand invegen", m2, m2 * 1.0))
        if onkruid: regels.append(("Onkruidmijdend voegzand", m2, m2 * 2.0))
        if coating: regels.append(("Coating", m2, m2 * 3.5))

        if not regels:
            st.warning("Selecteer minstens één optie.")
        else:
            totaal = sum(r[2] for r in regels)
            st.session_state.diensten.append({
                "titel": type_keuze,
                "regels": regels,
                "totaal": totaal
            })
            st.success(f"{type_keuze} toegevoegd")

# ---------------- VERVOERSKOSTEN ----------------
st.divider()
if st.button("🚗 Vervoerskosten toevoegen (€8)"):
    st.session_state.diensten.append({
        "titel": "Vervoerskosten",
        "regels": [("Vervoerskosten", 1, VERVOERSKOSTEN)],
        "totaal": VERVOERSKOSTEN
    })

# ---------------- OVERZICHT ----------------
st.divider()
st.subheader("📋 Overzicht diensten")

for d in st.session_state.diensten:
    st.markdown(f"### {d['titel']}")
    for oms, aantal, prijs in d["regels"]:
        col1, col2 = st.columns([6, 2])
        col1.write(f"{oms} ({aantal})")
        col2.write(f"€ {prijs:.2f}")
    st.markdown(f"**Totaal {d['titel']}: € {d['totaal']:.2f}**")
    st.divider()

subtotaal, btw, totaal = bereken_totalen()

st.write(f"**Subtotaal:** € {subtotaal:.2f}")
st.write(f"**BTW (21%):** € {btw:.2f}")
st.write(f"## **Totaal:** € {totaal:.2f}")

# ---------------- OFFERT KNOP ----------------
st.divider()
if st.button("📄 Maak offerte"):
    if not klant_naam.strip():
        st.error("Gelieve de klantnaam in te vullen.")
    else:
        st.success("Offertegegevens zijn volledig ✔️ (PDF/Excel kan hierna)")
