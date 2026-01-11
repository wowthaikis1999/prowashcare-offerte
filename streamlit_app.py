import streamlit as st
from datetime import datetime
from openpyxl import Workbook
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
import io
import os

# ================= CONFIG =================
st.set_page_config(page_title="ProWashCare Offerte", layout="centered")
st.title("🧼 ProWashCare – Offerte Tool")

BTW = 0.21
VERVOERSKOSTEN = 8.0

BEDRIJFSNAAM = "ProWashCare"
ADRES = "2930 Brasschaat, Antwerpen"
TEL = "+32 470 87 43 39"
EMAIL = "dennisg@prowashcare.com"
WEBSITE = "www.prowashcare.com"

# ================= SESSION STATE =================
if "diensten" not in st.session_state:
    st.session_state.diensten = []

# ================= HULPFUNCTIES =================
def bereken_totalen():
    subtotaal = sum(d["totaal"] for d in st.session_state.diensten)
    btw = subtotaal * BTW
    totaal = subtotaal + btw
    return subtotaal, btw, totaal

def maak_pdf(klant, adres, email):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    content = []

    nummer = datetime.now().strftime("PWC%Y%m%d%H%M")
    datum = datetime.now().strftime("%d-%m-%Y")

    # LOGO
    left = []
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        left.append(Image(logo_path, width=4*cm, height=4*cm))
        left.append(Spacer(1, 10))

    left += [
        Paragraph("<b>ProWashCare – Offerte</b>", styles["Title"]),
        Paragraph(f"<b>Naam:</b> {klant}", styles["Normal"]),
        Paragraph(f"<b>Adres:</b> {adres.replace(chr(10), '<br/>')}", styles["Normal"]),
        Paragraph(f"<b>E-mail:</b> {email}", styles["Normal"]),
        Paragraph(f"<b>Offertenummer:</b> {nummer}", styles["Normal"]),
        Paragraph(f"<b>Datum:</b> {datum}", styles["Normal"]),
    ]

    right = [
        Paragraph(f"<b>{BEDRIJFSNAAM}</b>", styles["Normal"]),
        Paragraph(ADRES, styles["Normal"]),
        Paragraph(f"Tel: {TEL}", styles["Normal"]),
        Paragraph(f"Email: {EMAIL}", styles["Normal"]),
        Paragraph(f"Website: {WEBSITE}", styles["Normal"]),
    ]

    header = Table([[left, right]], colWidths=[10*cm, 5*cm])
    content.append(header)
    content.append(Spacer(1, 20))

    # TABEL
    data = [["Omschrijving", "Bedrag (€)"]]
    for d in st.session_state.diensten:
        for r in d["regels"]:
            data.append([r[0], f"{r[2]:.2f}"])
        data.append([f"<b>Subtotaal {d['titel']}</b>", f"<b>{d['totaal']:.2f}</b>"])

    sub, btw, tot = bereken_totalen()
    data += [
        ["", ""],
        ["Subtotaal", f"{sub:.2f}"],
        ["BTW 21%", f"{btw:.2f}"],
        ["<b>Totaal</b>", f"<b>{tot:.2f}</b>"],
    ]

    content.append(Table(data, colWidths=[11*cm, 4*cm]))
    doc.build(content)
    buffer.seek(0)
    return buffer

def maak_excel(klant):
    wb = Workbook()
    ws = wb.active
    ws.title = "Offerte"

    ws.append(["ProWashCare – Offerte"])
    ws.append([f"Klant: {klant}"])
    ws.append([])

    ws.append(["Omschrijving", "Bedrag (€)"])
    for d in st.session_state.diensten:
        for r in d["regels"]:
            ws.append([r[0], r[2]])
        ws.append([f"Subtotaal {d['titel']}", d["totaal"]])

    sub, btw, tot = bereken_totalen()
    ws.append([])
    ws.append(["Subtotaal", sub])
    ws.append(["BTW 21%", btw])
    ws.append(["Totaal", tot])

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

# ================= KLANT =================
st.subheader("👤 Klantgegevens")
c1, c2 = st.columns(2)
with c1:
    klant = st.text_input("Naam")
    klant_email = st.text_input("E-mail")
with c2:
    klant_adres = st.text_area("Adres", height=80)

# ================= DIENST SELECTIE =================
st.divider()
dienst = st.selectbox("Dienst", [
    "Ramen wassen", "Zonnepanelen", "Gevelreiniging", "Oprit / Terras / Bedrijfsterrein"
])

