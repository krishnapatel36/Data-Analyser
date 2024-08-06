This code implements a Streamlit app designed to process and analyze data from an uploaded Excel file (data.xlsx). The app performs several key functions:

Data Processing:

Time Standardization: Converts time strings in the Archiving and Phone columns to a consistent datetime format.
IP Address Geolocation: Determines the state associated with each unique IP address using the IPInfo API.
Time Extraction and Difference Calculation: Extracts time information from text, calculates the time difference between Archiving and Extracted Time, and aggregates the total time spent by each user.
Visualization:

Time Interval Distribution: Generates a bar graph showing the distribution of participation times across various intervals.
PDF Report Generation:

State Counts and Time Interval Counts: Summarizes the count of participants from different states and their participation time intervals.
Graph Embedding: Includes the generated graph in the PDF report.
User Interaction:

File Upload: Allows users to upload an Excel file.
Data Display: Shows a summary of state counts and the generated time interval distribution graph.
PDF Download: Provides a downloadable PDF report containing the data analysis.
