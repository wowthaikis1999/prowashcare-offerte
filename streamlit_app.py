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

def get_dienst(titel):
    for d in st.session_state.diensten:
        if d["titel"] == titel:
            return d
    return None

def bereken_totalen():
    sub = sum(d["totaal"] for d in st.session_state.diensten)
    btw = sub * BTW
    return sub, btw, sub + btw

# ---------------- KLANT ----------------
st.subheader("👤 Klantgegevens")
c1, c2 = st.columns(2)
with c1:
    klant = st.text_input("Naam")
    email = st.text_input("E-mail")
with c2:
    adres = st.text_area("Adres", height=80)

# ---------------- DIENST ----------------
st.divider()
dienst = st.selectbox(
    "Dienst",
    ["Ramen wassen", "Zonnepanelen", "Gevelreiniging", "Oprit / Terras / Bedrijfsterrein"]
)

# ================= RAMEN WASSEN =================
if dienst == "Ramen wassen":
    st.subheader("Ramen wassen")

    for k in ["kb","gb","db","kbui","gbui","dbui"]:
        if k not in st.session_state:
            st.session_state[k] = 0

    st.markdown("**Binnen**")
    c1, c2, c3 = st.columns(3)
    kb = c1.number_input("Kleine ramen", 0, step=1, key="kb")
    gb = c2.number_input("Grote ramen", 0, step=1, key="gb")
    db = c3.number_input("Dakramen (moeilijk bereikbaar)", 0, step=1, key="db")

    st.markdown("**Buiten**")
    c4, c5, c6 = st.columns(3)
    kbui = c4.number_input("Kleine ramen", 0, step=1, key="kbui")
    gbui = c5.number_input("Grote ramen", 0, step=1, key="gbui")
    dbui = c6.number_input("Dakramen (moeilijk bereikbaar)", 0, step=1, key="dbui")

    if st.button("Ramen wassen toevoegen / aanpassen"):
        dienst_rw = get_dienst("Ramen wassen")
        if not dienst_rw:
            dienst_rw = {"titel":"Ramen wassen","regels":[],"totaal":0}
            st.session_state.diensten.append(dienst_rw)

        def add(label, aantal, prijs):
            if aantal == 0: return
            for r in dienst_rw["regels"]:
                if r["label"] == label:
                    r["aantal"] += aantal
                    r["prijs"] += aantal * prijs
                    return
            dienst_rw["regels"].append({
                "label":label,
                "aantal":aantal,
                "prijs":aantal * prijs
            })

        add("Kleine ramen binnen", kb, 2)
        add("Grote ramen binnen", gb, 2.5)
        add("Dakramen binnen (moeilijk bereikbaar)", db, 2.5)
        add("Kleine ramen buiten", kbui, 1.5)
        add("Grote ramen buiten", gbui, 2)
        add("Dakramen buiten (moeilijk bereikbaar)", dbui, 2.5)

        dienst_rw["totaal"] = max(50, sum(r["prijs"] for r in dienst_rw["regels"]))

        for k in ["kb","gb","db","kbui","gbui","dbui"]:
            st.session_state[k] = 0

        st.success("Ramen wassen aangepast")

# ================= ANDERE DIENSTEN (ONGEWIJZIGD) =================
elif dienst == "Zonnepanelen":
    aantal = st.number_input("Aantal zonnepanelen", 1)
    if st.button("Dienst toevoegen"):
        st.session_state.diensten.append({
            "titel":"Zonnepanelen",
            "regels":[{"label":"Zonnepanelen reinigen","aantal":aantal,"prijs":aantal*5}],
            "totaal":max(79,aantal*5)
        })

elif dienst == "Gevelreiniging":
    m2 = st.number_input("Oppervlakte (m²)", 0.1)
    impreg = st.checkbox("Impregneren")
    if st.button("Dienst toevoegen"):
        regels=[{"label":"Gevel reinigen","aantal":m2,"prijs":m2*5}]
        if impreg:
            regels.append({"label":"Impregneren","aantal":m2,"prijs":m2*4})
        st.session_state.diensten.append({
            "titel":"Gevelreiniging",
            "regels":regels,
            "totaal":max(299,sum(r["prijs"] for r in regels))
        })

elif dienst == "Oprit / Terras / Bedrijfsterrein":
    soort = st.radio("Type",["Oprit","Terras","Bedrijfsterrein"],horizontal=True)
    m2 = st.number_input("Oppervlakte (m²)",0.1)
    rein = st.checkbox("Reinigen")
    if st.button("Dienst toevoegen"):
        regels=[]
        if rein:
            regels.append({"label":"Reinigen","aantal":m2,"prijs":m2*3.5})
        if regels:
            st.session_state.diensten.append({
                "titel":soort,
                "regels":regels,
                "totaal":sum(r["prijs"] for r in regels)
            })

# ---------------- OVERZICHT ----------------
st.divider()
st.subheader("📋 Overzicht")

for i,d in enumerate(st.session_state.diensten):
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
