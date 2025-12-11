import streamlit as st
import pandas as pd
import plotly.express as px
import time
from api_client import get_nodes, get_workloads, submit_workload, login_user, signup_user

st.set_page_config(page_title="AI Orchestrator", layout="wide")

# (Global title removed to avoid duplication on login screen)

# --- CUSTOM CSS: Black & White + Typewriter (No Box) ---
st.markdown("""
<style>
    /* B&W Theme Variables */
    :root {
        --primary-color: #000000;
        --secondary-color: #ffffff;
        --accent-color: #333333;
    }

    /* Typewriter Animation */
    @keyframes typing {
        from { width: 0 }
        to { width: 100% }
    }
    @keyframes blink-caret {
        from, to { border-color: transparent }
        50% { border-color: white; }
    }
    
    .typewriter-container {
        display: flex;
        justify-content: center;
        margin-bottom: 30px;
    }

    /* ensure the text fits in the container */
    .typewriter h2 {
        overflow: hidden;
        border-right: .15em solid white; 
        white-space: nowrap;
        margin: 0 auto;
        letter-spacing: .15em; 
        color: white;
        font-family: 'Courier New', Courier, monospace; /* Monospace for classic terminal look */
        animation: 
            typing 3.5s steps(30, end),
            blink-caret .75s step-end infinite;
        max-width: fit-content;
    }
    
    /* Login Form Clean Styling (No Box) */
    .stTextInput input {
        background-color: #000 !important;
        color: #fff !important;
        border: 1px solid #333 !important;
        border-radius: 5px !important;
    }
    .stTextInput input:focus {
        border-color: #fff !important;
    }
    
    .stButton button {
        background-color: #fff !important;
        color: #000 !important;
        font-weight: bold !important;
        border-radius: 5px !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }
    .stButton button:hover {
        background-color: #ddd !important;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# Session Management
if 'token' not in st.session_state:
    # Try to get from URL params
    params = st.query_params
    token_param = params.get("token", None)
    if token_param:
        st.session_state['token'] = token_param
        # Ideally we should validate the token against the backend here or fetch user info
        # For prototype, we'll assume it's valid or let the next API call fail if expired
        st.session_state['username'] = "User" # Placeholder until we fetch profile or decode token
    else:
        st.session_state['token'] = None

if 'username' not in st.session_state:
    st.session_state['username'] = None

# --- AUTHENTICATION FLOW ---
if not st.session_state['token']:
    # Centered Layout
    c1, c2, c3 = st.columns([1, 1.2, 1]) 
    
    with c2:
        # Typewriter text replacement
        st.markdown("""
            <div class="typewriter-container">
                <div class="typewriter">
                    <h2>AI Orchestrator</h2>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Container WITHOUT border for a clean look
        with st.container(border=False):
            # No inner div class .login-card
            
            auth_mode = st.radio("Access Mode", ["Login", "Create Account"], horizontal=True, label_visibility="collapsed")
            st.divider()
            
            if auth_mode == "Login":
                st.subheader("Access Terminal")
                username = st.text_input("Username", key="login_user")
                password = st.text_input("Password", type="password", key="login_pass")
                st.write("")
                if st.button("AUTHENTICATE", type="primary", use_container_width=True):
                    with st.spinner("Verifying Credentials..."):
                        token_data = login_user(username, password)
                        if token_data and "access_token" in token_data:
                            token = token_data['access_token']
                            st.session_state['token'] = token
                            st.session_state['username'] = username
                            st.query_params["token"] = token 
                            st.rerun()
                        else:
                            err_msg = token_data.get('error', 'Unknown error') if token_data else "Unknown error"
                            st.error(f"Access Denied: {err_msg}")

            else: # Create Account
                st.subheader("New Uplink")
                new_user = st.text_input("Assign Identity", key="signup_user")
                new_pass = st.text_input("Set Passkey", type="password", key="signup_pass")
                st.write("")
                if st.button("INITIALIZE", type="primary", use_container_width=True):
                    with st.spinner("Registering Uplink..."):
                        token_data = signup_user(new_user, new_pass)
                        if token_data and "access_token" in token_data:
                            token = token_data['access_token']
                            st.session_state['token'] = token
                            st.session_state['username'] = new_user
                            st.query_params["token"] = token 
                            st.balloons()
                            time.sleep(1) 
                            st.rerun()
                        else:
                            err_msg = token_data.get('error', 'Unknown error') if token_data else "Unknown error"
                            st.error(f"Initialization Failed: {err_msg}")

else:
    # --- LOGGED IN DASHBOARD ---
    st.title("AI-Powered Workload Orchestrator")
    
    with st.sidebar:
        st.write(f"User: **{st.session_state['username']}**")
        if st.button("Logout"):
            st.session_state['token'] = None
            st.session_state['username'] = None
            st.query_params.clear() # Clear URL params
            st.rerun()
        
        page = st.selectbox("Navigation", ["Dashboard", "Submit Task"])

    if page == "Dashboard":
        st.header("Cluster Overview")
        
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
                    st.metric(label=node['name'], value=f"{node['status']}", delta=f"{node['cpu_usage']:.1f}% CPU")
                    st.caption(f"Type: {node['type']}")
                    st.progress(node['cpu_usage'] / 100)
            
            # Detailed Dataframe
            st.subheader("Node Details")
            node_data = []
            for n in nodes:
                node_data.append({
                    "Name": n['name'],
                    "Type": n['type'],
                    "Status": n['status'],
                    "CPU (%)": n['cpu_usage'],
                    "RAM (%)": n['ram_usage'],
                    "Latency (ms)": n['latency_ms'],
                    "Cost ($/hr)": n['cost_per_hour']
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
        st.divider()
        
        # Pass Token to get_workloads
        workloads = get_workloads(st.session_state['token'])
        
        if workloads:
            df_all = pd.DataFrame(workloads)
            
            # Split into Active and Completed
            df_active = df_all[df_all['status'] != 'completed']
            df_completed = df_all[df_all['status'] == 'completed']

            # --- Active Workloads ---
            st.subheader("Active Workloads")
            if not df_active.empty:
                st.dataframe(
                    df_active[['name', 'priority', 'status', 'progress', 'assigned_node_id', 'submitted_at']],
                    column_config={
                        "progress": st.column_config.ProgressColumn(
                            "Progress",
                            help="Task Completion Status",
                            format="%d%%",
                            min_value=0,
                            max_value=100,
                        ),
                        "submitted_at": st.column_config.DatetimeColumn(
                            "Submitted At",
                            format="D MMM YYYY, h:mm a"
                        )
                    },
                    hide_index=True
                )
            else:
                st.info("No active workloads.")

            # --- Completed Workloads ---
            st.subheader("Completed History")
            if not df_completed.empty:
                st.dataframe(
                    df_completed[['name', 'priority', 'status', 'assigned_node_id', 'submitted_at']],
                    column_config={
                        "submitted_at": st.column_config.DatetimeColumn(
                            "Submitted At",
                            format="D MMM YYYY, h:mm a"
                        )
                    },
                    hide_index=True
                )
            else:
                st.caption("No completed tasks yet.")

        else:
            st.info("No workloads found (or you haven't submitted any).")

    elif page == "Submit Task":
        st.header("Submit New Workload")
        
        with st.form("workload_form"):
            default_name = f"Job-{int(time.time())}"
            name = st.text_input("Task Name", default_name)
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
                # Pass Token to submit_workload
                result = submit_workload(st.session_state['token'], name, priority, cpu, ram, gpu, latency if latency > 0 else None)
                if "error" in result:
                    st.error(f"Submission failed: {result['error']}")
                else:
                    st.success(f"Workload submitted! Assigned to: {result.get('assigned_node_id', 'Pending')}")
                    st.json(result)
