import streamlit as st
import json
import urllib.request
import urllib.error
import os

# Set page layout to wide and brand with Dutch green styling
st.set_page_config(
    page_title="MPG & MKI Verwerker",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (using Streamlit's native elements for a premium look)
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; }
        div[data-testid="stMetricValue"] { font-size: 2.2rem; font-weight: 700; color: #059669; }
        .stButton>button { width: 100%; border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

# 1. Default Mock MKI Database (NMD Estimates in NL)
MOCK_MKI_DATABASE = [
    {"id": "beton", "label": "Constructiebeton (C30/37)", "mki_m3": 15.50, "mki_m2": 0.0, "unit": "m³"},
    {"id": "baksteen", "label": "Metselwerk baksteen gevel", "mki_m3": 45.00, "mki_m2": 0.0, "unit": "m³"},
    {"id": "glas", "label": "Isolerend HR++ glas (dubbel)", "mki_m3": 0.0, "mki_m2": 6.20, "unit": "m²"},
    {"id": "hout_kozijn", "label": "Hout (Naaldhout / Lariks)", "mki_m3": -25.00, "mki_m2": 0.0, "unit": "m³"},
    {"id": "gips", "label": "Gipsplaten (binnenwanden)", "mki_m3": 0.0, "mki_m2": 1.80, "unit": "m²"},
    {"id": "isolatie_minerale_wol", "label": "Minerale wol isolatiedeken", "mki_m3": 12.00, "mki_m2": 0.0, "unit": "m³"},
    {"id": "cement", "label": "Dekvloer zandcement", "mki_m3": 18.20, "mki_m2": 0.0, "unit": "m³"},
    {"id": "staal", "label": "Staalconstructieprofielen S235", "mki_m3": 145.00, "mki_m2": 0.0, "unit": "m³"}
]

# Create helper maps for speedy lookups
MKI_LOOKUP = {item["id"]: item for item in MOCK_MKI_DATABASE}
LABELS_TO_ID = {item["label"]: item["id"] for item in MOCK_MKI_DATABASE}
LABEL_LIST = ["-- Kies categorie --"] + [item["label"] for item in MOCK_MKI_DATABASE]

# 2. Local fallback rule-based auto-matcher
def auto_match_material(name):
    lower = name.lower()
    if any(x in lower for x in ['beton', 'concrete']): return 'beton'
    if any(x in lower for x in ['glas', 'glass', 'glazing']): return 'glas'
    if any(x in lower for x in ['hout', 'wood', 'timber', 'kozijn']): return 'hout_kozijn'
    if any(x in lower for x in ['gips', 'drywall', 'plaster']): return 'gips'
    if any(x in lower for x in ['isolatie', 'wool', 'isol']): return 'isolatie_minerale_wol'
    if any(x in lower for x in ['cement', 'dekvloer']): return 'cement'
    if any(x in lower for x in ['staal', 'steel', 'structure']): return 'staal'
    if any(x in lower for x in ['brick', 'steen', 'metsel']): return 'baksteen'
    return ""

# 3. Gemini AI Automapping caller
def call_gemini_mapping(material_names):
    # Retrieve the API key securely. In the environment, it is empty or managed.
    api_key = os.environ.get("GEMINI_API_KEY", "")
    
    # Target system prompt and user instructions for the MPG & NMD context
    system_prompt = (
        "Je bent een expert in de Nederlandse Milieuprestatie Gebouwen (MPG) en de Nationale Milieudatabase (NMD). "
        "Je taak is om Revit materiaalnamen te matchen met de meest geschikte NMD categorie-ID uit deze lijst: "
        f"{json.dumps([{ 'id': d['id'], 'label': d['label'] } for d in MOCK_MKI_DATABASE])}"
    )
    
    user_query = (
        "Geef voor elk van de volgende Revit-materialen de meest geschikte ID terug uit de lijst. "
        "Antwoord uitsluitend in een valide JSON-lijst met objecten die de sleutels 'material_name' en 'matched_id' bevatten. "
        f"De materialen zijn: {json.dumps(material_names)}"
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "material_name": {"type": "STRING"},
                        "matched_id": {"type": "STRING"}
                    },
                    "required": ["material_name", "matched_id"]
                }
            }
        },
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        }
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            text_response = res_data['candidates'][0]['content']['parts'][0]['text']
            return json.loads(text_response)
    except Exception as e:
        # Fallback to local rule-based matching if API fails or isn't configured
        return None

