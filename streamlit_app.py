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

# ---------------- CONFIG ----------------
st.set_page_config(page_title="ProWashCare Offerte", layout="centered")
st.title("🧼 ProWashCare – Offerte Tool")

BEDRIJFSNAAM = "ProWashCare"
ADRES = "2930 Brasschaat, Antwerpen"
TELEFOON = "+32 470 87 43 39"
EMAIL = "dennisg@prowashcare.com"
WEBSITE = "www.prowashcare.com"

VERVOERSKOSTEN = 8.0

# ---------------- SESSION STATE ----------------
if "diensten" not in st.session_state:
    st.session_state.diensten = []
    st.session_state.vervoer_toegevoegd = False

# ---------------- FUNCTIES ----------------
def bereken_totaal():
    diensten_clean = []
    for d in st.session_state.diensten:
        if isinstance(d, tuple) and len(d) == 2 and isinstance(d[1], (int, float)):
            diensten_clean.append(d)

    subtotaal = sum(d[1] for d in diensten_clean)
    btw = subtotaal * 0.21
    totaal = subtotaal + btw
    return diensten_clean, subtotaal, btw, totaal


def maak_pdf_en_excel(diensten, klant_naam, klant_adres, klant_email, subtotaal, btw, totaal):
    nu = datetime.now()
    nummer = nu.strftime("PWC%Y%m%d%H%M")
    datum = nu.strftime("%d-%m-%Y")

    # -------- EXCEL --------
    wb = Workbook()
    ws = wb.active
    ws.title = "Offerte"

    bold = Font(bold=True)
    ws["A1"] = "ProWashCare – OFFERTE"
    ws["A1"].font = Font(bold=True, size=16)
    ws.merge_cells("A1:B1")

    ws["A3"] = f"Klant: {klant_naam}"
    ws["A4"] = f"Offertenummer: {nummer}"
    ws["A5"] = f"Datum: {datum}"
    ws["A3"].font = ws["A4"].font = ws["A5"].font = bold

    ws["A7"] = "Omschrijving"
    ws["B7"] = "Bedrag (€)"
    ws["A7"].font = ws["B7"].font = bold

    row = 8
    for oms, prijs in diensten:
        ws[f"A{row}"] = oms
        ws[f"B{row}"] = prijs
        ws[f"B{row}"].number_format = '€#,##0.00'
        row += 1

    ws[f"A{row}"] = "Subtotaal"
    ws[f"B{row}"] = subtotaal
    row += 1
    ws[f"A{row}"] = "BTW 21%"
    ws[f"B{row}"] = btw
    row += 1
    ws[f"A{row}"] = "Totaal"
    ws[f"B{row}"] = totaal

    excel_buffer = io.BytesIO()
    wb.save(excel_buffer)
    excel_buffer.seek(0)

    # -------- PDF --------
    pdf_buffer = io.BytesIO()
    pdf = SimpleDocTemplate(pdf_buffer)
    styles = getSampleStyleSheet()
    content = []

    if os.path.exists("logo.png"):
        img = utils.ImageReader("logo.png")
        iw, ih = img.getSize()
        logo = Image("logo.png", width=4*cm, height=(4*cm*ih/iw))
        content.append(logo)

    content.append(Paragraph("<b>Offerte</b>", styles["Title"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph(f"<b>Klant:</b> {klant_naam}", styles["Normal"]))
    content.append(Paragraph(f"<b>Adres:</b> {klant_adres.replace(chr(10), '<br/>')}", styles["Normal"]))
    content.append(Paragraph(f"<b>E-mail:</b> {klant_email}", styles["Normal"]))
    content.append(Paragraph(f"Offertenummer: {nummer}", styles["Normal"]))
    content.append(Paragraph(f"Datum: {datum}", styles["Normal"]))
    content.append(Spacer(1, 12))

    data = [["Omschrijving", "Bedrag"]]
    for oms, prijs in diensten:
        data.append([Paragraph(oms.replace("\n", "<br/>"), styles["Normal"]), f"€ {prijs:.2f}"])

    data += [
        ["", ""],
        ["Subtotaal", f"€ {subtotaal:.2f}"],
        ["BTW 21%", f"€ {btw:.2f}"],
        ["Totaal", f"€ {totaal:.2f}"]
    ]

    content.append(RLTable(data, colWidths=[350, 100]))
    pdf.build(content)
    pdf_buffer.seek(0)

    return excel_buffer, pdf_buffer, nummer

# ---------------- UI ----------------
st.subheader("👤 Klantgegevens")
klant_naam = st.text_input("Naam")
klant_email = st.text_input("E-mail")
klant_adres = st.text_area("Adres", height=80)

st.divider()
dienst = st.selectbox("Dienst", [
    "Ramen wassen", "Zonnepanelen", "Gevelreiniging", "Oprit / Terras / Bedrijfsterrein"
])

bedrag = 0
omschrijving = dienst

if dienst == "Zonnepanelen":
    aantal = st.number_input("Aantal panelen", 1, step=1)
    bedrag = max(79, aantal * 5)
    omschrijving += f"\n({aantal} panelen)"

if st.button("Dienst toevoegen") and bedrag > 0:
    if not st.session_state.vervoer_toegevoegd:
        st.session_state.diensten.append(("Vervoerskosten", VERVOERSKOSTEN))
        st.session_state.vervoer_toegevoegd = True
    st.session_state.diensten.append((omschrijving, bedrag))
    st.rerun()

st.divider()
st.subheader("📋 Overzicht")

diensten_final, subtotaal, btw, totaal = bereken_totaal()

for oms, prijs in diensten_final:
    st.write(f"{oms} — € {prijs:.2f}")

st.write(f"**Subtotaal:** € {subtotaal:.2f}")
st.write(f"**BTW:** € {btw:.2f}")
st.write(f"## **Totaal:** € {totaal:.2f}")

if st.button("📄 Maak offerte"):
    excel, pdf, nr = maak_pdf_en_excel(
        diensten_final, klant_naam, klant_adres, klant_email, subtotaal, btw, totaal
    )

    st.download_button("📊 Download Excel", excel, f"Offerte_{nr}.xlsx")
    st.download_button("📄 Download PDF", pdf, f"Offerte_{nr}.pdf")
