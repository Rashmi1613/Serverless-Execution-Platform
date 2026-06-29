# app.py
import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime
import altair as alt

# Set page configuration
st.set_page_config(
    page_title="Lambda Function Manager",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define API endpoints
API_BASE_URL = "http://localhost:8000"

# Sidebar for navigation
st.sidebar.title("Lambda Function Manager")
page = st.sidebar.radio("Navigation", ["Functions", "Deploy Function", "Execute Function", "Monitoring Dashboard"])

# Helper functions for API calls
def get_functions():
    try:
        response = requests.get(f"{API_BASE_URL}/functions/list")
        if response.status_code == 200:
            # Make sure to return a dictionary, not a string
            return response.json()
        else:
            st.error(f"Error: {response.status_code}")
            return {}
    except requests.exceptions.RequestException as e:
        st.error(f"API connection error: {e}")
        return {}

	
	


def get_runtime_metrics():
    try:
        response = requests.get(f"{API_BASE_URL}/functions/runtime-metrics")
        if response.status_code == 200:
            return response.json()
        else:
            return {}
    except requests.exceptions.RequestException as e:
        st.error(f"API connection error: {e}")
        return {}

def get_function_details(function_name):
    try:
        response = requests.get(f"{API_BASE_URL}/functions/get/{function_name}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching function details: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"API connection error: {e}")
        return None

def get_function_metrics(function_name):
    try:
        response = requests.get(f"{API_BASE_URL}/functions/metrics/{function_name}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching metrics: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"API connection error: {e}")
        return None

# Function List Page
if page == "Functions":
    st.title("Function Management")
    
    # Refresh button
    if st.button("Refresh Functions"):
        st.rerun()
    
    functions = get_functions()
    
    if not functions:
        st.info("No functions are registered. Go to Deploy Function page to create one.")
    else:
        # Convert functions dictionary to a list of dictionaries for display
        function_list = []
        for name, details in functions.items():
            # Make sure details is a dictionary, not a string
            if isinstance(details, dict):
                function_list.append({
                    "Name": name,
                    "Route": details.get("route", ""),
                    "Language": details.get("language", ""),
                    "Timeout (seconds)": details.get("timeout", 0)
                })
            else:
                # If details is not a dictionary, create a simpler entry
                function_list.append({
                    "Name": name,
                    "Details": str(details)
                })
        
        # Display function table
        st.dataframe(pd.DataFrame(function_list), use_container_width=True)
        
        # Select function for actions
        selected_function = st.selectbox("Select Function", list(functions.keys()))
        
        col1, col2, col3 = st.columns(3)
        
        # View details button
        with col1:
            if st.button("View Details"):
                details = get_function_details(selected_function)
                if details:
                    st.json(details)
        
        # Delete function button
        with col2:
            if st.button("Delete Function"):
                try:
                    response = requests.delete(f"{API_BASE_URL}/functions/delete/{selected_function}")
                    if response.status_code == 200:
                        st.success(f"Function {selected_function} deleted successfully!")
                        time.sleep(1)  # Give user time to see the message
                        st.rerun()
                    else:
                        st.error(f"Failed to delete function: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error: {e}")
        
        # View metrics button
        with col3:
            if st.button("View Metrics"): 
                metrics = get_function_metrics(selected_function)
                if metrics:
                    st.subheader(f"Metrics for {selected_function}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Average Duration (seconds)", f"{metrics.get('average_duration') or 0.0:.4f}")
                    with col2:
                        st.metric("Total Invocations", metrics.get("total_invocations", 0))

# Deploy Function Page
elif page == "Deploy Function":
    st.title("Deploy New Function")
    
    # Check if editing an existing function
    functions = get_functions()
    edit_mode = st.checkbox("Edit Existing Function")
    
    if edit_mode and functions:
        function_to_edit = st.selectbox("Select Function to Edit", list(functions.keys()))
        function_details = get_function_details(function_to_edit)
        
        if function_details and isinstance(function_details, dict):
            # Pre-fill form with existing values
            name = st.text_input("Function Name", value=function_details.get("name", ""), disabled=True)
            route = st.text_input("Route", value=function_details.get("route", ""))
            language = st.selectbox("Language", ["python", "javascript"], 
                                  index=0 if function_details.get("language") == "python" else 1)
            timeout = st.slider("Timeout (seconds)", min_value=1, max_value=300, 
                              value=function_details.get("timeout", 10))
            
            if st.button("Update Function"):
                data = {
                    "name": name,
                    "route": route,
                    "language": language,
                    "timeout": timeout
                }
                try:
                    response = requests.put(f"{API_BASE_URL}/functions/update/{name}", json=data)
                    if response.status_code == 200:
                        st.success(f"Function {name} updated successfully!")
                    else:
                        st.error(f"Failed to update function: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error: {e}")
        else:
            st.error("Could not load function details or invalid format")
    else:
        # Form for new function
        with st.form("deploy_function_form"):
            name = st.text_input("Function Name")
            route = st.text_input("Route (e.g., /hello)")
            language = st.selectbox("Language", ["python"])
            timeout = st.slider("Timeout (seconds)", min_value=1, max_value=300, value=10)
            
            submitted = st.form_submit_button("Deploy Function")
            if submitted:
                if not name or not route:
                    st.error("Name and route are required!")
                else:
                    data = {
                        "name": name,
                        "route": route,
                        "language": language,
                        "timeout": timeout
                    }
                    try:
                        response = requests.post(f"{API_BASE_URL}/functions/register", json=data)
                        if response.status_code == 200:
                            st.success(f"Function {name} deployed successfully!")
                        else:
                            st.error(f"Failed to deploy function: {response.status_code}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error: {e}")

# Execute Function Page
elif page == "Execute Function":
    st.title("Execute Function")
    
    runtime_options = ["docker", "docker-warm","gvisor"]
    if "second_runtime" in st.session_state:
        runtime_options.append(st.session_state.second_runtime)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        function_code = st.text_area("Function Code", 
                                    value='print("Hello Lambda!")', 
                                    height=300)
    
    
    with col2:
        language = st.selectbox("Language", ["python"])
        runtime = st.selectbox("Runtime", runtime_options)
        
        if st.button("Execute", type="primary"):
            execute_data = {
                "functionCode": function_code,
                "language": language,
                "runtime": runtime
            }
            
            try:
                with st.spinner("Executing function..."):
                    start_time = time.time()
                    response = requests.post(f"{API_BASE_URL}/functions/execute", json=execute_data)
                    execution_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.subheader("Execution Results")
                        st.text("Standard Output:")
                        st.code(result.get("stdout", ""))
                        
                        if result.get("stderr"):
                            st.text("Standard Error:")
                            st.code(result.get("stderr"))
                        
                        # Display execution metrics
                        st.subheader("Execution Metrics")
                        metrics = result.get("metrics", {})
                        
                        metric_cols = st.columns(4)
                        metric_cols[0].metric("Duration (s)", f"{metrics.get('duration', 0):.4f}")
                        metric_cols[1].metric("API Latency (s)", f"{execution_time:.4f}")
                        metric_cols[2].metric("CPU (%)", metrics.get("cpu_percent", 0))
                        metric_cols[3].metric("Memory (MB)", metrics.get("memory_mb", 0))
                    else:
                        st.error(f"Execution failed: {response.status_code}")
                        st.text(response.text)
            except requests.exceptions.RequestException as e:
                st.error(f"Error: {e}")

# Monitoring Dashboard Page

# Monitoring Dashboard Page
elif page == "Monitoring Dashboard":
    st.title("Function Monitoring Dashboard")

    runtime_data = get_runtime_metrics()

    st.header("System-wide Statistics")

    if not runtime_data:
        st.info("No metrics yet. Execute some functions first!")
    else:
        runtimes = list(runtime_data.keys())
        avg_durations = [runtime_data[r]["average_duration"] for r in runtimes]
        invocations = [runtime_data[r]["invocations"] for r in runtimes]

        df_runtime = pd.DataFrame({
            "Runtime": runtimes,
            "Average Duration (s)": avg_durations,
            "Invocations": invocations
        })

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Invocations per Runtime")
            fig1 = px.bar(df_runtime, x="Runtime", y="Invocations", color="Runtime")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.subheader("Avg Duration per Runtime (s)")
            fig2 = px.bar(df_runtime, x="Runtime", y="Average Duration (s)", color="Runtime")
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Summary Table")
        st.dataframe(df_runtime, use_container_width=True)

    st.header("Individual Function Metrics")
    functions = get_functions()

    if functions:
        selected_function = st.selectbox("Select Function", list(functions.keys()))
        if selected_function:
            metrics = get_function_metrics(selected_function)
            if metrics:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Invocations", metrics.get("total_invocations", 0))
                with col2:
                    st.metric("Average Duration (seconds)", f"{metrics.get('average_duration') or 0.0:.4f}")
    else:
        st.info("No functions registered yet.")
import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../metrics.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
       CREATE TABLE IF NOT EXISTS metrics (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           function_name TEXT,
           runtime TEXT,
           duration FLOAT,
           cpu_percent FLOAT,
           memory_mb FLOAT,
           error TEXT,
           timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
       );
    """)
    conn.commit()
    conn.close()

def store_metrics(function_name, runtime, metrics):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO metrics (
           function_name,
           runtime,
           duration,
           cpu_percent,
           memory_mb,
           error
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        function_name,
        runtime,
        metrics.get("duration", 0),
        metrics.get("cpu_percent", 0),
        metrics.get("memory_mb", 0),
        metrics.get("error")
    ))
    conn.commit()
    conn.close()

def get_aggregated_metrics(function_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT AVG(duration), COUNT(*)
        FROM metrics
        WHERE function_name = ?
    """, (function_name,))
    result = c.fetchone()
    conn.close()
    return {
        "average_duration": result[0],
        "total_invocations": result[1]
    }
def get_runtime_metrics():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT runtime,
               AVG(duration),
               COUNT(*)
        FROM metrics
        GROUP BY runtime
    """)

    rows = c.fetchall()

    conn.close()

    result = {}

    for runtime, avg_duration, count in rows:
        result[runtime] = {
            "average_duration": round(avg_duration, 4),
            "invocations": count
        }

    return result
 
    

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Lambda Function Manager v1.0")
st.sidebar.caption(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
