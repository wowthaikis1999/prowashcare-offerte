import streamlit as st
from openpyxl import Workbook
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import io

# ================= CONFIG =================
st.set_page_config(page_title="ProWashCare Offerte", layout="centered")
st.title("🧼 ProWashCare – Offerte Tool")

BEDRIJFSNAAM = "ProWashCare"
ADRES = "2930 Brasschaat, Antwerpen"
TELEFOON = "+32 470 87 43 39"
EMAIL = "dennisg@prowashcare.com"
WEBSITE = "www.prowashcare.com"

BTW = 0.21
VERVOERSKOSTEN = 8.0

# ================= SESSION =================
if "diensten" not in st.session_state:
    st.session_state.diensten = []

# ================= FUNCTIES =================
def bereken_totalen():
    subtotaal = sum(d["totaal"] for d in st.session_state.diensten)
    btw = subtotaal * BTW
    totaal = subtotaal + btw
    return subtotaal, btw, totaal

def maak_pdf_excel():
    now = datetime.now()
    nummer = now.strftime("PWC%Y%m%d%H%M")
    datum = now.strftime("%d-%m-%Y")

    subtotaal, btw, totaal = bereken_totalen()

    # -------- EXCEL --------
    wb = Workbook()
    ws = wb.active
    ws.title = "Offerte"

    ws["A1"] = "ProWashCare – Offerte"
    ws["A3"] = f"Klant: {klant_naam}"
    ws["A4"] = f"Adres: {klant_adres}"
    ws["A5"] = f"E-mail: {klant_email}"
    ws["A6"] = f"Offertenummer: {nummer}"
    ws["A7"] = f"Datum: {datum}"

    ws["A9"] = "Omschrijving"
    ws["B9"] = "Bedrag (€)"

    r = 10
    for d in st.session_state.diensten:
        for oms, prijs in d["regels"]:
            ws[f"A{r}"] = oms
            ws[f"B{r}"] = prijs
            r += 1

    ws[f"A{r}"] = "Subtotaal"
    ws[f"B{r}"] = subtotaal
    r += 1
    ws[f"A{r}"] = "BTW 21%"
    ws[f"B{r}"] = btw
    r += 1
    ws[f"A{r}"] = "Totaal"
    ws[f"B{r}"] = totaal

    excel = io.BytesIO()
    wb.save(excel)
    excel.seek(0)

    # -------- PDF --------
    pdf = io.BytesIO()
    doc = SimpleDocTemplate(pdf)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>ProWashCare – Offerte</b>", styles["Title"]))
    story.append(Paragraph(f"Klant: {klant_naam}", styles["Normal"]))
    story.append(Paragraph(f"Adres: {klant_adres}", styles["Normal"]))
    story.append(Paragraph(f"E-mail: {klant_email}", styles["Normal"]))
    story.append(Paragraph(f"Offertenummer: {nummer}", styles["Normal"]))
    story.append(Paragraph(f"Datum: {datum}", styles["Normal"]))

    data = [["Omschrijving", "Bedrag (€)"]]
    for d in st.session_state.diensten:
        for oms, prijs in d["regels"]:
            data.append([oms, f"{prijs:.2f}"])

    data += [
        ["Subtotaal", f"{subtotaal:.2f}"],
        ["BTW 21%", f"{btw:.2f}"],
        ["Totaal", f"{totaal:.2f}"],
    ]

    story.append(Table(data, colWidths=[350, 100]))
    doc.build(story)
    pdf.seek(0)

    return excel, pdf, nummer

# ================= KLANT =================
st.subheader("👤 Klantgegevens")
klant_naam = st.text_input("Naam")
klant_email = st.text_input("E-mail")
klant_adres = st.text_area("Adres")

# ================= DIENSTEN =================
st.divider()
dienst = st.selectbox("Dienst", [
    "Ramen wassen", "Zonnepanelen", "Gevelreiniging", "Oprit / Terras / Bedrijfsterrein"
])

