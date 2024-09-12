# # # # # import streamlit as st
# # # # # import pandas as pd
# # # # # import matplotlib.pyplot as plt
# # # # # from datetime import datetime
# # # # # import re
# # # # # import requests
# # # # # from fpdf import FPDF
# # # # # import base64

# # # # # # Function to process data
# # # # # def process_data(data, medium):
# # # # #     def standardize_time(time_str):
# # # # #         if 'AM' in time_str or 'PM' in time_str:
# # # # #             return pd.to_datetime(time_str, format='%I:%M:%S %p', errors='coerce')
# # # # #         else:
# # # # #             return pd.to_datetime(time_str, format='%H:%M:%S', errors='coerce')

# # # # #     def get_state_from_ip(ip_address, api_key):
# # # # #         url = f"https://ipinfo.io/{ip_address}/json?token={api_key}"
# # # # #         response = requests.get(url)
# # # # #         if response.status_code == 200:
# # # # #             data = response.json()
# # # # #             return data.get('region', 'Unknown')
# # # # #         else:
# # # # #             return 'Unknown'

# # # # #     api_key = '7837dcaf59814e'  # Replace with your actual IPInfo API key
# # # # #     unique_df = data.drop_duplicates(subset=['Meeting ID'])
# # # # #     unique_df['State'] = unique_df['User Type'].apply(lambda ip: get_state_from_ip(ip, api_key))
# # # # #     state_counts = unique_df['State'].value_counts()

# # # # #     # Filter states based on medium
# # # # #     if medium == 'Hindi Medium':
# # # # #         relevant_states = ["Gujarat", "Uttar Pradesh", "Rajasthan", "Haryana", "Himachal Pradesh", "Jharkhand", "Madhya Pradesh"]
# # # # #     else:
# # # # #         relevant_states = ["Telangana", "Andhra Pradesh", "Manipur", "Mizoram", "Tripura"]

# # # # #     filtered_state_counts = state_counts[state_counts.index.isin(relevant_states)]
# # # # #     other_states_df = state_counts[~state_counts.index.isin(relevant_states)].reset_index()
# # # # #     other_states_df.columns = ['State', 'Count']
# # # # #     other_states_df = pd.concat([
# # # # #         other_states_df,
# # # # #         pd.DataFrame({'State': ['Other States'], 'Count': [other_states_df['Count'].sum()]})
# # # # #     ], ignore_index=True)

# # # # #     data['Archiving'] = data['Archiving'].apply(lambda x: standardize_time(str(x)))
# # # # #     data = data.dropna(subset=['Archiving'])
# # # # #     data['Archiving'] = data['Archiving'].dt.strftime('%I:%M:%S').str.lstrip('0')
# # # # #     if 'Phone' in data.columns:
# # # # #         def extract_time(text):
# # # # #             if isinstance(text, str):
# # # # #                 time_match = re.search(r'\d{2}:\d{2}:\d{2} [APM]{2}', text)
# # # # #                 if time_match:
# # # # #                     return time_match.group(0)
# # # # #             return None

# # # # #         data['Phone'] = data['Phone'].astype(str)
# # # # #         sliced_data = data.loc[3:].copy()
# # # # #         sliced_data['Extracted Time'] = sliced_data['Phone'].apply(extract_time)
# # # # #         data.loc[3:, 'Extracted Time'] = sliced_data['Extracted Time'].values

# # # # #         def remove_am_pm(time_str):
# # # # #             if isinstance(time_str, str):
# # # # #                 return time_str.split()[0]
# # # # #             return time_str

# # # # #         data['Extracted Time'] = data['Extracted Time'].apply(remove_am_pm)
# # # # #         data['Archiving'] = data['Archiving'].apply(remove_am_pm)
# # # # #         data['Archiving'] = pd.to_datetime(data['Archiving'], format='%H:%M:%S', errors='coerce').dt.time
# # # # #         data['Extracted Time'] = pd.to_datetime(data['Extracted Time'], format='%H:%M:%S', errors='coerce').dt.time

