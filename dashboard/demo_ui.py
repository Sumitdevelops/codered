"""
Demo UI - Interactive Workload Submission Interface
Simulates real-world task triggers with button-based interactions
"""

import streamlit as st
import requests
import json
import time
from typing import Dict, Any

# Page configuration
st.set_page_config(
    page_title="AI Workload Orchestrator - Demo",
    page_icon="🚀",
    layout="wide"
)

# Orchestrator API endpoint
ORCHESTRATOR_URL = "http://localhost:8000/api"

# Custom CSS for better UI
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        height: 80px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 10px;
        margin: 5px 0;
    }
    .success-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 10px 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #007bff;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🚀 AI Workload Orchestrator")
st.markdown("### Interactive Demo - Real-Time Task Routing")
st.markdown("---")

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = []

def submit_task(task_type: str, priority: int, latency: int, requires_gpu: bool, description: str) -> None:
    """Submit task to orchestrator and display results"""
    
    with st.spinner(f"🔄 Routing {description}..."):
        try:
            # Prepare task payload
            payload = {
                "taskType": task_type,
                "priority": priority,
                "latency": latency,
                "requiresGPU": requires_gpu,
                "payload": {
                    "description": description,
                    "timestamp": time.time()
                },
                "cost_sensitivity": 10 - priority  # Inverse relationship
            }
            
            # Submit to orchestrator
            response = requests.post(
                f"{ORCHESTRATOR_URL}/submit-task",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Store result in session state
                st.session_state.results.insert(0, {
                    'description': description,
                    'result': result,
                    'timestamp': time.time()
                })
                
                # Display success
                st.success(f"✅ Task routed successfully!")
                
                # Display routing decision
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Chosen Node", result['chosen_node'])
                
                with col2:
                    st.metric("Confidence", f"{result['confidence']:.1%}")
                
                with col3:
                    st.metric("Execution Time", f"{result['execution_time']:.3f}s")
                
                with col4:
                    st.metric("Cost", f"${result['cost']:.4f}")
                
                # Display explanation
                st.info(f"**Decision Explanation:** {result['explanation']}")
                
            else:
                st.error(f"❌ Error: {response.status_code} - {response.text}")
        
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to orchestrator. Make sure all services are running.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


# Main UI - Task Buttons
st.markdown("## 🎯 Simulate Real-World Workloads")
st.markdown("Click buttons below to trigger different types of tasks:")

# Create two columns for buttons
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### ⚡ Real-Time Tasks")
    
    if st.button("🔍 Run Fraud Detection", use_container_width=True):
        submit_task(
            task_type="fraud_detection",
            priority=9,
            latency=10,
            requires_gpu=False,
            description="Real-time fraud detection on transaction"
        )
    
    if st.button("📡 Trigger Sensor Alert", use_container_width=True):
        submit_task(
            task_type="sensor_alert",
            priority=10,
            latency=10,
            requires_gpu=False,
            description="Critical sensor alert - temperature threshold exceeded"
        )
    
    if st.button("🖼️ Image Classification", use_container_width=True):
        submit_task(
            task_type="image_classification",
            priority=7,
            latency=6,
            requires_gpu=True,
            description="Classify uploaded images using CNN model"
        )

with col_right:
    st.markdown("### 📊 Batch Processing Tasks")
    
    if st.button("📈 Generate Daily Report", use_container_width=True):
        submit_task(
            task_type="daily_report",
            priority=3,
            latency=2,
            requires_gpu=False,
            description="Generate daily analytics report"
        )
    
    if st.button("🤖 ML Training Job", use_container_width=True):
        submit_task(
            task_type="ml_training",
            priority=5,
            latency=3,
            requires_gpu=True,
            description="Train deep learning model on large dataset"
        )
    
    if st.button("🔄 Data Processing Pipeline", use_container_width=True):
        submit_task(
            task_type="data_processing",
            priority=4,
            latency=3,
            requires_gpu=False,
            description="Process and transform large dataset"
        )

st.markdown("---")

# Recent Results Section
if st.session_state.results:
    st.markdown("## 📋 Recent Task Executions")
    
    for idx, item in enumerate(st.session_state.results[:5]):
        result = item['result']
        
        with st.expander(f"**{item['description']}** → {result['chosen_node']}", expanded=(idx == 0)):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Explanation:** {result['explanation']}")
                st.markdown(f"**Task ID:** `{result['task_id']}`")
                st.markdown(f"**Status:** {result['status'].upper()}")
            
            with col2:
                st.metric("Node", result['chosen_node'])
                st.metric("Time", f"{result['execution_time']:.3f}s")
                st.metric("Cost", f"${result['cost']:.4f}")
                st.metric("Confidence", f"{result['confidence']:.1%}")

    # Clear history button
    if st.button("🗑️ Clear History"):
        st.session_state.results = []
        st.rerun()

else:
    st.info("👆 Click any button above to submit a task and see routing decisions in real-time!")

# Sidebar - System Status
with st.sidebar:
    st.markdown("### 📊 System Status")
    
    if st.button("🔄 Refresh Status"):
        st.rerun()
    
    try:
        # Get node status
        status_response = requests.get(f"{ORCHESTRATOR_URL}/node-status", timeout=5)
        
        if status_response.status_code == 200:
            node_status = status_response.json()['nodes']
            
            for node_name in ['EDGE', 'CLOUD', 'GPU']:
                status = node_status.get(node_name, {})
                load = status.get('load', 0)
                health = status.get('health', 'unknown')
                
                # Color coding based on health
                if health == 'healthy':
                    color = '🟢'
                elif health == 'warning':
                    color = '🟡'
                else:
                    color = '🔴'
                
                st.markdown(f"{color} **{node_name}**")
                st.progress(load / 100)
                st.caption(f"Load: {load:.1f}% | Latency: {status.get('latency', 0):.0f}ms")
        
        else:
            st.warning("Cannot fetch node status")
    
    except:
        st.error("Orchestrator offline")
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.caption("This demo simulates real-world workload routing using ML-based decision making.")