# ================= RAMEN =================
if dienst == "Ramen wassen":
    st.subheader("Ramen wassen")

    st.markdown("**Binnen**")
    c1, c2, c3 = st.columns(3)
    kb = c1.number_input("Kleine ramen", 0, step=1)
    gb = c2.number_input("Grote ramen", 0, step=1)
    db = c3.number_input("Dakramen / moeilijk bereikbaar", 0, step=1)

    st.markdown("**Buiten**")
    c4, c5, c6 = st.columns(3)
    kbui = c4.number_input("Kleine ramen ", 0, step=1)
    gbui = c5.number_input("Grote ramen ", 0, step=1)
    dbui = c6.number_input("Dakramen / moeilijk bereikbaar ", 0, step=1)

    if st.button("Dienst toevoegen"):
        regels = []
        if kb: regels.append(("Kleine ramen binnen", kb, kb*2))
        if kbui: regels.append(("Kleine ramen buiten", kbui, kbui*1.5))
        if gb: regels.append(("Grote ramen binnen", gb, gb*2.5))
        if gbui: regels.append(("Grote ramen buiten", gbui, gbui*2))
        if db: regels.append(("Dakramen / moeilijk bereikbaar binnen", db, db*2.5))
        if dbui: regels.append(("Dakramen / moeilijk bereikbaar buiten", dbui, dbui*2.5))

        totaal = max(50, sum(r[2] for r in regels))
        st.session_state.diensten.append({
            "titel": "Ramen wassen",
            "regels": regels,
            "totaal": totaal
        })

# ================= ANDERE DIENSTEN =================
elif dienst == "Zonnepanelen":
    aantal = st.number_input("Aantal zonnepanelen", 1, step=1)
    if st.button("Dienst toevoegen"):
        totaal = max(79, aantal*5)
        st.session_state.diensten.append({
            "titel": "Zonnepanelen",
            "regels": [("Zonnepanelen reinigen", aantal, aantal*5)],
            "totaal": totaal
        })

elif dienst == "Gevelreiniging":
    m2 = st.number_input("Oppervlakte (m²)", 0.1, step=0.1)
    impreg = st.checkbox("Impregneren")
    if st.button("Dienst toevoegen"):
        regels = [("Gevel reinigen", m2, m2*5)]
        if impreg:
            regels.append(("Impregneren", m2, m2*4))
        totaal = max(299, sum(r[2] for r in regels))
        st.session_state.diensten.append({
            "titel": "Gevelreiniging",
            "regels": regels,
            "totaal": totaal
        })

elif dienst == "Oprit / Terras / Bedrijfsterrein":
    type_k = st.radio("Type", ["Oprit", "Terras", "Bedrijfsterrein"], horizontal=True)
    m2 = st.number_input("Oppervlakte (m²)", 0.1, step=0.1)
    c1, c2, c3, c4 = st.columns(4)
    reinigen = c1.checkbox("Reinigen")
    zand = c2.checkbox("Zand invegen")
    onkruid = c3.checkbox("Onkruidmijdend voegzand")
    coating = c4.checkbox("Coating")

    if st.button("Dienst toevoegen"):
        regels = []
        if reinigen: regels.append(("Reinigen", m2, m2*3.5))
        if zand: regels.append(("Zand invegen", m2, m2*1))
        if onkruid: regels.append(("Onkruidmijdend voegzand", m2, m2*2))
        if coating: regels.append(("Coating", m2, m2*3.5))
        if regels:
            st.session_state.diensten.append({
                "titel": type_k,
                "regels": regels,
                "totaal": sum(r[2] for r in regels)
            })

# ================= VERVOER =================
st.divider()
if st.button("🚗 Vervoerskosten toevoegen"):
    st.session_state.diensten.append({
        "titel": "Vervoerskosten",
        "regels": [("Vervoerskosten", 1, VERVOERSKOSTEN)],
        "totaal": VERVOERSKOSTEN
    })

# ================= OVERZICHT =================
st.divider()
st.subheader("📋 Overzicht")

for i, d in enumerate(st.session_state.diensten):
    with st.expander(d["titel"]):
        for r in d["regels"]:
            st.write(f"{r[0]} – € {r[2]:.2f}")
        st.write(f"**Totaal: € {d['totaal']:.2f}**")
        if st.button("❌ Verwijderen", key=f"del{i}"):
            st.session_state.diensten.pop(i)
            st.rerun()

sub, btw, tot = bereken_totalen()
st.write(f"Subtotaal: € {sub:.2f}")
st.write(f"BTW: € {btw:.2f}")
st.write(f"## Totaal: € {tot:.2f}")

# ================= EXPORT =================
st.divider()
if klant:
    c1, c2 = st.columns(2)
    c1.download_button("📄 Download PDF", maak_pdf(klant, klant_adres, klant_email), "offerte.pdf")
    c2.download_button("📊 Download Excel", maak_excel(klant), "offerte.xlsx")
else:
    st.info("Vul klantgegevens in om te exporteren")
