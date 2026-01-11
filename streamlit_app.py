st.session_state.diensten = []
import streamlit as st
from datetime import datetime
from openpyxl import Workbook
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import io

# ================= CONFIG =================
st.set_page_config(page_title="ProWashCare Offerte", layout="centered")
st.title("🧼 ProWashCare – Offerte Tool")

BTW = 0.21
VERVOERSKOSTEN = 8.0

# ================= SESSION STATE =================
if "diensten" not in st.session_state:
    st.session_state.diensten = []

if "reset_ramen" not in st.session_state:
    st.session_state.reset_ramen = False

# reset raam-inputs vóór rendering
if st.session_state.reset_ramen:
    for k in ["kb","gb","db","kbui","gbui","dbui"]:
        st.session_state[k] = 0
    st.session_state.reset_ramen = False

# ================= HULPFUNCTIES =================
def bereken_totalen():
    subtotaal = sum(d["totaal"] for d in st.session_state.diensten)
    btw = subtotaal * BTW
    return subtotaal, btw, subtotaal + btw


def get_ramen_dienst():
    for d in st.session_state.diensten:
        if d["type"] == "ramen":
            return d
    return None


def maak_pdf(klant, adres, email):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Right", alignment=TA_RIGHT))
    content = []

    nummer = datetime.now().strftime("PWC%Y%m%d%H%M")
    datum = datetime.now().strftime("%d-%m-%Y")

    header = Table([[
        [
            Paragraph("<b>ProWashCare – Offerte</b>", styles["Title"]),
            Spacer(1,6),
            Paragraph(f"<b>Naam:</b> {klant}", styles["Normal"]),
            Paragraph(f"<b>Adres:</b> {adres.replace(chr(10),'<br/>')}", styles["Normal"]),
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
    ]], colWidths=[10*cm, 5*cm])

    content.append(header)
    content.append(Spacer(1,20))

    data = [["Omschrijving", "Bedrag (€)"]]

    for d in st.session_state.diensten:
        data.append([Paragraph(f"<b>{d['titel']}</b>", styles["Normal"]), ""])
        for r in d["regels"]:
            data.append([f"– {r[0]} ({r[1]}x)", f"{r[2]:.2f}"])
        data.append(["Subtotaal", f"{d['totaal']:.2f}"])
        data.append(["",""])

    sub, btw, tot = bereken_totalen()
    data += [
        ["Subtotaal (excl.)", f"{sub:.2f}"],
        ["BTW 21%", f"{btw:.2f}"],
        [Paragraph("<b>Totaal</b>", styles["Normal"]), Paragraph(f"<b>{tot:.2f}</b>", styles["Normal"])]
    ]

    table = Table(data, colWidths=[12*cm,3*cm])
    table.setStyle([
        ("GRID",(0,0),(-1,-1),0.25,"grey"),
        ("BACKGROUND",(0,0),(-1,0),"#EEEEEE"),
        ("ALIGN",(1,1),(-1,-1),"RIGHT")
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

    ws.append(["Omschrijving","Aantal","Bedrag"])

    for d in st.session_state.diensten:
        for r in d["regels"]:
            ws.append([r[0], r[1], r[2]])
        ws.append([f"Totaal {d['titel']}", "", d["totaal"]])

    sub, btw, tot = bereken_totalen()
    ws.append([])
    ws.append(["Subtotaal","",sub])
    ws.append(["BTW","",btw])
    ws.append(["Totaal","",tot])

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

# ================= KLANT =================
st.subheader("👤 Klantgegevens")
c1,c2 = st.columns(2)
with c1:
    klant = st.text_input("Naam")
    email = st.text_input("E-mail")
with c2:
    adres = st.text_area("Adres", height=80)

# ================= DIENST SELECTIE =================
st.divider()
dienst = st.selectbox("Dienst", [
    "Ramen wassen","Zonnepanelen","Gevelreiniging","Oprit / Terras / Bedrijfsterrein"
])

# ================= RAMEN =================
if dienst == "Ramen wassen":
    st.subheader("Ramen wassen")

    b1,b2,b3 = st.columns(3)
    kb = b1.number_input("Kleine ramen binnen",0,key="kb")
    gb = b2.number_input("Grote ramen binnen",0,key="gb")
    db = b3.number_input("Dakramen binnen",0,key="db")

    b4,b5,b6 = st.columns(3)
    kbui = b4.number_input("Kleine ramen buiten",0,key="kbui")
    gbui = b5.number_input("Grote ramen buiten",0,key="gbui")
    dbui = b6.number_input("Dakramen buiten",0,key="dbui")

    if st.button("Dienst toevoegen"):
        prijzen = {
            "Kleine ramen binnen": (kb, 2),
            "Kleine ramen buiten": (kbui, 1.5),
            "Grote ramen binnen": (gb, 2.5),
            "Grote ramen buiten": (gbui, 2),
            "Dakramen binnen": (db, 2.5),
            "Dakramen buiten": (dbui, 2.5),
        }

        regels = [(k,a,a*p) for k,(a,p) in prijzen.items() if a>0]
        if not regels:
            st.warning("Geen ramen ingegeven")
            st.stop()

        dienst_ramen = get_ramen_dienst()

        if dienst_ramen:
            for r in regels:
                dienst_ramen["regels"].append(r)
            dienst_ramen["totaal"] = max(50, sum(r[2] for r in dienst_ramen["regels"]))
        else:
            st.session_state.diensten.append({
                "type":"ramen",
                "titel":"Ramen wassen",
                "regels": regels,
                "totaal": max(50, sum(r[2] for r in regels))
            })

        st.session_state.reset_ramen = True
        st.rerun()

# ================= OVERIGE DIENSTEN =================
elif dienst == "Zonnepanelen":
    aantal = st.number_input("Aantal zonnepanelen",1)
    if st.button("Dienst toevoegen"):
        st.session_state.diensten.append({
            "type":"zonnepanelen",
            "titel":"Zonnepanelen",
            "regels":[("Zonnepanelen reinigen",aantal,aantal*5)],
            "totaal":max(79,aantal*5)
        })

elif dienst == "Gevelreiniging":
    m2 = st.number_input("Oppervlakte (m²)",0.1)
    impreg = st.checkbox("Impregneren")
    if st.button("Dienst toevoegen"):
        regels=[("Gevel reinigen",m2,m2*5)]
        if impreg: regels.append(("Impregneren",m2,m2*4))
        st.session_state.diensten.append({
            "type":"gevel",
            "titel":"Gevelreiniging",
            "regels":regels,
            "totaal":max(299,sum(r[2] for r in regels))
        })

elif dienst == "Oprit / Terras / Bedrijfsterrein":
    type_k = st.radio("Type",["Oprit","Terras","Bedrijfsterrein"],horizontal=True)
    m2 = st.number_input("Oppervlakte (m²)",0.1)
    r,z,o,c = st.columns(4)
    reinigen=r.checkbox("Reinigen")
    zand=z.checkbox("Zand invegen")
    onkruid=o.checkbox("Onkruidmijdend voegzand")
    coating=c.checkbox("Coating")

    if st.button("Dienst toevoegen"):
        regels=[]
        if reinigen: regels.append(("Reinigen",m2,m2*3.5))
        if zand: regels.append(("Zand invegen",m2,m2*1))
        if onkruid: regels.append(("Onkruidmijdend voegzand",m2,m2*2))
        if coating: regels.append(("Coating",m2,m2*3.5))
        if regels:
            st.session_state.diensten.append({
                "type":"oprit",
                "titel":type_k,
                "regels":regels,
                "totaal":sum(r[2] for r in regels)
            })

# ================= OVERZICHT =================
st.divider()
st.subheader("📋 Overzicht")

for i,d in enumerate(st.session_state.diensten):
    with st.expander(d["titel"]):
        for r in d["regels"]:
            st.write(f"{r[0]} – {r[1]}x – € {r[2]:.2f}")
        st.write(f"**Totaal: € {d['totaal']:.2f}**")
        if st.button("❌ Verwijderen",key=f"del{i}"):
            st.session_state.diensten.pop(i)
            st.rerun()

sub,btw,tot = bereken_totalen()
st.write(f"Subtotaal: € {sub:.2f}")
st.write(f"BTW: € {btw:.2f}")
st.write(f"## Totaal: € {tot:.2f}")

# ================= EXPORT =================
st.divider()
if klant:
    c1,c2 = st.columns(2)
    c1.download_button("📄 PDF", maak_pdf(klant,adres,email), "offerte.pdf")
    c2.download_button("📊 Excel", maak_excel(klant), "offerte.xlsx")
else:
    st.info("Vul klantgegevens in")
