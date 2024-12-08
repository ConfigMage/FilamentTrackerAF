import streamlit as st
import pandas as pd
import hashlib
import os

st.set_page_config(
    page_title="Fredrickson's Printing - Filament Tracker",
    page_icon="🖨️",
    layout="wide"
)

st.markdown("""
    <style>
    :root {
        --fp-blue: #4169E1;
    }
    
    .fp-header {
        background-color: var(--fp-blue);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .fp-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .fp-subtitle {
        font-size: 1.5rem;
        opacity: 0.9;
    }
    
    table.dataframe {
        width: 100% !important;
        background-color: #f8f9fa !important;
        border-collapse: collapse !important;
        border: 2px solid #dee2e6 !important;
        margin: 1rem 0 !important;
        font-size: 1.1rem !important;
        color: #212529 !important;
    }
    
    .dataframe th {
        background-color: var(--fp-blue) !important;
        color: white !important;
        padding: 15px !important;
        font-size: 1.2rem !important;
        text-align: left !important;
        border: 1px solid #dee2e6 !important;
        white-space: nowrap !important;
    }
    
    .dataframe td {
        padding: 12px !important;
        border: 1px solid #dee2e6 !important;
        background-color: white !important;
        color: #212529 !important;
        text-align: left !important;
    }
    
    .dataframe tr:hover td {
        background-color: #f1f3f5 !important;
    }
    
    .color-preview {
        display: inline-block;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        border: 2px solid #dee2e6;
        vertical-align: middle;
    }
    
    .stTextInput > div > div > input {
        border: 1px solid var(--fp-blue);
        border-radius: 5px;
        padding: 0.5rem;
    }
    
    .stButton > button {
        background-color: var(--fp-blue);
        color: white;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        border: none;
    }
    
    h3 {
        color: var(--fp-blue);
        margin-top: 2rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--fp-blue);
    }
    </style>
""", unsafe_allow_html=True)

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'password_hash' not in st.session_state:
    st.session_state.password_hash = '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'
if 'show_admin' not in st.session_state:
    st.session_state.show_admin = False

def check_password(password):
    return hashlib.sha256(password.encode()).hexdigest() == st.session_state.password_hash

def load_data():
    if not os.path.exists('filaments.csv'):
        data = {
            'color': ['Army Green', 'Fluorescent Green', 'Ruby Red'],
            'company': ['Creality', 'Creality', 'Creality'],
            'type': ['PLA', 'PLA', 'PLA'],
            'remaining': [50, 50, 50],
            'color_hex': ['#4B5320', '#39FF14', '#E0115F']
        }
        df = pd.DataFrame(data)
        df.to_csv('filaments.csv', index=False)
    return pd.read_csv('filaments.csv')

def save_data(df):
    df.to_csv('filaments.csv', index=False)
    return load_data()

