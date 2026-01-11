import streamlit as st
from datetime import datetime
from openpyxl import Workbook
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
import io

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


def maak_pdf(klant, adres, email):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, rightMargin=36, leftMargin=36, topMargin=36)
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="Rechts",
        parent=styles["Normal"],
        alignment=TA_RIGHT
    ))

    content = []

    # ---------- HEADER ----------
    content.append(Paragraph("<b>ProWashCare</b>", styles["Title"]))
    content.append(Paragraph("Professionele reinigingsdiensten", styles["Normal"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph(
        f"<b>Offerte voor:</b><br/>{klant}<br/>{adres}<br/>{email}",
        styles["Normal"]
    ))

    content.append(Paragraph(
        f"Datum: {datetime.now().strftime('%d-%m-%Y')}",
        styles["Rechts"]
    ))

    content.append(Spacer(1, 20))

    # ---------- DIENSTEN ----------
    for d in st.session_state.diensten:
        content.append(Paragraph(f"<b>{d['titel']}</b>", styles["Heading3"]))

        table_data = []
        for r in d["regels"]:
            table_data.append([
                f"– {r[0]}",
                f"€ {r[2]:.2f}"
            ])

        table_data.append([
            "<b>Subtotaal</b>",
            f"<b>€ {d['totaal']:.2f}</b>"
        ])

        content.append(Table(
            table_data,
            colWidths=[350, 100],
            hAlign="LEFT"
        ))
        content.append(Spacer(1, 14))

    # ---------- TOTALEN ----------
    subtotaal, btw, totaal = bereken_totalen()

    totalen = [
        ["Subtotaal", f"€ {subtotaal:.2f}"],
        ["BTW 21%", f"€ {btw:.2f}"],
        ["Totaal", f"€ {totaal:.2f}"]
    ]

    content.append(Spacer(1, 12))
    content.append(Table(totalen, colWidths=[350, 100]))

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
        ws.append([f"Totaal {d['titel']}", d["totaal"]])

    subtotaal, btw, totaal = bereken_totalen()
    ws.append([])
    ws.append(["Subtotaal", subtotaal])
    ws.append(["BTW 21%", btw])
    ws.append(["Totaal", totaal])

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

# ---------------- KLANTGEGEVENS ----------------
st.subheader("👤 Klantgegevens")
c1, c2 = st.columns(2)
with c1:
    klant_naam = st.text_input("Naam")
    klant_email = st.text_input("E-mail")
with c2:
    klant_adres = st.text_area("Adres", height=80)

# ---------------- DIENST SELECTIE ----------------
st.divider()
dienst = st.selectbox("Dienst", [
    "Ramen wassen",
    "Zonnepanelen",
    "Gevelreiniging",
    "Oprit / Terras / Bedrijfsterrein"
])

# ---------------- RAMEN WASSEN ----------------
if dienst == "Ramen wassen":
    st.subheader("Ramen wassen")

    st.markdown("**Binnen**")
    b1, b2, b3 = st.columns(3)
    kb = b1.number_input("Kleine ramen", 0, step=1)
    gb = b2.number_input("Grote ramen", 0, step=1)
    db = b3.number_input("Dakramen / moeilijk bereikbaar", 0, step=1)

    st.markdown("**Buiten**")
    b4, b5, b6 = st.columns(3)
    kbui = b4.number_input("Kleine ramen ", 0, step=1)
    gbui = b5.number_input("Grote ramen ", 0, step=1)
    dbui = b6.number_input("Dakramen / moeilijk bereikbaar ", 0, step=1)

    if st.button("Dienst toevoegen"):
        regels = []
        if kb: regels.append(("Kleine ramen binnen", kb, kb * 2))
        if kbui: regels.append(("Kleine ramen buiten", kbui, kbui * 1.5))
        if gb: regels.append(("Grote ramen binnen", gb, gb * 2.5))
        if gbui: regels.append(("Grote ramen buiten", gbui, gbui * 2))
        if db: regels.append(("Dakramen binnen", db, db * 2.5))
        if dbui: regels.append(("Dakramen buiten", dbui, dbui * 2.5))

        totaal = max(50, sum(r[2] for r in regels))
        st.session_state.diensten.append({"titel": "Ramen wassen", "regels": regels, "totaal": totaal})

# ---------------- ZONNEPANELEN ----------------
elif dienst == "Zonnepanelen":
    st.subheader("Zonnepanelen")
    aantal = st.number_input("Aantal zonnepanelen", 1, step=1)
    if st.button("Dienst toevoegen"):
        regels = [("Zonnepanelen reinigen", aantal, aantal * 5)]
        totaal = max(79, aantal * 5)
        st.session_state.diensten.append({"titel": "Zonnepanelen", "regels": regels, "totaal": totaal})

# ---------------- GEVEL ----------------
elif dienst == "Gevelreiniging":
    st.subheader("Gevelreiniging")
    m2 = st.number_input("Oppervlakte (m²)", 0.1, step=0.1)
    impreg = st.checkbox("Impregneren")
    if st.button("Dienst toevoegen"):
        regels = [("Gevel reinigen", m2, m2 * 5)]
        if impreg:
            regels.append(("Impregneren", m2, m2 * 4))
        totaal = max(299, sum(r[2] for r in regels))
        st.session_state.diensten.append({"titel": "Gevelreiniging", "regels": regels, "totaal": totaal})

# ---------------- OPRIT ----------------
elif dienst == "Oprit / Terras / Bedrijfsterrein":
    st.subheader("Oprit / Terras / Bedrijfsterrein")
    type_k = st.radio("Type", ["Oprit", "Terras", "Bedrijfsterrein"], horizontal=True)
    m2 = st.number_input("Oppervlakte (m²)", 0.1, step=0.1)

    c1, c2, c3, c4 = st.columns(4)
    reinigen = c1.checkbox("Reinigen")
    zand = c2.checkbox("Zand invegen")
    onkruid = c3.checkbox("Onkruidmijdend voegzand")
    coating = c4.checkbox("Coating")

    if st.button("Dienst toevoegen"):
        regels = []
        if reinigen: regels.append(("Reinigen", m2, m2 * 3.5))
        if zand: regels.append(("Zand invegen", m2, m2 * 1))
        if onkruid: regels.append(("Onkruidmijdend voegzand", m2, m2 * 2))
        if coating: regels.append(("Coating", m2, m2 * 3.5))

        if regels:
            st.session_state.diensten.append({"titel": type_k, "regels": regels, "totaal": sum(r[2] for r in regels)})

# ---------------- VERVOERSKOSTEN ----------------
st.divider()
if st.button("🚗 Vervoerskosten toevoegen"):
    st.session_state.diensten.append({
        "titel": "Vervoerskosten",
        "regels": [("Vervoerskosten", 1, VERVOERSKOSTEN)],
        "totaal": VERVOERSKOSTEN
    })

# ---------------- OVERZICHT ----------------
st.divider()
st.subheader("📋 Overzicht")

for i, d in enumerate(st.session_state.diensten):
    with st.expander(d["titel"], expanded=False):
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

# ---------------- EXPORT ----------------
st.divider()
if klant_naam:
    col1, col2 = st.columns(2)
    col1.download_button("📄 Maak PDF offerte", maak_pdf(klant_naam, klant_adres, klant_email), "offerte.pdf")
    col2.download_button("📊 Maak Excel offerte", maak_excel(klant_naam), "offerte.xlsx")
else:
    st.info("Vul eerst klantgegevens in")
