"""
Streamlit dashboard for AI-Driven Rostering Agent.
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="AI Rostering Agent",
    page_icon="📅",
    layout="wide"
)

# API endpoint
API_BASE_URL = "http://localhost:8000"

# Title
st.title("🤖 AI-Driven Multi-Country Rostering Agent")
st.markdown("Optimize shift schedules with labour law compliance across multiple countries")

# Sidebar
st.sidebar.header("Configuration")

# Check API health
try:
    health_response = requests.get(f"{API_BASE_URL}/health", timeout=2)
    if health_response.status_code == 200:
        st.sidebar.success("✅ API Connected")
    else:
        st.sidebar.error("❌ API Error")
except Exception as e:
    st.sidebar.error(f"❌ API Offline: {e}")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Optimize Schedule", "✅ Validate Schedule", "📊 Analytics", "ℹ️ About"])

# Tab 1: Optimize Schedule
with tab1:
    st.header("Shift Schedule Optimization")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Workers")
        
        # Load sample data button
        if st.button("Load Sample Data"):
            try:
                response = requests.get(f"{API_BASE_URL}/sample-data")
                if response.status_code == 200:
                    sample_data = response.json()
                    st.session_state['workers'] = sample_data['workers']
                    st.session_state['requirements'] = sample_data['requirements']['demand']
                    st.success("Sample data loaded!")
            except Exception as e:
                st.error(f"Error loading sample data: {e}")
        
        # Number of workers
        num_workers = st.number_input("Number of Workers", min_value=1, max_value=20, value=5)
        
        # Worker input
        if 'workers' not in st.session_state:
            st.session_state['workers'] = []
        
        workers = []
        for i in range(num_workers):
            with st.expander(f"Worker {i+1}", expanded=(i < 2)):
                name = st.text_input(f"Name", value=f"Worker {i+1}", key=f"name_{i}")
                country = st.selectbox(
                    f"Country",
                    options=["US", "UK", "SG", "DE", "JP"],
                    key=f"country_{i}"
                )
                skills = st.multiselect(
                    f"Skills",
                    options=["morning", "afternoon", "night"],
                    default=["morning", "afternoon"],
                    key=f"skills_{i}"
                )
                max_shifts = st.slider(
                    f"Max Shifts/Week",
                    min_value=1,
                    max_value=7,
                    value=5,
                    key=f"max_shifts_{i}"
                )
                
                workers.append({
                    "id": i + 1,
                    "name": name,
                    "country": country,
                    "skills": skills,
                    "max_shifts_per_week": max_shifts,
                    "unavailable_days": []
                })
    
    with col2:
        st.subheader("Schedule Parameters")
        
        num_days = st.slider("Number of Days", min_value=7, max_value=30, value=14)
        
        st.subheader("Shift Requirements (per day)")
        morning_req = st.number_input("Morning Shift", min_value=0, max_value=10, value=2)
        afternoon_req = st.number_input("Afternoon Shift", min_value=0, max_value=10, value=2)
        night_req = st.number_input("Night Shift", min_value=0, max_value=10, value=1)
        
        shift_requirements = {
            "morning": morning_req,
            "afternoon": afternoon_req,
            "night": night_req
        }
        
        track_experiment = st.checkbox("Track with MLflow", value=True)
        run_name = st.text_input("Run Name (optional)", value="")
    
    # Optimize button
    if st.button("🚀 Optimize Schedule", type="primary"):
        if not workers:
            st.error("Please add at least one worker")
        else:
            with st.spinner("Optimizing schedule..."):
                try:
                    payload = {
                        "workers": workers,
                        "num_days": num_days,
                        "shift_requirements": shift_requirements,
                        "track_experiment": track_experiment,
                        "run_name": run_name if run_name else None
                    }
                    
                    response = requests.post(
                        f"{API_BASE_URL}/optimize",
                        json=payload,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state['optimization_result'] = result
                        
                        st.success(f"✅ Optimization {result['status']}!")
                        
                        if result.get('mlflow_run_id'):
                            st.info(f"📊 MLflow Run ID: {result['mlflow_run_id']}")
                        
                        # Display metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Status", result['status'].upper())
                        with col2:
                            st.metric("Solve Time", f"{result.get('solve_time', 0):.2f}s")
                        with col3:
                            st.metric("Objective Value", f"{result.get('objective_value', 0):.2f}")
                        
                        # Display schedule
                        if result.get('schedule'):
                            st.subheader("Generated Schedule")
                            schedule_data = []
                            for day in result['schedule']:
                                for shift_type, assignments in day['shifts'].items():
                                    for assignment in assignments:
                                        schedule_data.append({
                                            'Day': day['day'] + 1,
                                            'Shift': shift_type.capitalize(),
                                            'Worker': assignment['worker_name'],
                                            'Country': assignment['country']
                                        })
                            
                            if schedule_data:
                                df = pd.DataFrame(schedule_data)
                                st.dataframe(df, use_container_width=True)
                                
                                # Visualization
                                st.subheader("Schedule Visualization")
                                fig = px.scatter(
                                    df,
                                    x='Day',
                                    y='Worker',
                                    color='Shift',
                                    title='Shift Assignments',
                                    height=400
                                )
                                st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error(f"Error: {response.text}")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Tab 2: Validate Schedule
with tab2:
    st.header("Schedule Validation")
    
    st.markdown("Upload or paste a schedule to validate against labour law constraints.")
    
    schedule_input = st.text_area(
        "Schedule JSON",
        height=200,
        placeholder='[{"day": 0, "shifts": {"morning": [{"worker_id": 1, "worker_name": "John", "country": "US"}]}}]'
    )
    
    workers_input = st.text_area(
        "Workers JSON",
        height=150,
        placeholder='[{"id": 1, "name": "John", "country": "US", "skills": ["morning"], "max_shifts_per_week": 5, "unavailable_days": []}]'
    )
    
    if st.button("✅ Validate", type="primary"):
        try:
            schedule = json.loads(schedule_input)
            workers = json.loads(workers_input)
            
            with st.spinner("Validating schedule..."):
                response = requests.post(
                    f"{API_BASE_URL}/validate",
                    json={"schedule": schedule, "workers": workers},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result['valid']:
                        st.success("✅ Schedule is valid and compliant!")
                    else:
                        st.error(f"❌ Found {result['total_violations']} violation(s)")
                        
                        if result['violations']:
                            st.subheader("Violations")
                            violations_df = pd.DataFrame(result['violations'])
                            st.dataframe(violations_df, use_container_width=True)
                else:
                    st.error(f"Error: {response.text}")
        
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON: {e}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Tab 3: Analytics
with tab3:
    st.header("Schedule Analytics")
    
    if 'optimization_result' in st.session_state:
        result = st.session_state['optimization_result']
        
        if result.get('schedule'):
            # Create analytics
            schedule_data = []
            for day in result['schedule']:
                for shift_type, assignments in day['shifts'].items():
                    for assignment in assignments:
                        schedule_data.append({
                            'Day': day['day'] + 1,
                            'Shift': shift_type.capitalize(),
                            'Worker': assignment['worker_name'],
                            'Country': assignment['country']
                        })
            
            df = pd.DataFrame(schedule_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Shifts by Worker")
                worker_counts = df['Worker'].value_counts()
                fig = px.bar(
                    x=worker_counts.index,
                    y=worker_counts.values,
                    labels={'x': 'Worker', 'y': 'Number of Shifts'},
                    title='Total Shifts per Worker'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Shifts by Type")
                shift_counts = df['Shift'].value_counts()
                fig = px.pie(
                    values=shift_counts.values,
                    names=shift_counts.index,
                    title='Distribution of Shift Types'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Shifts by Country")
            country_counts = df['Country'].value_counts()
            fig = px.bar(
                x=country_counts.index,
                y=country_counts.values,
                labels={'x': 'Country', 'y': 'Number of Shifts'},
                title='Shifts by Country'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Heatmap
            st.subheader("Schedule Heatmap")
            pivot = df.pivot_table(
                index='Worker',
                columns='Day',
                values='Shift',
                aggfunc='first'
            )
            
            # Convert to numeric for heatmap
            shift_map = {'Morning': 1, 'Afternoon': 2, 'Night': 3}
            pivot_numeric = pivot.applymap(lambda x: shift_map.get(x, 0) if pd.notna(x) else 0)
            
            fig = go.Figure(data=go.Heatmap(
                z=pivot_numeric.values,
                x=pivot_numeric.columns,
                y=pivot_numeric.index,
                colorscale=[[0, 'white'], [0.33, 'lightblue'], [0.66, 'orange'], [1, 'darkblue']],
                showscale=False
            ))
            fig.update_layout(
                title='Worker Schedule Heatmap',
                xaxis_title='Day',
                yaxis_title='Worker',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run an optimization first to see analytics")

# Tab 4: About
with tab4:
    st.header("About AI-Driven Rostering Agent")
    
    st.markdown("""
    ### Features
    
    - **Multi-Country Support**: Handles labour law compliance for US, UK, Singapore, Germany, and Japan
    - **Constraint Programming**: Uses OR-Tools CP-SAT solver for optimal shift assignments
    - **RAG-based Compliance**: LangChain + Chroma for intelligent labour law checking
    - **Experiment Tracking**: MLflow integration for tracking optimization runs
    - **REST API**: FastAPI endpoints for programmatic access
    - **Interactive Dashboard**: Real-time optimization and validation
    
    ### Architecture
    
    ```
    ├── Optimization Layer (OR-Tools CP-SAT)
    ├── Compliance Layer (LangChain + Chroma RAG)
    ├── API Layer (FastAPI)
    ├── Tracking Layer (MLflow)
    └── UI Layer (Streamlit)
    ```
    
    ### Constraints Handled
    
    - Maximum working hours per week
    - Maximum consecutive working days
    - Minimum rest periods between shifts
    - Worker skills and availability
    - Shift demand requirements
    - Country-specific labour laws
    
    ### Technology Stack
    
    - **Optimization**: OR-Tools CP-SAT
    - **API**: FastAPI, Uvicorn
    - **RAG**: LangChain, Chroma, OpenAI
    - **Dashboard**: Streamlit, Plotly
    - **Tracking**: MLflow
    - **Python**: 3.8+
    """)
    
    st.subheader("API Endpoints")
    
    endpoints = [
        {"Method": "POST", "Path": "/optimize", "Description": "Optimize shift schedule"},
        {"Method": "POST", "Path": "/validate", "Description": "Validate schedule"},
        {"Method": "GET", "Path": "/labour-laws/{country}", "Description": "Query labour laws"},
        {"Method": "GET", "Path": "/countries", "Description": "List available countries"},
        {"Method": "GET", "Path": "/sample-data", "Description": "Get sample data"},
        {"Method": "GET", "Path": "/health", "Description": "Health check"},
    ]
    
    st.table(pd.DataFrame(endpoints))
    
    st.subheader("Countries Supported")
    
    try:
        response = requests.get(f"{API_BASE_URL}/countries")
        if response.status_code == 200:
            countries = response.json()['countries']
            st.json(countries)
    except:
        st.info("Start the API to see country configurations")