def admin_interface():
    st.markdown("### 📝 Inventory Management")
    df = load_data()
    
    action = st.radio("Select Action", ["Add New Filament", "Edit Existing Filament"])
    
    if action == "Add New Filament":
        with st.form(key="add_filament"):
            cols = st.columns([1, 1, 1])
            with cols[0]:
                new_color_name = st.text_input("Color Name")
                new_color_hex = st.color_picker("Select Color", "#000000")
            with cols[1]:
                new_company = st.text_input("Company")
                new_type = st.text_input("Type")
            with cols[2]:
                new_remaining = st.slider("Remaining %", 0, 100, 50)
            
            submit_button = st.form_submit_button("Add Filament")
            
            if submit_button and new_color_name and new_company and new_type:
                new_row = pd.DataFrame({
                    'color': [new_color_name],
                    'company': [new_company],
                    'type': [new_type],
                    'remaining': [new_remaining],
                    'color_hex': [new_color_hex]
                })
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                st.success("✅ Filament added successfully!")
                st.experimental_rerun()
    
    else:
        if len(df) > 0:
            with st.form(key="edit_filament"):
                filament_list = [f"{row['color']} ({row['type']})" for _, row in df.iterrows()]
                selected_filament = st.selectbox("Select Filament to Edit", filament_list)
                
                selected_index = filament_list.index(selected_filament)
                current_filament = df.iloc[selected_index]
                
                cols = st.columns([1, 1, 1])
                with cols[0]:
                    edited_color_name = st.text_input("Color Name", current_filament['color'])
                    edited_color_hex = st.color_picker("Select Color", current_filament['color_hex'])
                with cols[1]:
                    edited_company = st.text_input("Company", current_filament['company'])
                    edited_type = st.text_input("Type", current_filament['type'])
                with cols[2]:
                    edited_remaining = st.slider("Remaining %", 0, 100, int(current_filament['remaining']))
                
                col1, col2 = st.columns(2)
                with col1:
                    submit_button = st.form_submit_button("Update Filament")
                with col2:
                    delete_button = st.form_submit_button("Delete Filament")
                
                if submit_button:
                    df.at[selected_index, 'color'] = edited_color_name
                    df.at[selected_index, 'color_hex'] = edited_color_hex
                    df.at[selected_index, 'company'] = edited_company
                    df.at[selected_index, 'type'] = edited_type
                    df.at[selected_index, 'remaining'] = edited_remaining
                    save_data(df)
                    st.success("✅ Filament updated successfully!")
                    st.experimental_rerun()
                
                if delete_button:
                    df = df.drop(selected_index).reset_index(drop=True)
                    save_data(df)
                    st.success("🗑️ Filament deleted successfully!")
                    st.experimental_rerun()

def create_color_preview(color_hex):
    return f'<div class="color-preview" style="background-color: {color_hex};"></div>'

def main():
    st.markdown("""
        <div class="fp-header">
            <div class="fp-title">🖨️ Fredrickson's Printing</div>
            <div class="fp-subtitle">Filament Inventory Management System</div>
        </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.authenticated:
        st.markdown("### Welcome to Fredrickson's Printing")
        st.markdown("Please login to access the filament inventory system.")
        password = st.text_input("Enter password:", type="password")
        if st.button("Login"):
            if check_password(password):
                st.session_state.authenticated = True
                st.experimental_rerun()
            else:
                st.error("Incorrect password")
        return

    with st.sidebar:
        st.markdown("### 🎛️ Controls")
        if st.button("Toggle Admin Interface"):
            st.session_state.show_admin = not st.session_state.show_admin
    
    if st.session_state.show_admin:
        admin_interface()
    
    df = load_data()
    
    st.markdown("### 🔍 Filter Inventory")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        color_filter = st.multiselect("Filter by Color", options=sorted(df['color'].unique()))
    with col2:
        company_filter = st.multiselect("Filter by Company", options=sorted(df['company'].unique()))
    with col3:
        type_filter = st.multiselect("Filter by Type", options=sorted(df['type'].unique()))

    filtered_df = df.copy()
    if color_filter:
        filtered_df = filtered_df[filtered_df['color'].isin(color_filter)]
    if company_filter:
        filtered_df = filtered_df[filtered_df['company'].isin(company_filter)]
    if type_filter:
        filtered_df = filtered_df[filtered_df['type'].isin(type_filter)]

    st.markdown("### 📦 Current Inventory")
    
    styled_df = filtered_df.copy()
    styled_df['Color Preview'] = styled_df['color_hex'].apply(create_color_preview)
    
    display_df = styled_df[['Color Preview', 'color', 'company', 'type', 'remaining']]
    display_df.columns = ['', 'Color', 'Company', 'Type', 'Remaining %']
    
    st.markdown(f"""
        <div style="padding: 1rem; background-color: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            {display_df.to_html(escape=False, index=False)}
        </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.experimental_rerun()

if __name__ == "__main__":
    main()