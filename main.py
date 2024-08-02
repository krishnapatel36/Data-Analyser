import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import re
from fpdf import FPDF
import base64
import requests

# Function to process data
def process_data(data):
    def get_state_from_ip(ip_address, api_key):
        url = f"https://ipinfo.io/{ip_address}/json?token={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get('region', 'Unknown')
        else:
            return 'Unknown'
    api_key = '7837dcaf59814e'  # Replace with your actual IPInfo API key

    data['State'] = data['User Type'].apply(lambda ip: get_state_from_ip(ip, api_key))
    state_counts = data['State'].value_counts()

    data['Archiving'] = pd.to_datetime(data['Archiving'], format='%H:%M:%S', errors='coerce')
    data = data.dropna(subset=['Archiving'])

    data['Archiving'] = data['Archiving'].dt.strftime('%I:%M:%S').str.lstrip('0')

    if 'Phone' in data.columns:
        def extract_time(text):
            if isinstance(text, str):
                time_match = re.search(r'\d{2}:\d{2}:\d{2} [APM]{2}', text)
                if time_match:
                    return time_match.group(0)
            return None

        data['Phone'] = data['Phone'].astype(str)
        data['Extracted Time'] = data['Phone'].apply(extract_time)
        data['Extracted Time'] = data['Extracted Time'].apply(lambda x: x.split()[0] if isinstance(x, str) else x)
        data['Archiving'] = data['Archiving'].apply(lambda x: x.split()[0] if isinstance(x, str) else x)
        data['Archiving'] = pd.to_datetime(data['Archiving'], format='%H:%M:%S', errors='coerce').dt.time
        data['Extracted Time'] = pd.to_datetime(data['Extracted Time'], format='%H:%M:%S', errors='coerce').dt.time

        def time_difference(row):
            time_format = '%H:%M:%S'
            try:
                archiving_time = datetime.strptime(str(row['Archiving']), time_format)
                extracted_time = datetime.strptime(str(row['Extracted Time']), time_format)
                time_diff = extracted_time - archiving_time
                return time_diff.total_seconds() / 60.0
            except:
                return None

        data['diff'] = data.apply(time_difference, axis=1)
        data['diff'] = pd.to_numeric(data['diff'], errors='coerce')

        aggregated_data = data.groupby('User Type', as_index=False).agg({'diff': 'sum'})
        aggregated_data.columns = ['Unique IP Add', 'Total Time Spend']

        data['Unique IP'] = aggregated_data['Unique IP Add']
        data['Total Time Spend'] = aggregated_data['Total Time Spend']

        bin_edges = [0, 1, 5, 20, 40, 60, 80, float('inf')]
        bin_labels = ['<1 min', '1-5 mins', '5-20 mins', '20-40 mins', '40-60 mins', '60-80 mins', '80+ mins']

        data['Time Interval'] = pd.cut(data['Total Time Spend'], bins=bin_edges, labels=bin_labels, right=False)
        time_interval_counts = data['Time Interval'].value_counts().sort_index()

        return time_interval_counts, state_counts, aggregated_data
    else:
        st.error("The 'Phone' column is missing in the uploaded file.")
        return None, None, None

# Function to create PDF
def create_pdf(state_counts, time_interval_counts_df, aggregated_data_df):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", size = 12)
    
    pdf.cell(200, 10, txt = "Data Analysis Report", ln = True, align = 'C')
    
    pdf.ln(10)
    pdf.cell(200, 10, txt = "State Counts", ln = True)
    for state, count in state_counts.items():
        pdf.cell(200, 10, txt = f"{state}: {count}", ln = True)
    
    pdf.ln(10)
    pdf.cell(200, 10, txt = "Time Interval Counts", ln = True)
    for index, row in time_interval_counts_df.iterrows():
        pdf.cell(200, 10, txt = f"{row['Time Interval']}: {row['Count']}", ln = True)
    
    pdf.add_page()
    pdf.image('graph.png',50,50,110)
    
    pdf_file_path = "data_analysis_report.pdf"
    pdf.output(pdf_file_path)
    return pdf_file_path

# Streamlit app
st.title('Data Analysis and Report Generation')

uploaded_file = st.file_uploader("Upload data.xlsx", type="xlsx")

if uploaded_file:
    data = pd.read_excel(uploaded_file)
    time_interval_counts, state_counts, aggregated_data = process_data(data)
    
    if time_interval_counts is not None:
        fig, ax = plt.subplots()
        time_interval_counts_df = time_interval_counts.reset_index()
        time_interval_counts_df.columns = ['Time Interval', 'Count']
        ax.bar(time_interval_counts_df['Time Interval'].astype(str), time_interval_counts_df['Count'])
        plt.xticks(rotation=90)
        plt.xlabel('Time Interval')
        plt.ylabel('Count')
        plt.title('Time Interval Distribution')
        plt.tight_layout()
        plt.savefig('graph.png')
        st.image('graph.png', caption='Time Interval Distribution')

        # Display time interval counts as table
        # st.write("Summary of Time Intervals:")
        # st.dataframe(time_interval_counts_df)

        # Display state counts as table
        st.write("Summary of State Counts:")
        st.dataframe(state_counts.reset_index().rename(columns={'index': 'State', 'State': 'Count'}))

        # Generate and provide PDF download
        pdf_file_path = create_pdf(state_counts, time_interval_counts_df, aggregated_data)
        
        with open(pdf_file_path, "rb") as f:
            pdf_base64 = base64.b64encode(f.read()).decode('utf-8')
            st.markdown(f'<a href="data:application/pdf;base64,{pdf_base64}" download="{pdf_file_path}">Download PDF Report</a>', unsafe_allow_html=True)
