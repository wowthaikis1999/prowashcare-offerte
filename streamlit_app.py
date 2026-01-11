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

# ================= BASIS =================
st.set_page_config(page_title="ProWashCare Offerte", layout="centered")
st.title("🧼 ProWashCare – Offerte Tool")

BEDRIJFSNAAM = "ProWashCare"
ADRES = "2930 Brasschaat, Antwerpen"
TELEFOON = "+32 470 87 43 39"
EMAIL = "dennisg@prowashcare.com"
WEBSITE = "www.prowashcare.com"

VERVOERSKOSTEN = 8.0

if "diensten" not in st.session_state:
    st.session_state.diensten = []

# ================= FUNCTIES =================
def bereken_totaal():
    subtotaal = sum(d[1] for d in st.session_state.diensten)
    btw = subtotaal * 0.21
    totaal = subtotaal + btw
    return subtotaal, btw, totaal

def maak_pdf_en_excel(diensten, klant_naam, klant_adres, klant_email, subtotaal, btw, totaal):
    nu = datetime.now()
    nummer = nu.strftime("PWC%Y%m%d%H%M")
    datum_str = nu.strftime('%d-%m-%Y')

    # ===== EXCEL =====
    wb = Workbook()
    ws = wb.active
    ws.title = "Offerte"

    bold = Font(bold=True)
    right = Alignment(horizontal="right")

    ws["A1"] = "ProWashCare – OFFERTE"
    ws["A1"].font = Font(bold=True, size=16)

    ws["A3"] = f"Klant: {klant_naam}"
    ws["A4"] = f"Adres: {klant_adres}"
    ws["A5"] = f"E-mail: {klant_email}"
    ws["A6"] = f"Offertenummer: {nummer}"
    ws["A7"] = f"Datum: {datum_str}"

    ws["A9"] = "Omschrijving"
    ws["B9"] = "Bedrag"
    ws["A9"].font = bold
    ws["B9"].font = bold

    row = 10
    for oms, bed in diensten:
        ws[f"A{row}"] = oms
        ws[f"B{row}"] = bed
        ws[f"B{row}"].number_format = '€#,##0.00'
        ws[f"B{row}"].alignment = right
        row += 1

    ws[f"A{row}"] = "Subtotaal"
    ws[f"B{row}"] = subtotaal
    row += 1
    ws[f"A{row}"] = "BTW 21%"
    ws[f"B{row}"] = btw
    row += 1
    ws[f"A{row}"] = "Totaal"
    ws[f"B{row}"] = totaal

    excel_buf = io.BytesIO()
    wb.save(excel_buf)
    excel_buf.seek(0)

    # ===== PDF =====
    pdf_buf = io.BytesIO()
    pdf = SimpleDocTemplate(pdf_buf)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("<b>ProWashCare – Offerte</b>", styles["Title"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph(f"<b>Naam:</b> {klant_naam}", styles["Normal"]))
    content.append(Paragraph(f"<b>Adres:</b> {klant_adres}", styles["Normal"]))
    content.append(Paragraph(f"<b>E-mail:</b> {klant_email}", styles["Normal"]))
    content.append(Paragraph(f"Offertenummer: {nummer}", styles["Normal"]))
    content.append(Paragraph(f"Datum: {datum_str}", styles["Normal"]))
    content.append(Spacer(1, 20))

    data = [["Omschrijving", "Bedrag (€)"]]
    for d in diensten:
        data.append([Paragraph(d[0].replace("\n", "<br/>"), styles["Normal"]), f"{d[1]:.2f}"])

    data += [
        ["Subtotaal", f"{subtotaal:.2f}"],
        ["BTW 21%", f"{btw:.2f}"],
        ["Totaal", f"{totaal:.2f}"],
    ]

    content.append(RLTable(data))
    pdf.build(content)
    pdf_buf.seek(0)

    return excel_buf, pdf_buf, nummer

# ================= KLANTGEGEVENS =================
st.write("### Klantgegevens")
col1, col2 = st.columns(2)
with col1:
    klant_naam = st.text_input("Naam")
    klant_email = st.text_input("E-mail")
with col2:
    klant_adres = st.text_area("Adres", height=80)

st.write("---")

# ================= DIENSTEN =================
st.write("### Dienst toevoegen")
dienst = st.selectbox("Dienst", [
    "Ramen wassen",
    "Zonnepanelen",
    "Gevelreiniging",
    "Vervoerskosten"
])

omschrijving = ""
bedrag = 0

if dienst == "Ramen wassen":
    st.write("#### Ramen wassen")
    klein_binnen = st.number_input("Kleine ramen binnen", 0)
    klein_buiten = st.number_input("Kleine ramen buiten", 0)
    groot_binnen = st.number_input("Grote ramen binnen", 0)
    groot_buiten = st.number_input("Grote ramen buiten", 0)
    dak = st.number_input("Dakramen / moeilijk te bereiken ramen", 0)

    details = []
    totaal = 0

    if klein_binnen:
        details.append(f"- Kleine ramen binnen: {klein_binnen} × €2.00 = €{klein_binnen*2:.2f}")
        totaal += klein_binnen*2
    if klein_buiten:
        details.append(f"- Kleine ramen buiten: {klein_buiten} × €1.50 = €{klein_buiten*1.5:.2f}")
        totaal += klein_buiten*1.5
    if groot_binnen:
        details.append(f"- Grote ramen binnen: {groot_binnen} × €2.50 = €{groot_binnen*2.5:.2f}")
        totaal += groot_binnen*2.5
    if groot_buiten:
        details.append(f"- Grote ramen buiten: {groot_buiten} × €2.00 = €{groot_buiten*2:.2f}")
        totaal += groot_buiten*2
    if dak:
        details.append(f"- Dakramen / moeilijk bereikbaar: {dak} × €2.50 = €{dak*2.5:.2f}")
        totaal += dak*2.5

    if details:
        omschrijving = "Ramen wassen\n" + "\n".join(details)
        bedrag = max(50, totaal)

elif dienst == "Zonnepanelen":
    aantal = st.number_input("Aantal zonnepanelen", 1)
    bedrag = max(79, aantal * 5)
    omschrijving = f"Zonnepanelen reinigen\n- {aantal} panelen × €5.00"

elif dienst == "Gevelreiniging":
    m2 = st.number_input("Oppervlakte (m²)", 1.0)
    bedrag = max(299, m2 * 5)
    omschrijving = f"Gevelreiniging\n- {m2} m² × €5.00"

elif dienst == "Vervoerskosten":
    bedrag = VERVOERSKOSTEN
    omschrijving = "Vervoerskosten"

if st.button("Dienst toevoegen") and bedrag > 0:
    st.session_state.diensten.append((omschrijving, bedrag))
    st.success("Dienst toegevoegd!")
    st.rerun()

# ================= OVERZICHT =================
st.write("### Overzicht")
for i, d in enumerate(st.session_state.diensten):
    col1, col2, col3 = st.columns([6, 2, 1])
    col1.write(d[0].replace("\n", "  \n"))
    col2.write(f"€ {d[1]:.2f}")
    if col3.button("❌", key=i):
        st.session_state.diensten.pop(i)
        st.rerun()

subtotaal, btw, totaal = bereken_totaal()

st.write("---")
st.write(f"**Subtotaal:** € {subtotaal:.2f}")
st.write(f"**BTW (21%):** € {btw:.2f}")
st.write(f"**Totaal:** € {totaal:.2f}")

# ================= OFFERTES =================
if st.button("Maak offerte (Excel + PDF)"):
    if not klant_naam.strip():
        st.error("Naam ontbreekt")
    else:
        excel, pdf, nr = maak_pdf_en_excel(
            st.session_state.diensten,
            klant_naam,
            klant_adres,
            klant_email,
            subtotaal,
            btw,
            totaal
        )

        st.success(f"Offerte {nr} aangemaakt")

        st.download_button("📊 Download Excel", excel, f"Offerte_{nr}.xlsx")
        st.download_button("📄 Download PDF", pdf, f"Offerte_{nr}.pdf")