# # # # #         def time_difference(row):
# # # # #             time_format = '%H:%M:%S'
# # # # #             try:
# # # # #                 archiving_time = datetime.strptime(str(row['Archiving']), time_format)
# # # # #                 extracted_time = datetime.strptime(str(row['Extracted Time']), time_format)
# # # # #                 time_diff = extracted_time - archiving_time
# # # # #                 return time_diff.total_seconds() / 60.0
# # # # #             except:
# # # # #                 return None

# # # # #         data['diff'] = data.apply(time_difference, axis=1)
# # # # #         data = data.iloc[0:].reset_index(drop=True)
# # # # #         data['diff'] = pd.to_numeric(data['diff'], errors='coerce')

# # # # #         aggregated_data = data.groupby('User Type', as_index=False).agg({'diff': 'sum'})
# # # # #         aggregated_data.columns = ['Unique IP Add', 'Total Time Spend']

# # # # #         data['Unique IP'] = aggregated_data['Unique IP Add']
# # # # #         data['Total Time Spend'] = aggregated_data['Total Time Spend']
# # # # #         bin_edges = [0, 1, 5, 20, 40, 60, 80, float('inf')]
# # # # #         bin_labels = ['<1 min', '1-5 mins', '5-20 mins', '20-40 mins', '40-60 mins', '60-80 mins', '80+ mins']

# # # # #         data['Time Interval'] = pd.cut(data['Total Time Spend'], bins=bin_edges, labels=bin_labels, right=False)
# # # # #         time_interval_counts = data['Time Interval'].value_counts().sort_index()
# # # # #         return time_interval_counts, filtered_state_counts, aggregated_data, other_states_df
# # # # #     else:
# # # # #         st.error("The 'Phone' column is missing in the uploaded file.")
# # # # #         return None, None, None, None


# # # # # # Function to create PDF
# # # # # def create_pdf(state_counts, time_interval_counts_df, aggregated_data_df, other_states_df):
# # # # #     pdf = FPDF()
# # # # #     pdf.add_page()
    
# # # # #     pdf.set_font("Arial", size=12)
    
# # # # #     pdf.cell(200, 10, txt="Data Analysis Report", ln=True, align='C')
    
# # # # #     pdf.ln(10)
# # # # #     pdf.cell(200, 10, txt="State Counts", ln=True)
# # # # #     for state, count in state_counts.items():
# # # # #         pdf.cell(200, 10, txt=f"{state}: {count}", ln=True)
    
# # # # #     pdf.ln(10)
# # # # #     pdf.cell(200, 10, txt="Other States", ln=True)
# # # # #     for index, row in other_states_df.iterrows():
# # # # #         pdf.cell(200, 10, txt=f"{row['State']}: {row['Count']}", ln=True)
    
# # # # #     pdf.ln(10)
# # # # #     pdf.cell(200, 10, txt="Time Interval Counts", ln=True)
# # # # #     for index, row in time_interval_counts_df.iterrows():
# # # # #         pdf.cell(200, 10, txt=f"{row['Time Interval']}: {row['Count']}", ln=True)
    
# # # # #     pdf.add_page()
# # # # #     pdf.image('graph.png', 50, 50, 110)
    
# # # # #     pdf_file_path = "data_analysis_report.pdf"
# # # # #     pdf.output(pdf_file_path)
# # # # #     return pdf_file_path

# # # # # # Streamlit app
# # # # # st.title('Data Analysis and Report Generation')

# # # # # medium = st.selectbox("Select Medium", ["Hindi Medium", "English Medium"])

# # # # # uploaded_file = st.file_uploader("Upload data.xlsx", type="xlsx")

# # # # # if uploaded_file:
# # # # #     data = pd.read_excel(uploaded_file)
# # # # #     time_interval_counts, state_counts, aggregated_data, other_states_df = process_data(data, medium)
    