# --- STREAMLIT UI LAYOUT ---

st.title("🌱 MPG & MKI Dashboard")
st.caption("Native Streamlit verwerker voor Dynamo Revit data en NMD-gemiddeldes")

# Session State Initialization
if "project_data" not in st.session_state:
    st.session_state.project_data = {"project_info": {"document_title": "Nieuw Project", "estimated_bvo": 120}, "materials": []}
if "material_mappings" not in st.session_state:
    st.session_state.material_mappings = {} # key: material_name, value: mapped_db_id

# Sidebar inputs
st.sidebar.header("1. Revit Data Upload")
uploaded_file = st.sidebar.file_uploader("Upload revit_mki_export.json", type=["json"])

# Handle File Parsing
if uploaded_file is not None:
    try:
        raw_json = json.load(uploaded_file)
        if "materials" in raw_json:
            st.session_state.project_data = raw_json
            # Auto map materials locally on first load if not mapped yet
            for mat in raw_json["materials"]:
                name = mat["name"]
                if name not in st.session_state.material_mappings:
                    st.session_state.material_mappings[name] = auto_match_material(name)
        else:
            st.sidebar.error("Ongeldig formaat: mist 'materials' array.")
    except Exception as e:
        st.sidebar.error(f"Fout bij laden: {str(e)}")

# Sidebar project specifications
st.sidebar.markdown("---")
st.sidebar.header("2. Project Parameters")

building_function = st.sidebar.selectbox(
    "Gebouwfunctie",
    ["Woonfunctie (Eengezins / Appartement)", "Kantoorfunctie", "Bijeenkomst / Onderwijs", "Gezondheidszorg"]
)

# Fetch defaults from parsed JSON if possible
default_bvo = float(st.session_state.project_data["project_info"].get("estimated_bvo", 120.0))
bvo = st.sidebar.number_input("BVO (m²)", min_value=1.0, value=default_bvo, step=10.0)
lifespan = st.sidebar.number_input("Levensduur (jaar)", min_value=1, value=75, step=5)

# Back-end computations
materials_list = st.session_state.project_data["materials"]
total_mki = 0.0
mapped_count = 0

# Construct a list of records for processing and display
processed_materials = []
for mat in materials_list:
    name = mat["name"]
    vol = mat.get("volume_m3", 0.0)
    area = mat.get("area_m2", 0.0)
    
    mapped_id = st.session_state.material_mappings.get(name, "")
    db_item = MKI_LOOKUP.get(mapped_id) if mapped_id else None
    
    if db_item:
        mapped_count += 1
        unit = db_item["unit"]
        mki_factor = db_item["mki_m3"] if unit == "m³" else db_item["mki_m2"]
        qty = vol if unit == "m³" else area
        item_mki = qty * mki_factor
        total_mki += item_mki
    else:
        unit = "m³"
        mki_factor = 0.0
        item_mki = 0.0
        
    processed_materials.append({
        "name": name,
        "volume_m3": vol,
        "area_m2": area,
        "mapped_id": mapped_id,
        "unit": unit,
        "mki_factor": mki_factor,
        "total_mki": item_mki
    })

# Compute final MPG
mpg_score = total_mki / (bvo * lifespan) if bvo and lifespan else 0.0

# Display Top KPIs
kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

