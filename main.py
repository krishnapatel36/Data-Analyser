import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import re
import requests
from fpdf import FPDF
import base64

# Function to process data
def process_data(data, medium):
    def standardize_time(time_str):
        if 'AM' in time_str or 'PM' in time_str:
            return pd.to_datetime(time_str, format='%I:%M:%S %p', errors='coerce')
        else:
            return pd.to_datetime(time_str, format='%H:%M:%S', errors='coerce')

    def get_state_from_ip(ip_address, api_key):
        url = f"https://ipinfo.io/{ip_address}/json?token={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get('region', 'Unknown')
        else:
            return 'Unknown'

    api_key = '7837dcaf59814e'  # Replace with your actual IPInfo API key
    unique_df = data.drop_duplicates(subset=['Meeting ID'])
    unique_df['State'] = unique_df['User Type'].apply(lambda ip: get_state_from_ip(ip, api_key))
    state_counts = unique_df['State'].value_counts()

    # Filter states based on medium
    if medium == 'Hindi Medium':
        relevant_states = ["UP", "Gujarat", "Jharkhand", "Rajasthan", "Madhya Pradesh", "Haryana", "Himachal Pradesh"]
    else:
        relevant_states = ["Telangana", "Andhra Pradesh", "Manipur", "Mizoram", "Tripura"]

    filtered_state_counts = state_counts[state_counts.index.isin(relevant_states)]
    
    # Ensure states appear in the specified order
    state_order = ["Telangana", "Andhra Pradesh", "Manipur", "Mizoram", "Tripura",
                   "UP", "Gujarat", "Jharkhand", "Rajasthan", "Madhya Pradesh",
                   "Haryana", "Himachal Pradesh"]
    
    # Creating CSV Data with KGBVS count for each state
    csv_data = []
    for state in state_order:
        attendees = filtered_state_counts.get(state, 0)
        csv_data.append({
            'State': state,
            'Language': medium,
            'Week': '1',  # This could be dynamic depending on your data
            'Session No.': '1',  # This could be dynamic
            'Session Name': 'Session A',  # This could be dynamic
            'Date': '2024-09-12',  # You can adjust this date dynamically
            'KGBVS who attended': attendees
        })

    # Creating a DataFrame for CSV
    csv_df = pd.DataFrame(csv_data)
    csv_file_path = "kgbvs_attendance.csv"
    csv_df.to_csv(csv_file_path, index=False)

    # Return data for further processing
    return filtered_state_counts, csv_file_path, state_counts

# Function to create PDF with graph and state counts
def create_pdf(state_counts):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Time Interval Distribution", ln=True, align='C')
    
    # Add the graph image to the PDF
    pdf.image('graph.png', 50, 50, 110)  # Add the graph image
    
    pdf.ln(85)  # Move cursor to next line
    pdf.cell(200, 10, txt="State-wise KGBVS Attendance Counts:", ln=True, align='C')

    pdf.ln(10)  # Space before printing state counts

    # Print each state's count below the graph
    for state, count in state_counts.items():
        pdf.cell(200, 10, txt=f"{state}: {count}", ln=True, align='L')

    pdf_file_path = "data_analysis_report.pdf"
    pdf.output(pdf_file_path)
    return pdf_file_path

# Streamlit app
st.title('Data Analysis and Report Generation')

medium = st.selectbox("Select Medium", ["Hindi Medium", "English Medium"])

uploaded_file = st.file_uploader("Upload data file (xlsx or csv)", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # Handling xlsx and csv file upload
        if uploaded_file.name.endswith('.xlsx'):
            data = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)

        # Ensure the required columns exist in the uploaded file
        required_columns = ['Meeting ID', 'User Type']  # Adjust based on your data
        if all(col in data.columns for col in required_columns):
            state_counts, csv_file_path, full_state_counts = process_data(data, medium)
            
            if state_counts is not None:
                # Plotting the graph
                fig, ax = plt.subplots(figsize=(10, 6))
                state_counts_df = state_counts.reset_index()
                state_counts_df.columns = ['State', 'Count']
                ax.bar(state_counts_df['State'].astype(str), state_counts_df['Count'], color='skyblue')
                plt.xticks(rotation=45)
                plt.xlabel('State')
                plt.ylabel('Count')
                plt.title('KGBVS Attendance by State')
                plt.grid(axis='y', linestyle='--', alpha=0.7)
                plt.tight_layout()
                plt.savefig('graph.png')
                st.image('graph.png', caption='KGBVS Attendance Distribution by State')

                # Generate and provide PDF download
                pdf_file_path = create_pdf(full_state_counts)
                
                with open(pdf_file_path, "rb") as f:
                    pdf_base64 = base64.b64encode(f.read()).decode('utf-8')
                    st.markdown(f'<a href="data:application/pdf;base64,{pdf_base64}" download="{pdf_file_path}">Download PDF Report</a>', unsafe_allow_html=True)

                # Provide CSV download link
                st.markdown(f'<a href="data:file/csv;base64,{base64.b64encode(open(csv_file_path, "rb").read()).decode()}" download="{csv_file_path}">Download CSV Report</a>', unsafe_allow_html=True)
        else:
            st.error("Uploaded file does not have the required columns.")
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