# # # # #     if time_interval_counts is not None:
# # # # #         # Plotting the graph
# # # # #         fig, ax = plt.subplots(figsize=(10, 6))
# # # # #         time_interval_counts_df = time_interval_counts.reset_index()
# # # # #         time_interval_counts_df.columns = ['Time Interval', 'Count']
# # # # #         ax.bar(time_interval_counts_df['Time Interval'].astype(str), time_interval_counts_df['Count'], color='skyblue')
# # # # #         plt.xticks(rotation=45)
# # # # #         plt.xlabel('Time Interval (minutes)')
# # # # #         plt.ylabel('Count')
# # # # #         plt.title('Count of Participation in Different Time Intervals')
# # # # #         plt.grid(axis='y', linestyle='--', alpha=0.7)
# # # # #         plt.tight_layout()
# # # # #         plt.savefig('graph.png')
# # # # #         st.image('graph.png', caption='Time Interval Distribution')

# # # # #         st.write("Summary of State Counts:")
# # # # #         st.dataframe(state_counts.reset_index().rename(columns={'index': 'State', 'State': 'Count'}))

# # # # #         st.write("Other States:")
# # # # #         st.dataframe(other_states_df)

# # # # #         # Generate and provide PDF download
# # # # #         pdf_file_path = create_pdf(state_counts, time_interval_counts_df, aggregated_data, other_states_df)
        
# # # # #         with open(pdf_file_path, "rb") as f:
# # # # #             pdf_base64 = base64.b64encode(f.read()).decode('utf-8')
# # # # #             st.markdown(f'<a href="data:application/pdf;base64,{pdf_base64}" download="{pdf_file_path}">Download PDF Report</a>', unsafe_allow_html=True)

# # # # import streamlit as st
# # # # import pandas as pd
# # # # import matplotlib.pyplot as plt
# # # # from datetime import datetime
# # # # import re
# # # # import requests
# # # # from fpdf import FPDF
# # # # import base64

# # # # # Function to process data
# # # # def process_data(data, medium):
# # # #     def standardize_time(time_str):
# # # #         if 'AM' in time_str or 'PM' in time_str:
# # # #             return pd.to_datetime(time_str, format='%I:%M:%S %p', errors='coerce')
# # # #         else:
# # # #             return pd.to_datetime(time_str, format='%H:%M:%S', errors='coerce')

# # # #     def get_state_from_ip(ip_address, api_key):
# # # #         url = f"https://ipinfo.io/{ip_address}/json?token={api_key}"
# # # #         response = requests.get(url)
# # # #         if response.status_code == 200:
# # # #             data = response.json()
# # # #             return data.get('region', 'Unknown')
# # # #         else:
# # # #             return 'Unknown'

# # # #     api_key = '7837dcaf59814e'  # Replace with your actual IPInfo API key
# # # #     unique_df = data.drop_duplicates(subset=['Meeting ID'])
# # # #     unique_df['State'] = unique_df['User Type'].apply(lambda ip: get_state_from_ip(ip, api_key))
# # # #     state_counts = unique_df['State'].value_counts()

# # # #     # Filter states based on medium
# # # #     if medium == 'Hindi Medium':
# # # #         relevant_states = ["Gujarat", "Uttar Pradesh", "Rajasthan", "Haryana", "Himachal Pradesh", "Jharkhand", "Madhya Pradesh"]
# # # #     else:
# # # #         relevant_states = ["Telangana", "Andhra Pradesh", "Manipur", "Mizoram", "Tripura"]

# # # #     filtered_state_counts = state_counts[state_counts.index.isin(relevant_states)]
# # # #     other_states_df = state_counts[~state_counts.index.isin(relevant_states)].reset_index()
# # # #     other_states_df.columns = ['State', 'Count']
# # # #     other_states_df = pd.concat([other_states_df, pd.DataFrame({'State': ['Other States'], 'Count': [other_states_df['Count'].sum()]})], ignore_index=True)

