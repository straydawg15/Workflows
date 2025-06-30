import streamlit as st
import requests
import json
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="Cat Facts via n8n",
    page_icon="🐱",
    layout="wide"
)

# Title and description
st.title("🐱 Cat Facts Generator")
st.markdown("*Powered by n8n workflow automation*")

# Sidebar for configuration
st.sidebar.header("⚙️ Configuration")

# n8n webhook URL input
webhook_url = st.sidebar.text_input(
    "n8n Webhook URL", 
    placeholder="https://your-n8n-instance.com/webhook/your-webhook-id",
    help="Enter your n8n webhook URL to trigger the workflow"
)

# Add some styling
st.markdown("""
<style>
.cat-fact-box {
    background-color: #f0f8ff;
    padding: 20px;
    border-radius: 10px;
    border-left: 5px solid #4CAF50;
    margin: 10px 0;
}
.error-box {
    background-color: #ffebee;
    padding: 20px;
    border-radius: 10px;
    border-left: 5px solid #f44336;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Get a Random Cat Fact")
    
    # Button to trigger the workflow
    if st.button("🎯 Get Cat Fact", type="primary", use_container_width=True):
        if not webhook_url:
            st.error("Please enter your n8n webhook URL in the sidebar first!")
        else:
            with st.spinner("Fetching cat fact from n8n workflow..."):
                try:
                    # Trigger the n8n workflow
                    response = requests.post(
                        webhook_url,
                        json={},
                        headers={'Content-Type': 'application/json'},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        # Parse the response
                        data = response.json()
                        
                        # Display the cat fact
                        st.markdown('<div class="cat-fact-box">', unsafe_allow_html=True)
                        st.markdown("### 🐾 Cat Fact")
                        
                        # Handle different possible response structures
                        if isinstance(data, list) and len(data) > 0:
                            fact_data = data[0]
                        else:
                            fact_data = data
                            
                        # Extract the cat fact
                        cat_fact = fact_data.get('cat_fact', fact_data.get('fact', 'No fact found'))
                        fact_length = fact_data.get('fact_length', fact_data.get('length', len(cat_fact)))
                        timestamp = fact_data.get('timestamp', datetime.now().isoformat())
                        
                        st.markdown(f"*\"{cat_fact}\"*")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Additional info
                        col_info1, col_info2 = st.columns(2)
                        with col_info1:
                            st.metric("Fact Length", f"{fact_length} characters")
                        with col_info2:
                            st.metric("Retrieved At", timestamp.split('T')[0] if 'T' in str(timestamp) else str(timestamp))
                        
                        # Store in session state for history
                        if 'cat_facts_history' not in st.session_state:
                            st.session_state.cat_facts_history = []
                        
                        st.session_state.cat_facts_history.append({
                            'fact': cat_fact,
                            'length': fact_length,
                            'timestamp': timestamp
                        })
                        
                    else:
                        st.markdown('<div class="error-box">', unsafe_allow_html=True)
                        st.error(f"Error: Received status code {response.status_code}")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                except requests.exceptions.Timeout:
                    st.error("Request timed out. Please check your n8n webhook URL and try again.")
                except requests.exceptions.ConnectionError:
                    st.error("Connection error. Please check your n8n webhook URL and internet connection.")
                except json.JSONDecodeError:
                    st.error("Invalid JSON response from n8n workflow.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

with col2:
    st.header("📊 Stats")
    
    if 'cat_facts_history' in st.session_state and st.session_state.cat_facts_history:
        total_facts = len(st.session_state.cat_facts_history)
        avg_length = sum([fact['length'] for fact in st.session_state.cat_facts_history]) / total_facts
        
        st.metric("Total Facts Retrieved", total_facts)
        st.metric("Average Length", f"{avg_length:.1f} chars")
    else:
        st.info("No facts retrieved yet!")

# History section
if 'cat_facts_history' in st.session_state and st.session_state.cat_facts_history:
    st.header("📚 Fact History")
    
    # Option to clear history
    if st.button("🗑️ Clear History"):
        st.session_state.cat_facts_history = []
        st.rerun()
    
    # Display history in reverse order (newest first)
    for i, fact_data in enumerate(reversed(st.session_state.cat_facts_history)):
        with st.expander(f"Fact #{len(st.session_state.cat_facts_history) - i} - {fact_data['length']} chars"):
            st.write(fact_data['fact'])
            st.caption(f"Retrieved: {fact_data['timestamp']}")

# Instructions section
st.header("🔧 Setup Instructions")

with st.expander("How to set up your n8n webhook"):
    st.markdown("""
    1. **In your n8n workflow:**
       - Replace the "Manual Trigger" with a "Webhook" trigger node
       - Set the webhook method to "POST"
       - Copy the webhook URL from the node
    
    2. **Update your workflow:**
       - Make sure your workflow returns the cat fact data
       - The response should include fields like `cat_fact`, `fact_length`, etc.
    
    3. **In this Streamlit app:**
       - Paste your webhook URL in the sidebar
       - Click "Get Cat Fact" to test the connection
    
    **Example n8n Webhook trigger settings:**
    - HTTP Method: POST
    - Path: Leave blank (auto-generated)
    - Authentication: None
    - Response Mode: Using 'Respond to Webhook' Node (recommended)
    """)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and n8n")