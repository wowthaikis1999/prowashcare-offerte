import streamlit as st
from datetime import datetime
from openpyxl import Workbook
import io

# ---------------- CONFIG ----------------
st.set_page_config(page_title="ProWashCare Offerte", layout="centered")
st.title("🧼 ProWashCare – Offerte Tool")

BTW = 0.21
VERVOERSKOSTEN = 8.0

# ---------------- SESSION ----------------
if "diensten" not in st.session_state:
    st.session_state.diensten = []

# ---------------- FUNCTIES ----------------
def bereken_totaal():
    subtotaal = sum(d["totaal"] for d in st.session_state.diensten)
    btw = subtotaal * BTW
    totaal = subtotaal + btw
    return subtotaal, btw, totaal

# ---------------- DIENST SELECTIE ----------------
st.subheader("➕ Dienst toevoegen")
dienst = st.selectbox(
    "Dienst",
    ["Ramen wassen", "Zonnepanelen", "Gevelreiniging", "Oprit / Terras / Bedrijfsterrein"]
)

# ---------------- RAMEN WASSEN ----------------
if dienst == "Ramen wassen":
    st.markdown("### Ramen wassen")

    c1, c2, c3 = st.columns(3)
    with c1:
        kb = st.number_input("Kleine ramen – Binnen", 0, step=1)
        kbui = st.number_input("Kleine ramen – Buiten", 0, step=1)
    with c2:
        gb = st.number_input("Grote ramen – Binnen", 0, step=1)
        gbui = st.number_input("Grote ramen – Buiten", 0, step=1)
    with c3:
        db = st.number_input("Dakramen / moeilijk bereikbaar – Binnen", 0, step=1)
        dbui = st.number_input("Dakramen / moeilijk bereikbaar – Buiten", 0, step=1)

    if st.button("➕ Dienst toevoegen", key="ramen"):
        regels = []

        if kb: regels.append((f"Kleine ramen binnen ({kb}x)", kb * 2.0))
        if kbui: regels.append((f"Kleine ramen buiten ({kbui}x)", kbui * 1.5))
        if gb: regels.append((f"Grote ramen binnen ({gb}x)", gb * 2.5))
        if gbui: regels.append((f"Grote ramen buiten ({gbui}x)", gbui * 2.0))
        if db: regels.append((f"Dakramen / moeilijk bereikbaar binnen ({db}x)", db * 2.5))
        if dbui: regels.append((f"Dakramen / moeilijk bereikbaar buiten ({dbui}x)", dbui * 2.5))

        totaal = max(50, sum(p for _, p in regels))

        st.session_state.diensten.append({
            "titel": "Ramen wassen",
            "regels": regels,
            "totaal": totaal
        })
        st.success("Ramen wassen toegevoegd")

# ---------------- ZONNEPANELEN ----------------
elif dienst == "Zonnepanelen":
    aantal = st.number_input("Aantal zonnepanelen", 1, step=1)

    if st.button("➕ Dienst toevoegen", key="panelen"):
        regels = [(f"Zonnepanelen reinigen ({aantal}x)", aantal * 5)]
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
    impregneer = st.checkbox("Impregneren (+ €4/m²)")

    if st.button("➕ Dienst toevoegen", key="gevel"):
        regels = [(f"Gevel reinigen ({m2} m²)", m2 * 5)]

        if impregneer:
            regels.append((f"Impregneren ({m2} m²)", m2 * 4))

        totaal = max(299, sum(p for _, p in regels))

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

    if st.button("➕ Dienst toevoegen", key="oprit"):
        regels = []

        if reinigen: regels.append((f"Reinigen ({m2} m²)", m2 * 3.5))
        if zand: regels.append((f"Zand invegen ({m2} m²)", m2 * 1.0))
        if onkruid: regels.append((f"Onkruidmijdend voegzand ({m2} m²)", m2 * 2.0))
        if coating: regels.append((f"Coating ({m2} m²)", m2 * 3.5))

        if not regels:
            st.warning("Selecteer minstens één optie")
        else:
            totaal = sum(p for _, p in regels)
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
        "regels": [("Vervoerskosten", VERVOERSKOSTEN)],
        "totaal": VERVOERSKOSTEN
    })

# ---------------- OVERZICHT ----------------
st.divider()
st.subheader("📋 Overzicht diensten")

subtotaal = 0
for i, d in enumerate(st.session_state.diensten):
    st.markdown(f"### {d['titel']}")
    for oms, prijs in d["regels"]:
        c1, c2 = st.columns([6, 2])
        c1.write(oms)
        c2.write(f"€ {prijs:.2f}")
    st.markdown(f"**Totaal {d['titel']}: € {d['totaal']:.2f}**")
    subtotaal += d["totaal"]
    st.divider()

btw = subtotaal * BTW
totaal = subtotaal + btw

st.write(f"**Subtotaal:** € {subtotaal:.2f}")
st.write(f"**BTW (21%):** € {btw:.2f}")
st.write(f"## **Totaal:** € {totaal:.2f}")