# # # #     data['Archiving'] = data['Archiving'].apply(lambda x: standardize_time(str(x)))
# # # #     data = data.dropna(subset=['Archiving'])
# # # #     data['Archiving'] = data['Archiving'].dt.strftime('%I:%M:%S').str.lstrip('0')
    
# # # #     if 'Phone' in data.columns:
# # # #         def extract_time(text):
# # # #             if isinstance(text, str):
# # # #                 time_match = re.search(r'\d{2}:\d{2}:\d{2} [APM]{2}', text)
# # # #                 if time_match:
# # # #                     return time_match.group(0)
# # # #             return None

# # # #         data['Phone'] = data['Phone'].astype(str)
# # # #         sliced_data = data.loc[3:].copy()
# # # #         sliced_data['Extracted Time'] = sliced_data['Phone'].apply(extract_time)
# # # #         data.loc[3:, 'Extracted Time'] = sliced_data['Extracted Time'].values

# # # #         def remove_am_pm(time_str):
# # # #             if isinstance(time_str, str):
# # # #                 return time_str.split()[0]
# # # #             return time_str

# # # #         data['Extracted Time'] = data['Extracted Time'].apply(remove_am_pm)
# # # #         data['Archiving'] = data['Archiving'].apply(remove_am_pm)
# # # #         data['Archiving'] = pd.to_datetime(data['Archiving'], format='%H:%M:%S', errors='coerce').dt.time
# # # #         data['Extracted Time'] = pd.to_datetime(data['Extracted Time'], format='%H:%M:%S', errors='coerce').dt.time

# # # #         def time_difference(row):
# # # #             time_format = '%H:%M:%S'
# # # #             try:
# # # #                 archiving_time = datetime.strptime(str(row['Archiving']), time_format)
# # # #                 extracted_time = datetime.strptime(str(row['Extracted Time']), time_format)
# # # #                 time_diff = extracted_time - archiving_time
# # # #                 return time_diff.total_seconds() / 60.0
# # # #             except:
# # # #                 return None

# # # #         data['diff'] = data.apply(time_difference, axis=1)
# # # #         data = data.iloc[0:].reset_index(drop=True)
# # # #         data['diff'] = pd.to_numeric(data['diff'], errors='coerce')

# # # #         aggregated_data = data.groupby('User Type', as_index=False).agg({'diff': 'sum'})
# # # #         aggregated_data.columns = ['Unique IP Add', 'Total Time Spend']

# # # #         data['Unique IP'] = aggregated_data['Unique IP Add']
# # # #         data['Total Time Spend'] = aggregated_data['Total Time Spend']
# # # #         bin_edges = [0, 1, 5, 20, 40, 60, 80, float('inf')]
# # # #         bin_labels = ['<1 min', '1-5 mins', '5-20 mins', '20-40 mins', '40-60 mins', '60-80 mins', '80+ mins']

# # # #         data['Time Interval'] = pd.cut(data['Total Time Spend'], bins=bin_edges, labels=bin_labels, right=False)
# # # #         time_interval_counts = data['Time Interval'].value_counts().sort_index()
# # # #         return time_interval_counts, filtered_state_counts, aggregated_data, other_states_df
# # # #     else:
# # # #         st.error("The 'Phone' column is missing in the uploaded file.")
# # # #         return None, None, None, None

# # # # # Function to create PDF
# # # # def create_pdf(state_counts, time_interval_counts_df, aggregated_data_df, other_states_df):
# # # #     pdf = FPDF()
# # # #     pdf.add_page()
    
# # # #     pdf.set_font("Arial", size=12)
    
# # # #     pdf.cell(200, 10, txt="Data Analysis Report", ln=True, align='C')
    
# # # #     pdf.ln(10)
# # # #     pdf.cell(200, 10, txt="State Counts", ln=True)
# # # #     for state, count in state_counts.items():
# # # #         pdf.cell(200, 10, txt=f"{state}: {count}", ln=True)
    
