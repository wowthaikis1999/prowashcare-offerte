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


def vind_dienst(titel):
    for d in st.session_state.diensten:
        if d["titel"] == titel:
            return d
    return None


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

    header = Table([[
        [
            Paragraph("<b>ProWashCare – Offerte</b>", styles["Title"]),
            Spacer(1, 6),
            Paragraph(f"<b>Naam:</b> {klant}", styles["Normal"]),
            Paragraph(f"<b>Adres:</b> {adres.replace(chr(10), '<br/>')}", styles["Normal"]),
            Paragraph(f"<b>E-mail:</b> {email}", styles["Normal"]),
            Paragraph(f"<b>Offertenummer:</b> {nummer}", styles["Normal"]),
            Paragraph(f"<b>Datum:</b> {datum}", styles["Normal"]),
        ],
        [
            Paragraph("<b>ProWashCare</b>", styles["Normal"]),
            Paragraph("2930 Brasschaat, Antwerpen", styles["Normal"]),
            Paragraph("Tel: +32 470 87 43 39", styles["Normal"]),
            Paragraph("dennisg@prowashcare.com", styles["Normal"]),
            Paragraph("www.prowashcare.com", styles["Normal"]),
        ]
    ]], colWidths=[10 * cm, 5 * cm])

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
            data.append([f"– {r['label']} ({r['aantal']}x)", f"{r['prijs']:.2f}"])
        data.append(["Subtotaal", f"{d['totaal']:.2f}"])
        data.append(["", ""])

    sub, btw, tot = bereken_totalen()
    data += [
        ["Subtotaal (excl. btw)", f"{sub:.2f}"],
        ["BTW 21%", f"{btw:.2f}"],
        [Paragraph("<b>Totaal (incl. btw)</b>", styles["Normal"]),
         Paragraph(f"<b>{tot:.2f}</b>", styles["Normal"])]
    ]

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

    ws.append(["Omschrijving", "Aantal", "Bedrag (€)"])

    for d in st.session_state.diensten:
        ws.append([d["titel"], "", ""])
        for r in d["regels"]:
            ws.append([r["label"], r["aantal"], r["prijs"]])
        ws.append(["Subtotaal", "", d["totaal"]])
        ws.append([])

    sub, btw, tot = bereken_totalen()
    ws.append(["Subtotaal", "", sub])
    ws.append(["BTW", "", btw])
    ws.append(["Totaal", "", tot])

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

# ---------------- KLANTGEVENS ----------------
st.subheader("👤 Klantgegevens")
c1, c2 = st.columns(2)
with c1:
    klant_naam = st.text_input("Naam")
    klant_email = st.text_input("E-mail")
with c2:
    klant_adres = st.text_area("Adres", height=80)

# ---------------- RAMEN WASSEN ----------------
st.divider()
st.subheader("Ramen wassen")

b1, b2, b3 = st.columns(3)
kb = b1.number_input("Kleine ramen binnen", 0, step=1)
gb = b2.number_input("Grote ramen binnen", 0, step=1)
db = b3.number_input("Dakramen binnen", 0, step=1)

b4, b5, b6 = st.columns(3)
kbui = b4.number_input("Kleine ramen buiten", 0, step=1)
gbui = b5.number_input("Grote ramen buiten", 0, step=1)
dbui = b6.number_input("Dakramen buiten", 0, step=1)

if st.button("Ramen wassen toevoegen / aanpassen"):
    dienst = vind_dienst("Ramen wassen")
    if not dienst:
        dienst = {"titel": "Ramen wassen", "regels": [], "totaal": 0}
        st.session_state.diensten.append(dienst)

    def voeg_toe(label, aantal, prijs_per):
        if aantal == 0:
            return
        for r in dienst["regels"]:
            if r["label"] == label:
                r["aantal"] += aantal
                r["prijs"] += aantal * prijs_per
                return
        dienst["regels"].append({
            "label": label,
            "aantal": aantal,
            "prijs": aantal * prijs_per
        })

    voeg_toe("Kleine ramen binnen", kb, 2)
    voeg_toe("Kleine ramen buiten", kbui, 1.5)
    voeg_toe("Grote ramen binnen", gb, 2.5)
    voeg_toe("Grote ramen buiten", gbui, 2)
    voeg_toe("Dakramen binnen", db, 2.5)
    voeg_toe("Dakramen buiten", dbui, 2.5)

    dienst["totaal"] = max(50, sum(r["prijs"] for r in dienst["regels"]))
    st.success("Ramen wassen aangepast")

# ---------------- OVERZICHT ----------------
st.divider()
st.subheader("📋 Overzicht")

for i, d in enumerate(st.session_state.diensten):
    with st.expander(d["titel"]):
        for r in d["regels"]:
            st.write(f"{r['label']} – {r['aantal']}x – € {r['prijs']:.2f}")
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
    c1, c2 = st.columns(2)
    c1.download_button("📄 PDF offerte", maak_pdf(klant_naam, klant_adres, klant_email), "offerte.pdf")
    c2.download_button("📊 Excel offerte", maak_excel(klant_naam), "offerte.xlsx")
else:
    st.info("Vul eerst klantgegevens in")
