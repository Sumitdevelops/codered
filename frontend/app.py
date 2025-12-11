import streamlit as st
import pandas as pd
import plotly.express as px
import time
from api_client import get_nodes, get_workloads, submit_workload

st.set_page_config(page_title="AI Orchestrator", layout="wide")

st.title("AI-Powered Workload Orchestrator")

# Sidebar
page = st.sidebar.selectbox("Navigation", ["Dashboard", "Submit Task"])

if page == "Dashboard":
    st.header("Cluster Overview")
    
    # Auto-refresh loop placeholder (Streamlit reruns on interaction, but we can use st.empty for loops)
    placeholder = st.empty()
    
    # For prototype, just load once or add a refresh button
    if st.button("Refresh Metrics"):
        st.rerun()

    nodes = get_nodes()
    if not nodes:
        st.error("Could not connect to Backend API. Is it running?")
    else:
        # Metrics Overview
        cols = st.columns(len(nodes))
        for i, node in enumerate(nodes):
            with cols[i]:
                st.metric(label=node['name'], value=f"{node['status']}", delta=f"{node['metrics']['cpu_usage']:.1f}% CPU")
                st.caption(f"Type: {node['type']}")
                st.progress(node['metrics']['cpu_usage'] / 100)
        
        # Detailed Dataframe
        st.subheader("Node Details")
        node_data = []
        for n in nodes:
            m = n['metrics']
            node_data.append({
                "Name": n['name'],
                "Type": n['type'],
                "Status": n['status'],
                "CPU (%)": m['cpu_usage'],
                "RAM (%)": m['ram_usage'],
                "Latency (ms)": m['latency_ms'],
                "Cost ($/hr)": m['cost_per_hour']
            })
        df_nodes = pd.DataFrame(node_data)
        st.dataframe(df_nodes)

        # Charts
        st.subheader("Real-time Analytics")
        c1, c2 = st.columns(2)
        with c1:
            fig_cpu = px.bar(df_nodes, x="Name", y="CPU (%)", color="Type", title="CPU Usage by Node")
            st.plotly_chart(fig_cpu, use_container_width=True)
        with c2:
            fig_lat = px.scatter(df_nodes, x="Cost ($/hr)", y="Latency (ms)", size="CPU (%)", color="Type", title="Cost vs Latency vs Load")
            st.plotly_chart(fig_lat, use_container_width=True)

    st.divider()
    st.subheader("Recent Workloads")
    workloads = get_workloads()
    if workloads:
        df_work = pd.DataFrame(workloads)
        st.dataframe(df_work[['name', 'priority', 'status', 'assigned_node_id', 'submitted_at']])
    else:
        st.info("No workloads submitted yet.")

elif page == "Submit Task":
    st.header("Submit New Workload")
    
    with st.form("workload_form"):
        name = st.text_input("Task Name", "Data-Process-Job-01")
        priority = st.selectbox("Priority", ["low", "medium", "high", "critical"])
        c1, c2 = st.columns(2)
        with c1:
            cpu = st.slider("Required CPU", 1, 32, 4)
            ram = st.slider("Required RAM (GB)", 1, 128, 8)
        with c2:
            latency = st.number_input("Max Latency (ms) (0 for none)", 0, 1000, 100)
            gpu = st.checkbox("Requires GPU")
            
        submitted = st.form_submit_button("Submit Workload")
        
        if submitted:
            result = submit_workload(name, priority, cpu, ram, gpu, latency if latency > 0 else None)
            if "error" in result:
                st.error(f"Submission failed: {result['error']}")
            else:
                st.success(f"Workload submitted! Assigned to: {result.get('assigned_node_id', 'Pending')}")
                st.json(result)
