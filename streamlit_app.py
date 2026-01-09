import streamlit as st
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table as RLTable, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib import utils
from datetime import datetime
import io
import os

# ================= PRIJZEN =================

PRIJZEN = {
    "ramen": {
        "klein_binnen": 1.5,
        "klein_buiten": 1.7,
        "groot_binnen": 2.0,
        "groot_buiten": 2.2,
        "dak_binnen": 2.5,
        "dak_buiten": 2.5,
        "minimum": 50.0
    },
    "zonnepanelen": {
        "per_stuk": 5.0,
        "minimum": 79.0
    },
    "gevel": {
        "reiniging_per_m2": 5.0,
        "impregneren_per_m2": 4.0,
        "minimum": 299.0
    },
    "oprit": {
        "reinigen": 3.5,
        "zand": 1.0,
        "onkruid": 2.0,
        "coating": 5.0,
        "minimum": 299.0
    },
    "vervoer": 8.0
}

# ================= BASIS =================

st.set_page_config(page_title="ProWashCare Offerte", layout="centered")
st.title("🧼 ProWashCare – Offerte Tool")

BEDRIJFSNAAM = "ProWashCare"
ADRES = "2930 Brasschaat, Antwerpen"
TELEFOON = "+32 470 87 43 39"
EMAIL = "dennisg@prowashcare.com"
WEBSITE = "www.prowashcare.com"

if "diensten" not in st.session_state:
    st.session_state.diensten = []
    st.session_state.vervoer_toegevoegd = False

# ================= FUNCTIES =================

def bereken_totaal():
    oprit_diensten = [d for d in st.session_state.diensten if d[0].startswith(("Oprit", "Terras", "Bedrijfsterrein"))]
    oprit_totaal = sum(d[1] for d in oprit_diensten)

    diensten_clean = [d for d in st.session_state.diensten if not d[0].startswith("Minimumtarief")]

    verschil = max(0, PRIJZEN["oprit"]["minimum"] - oprit_totaal) if oprit_diensten else 0

    if verschil > 0:
        diensten_clean.append(("Minimumtarief oprit/terras/bedrijfsterrein", verschil))

    subtotaal = sum(d[1] for d in diensten_clean)
    btw = subtotaal * 0.21
    totaal = subtotaal + btw

    return diensten_clean, subtotaal, btw, totaal

# ================= UI =================

klant = st.text_input("Klantnaam")

st.write("### Kies een dienst")
dienst = st.selectbox(
    "Dienst",
    ["Ramen wassen", "Zonnepanelen", "Gevelreiniging", "Oprit / Terras / Bedrijfsterrein"],
    label_visibility="collapsed"
)

omschrijving = dienst
eindbedrag = 0

# ================= RAMEN =================

if dienst == "Ramen wassen":
    col1, col2 = st.columns(2)
    with col1:
        klein_binnen = st.number_input("Kleine ramen - Binnen", 0)
        groot_binnen = st.number_input("Grote ramen - Binnen", 0)
        dak_binnen = st.number_input("Dakramen - Binnen", 0)
    with col2:
        klein_buiten = st.number_input("Kleine ramen - Buiten", 0)
        groot_buiten = st.number_input("Grote ramen - Buiten", 0)
        dak_buiten = st.number_input("Dakramen - Buiten", 0)

    berekend = (
        klein_binnen * PRIJZEN["ramen"]["klein_binnen"] +
        klein_buiten * PRIJZEN["ramen"]["klein_buiten"] +
        groot_binnen * PRIJZEN["ramen"]["groot_binnen"] +
        groot_buiten * PRIJZEN["ramen"]["groot_buiten"] +
        dak_binnen * PRIJZEN["ramen"]["dak_binnen"] +
        dak_buiten * PRIJZEN["ramen"]["dak_buiten"]
    )

    eindbedrag = max(PRIJZEN["ramen"]["minimum"], berekend)

# ================= ZONNEPANELEN =================

elif dienst == "Zonnepanelen":
    aantal = st.number_input("Aantal zonnepanelen", min_value=1)
    berekend = aantal * PRIJZEN["zonnepanelen"]["per_stuk"]
    eindbedrag = max(PRIJZEN["zonnepanelen"]["minimum"], berekend)
    omschrijving += f"\n({aantal} panelen)"

# ================= GEVEL =================

elif dienst == "Gevelreiniging":
    m2 = st.number_input("Oppervlakte (m²)", min_value=0.1)
    impregneer = st.checkbox("Impregneren")

    berekend = m2 * PRIJZEN["gevel"]["reiniging_per_m2"]
    if impregneer:
        berekend += m2 * PRIJZEN["gevel"]["impregneren_per_m2"]

    eindbedrag = max(PRIJZEN["gevel"]["minimum"], berekend)
    omschrijving += f"\n{m2} m²" + (" (Impregneren)" if impregneer else "")

# ================= OPRIT =================

elif dienst == "Oprit / Terras / Bedrijfsterrein":
    type_keuze = st.radio("Type", ["Oprit", "Terras", "Bedrijfsterrein"], horizontal=True)
    m2 = st.number_input("Oppervlakte (m²)", min_value=0.1)

    col1, col2, col3, col4 = st.columns(4)
    reinigen = col1.checkbox("Reinigen")
    zand = col2.checkbox("Zand")
    onkruid = col3.checkbox("Onkruidmijdend")
    coating = col4.checkbox("Coating")

    berekend = 0
    opties = []

    if reinigen:
        berekend += m2 * PRIJZEN["oprit"]["reinigen"]
        opties.append("Reinigen")
    if zand:
        berekend += m2 * PRIJZEN["oprit"]["zand"]
        opties.append("Zand")
    if onkruid:
        berekend += m2 * PRIJZEN["oprit"]["onkruid"]
        opties.append("Onkruidmijdend")
    if coating:
        berekend += m2 * PRIJZEN["oprit"]["coating"]
        opties.append("Coating")

    if opties:
        omschrijving = f"{type_keuze}\n{m2} m² ({', '.join(opties)})"
        eindbedrag = berekend
    else:
        st.warning("Selecteer minstens één optie.")

# ================= TOEVOEGEN =================

if st.button("Dienst toevoegen") and eindbedrag > 0:
    if not st.session_state.vervoer_toegevoegd:
        st.session_state.diensten.append(("Vervoerskosten", PRIJZEN["vervoer"]))
        st.session_state.vervoer_toegevoegd = True

    st.session_state.diensten.append((omschrijving, eindbedrag))
    st.success("Dienst toegevoegd")
    st.rerun()

# ================= OVERZICHT =================

st.write("### Overzicht diensten")
diensten_final, subtotaal, btw, totaal = bereken_totaal()

for oms, bed in diensten_final:
    st.write(f"**{oms.replace(chr(10), '  ')}** — € {bed:.2f}")

st.write("---")
st.write(f"**Subtotaal:** € {subtotaal:.2f}")
st.write(f"**BTW (21%):** € {btw:.2f}")
st.write(f"**Totaal:** € {totaal:.2f}")