# -------- RAMEN --------
if dienst == "Ramen wassen":
    kb = st.number_input("Kleine ramen binnen", 0)
    kbui = st.number_input("Kleine ramen buiten", 0)
    gb = st.number_input("Grote ramen binnen", 0)
    gbui = st.number_input("Grote ramen buiten", 0)
    db = st.number_input("Dakramen binnen", 0)
    dbui = st.number_input("Dakramen buiten", 0)

    if st.button("Dienst toevoegen"):
        regels = []
        if kb: regels.append(("Kleine ramen binnen", kb * 2))
        if kbui: regels.append(("Kleine ramen buiten", kbui * 1.5))
        if gb: regels.append(("Grote ramen binnen", gb * 2.5))
        if gbui: regels.append(("Grote ramen buiten", gbui * 2))
        if db: regels.append(("Dakramen binnen", db * 2.5))
        if dbui: regels.append(("Dakramen buiten", dbui * 2.5))

        totaal = max(50, sum(r[1] for r in regels))
        st.session_state.diensten.append({
            "titel": "Ramen wassen",
            "regels": regels,
            "totaal": totaal
        })
        st.success("Ramen wassen toegevoegd")

# -------- ZONNEPANELEN --------
elif dienst == "Zonnepanelen":
    aantal = st.number_input("Aantal panelen", 1)
    if st.button("Dienst toevoegen"):
        totaal = max(79, aantal * 5)
        st.session_state.diensten.append({
            "titel": "Zonnepanelen",
            "regels": [("Zonnepanelen reinigen", totaal)],
            "totaal": totaal
        })
        st.success("Zonnepanelen toegevoegd")

# -------- GEVEL --------
elif dienst == "Gevelreiniging":
    m2 = st.number_input("Oppervlakte m²", 0.1)
    impreg = st.checkbox("Impregneren")
    if st.button("Dienst toevoegen"):
        regels = [("Gevel reinigen", m2 * 5)]
        if impreg:
            regels.append(("Impregneren", m2 * 4))
        totaal = max(299, sum(r[1] for r in regels))
        st.session_state.diensten.append({
            "titel": "Gevelreiniging",
            "regels": regels,
            "totaal": totaal
        })
        st.success("Gevelreiniging toegevoegd")

# -------- OPRIT / TERRAS --------
elif dienst == "Oprit / Terras / Bedrijfsterrein":
    type_keuze = st.radio("Type", ["Oprit", "Terras", "Bedrijfsterrein"], horizontal=True)
    m2 = st.number_input("Oppervlakte m²", 0.1)
    reinigen = st.checkbox("Reinigen")
    zand = st.checkbox("Zand invegen")
    onkruid = st.checkbox("Onkruidmijdend voegzand")
    coating = st.checkbox("Coating")

    if st.button("Dienst toevoegen"):
        regels = []
        if reinigen: regels.append(("Reinigen", m2 * 3.5))
        if zand: regels.append(("Zand invegen", m2 * 1.0))
        if onkruid: regels.append(("Onkruidmijdend voegzand", m2 * 2.0))
        if coating: regels.append(("Coating", m2 * 3.5))

        if regels:
            totaal = sum(r[1] for r in regels)
            st.session_state.diensten.append({
                "titel": type_keuze,
                "regels": regels,
                "totaal": totaal
            })
            st.success(f"{type_keuze} toegevoegd")

# ================= VERVOERSKOSTEN =================
st.divider()
if st.button("🚗 Vervoerskosten toevoegen (€8)"):
    if not any(d["titel"] == "Vervoerskosten" for d in st.session_state.diensten):
        st.session_state.diensten.append({
            "titel": "Vervoerskosten",
            "regels": [("Vervoerskosten", VERVOERSKOSTEN)],
            "totaal": VERVOERSKOSTEN
        })
        st.success("Vervoerskosten toegevoegd")

# ================= OVERZICHT =================
st.divider()
st.subheader("📋 Overzicht")

for i, d in enumerate(st.session_state.diensten):
    col1, col2, col3 = st.columns([6, 2, 1])
    col1.write(d["titel"])
    col2.write(f"€ {d['totaal']:.2f}")
    if col3.button("❌", key=f"del_{i}"):
        st.session_state.diensten.pop(i)
        st.rerun()

subtotaal, btw, totaal = bereken_totalen()
st.write(f"**Subtotaal:** € {subtotaal:.2f}")
st.write(f"**BTW:** € {btw:.2f}")
st.write(f"## **Totaal:** € {totaal:.2f}")

# ================= OFFERTES =================
st.divider()
if st.button("📄 Maak offerte"):
    excel, pdf, nr = maak_pdf_excel()
    st.download_button("📊 Download Excel", excel, f"Offerte_{nr}.xlsx")
    st.download_button("📄 Download PDF", pdf, f"Offerte_{nr}.pdf")
