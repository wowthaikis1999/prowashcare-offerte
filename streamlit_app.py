import streamlit as st
from datetime import datetime
from openpyxl import Workbook
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
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
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Right", alignment=TA_RIGHT))
    content = []

    nummer = datetime.now().strftime("PWC%Y%m%d%H%M")
    datum = datetime.now().strftime("%d-%m-%Y")

    left = [
        Paragraph("<b>ProWashCare – Offerte</b>", styles["Title"]),
        Spacer(1, 6),
        Paragraph(f"<b>Naam:</b> {klant}", styles["Normal"]),
        Paragraph(f"<b>Adres:</b> {adres.replace(chr(10), '<br/>')}", styles["Normal"]),
        Paragraph(f"<b>E-mail:</b> {email}", styles["Normal"]),
        Paragraph(f"<b>Offertenummer:</b> {nummer}", styles["Normal"]),
        Paragraph(f"<b>Datum:</b> {datum}", styles["Normal"]),
    ]

    right = [
        Paragraph("<b>ProWashCare</b>", styles["Normal"]),
        Paragraph("2930 Brasschaat, Antwerpen", styles["Normal"]),
        Paragraph("Tel: +32 470 87 43 39", styles["Normal"]),
        Paragraph("dennisg@prowashcare.com", styles["Normal"]),
        Paragraph("www.prowashcare.com", styles["Normal"]),
    ]

    header = Table([[left, right]], colWidths=[10 * cm, 5 * cm])
    header.setStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
    ])

    content.append(header)
    content.append(Spacer(1, 20))

    data = [["Omschrijving", "Bedrag (€)"]]

    for d in st.session_state.diensten:
        data.append([Paragraph(f"<b>{d['titel']}</b>", styles["Normal"]), ""])
        for r in d["regels"]:
            data.append([f"– {r[0]}", f"{r[2]:.2f}"])
        data.append(["Subtotaal", f"{d['totaal']:.2f}"])
        data.append(["", ""])

    subtotaal, btw, totaal = bereken_totalen()
    data.append(["Subtotaal (excl. btw)", f"{subtotaal:.2f}"])
    data.append(["BTW 21%", f"{btw:.2f}"])
    data.append([
        Paragraph("<b>Totaal (incl. btw)</b>", styles["Normal"]),
        Paragraph(f"<b>{totaal:.2f}</b>", styles["Normal"]),
    ])

    table = Table(data, colWidths=[12 * cm, 3 * cm])
    table.setStyle([
        ("GRID", (0, 0), (-1, -1), 0.25, "grey"),
        ("BACKGROUND", (0, 0), (-1, 0), "#EEEEEE"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
    ])

    content.append(table)
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
    ws.append(["BTW", btw])
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

# ---------------- EXPORT ----------------
st.divider()

if klant_naam:
    c1, c2 = st.columns(2)
    c1.download_button(
        "📄 Maak PDF offerte",
        maak_pdf(klant_naam, klant_adres, klant_email),
        "offerte.pdf",
    )
    c2.download_button(
        "📊 Maak Excel offerte",
        maak_excel(klant_naam),
        "offerte.xlsx",
    )
else:
    st.info("Vul eerst klantgegevens in")
