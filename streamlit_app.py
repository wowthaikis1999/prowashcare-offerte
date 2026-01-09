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
# test
# Bedrijfsgegevens
BEDRIJFSNAAM = "ProWashCare"
ADRES = "2930 Brasschaat, Antwerpen"
TELEFOON = "+32 470 87 43 39"
EMAIL = "dennisg@prowashcare.com"
WEBSITE = "www.prowashcare.com"

# Session state
if "diensten" not in st.session_state:
    st.session_state.diensten = []
    st.session_state.vervoer_toegevoegd = False

VERVOERSKOSTEN = 8.0
OPRIT_MINIMUM = 299.0

# ================= FUNCTIES =================
def bereken_totaal():
    oprit_diensten = [d for d in st.session_state.diensten if d[0].startswith(("Oprit", "Terras", "Bedrijfsterrein"))]
    oprit_totaal = sum(d[1] for d in oprit_diensten)

    diensten_clean = [d for d in st.session_state.diensten if not d[0].startswith("Minimumtarief")]

    verschil = max(0, OPRIT_MINIMUM - oprit_totaal) if oprit_diensten else 0

    if verschil > 0 and st.session_state.vervoer_toegevoegd:
        diensten_clean = [d for d in diensten_clean if d[0] != "Vervoerskosten"]
        st.session_state.vervoer_toegevoegd = False

    if verschil > 0:
        diensten_clean.append(("Minimumtarief oprit/terras/bedrijfsterrein", verschil))

    subtotaal = sum(d[1] for d in diensten_clean)
    btw = subtotaal * 0.21
    totaal = subtotaal + btw

    return diensten_clean, subtotaal, btw, totaal

def maak_pdf_en_excel(diensten_final, klant_naam, klant_adres, klant_email, subtotaal, btw, totaal):

    nu = datetime.now()
    nummer = nu.strftime("PWC%Y%m%d%H%M")
    datum_str = nu.strftime('%d-%m-%Y')

    # Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Offerte"

    title_font = Font(bold=True, size=16)
    bold_font = Font(bold=True, size=12)
    right_align = Alignment(horizontal="right")
    center_align = Alignment(horizontal="center")
    gray_fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

    ws["A1"] = "ProWashCare – OFFERTE"
    ws["A1"].font = title_font
    ws["A1"].alignment = center_align
    ws.merge_cells("A1:B1")

    ws["A3"] = f"Klant: {klant}"
    ws["A4"] = f"Offertenummer: {nummer}"
    ws["A5"] = f"Datum: {datum_str}"
    ws["A3"].font = bold_font
    ws["A4"].font = bold_font
    ws["A5"].font = bold_font

    ws["A7"] = "Omschrijving"
    ws["B7"] = "Bedrag (€)"
    ws["A7"].font = bold_font
    ws["B7"].font = bold_font
    ws["A7"].fill = gray_fill
    ws["B7"].fill = gray_fill
    ws["A7"].alignment = center_align
    ws["B7"].alignment = center_align
    ws["A7"].border = thin_border
    ws["B7"].border = thin_border

    row = 8
    for oms, bed in diensten_final:
        lines = oms.split("\n")
        for i, line in enumerate(lines):
            ws[f"A{row + i}"] = line
            ws[f"A{row + i}"].border = thin_border
        ws[f"B{row}"] = bed
        ws[f"B{row}"].number_format = '€#,##0.00'
        ws[f"B{row}"].alignment = right_align
        ws[f"B{row}"].border = thin_border
        row += len(lines)

    ws[f"A{row}"] = "Subtotaal (excl. btw)"
    ws[f"B{row}"] = subtotaal
    ws[f"A{row}"].font = bold_font
    ws[f"B{row}"].font = bold_font
    ws[f"B{row}"].number_format = '€#,##0.00'
    ws[f"B{row}"].alignment = right_align
    ws[f"A{row}"].fill = gray_fill
    ws[f"B{row}"].fill = gray_fill

    row += 1
    ws[f"A{row}"] = "BTW 21%"
    ws[f"B{row}"] = btw
    ws[f"A{row}"].font = bold_font
    ws[f"B{row}"].font = bold_font
    ws[f"B{row}"].number_format = '€#,##0.00'
    ws[f"B{row}"].alignment = right_align

    row += 1
    ws[f"A{row}"] = "Totaal (incl. btw)"
    ws[f"B{row}"] = totaal
    ws[f"A{row}"].font = Font(bold=True, size=14)
    ws[f"B{row}"].font = Font(bold=True, size=14)
    ws[f"B{row}"].number_format = '€#,##0.00'
    ws[f"B{row}"].alignment = right_align
    ws[f"A{row}"].fill = gray_fill
    ws[f"B{row}"].fill = gray_fill

    ws.column_dimensions['A'].width = 80
    ws.column_dimensions['B'].width = 20

    excel_buffer = io.BytesIO()
    wb.save(excel_buffer)
    excel_buffer.seek(0)

    # PDF
    pdf_buffer = io.BytesIO()
    pdf = SimpleDocTemplate(pdf_buffer, rightMargin=72, leftMargin=72, topMargin=60, bottomMargin=72)
    styles = getSampleStyleSheet()
    content = []

    # Logo
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        img = utils.ImageReader(logo_path)
        iw, ih = img.getSize()
        aspect = ih / float(iw)
        logo_img = Image(logo_path, width=4*cm, height=4*cm * aspect)
        left_cell = [logo_img, Spacer(1, 12)]
    else:
        left_cell = []

    left_cell += [
    Paragraph("<b>ProWashCare – Offerte</b>", styles["Title"]),
    Paragraph(f"<b>Naam:</b> {klant_naam}", styles["Normal"]),
    Paragraph(f"<b>Adres:</b> {klant_adres.replace(chr(10), '<br/>')}", styles["Normal"]),
    Paragraph(f"<b>E-mail:</b> {klant_email}", styles["Normal"]),
    Paragraph(f"Offertenummer: {nummer}", styles["Normal"]),
    Paragraph(f"Datum: {datum_str}", styles["Normal"]),
]


    right_cell = [
        Spacer(1, 2*cm),
        Paragraph(f"<b>{BEDRIJFSNAAM}</b>", styles["Normal"]),
        Paragraph(ADRES, styles["Normal"]),
        Paragraph(f"Tel: {TELEFOON}", styles["Normal"]),
        Paragraph(f"Email: {EMAIL}", styles["Normal"]),
        Paragraph(f"Website: {WEBSITE}", styles["Normal"]),
    ]

    header_table = RLTable([[left_cell, right_cell]], colWidths=[9*cm, None])
    header_table.setStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
    ])
    content.append(header_table)
    content.append(Spacer(1, 36))

    data = [["Omschrijving", "Bedrag"]]
    for d in diensten_final:
        data.append([Paragraph(d[0].replace("\n", "<br/>"), styles["Normal"]), f"€ {d[1]:.2f}"])

    data += [
        ["", ""],
        ["Subtotaal (excl. btw)", f"€ {subtotaal:.2f}"],
        ["BTW 21%", f"€ {btw:.2f}"],
        ["Totaal (incl. btw)", f"€ {totaal:.2f}"],
    ]

    content.append(RLTable(data, colWidths=[400, 80]))
    pdf.build(content)
    pdf_buffer.seek(0)

    return excel_buffer, pdf_buffer, nummer

