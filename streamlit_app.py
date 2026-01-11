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

st.set_page_config(page_title="ProWashCare Offerte", layout="centered")
st.title("🧼 ProWashCare – Offerte Tool")

# ---------------- BEDRIJF ----------------
BEDRIJFSNAAM = "ProWashCare"
ADRES = "2930 Brasschaat, Antwerpen"
TELEFOON = "+32 470 87 43 39"
EMAIL = "dennisg@prowashcare.com"
WEBSITE = "www.prowashcare.com"

VERVOERSKOSTEN = 8.0
OPRIT_MINIMUM = 299.0

# ---------------- SESSION ----------------
if "diensten" not in st.session_state:
    st.session_state.diensten = []
    st.session_state.vervoer_toegevoegd = False

# ================= FUNCTIES =================
def bereken_totaal():
    diensten_clean = st.session_state.diensten.copy()
    subtotaal = sum(d[1] for d in diensten_clean)
    btw = subtotaal * 0.21
    totaal = subtotaal + btw
    return diensten_clean, subtotaal, btw, totaal


def maak_pdf_en_excel(diensten_final, klant_naam, klant_adres, klant_email, subtotaal, btw, totaal):
    nu = datetime.now()
    nummer = nu.strftime("PWC%Y%m%d%H%M")
    datum_str = nu.strftime('%d-%m-%Y')

    # -------- EXCEL --------
    wb = Workbook()
    ws = wb.active
    ws.title = "Offerte"

    ws["A1"] = "ProWashCare – OFFERTE"
    ws["A1"].font = Font(bold=True, size=16)
    ws.merge_cells("A1:B1")

    ws["A3"] = f"Klant: {klant_naam}"
    ws["A4"] = f"Offertenummer: {nummer}"
    ws["A5"] = f"Datum: {datum_str}"

    ws["A7"] = "Omschrijving"
    ws["B7"] = "Bedrag (€)"
    ws["A7"].font = ws["B7"].font = Font(bold=True)

    row = 8
    for oms, bed in diensten_final:
        ws[f"A{row}"] = oms
        ws[f"B{row}"] = bed
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

    content.append(Paragraph("<b>ProWashCare – Offerte</b>", styles["Title"]))
    content.append(Spacer(1, 12))
    content.append(Paragraph(f"Klant: {klant_naam}", styles["Normal"]))
    content.append(Paragraph(f"Adres: {klant_adres}", styles["Normal"]))
    content.append(Paragraph(f"E-mail: {klant_email}", styles["Normal"]))
    content.append(Paragraph(f"Offertenummer: {nummer}", styles["Normal"]))
    content.append(Paragraph(f"Datum: {datum_str}", styles["Normal"]))
    content.append(Spacer(1, 20))

    table_data = [["Omschrijving", "Bedrag (€)"]]
    for oms, bed in diensten_final:
        table_data.append([oms, f"€ {bed:.2f}"])

    table_data += [
        ["", ""],
        ["Subtotaal", f"€ {subtotaal:.2f}"],
        ["BTW 21%", f"€ {btw:.2f}"],
        ["Totaal", f"€ {totaal:.2f}"],
    ]

    content.append(RLTable(table_data, colWidths=[350, 100]))
    pdf.build(content)
    pdf_buffer.seek(0)

    return excel_buffer, pdf_buffer, nummer

# ================= UI =================
klant_naam = st.text_input("Naam")
klant_email = st.text_input("E-mail")
klant_adres = st.text_area("Adres")

st.divider()

st.write("### Diensten")
dienst = st.selectbox("Dienst", [
    "Ramen wassen", "Zonnepanelen", "Gevelreiniging", "Oprit / Terras / Bedrijfsterrein"
])

bedrag = 0
omschrijving = dienst

if dienst == "Zonnepanelen":
    aantal = st.number_input("Aantal zonnepanelen", min_value=1, step=1)
    bedrag = max(79, aantal * 5)
    omschrijving += f" ({aantal} panelen)"

if st.button("Dienst toevoegen") and bedrag > 0:
    if not st.session_state.vervoer_toegevoegd:
        st.session_state.diensten.append(("Vervoerskosten", VERVOERSKOSTEN))
        st.session_state.vervoer_toegevoegd = True
    st.session_state.diensten.append((omschrijving, bedrag))
    st.rerun()

st.divider()
st.write("### Overzicht")

diensten_final, subtotaal, btw, totaal = bereken_totaal()
for oms, bed in diensten_final:
    st.write(f"{oms} — € {bed:.2f}")

st.write(f"**Totaal:** € {totaal:.2f}")

# ================= DOWNLOAD KNOPPEN =================
st.divider()
st.write("### Offerte downloaden")

col1, col2 = st.columns(2)

with col1:
    if st.button("📄 Maak & download PDF"):
        if klant_naam.strip():
            excel_buf, pdf_buf, nummer = maak_pdf_en_excel(
                diensten_final, klant_naam, klant_adres, klant_email, subtotaal, btw, totaal
            )
            st.download_button(
                "⬇️ Download PDF",
                pdf_buf,
                f"Offerte_{nummer}.pdf",
                "application/pdf"
            )
        else:
            st.error("Naam ontbreekt")

with col2:
    if st.button("📊 Maak & download Excel"):
        if klant_naam.strip():
            excel_buf, pdf_buf, nummer = maak_pdf_en_excel(
                diensten_final, klant_naam, klant_adres, klant_email, subtotaal, btw, totaal
            )
            st.download_button(
                "⬇️ Download Excel",
                excel_buf,
                f"Offerte_{nummer}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("Naam ontbreekt")