# # # #     pdf.ln(10)
# # # #     pdf.cell(200, 10, txt="Other States", ln=True)
# # # #     for index, row in other_states_df.iterrows():
# # # #         pdf.cell(200, 10, txt=f"{row['State']}: {row['Count']}", ln=True)
    
# # # #     pdf.ln(10)
# # # #     pdf.cell(200, 10, txt="Time Interval Counts", ln=True)
# # # #     for index, row in time_interval_counts_df.iterrows():
# # # #         pdf.cell(200, 10, txt=f"{row['Time Interval']}: {row['Count']}", ln=True)
    
# # # #     pdf.add_page()
# # # #     pdf.image('graph.png', 50, 50, 110)
    
# # # #     pdf_file_path = "data_analysis_report.pdf"
# # # #     pdf.output(pdf_file_path)
# # # #     return pdf_file_path

# # # # # Streamlit app
# # # # st.title('Data Analysis and Report Generation')

# # # # medium = st.selectbox("Select Medium", ["Hindi Medium", "English Medium"])

# # # # uploaded_file = st.file_uploader("Upload data file (xlsx or csv)", type=["xlsx", "csv"])

# # # # if uploaded_file:
# # # #     file_extension = uploaded_file.name.split('.')[-1].lower()
    
# # # #     if file_extension == 'xlsx':
# # # #         data = pd.read_excel(uploaded_file)
# # # #     elif file_extension == 'csv':
# # # #         data = pd.read_csv(uploaded_file)
    
# # # #     time_interval_counts, state_counts, aggregated_data, other_states_df = process_data(data, medium)
    
# # # #     if time_interval_counts is not None:
# # # #         # Plotting the graph
# # # #         fig, ax = plt.subplots(figsize=(10, 6))
# # # #         time_interval_counts_df = time_interval_counts.reset_index()
# # # #         time_interval_counts_df.columns = ['Time Interval', 'Count']
# # # #         ax.bar(time_interval_counts_df['Time Interval'].astype(str), time_interval_counts_df['Count'], color='skyblue')
# # # #         plt.xticks(rotation=45)
# # # #         plt.xlabel('Time Interval (minutes)')
# # # #         plt.ylabel('Count')
# # # #         plt.title('Count of Participation in Different Time Intervals')
# # # #         plt.grid(axis='y', linestyle='--', alpha=0.7)
# # # #         plt.tight_layout()
# # # #         plt.savefig('graph.png')
# # # #         st.image('graph.png', caption='Time Interval Distribution')

# # # #         st.write("Summary of State Counts:")
# # # #         st.dataframe(state_counts.reset_index().rename(columns={'index': 'State', 'State': 'Count'}))

# # # #         st.write("Other States:")
# # # #         st.dataframe(other_states_df)

# # # #         # Generate and provide PDF download
# # # #         pdf_file_path = create_pdf(state_counts, time_interval_counts_df, aggregated_data, other_states_df)
        
# # # #         with open(pdf_file_path, "rb") as f:
# # # #             pdf_base64 = base64.b64encode(f.read()).decode('utf-8')
# # # #             st.markdown(f'<a href="data:application/pdf;base64,{pdf_base64}" download="{pdf_file_path}">Download PDF Report</a>', unsafe_allow_html=True)
# # import streamlit as st
# # import pandas as pd
# # import matplotlib.pyplot as plt
# # from datetime import datetime
# # import re
# # import requests
# # from fpdf import FPDF
# # import base64

# # # Function to process data
# # def process_data(data, medium):
# #     def standardize_time(time_str):
# #         if 'AM' in time_str or 'PM' in time_str:
# #             return pd.to_datetime(time_str, format='%I:%M:%S %p', errors='coerce')
# #         else:
# #             return pd.to_datetime(time_str, format='%H:%M:%S', errors='coerce')