# ================= UI =================
klant = st.text_input("Klantnaam")

st.write("### Kies een dienst")
dienst = st.selectbox("Dienst", [
    "Ramen wassen", "Zonnepanelen", "Gevelreiniging", "Oprit / Terras / Bedrijfsterrein"
], label_visibility="collapsed")

omschrijving = dienst
berekend = 0
eindbedrag = 0

if dienst == "Ramen wassen":
    st.write("#### Ramen wassen")
    col1, col2 = st.columns(2)
    with col1:
        klein_binnen = st.number_input("Kleine ramen - Binnen", min_value=0, step=1)
        groot_binnen = st.number_input("Grote ramen - Binnen", min_value=0, step=1)
        dak_binnen = st.number_input("Dakramen - Binnen", min_value=0, step=1)
    with col2:
        klein_buiten = st.number_input("Kleine ramen - Buiten", min_value=0, step=1)
        groot_buiten = st.number_input("Grote ramen - Buiten", min_value=0, step=1)
        dak_buiten = st.number_input("Dakramen - Buiten", min_value=0, step=1)

    berekend = klein_binnen*2.0 + klein_buiten*1.5 + groot_binnen*2.5 + groot_buiten*2.0 + dak_binnen*2.5 + dak_buiten*2.5
    details = []
    if klein_binnen or klein_buiten: details.append(f"Kleine ramen: {klein_binnen} binnen, {klein_buiten} buiten")
    if groot_binnen or groot_buiten: details.append(f"Grote ramen: {groot_binnen} binnen, {groot_buiten} buiten")
    if dak_binnen or dak_buiten: details.append(f"Dakramen: {dak_binnen} binnen, {dak_buiten} buiten")
    omschrijving += "\n" + "\n".join(details) if details else ""
    eindbedrag = max(50, berekend)