with kpi_col1:
    st.metric(label="MPG Score (€/m² BVO·jaar)", value=f"{mpg_score:.3f}")
    if total_mki == 0.0:
        st.info("Geen actieve mapping gekoppeld.")
    elif mpg_score <= 0.5:
        st.success("Uitstekend (BENG compliant)")
    elif mpg_score <= 0.8:
        st.warning("Voldoet aan bouwbesluit")
    else:
        st.error("Te hoog (Aandacht vereist!)")

with kpi_col2:
    st.metric(label="Totale Schaduwkosten", value=f"€ {total_mki:,.2f}")
    st.caption("Totale MKI som over de gehele levensduur")

with kpi_col3:
    total_materials = len(materials_list)
    st.metric(label="Gekoppelde Materialen", value=f"{mapped_count} / {total_materials}")
    st.caption("Aantal gekoppelde materialen aan de NMD")

st.markdown("---")

# Active Work Panel
st.subheader("3. Materialen Mappen & MKI Koppelen")

# Map database connection button
if st.button("🔄 Koppel NMD Gemiddeldes met AI", type="secondary"):
    if total_materials == 0:
        st.warning("Laad eerst een Revit model in!")
    else:
        with st.spinner("NMD gemiddeldes ophalen en mappen op de achtergrond..."):
            ai_matches = call_gemini_mapping([m["name"] for m in materials_list])
            if ai_matches:
                for match in ai_matches:
                    mat_name = match.get("material_name")
                    matched_id = match.get("matched_id")
                    if mat_name in st.session_state.material_mappings and matched_id in MKI_LOOKUP:
                        st.session_state.material_mappings[mat_name] = matched_id
                st.success("NMD Gemiddeldes succesvol gekoppeld met AI!")
                st.rerun()
            else:
                st.info("AI-koppeling niet direct beschikbaar. Standaard filters zijn toegepast.")

# Edit / Mapping Grid
if total_materials > 0:
    st.write("Pas de categorie-koppelingen direct aan in de tabel hieronder:")
    
    # Formulate table for the interactive editor
    editor_data = []
    for pm in processed_materials:
        db_item = MKI_LOOKUP.get(pm["mapped_id"])
        selected_label = db_item["label"] if db_item else "-- Kies categorie --"
        editor_data.append({
            "Revit Materiaal": pm["name"],
            "Volume (m³)": round(pm["volume_m3"], 2),
            "Oppervlakte (m²)": round(pm["area_m2"], 2),
            "NMD Categorie": selected_label,
            "MKI Factor (€)": pm["mki_factor"],
            "Totale Last (€)": round(pm["total_mki"], 2)
        })

    # Interactive data grid for immediate updates
    edited_df = st.data_editor(
        editor_data,
        column_config={
            "NMD Categorie": st.column_config.SelectboxColumn(
                "NMD Categorie",
                help="Kies de best passende NMD milieucategorie",
                options=LABEL_LIST,
                required=True
            ),
            "Revit Materiaal": st.column_config.TextColumn(disabled=True),
            "Volume (m³)": st.column_config.NumberColumn(disabled=True),
            "Oppervlakte (m²)": st.column_config.NumberColumn(disabled=True),
            "MKI Factor (€)": st.column_config.NumberColumn(disabled=True),
            "Totale Last (€)": st.column_config.NumberColumn(disabled=True),
        },
        use_container_width=True,
        hide_index=True
    )

    # Sync back changes from the UI table editor back to session state mappings
    has_changed = False
    for row in edited_df:
        mat_name = row["Revit Materiaal"]
        label_val = row["NMD Categorie"]
        target_id = LABELS_TO_ID.get(label_val, "")
        
        if st.session_state.material_mappings.get(mat_name) != target_id:
            st.session_state.material_mappings[mat_name] = target_id
            has_changed = True
            
    if has_changed:
        st.rerun()
else:
    st.info("Upload het geëxporteerde `revit_mki_export.json` bestand via de linkerkolom om direct de materialen te mappen.")