# #     def get_state_from_ip(ip_address, api_key):
# #         url = f"https://ipinfo.io/{ip_address}/json?token={api_key}"
# #         response = requests.get(url)
# #         if response.status_code == 200:
# #             data = response.json()
# #             return data.get('region', 'Unknown')
# #         else:
# #             return 'Unknown'

# #     api_key = '7837dcaf59814e'  # Replace with your actual IPInfo API key
# #     unique_df = data.drop_duplicates(subset=['Meeting ID'])
# #     unique_df['State'] = unique_df['User Type'].apply(lambda ip: get_state_from_ip(ip, api_key))
# #     state_counts = unique_df['State'].value_counts()

# #     # Filter states based on medium
# #     if medium == 'Hindi Medium':
# #         relevant_states = ["UP", "Gujarat", "Jharkhand", "Rajasthan", "Madhya Pradesh", "Haryana", "Himachal Pradesh"]
# #     else:
# #         relevant_states = ["Telangana", "Andhra Pradesh", "Manipur", "Mizoram", "Tripura"]

# #     filtered_state_counts = state_counts[state_counts.index.isin(relevant_states)]
    
# #     # Ensure states appear in the specified order
# #     state_order = ["Telangana", "Andhra Pradesh", "Manipur", "Mizoram", "Tripura",
# #                    "UP", "Gujarat", "Jharkhand", "Rajasthan", "Madhya Pradesh",
# #                    "Haryana", "Himachal Pradesh"]
    
# #     # Creating CSV Data with KGBVS count for each state
# #     csv_data = []
# #     for state in state_order:
# #         attendees = filtered_state_counts.get(state, 0)
# #         csv_data.append({
# #             'State': state,
# #             'Language': '',
# #             'Week': '',  # This could be dynamic depending on your data
# #             'Session No.': '',  # This could be dynamic
# #             'Session Name': '',  # This could be dynamic
# #             'Date': '',  # You can adjust this date dynamically
# #             'KGBVS who attended': attendees
# #         })

# #     # Creating a DataFrame for CSV
# #     csv_df = pd.DataFrame(csv_data)
# #     csv_file_path = "kgbvs_attendance.csv"
# #     csv_df.to_csv(csv_file_path, index=False)

# #     # Return data for further processing
# #     return filtered_state_counts, csv_file_path

# # # Function to create PDF with only the graph
# # def create_pdf(state_counts, additional_states):
# #     pdf = FPDF()
# #     pdf.add_page()
    
# #     # Title
# #     pdf.set_font("Arial", size=12)
# #     pdf.cell(200, 10, txt="KGBVS Attendance Distribution", ln=True, align='C')

# #     # Add the graph image to PDF
# #     pdf.image('graph.png', 50, 50, 110)
    
# #     # Add space after the graph
# #     pdf.ln(120)

# #     # Add table headers for the state counts
# #     pdf.set_font("Arial", size=10)
# #     pdf.cell(50, 10, 'State', 1, 0, 'C')
# #     pdf.cell(50, 10, 'KGBVS who attended', 1, 1, 'C')

# #     # First, include the states in the specified order
# #     for state, count in state_counts.items():
# #         pdf.cell(50, 10, state, 1, 0, 'C')
# #         pdf.cell(50, 10, str(count), 1, 1, 'C')

# #     # Now, include any other states not in the specified order
# #     pdf.cell(200, 10, txt="Other States:", ln=True, align='L')
# #     for state, count in additional_states.items():
# #         pdf.cell(50, 10, state, 1, 0, 'C')
# #         pdf.cell(50, 10, str(count), 1, 1, 'C')
    
# #     # Save the PDF
# #     pdf_file_path = "data_analysis_report.pdf"
# #     pdf.output(pdf_file_path)
# #     return pdf_file_path

# # # Streamlit app
# # st.title('Data Analysis and Report Generation')

# # medium = st.selectbox("Select Medium", ["Hindi Medium", "English Medium"])

# # uploaded_file = st.file_uploader("Upload data file (xlsx or csv)", type=["xlsx", "csv"])