elif dienst == "Zonnepanelen":
    aantal = st.number_input("Aantal zonnepanelen", min_value=1, step=1)
    berekend = aantal * 5
    omschrijving += f"\n({aantal} panelen)"
    eindbedrag = max(79, berekend)

elif dienst == "Gevelreiniging":
    m2 = st.number_input("Oppervlakte (m²)", min_value=0.1, format="%.1f")
    impregneer = st.checkbox("Impregneren (+ €4/m²)")
    berekend = m2 * 5.0 + (m2 * 4.0 if impregneer else 0)
    opties = ["Impregneren"] if impregneer else []
    omschrijving += f"\n{m2} m²" + (f" ({', '.join(opties)})" if opties else "")
    eindbedrag = max(299, berekend)

elif dienst == "Oprit / Terras / Bedrijfsterrein":
    type_keuze = st.radio("Type", ["Oprit", "Terras", "Bedrijfsterrein"], horizontal=True)
    m2 = st.number_input("Oppervlakte (m²)", min_value=0.1, format="%.1f")
    col1, col2, col3, col4 = st.columns(4)
    reinigen = col1.checkbox("Reinigen")
    zand = col2.checkbox("Zand invegen")
    onkruid = col3.checkbox("Onkruidmijdend voegzand")
    coating = col4.checkbox("Coating")

    berekend = 0
    opties = []
    if reinigen: berekend += m2 * 3.5; opties.append("Reinigen")
    if zand: berekend += m2 * 1.0; opties.append("Zand invegen")
    if onkruid: berekend += m2 * 2.0; opties.append("Onkruidmijdend voegzand")
    if coating: berekend += m2 * 3.5; opties.append("Coating")

    if opties:
        omschrijving = f"{type_keuze}\n{m2} m² ({', '.join(opties)})"
        eindbedrag = berekend
    else:
        st.warning("Selecteer minstens één optie.")
        eindbedrag = 0

if st.button("Dienst toevoegen") and eindbedrag > 0:
    if not st.session_state.diensten and not st.session_state.vervoer_toegevoegd:
        st.session_state.diensten.append(("Vervoerskosten", VERVOERSKOSTEN))
        st.session_state.vervoer_toegevoegd = True
    st.session_state.diensten.append((omschrijving, eindbedrag))
    st.success("Dienst toegevoegd!")
    st.rerun()

st.write("### Overzicht diensten")
diensten_final, subtotaal, btw, totaal = bereken_totaal()

for i in range(len(diensten_final)-1, -1, -1):
    oms, bed = diensten_final[i]
    col1, col2, col3 = st.columns([6, 2, 1])
    col1.write(oms.replace("\n", "  \n"))
    col2.write(f"€ {bed:.2f}")
    if col3.button("❌", key=f"del_{i}"):
        if oms == "Vervoerskosten":
            st.session_state.vervoer_toegevoegd = False
        orig_oms = st.session_state.diensten[i][0].split("\n")[0] if "\n" in st.session_state.diensten[i][0] else st.session_state.diensten[i][0]
        st.session_state.diensten = [d for d in st.session_state.diensten if not (d[0].startswith(orig_oms) and abs(d[1] - bed) < 0.01)]
        st.rerun()

st.write("---")
st.write(f"**Subtotaal (excl. btw):** € {subtotaal:.2f}")
st.write(f"**BTW (21%):** € {btw:.2f}")
st.write(f"**Totaal (incl. btw):** € {totaal:.2f}")
#naam adres email#
st.write("### Klantgegevens")

col1, col2 = st.columns(2)
with col1:
    klant_naam = st.text_input("Naam", key="klant_naam")
    klant_email = st.text_input("E-mail", key="klant_email")
with col2:
    klant_adres = st.text_area("Adres", key="klant_adres", height=80)
#-----#

if st.button("Maak offerte (Excel + PDF)"):
    if not klant_naam.strip():
    st.error("Voer een naam in!")
    else:
        excel_buf, pdf_buf, nummer = maak_pdf_en_excel(
    diensten_final,
    klant_naam,
    klant_adres,
    klant_email,
    subtotaal,
    btw,
    totaal
)

        st.success(f"Offerte {nummer} klaar!")

        col1, col2 = st.columns(2)
        col1.download_button("📊 Download Excel", excel_buf, f"Offerte_{nummer}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        col2.download_button("📄 Download PDF", pdf_buf, f"Offerte_{nummer}.pdf", "application/pdf")