"""
Admin Dashboard - Monitoring and Analytics Interface
Provides insights into task history, node health, and system metrics
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="AI Orchestrator - Admin Dashboard",
    page_icon="📊",
    layout="wide"
)

# Orchestrator API endpoint
ORCHESTRATOR_URL = "http://localhost:8000/api"

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #007bff;
    }
    .health-healthy {
        color: #28a745;
        font-weight: bold;
    }
    .health-warning {
        color: #ffc107;
        font-weight: bold;
    }
    .health-critical {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("📊 AI Workload Orchestrator - Admin Dashboard")
st.markdown("### Real-Time Monitoring & Analytics")
st.markdown("---")

# Auto-refresh toggle
col1, col2 = st.columns([3, 1])
with col2:
    auto_refresh = st.checkbox("Auto-refresh (10s)", value=False)
    if st.button("🔄 Refresh Now"):
        st.rerun()

if auto_refresh:
    time.sleep(10)
    st.rerun()

# Fetch data from orchestrator
@st.cache_data(ttl=10)
def fetch_task_history(limit=100):
    """Fetch task history from orchestrator"""
    try:
        response = requests.get(f"{ORCHESTRATOR_URL}/task-history?limit={limit}", timeout=5)
        if response.status_code == 200:
            return response.json()['tasks']
        return []
    except:
        return []

@st.cache_data(ttl=5)
def fetch_node_status():
    """Fetch current node status"""
    try:
        response = requests.get(f"{ORCHESTRATOR_URL}/node-status", timeout=5)
        if response.status_code == 200:
            return response.json()['nodes']
        return {}
    except:
        return {}

@st.cache_data(ttl=10)
def fetch_statistics():
    """Fetch aggregated statistics"""
    try:
        response = requests.get(f"{ORCHESTRATOR_URL}/statistics", timeout=5)
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}

# Fetch data
task_history = fetch_task_history(limit=200)
node_status = fetch_node_status()
statistics = fetch_statistics()

# ===== SECTION 1: Key Metrics =====
st.markdown("## 📈 Key Metrics")

if statistics:
    overall = statistics.get('overall', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Tasks Processed",
            overall.get('total_tasks', 0),
            delta=None
        )
    
    with col2:
        success_rate = overall.get('success_rate', 0) * 100
        st.metric(
            "Success Rate",
            f"{success_rate:.1f}%",
            delta=None
        )
    
    with col3:
        if task_history:
            avg_time = sum(t['execution_time'] for t in task_history) / len(task_history)
            st.metric("Avg Execution Time", f"{avg_time:.3f}s")
        else:
            st.metric("Avg Execution Time", "N/A")
    
    with col4:
        node_stats = statistics.get('node_statistics', [])
        total_cost = sum(n['total_cost'] for n in node_stats)
        st.metric("Total Cost", f"${total_cost:.2f}")

st.markdown("---")

# ===== SECTION 2: Node Health Panel =====
st.markdown("## 🖥️ Node Health Status")

if node_status:
    col1, col2, col3 = st.columns(3)
    
    for idx, (node_name, col) in enumerate(zip(['EDGE', 'CLOUD', 'GPU'], [col1, col2, col3])):
        status = node_status.get(node_name, {})
        load = status.get('load', 0)
        health = status.get('health', 'unknown')
        latency = status.get('latency', 0)
        cost = status.get('cost_per_task', 0)
        active = status.get('active_tasks', 0)
        
        with col:
            # Health indicator
            if health == 'healthy':
                health_color = 'green'
                health_emoji = '🟢'
            elif health == 'warning':
                health_color = 'orange'
                health_emoji = '🟡'
            else:
                health_color = 'red'
                health_emoji = '🔴'
            
            st.markdown(f"### {health_emoji} {node_name} Node")
            
            # Load gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=load,
                title={'text': "Load %"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': health_color},
                    'steps': [
                        {'range': [0, 60], 'color': "lightgray"},
                        {'range': [60, 80], 'color': "lightyellow"},
                        {'range': [80, 100], 'color': "lightcoral"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
            # Metrics
            st.metric("Latency", f"{latency:.0f}ms")
            st.metric("Cost/Task", f"${cost:.3f}")
            st.metric("Active Tasks", active)

else:
    st.warning("Unable to fetch node status")

st.markdown("---")

# ===== SECTION 3: Task Distribution =====
st.markdown("## 📊 Workload Distribution")

if task_history:
    col1, col2 = st.columns(2)
    
    with col1:
        # Tasks per node - Pie chart
        df = pd.DataFrame(task_history)
        node_counts = df['chosen_node'].value_counts()
        
        fig = px.pie(
            values=node_counts.values,
            names=node_counts.index,
            title="Tasks by Node",
            color=node_counts.index,
            color_discrete_map={'EDGE': '#28a745', 'CLOUD': '#007bff', 'GPU': '#dc3545'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Tasks by type
        type_counts = df['task_type'].value_counts()
        
        fig = px.bar(
            x=type_counts.index,
            y=type_counts.values,
            title="Tasks by Type",
            labels={'x': 'Task Type', 'y': 'Count'},
            color=type_counts.values,
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ===== SECTION 4: Cost & Performance Analysis =====
st.markdown("## 💰 Cost & Performance Analysis")

if task_history:
    col1, col2 = st.columns(2)
    
    with col1:
        # Cost by node
        cost_by_node = df.groupby('chosen_node')['cost'].sum().reset_index()
        
        fig = px.bar(
            cost_by_node,
            x='chosen_node',
            y='cost',
            title="Total Cost by Node",
            labels={'chosen_node': 'Node', 'cost': 'Total Cost ($)'},
            color='chosen_node',
            color_discrete_map={'EDGE': '#28a745', 'CLOUD': '#007bff', 'GPU': '#dc3545'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Execution time by node
        time_by_node = df.groupby('chosen_node')['execution_time'].mean().reset_index()
        
        fig = px.bar(
            time_by_node,
            x='chosen_node',
            y='execution_time',
            title="Average Execution Time by Node",
            labels={'chosen_node': 'Node', 'execution_time': 'Avg Time (s)'},
            color='chosen_node',
            color_discrete_map={'EDGE': '#28a745', 'CLOUD': '#007bff', 'GPU': '#dc3545'}
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ===== SECTION 5: Task History Table =====
st.markdown("## 📋 Task Execution History")

if task_history:
    # Convert to DataFrame
    df = pd.DataFrame(task_history)
    
    # Display options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_node = st.selectbox("Filter by Node", ["All"] + list(df['chosen_node'].unique()))
    
    with col2:
        filter_status = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    
    with col3:
        limit = st.slider("Show rows", 10, 100, 50)
    
    # Apply filters
    filtered_df = df.copy()
    
    if filter_node != "All":
        filtered_df = filtered_df[filtered_df['chosen_node'] == filter_node]
    
    if filter_status != "All":
        filtered_df = filtered_df[filtered_df['status'] == filter_status]
    
    # Display table
    st.dataframe(
        filtered_df[['task_type', 'chosen_node', 'priority', 'execution_time', 'cost', 'confidence', 'status', 'timestamp']].head(limit),
        use_container_width=True,
        hide_index=True
    )
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"task_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

else:
    st.info("No task history available. Submit tasks from the Demo UI to see data here.")

# Footer
st.markdown("---")
st.caption("AI Workload Orchestrator Admin Dashboard | Auto-updated every 10s when enabled")