# # # Main section of the app to handle data and display
# # if uploaded_file:
# #     # Reading the file based on its extension
# #     if uploaded_file.name.endswith('.xlsx'):
# #         data = pd.read_excel(uploaded_file)
# #     elif uploaded_file.name.endswith('.csv'):
# #         data = pd.read_csv(uploaded_file)
    
# #     # Process the data
# #     state_counts, csv_file_path = process_data(data, medium)

# #     # Separate the states that were not in the specified order
# #     state_order = ["Telangana", "Andhra Pradesh", "Manipur", "Mizoram", "Tripura",
# #                    "UP", "Gujarat", "Jharkhand", "Rajasthan", "Madhya Pradesh",
# #                    "Haryana", "Himachal Pradesh"]

# #     additional_states = {state: state_counts[state] for state in state_counts if state not in state_order}

# #     if state_counts is not None:
# #         # Plot the graph
# #         fig, ax = plt.subplots(figsize=(10, 6))
# #         state_counts_df = state_counts.reset_index()
# #         state_counts_df.columns = ['State', 'Count']
# #         ax.bar(state_counts_df['State'].astype(str), state_counts_df['Count'], color='skyblue')
# #         plt.xticks(rotation=45)
# #         plt.xlabel('State')
# #         plt.ylabel('Count')
# #         plt.title('KGBVS Attendance by State')
# #         plt.grid(axis='y', linestyle='--', alpha=0.7)
# #         plt.tight_layout()
# #         plt.savefig('graph.png')
# #         st.image('graph.png', caption='KGBVS Attendance Distribution by State')

# #         # Generate and provide PDF download with the additional states
# #         pdf_file_path = create_pdf(state_counts, additional_states)
        
# #         with open(pdf_file_path, "rb") as f:
# #             pdf_base64 = base64.b64encode(f.read()).decode('utf-8')
# #             st.markdown(f'<a href="data:application/pdf;base64,{pdf_base64}" download="{pdf_file_path}">Download PDF Report</a>', unsafe_allow_html=True)

# #         # Provide CSV download link
# #         st.markdown(f'<a href="data:file/csv;base64,{base64.b64encode(open(csv_file_path, "rb").read()).decode()}" download="{csv_file_path}">Download CSV Report</a>', unsafe_allow_html=True)

# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt
# from datetime import datetime
# import re
# import requests
# from fpdf import FPDF
# import base64

# # Function to process data
# def process_data(data, medium):
#     def standardize_time(time_str):
#         if 'AM' in time_str or 'PM' in time_str:
#             return pd.to_datetime(time_str, format='%I:%M:%S %p', errors='coerce')
#         else:
#             return pd.to_datetime(time_str, format='%H:%M:%S', errors='coerce')

#     def get_state_from_ip(ip_address, api_key):
#         url = f"https://ipinfo.io/{ip_address}/json?token={api_key}"
#         response = requests.get(url)
#         if response.status_code == 200:
#             data = response.json()
#             return data.get('region', 'Unknown')
#         else:
#             return 'Unknown'

#     api_key = '7837dcaf59814e'  # Replace with your actual IPInfo API key
#     unique_df = data.drop_duplicates(subset=['Meeting ID'])
#     unique_df['State'] = unique_df['User Type'].apply(lambda ip: get_state_from_ip(ip, api_key))
#     state_counts = unique_df['State'].value_counts()

#     # Filter states based on medium
#     if medium == 'Hindi Medium':
#         relevant_states = ["UP", "Gujarat", "Jharkhand", "Rajasthan", "Madhya Pradesh", "Haryana", "Himachal Pradesh"]
#     else:
#         relevant_states = ["Telangana", "Andhra Pradesh", "Manipur", "Mizoram", "Tripura"]

#     filtered_state_counts = state_counts[state_counts.index.isin(relevant_states)]
    
#     # Ensure states appear in the specified order
#     state_order = ["Telangana", "Andhra Pradesh", "Manipur", "Mizoram", "Tripura",
#                    "UP", "Gujarat", "Jharkhand", "Rajasthan", "Madhya Pradesh",
#                    "Haryana", "Himachal Pradesh"]
    
#     # Creating CSV Data with KGBVS count for each state
#     csv_data = []
#     for state in state_order:
#         attendees = filtered_state_counts.get(state, 0)
#         csv_data.append({
#             'State': state,
#             'Language': medium,
#             'Week': '1',  # This could be dynamic depending on your data
#             'Session No.': '1',  # This could be dynamic
#             'Session Name': 'Session A',  # This could be dynamic
#             'Date': '2024-09-12',  # You can adjust this date dynamically
#             'KGBVS who attended': attendees
#         })

#     # Creating a DataFrame for CSV
#     csv_df = pd.DataFrame(csv_data)
#     csv_file_path = "kgbvs_attendance.csv"
#     csv_df.to_csv(csv_file_path, index=False)

#     # Return data for further processing
#     return filtered_state_counts, csv_file_path, state_counts

# # Function to create PDF with graph and state counts
# def create_pdf(state_counts):
#     pdf = FPDF()
#     pdf.add_page()
    
#     pdf.set_font("Arial", size=12)
#     pdf.cell(200, 10, txt="Time Interval Distribution", ln=True, align='C')
    
#     # Add the graph image to the PDF
#     pdf.image('graph.png', 50, 50, 110)  # Add the graph image
    
#     pdf.ln(85)  # Move cursor to next line
#     pdf.cell(200, 10, txt="State-wise KGBVS Attendance Counts:", ln=True, align='C')

#     pdf.ln(10)  # Space before printing state counts

#     # Print each state's count below the graph
#     for state, count in state_counts.items():
#         pdf.cell(200, 10, txt=f"{state}: {count}", ln=True, align='L')

#     pdf_file_path = "data_analysis_report.pdf"
#     pdf.output(pdf_file_path)
#     return pdf_file_path

# # Streamlit app
# st.title('Data Analysis and Report Generation')

# medium = st.selectbox("Select Medium", ["Hindi Medium", "English Medium"])

# uploaded_file = st.file_uploader("Upload data file (xlsx or csv)", type=["xlsx", "csv"])

# if uploaded_file:
#     # Reading the file based on its extension
#     if uploaded_file.name.endswith('.xlsx'):
#         data = pd.read_excel(uploaded_file)
#     elif uploaded_file.name.endswith('.csv'):
#         data = pd.read_csv(uploaded_file)
    
#     state_counts, csv_file_path, full_state_counts = process_data(data, medium)
    
#     if state_counts is not None:
#         # Plotting the graph
#         fig, ax = plt.subplots(figsize=(10, 6))
#         state_counts_df = state_counts.reset_index()
#         state_counts_df.columns = ['State', 'Count']
#         ax.bar(state_counts_df['State'].astype(str), state_counts_df['Count'], color='skyblue')
#         plt.xticks(rotation=45)
#         plt.xlabel('State')
#         plt.ylabel('Count')
#         plt.title('KGBVS Attendance by State')
#         plt.grid(axis='y', linestyle='--', alpha=0.7)
#         plt.tight_layout()
#         plt.savefig('graph.png')
#         st.image('graph.png', caption='KGBVS Attendance Distribution by State')

#         # Generate and provide PDF download
#         pdf_file_path = create_pdf(full_state_counts)
        
#         with open(pdf_file_path, "rb") as f:
#             pdf_base64 = base64.b64encode(f.read()).decode('utf-8')
#             st.markdown(f'<a href="data:application/pdf;base64,{pdf_base64}" download="{pdf_file_path}">Download PDF Report</a>', unsafe_allow_html=True)

#         # Provide CSV download link
#         st.markdown(f'<a href="data:file/csv;base64,{base64.b64encode(open(csv_file_path, "rb").read()).decode()}" download="{csv_file_path}">Download CSV Report</a>', unsafe_allow_html=True)

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
