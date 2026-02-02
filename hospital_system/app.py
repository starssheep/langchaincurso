import streamlit as st
import os
import sys

# Adiciona o diretório base ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hospital_system.agents import HospitalCareTeam
from langchain_core.messages import HumanMessage, AIMessage

# Configuração da página
st.set_page_config(
    page_title="CareFlow Hospital - Concierge Digital",
    page_icon="🏥",
    layout="wide"
)

# Estilização Médica
st.markdown("""
<style>
    .stApp {
        background-color: #f8fafc;
    }
    .main-header {
        color: #0f172a;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .chat-container {
        border-radius: 15px;
        padding: 20px;
        background: white;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Inicialização
if "hospital_team" not in st.session_state:
    st.session_state.hospital_team = HospitalCareTeam()

if "hospital_messages" not in st.session_state:
    st.session_state.hospital_messages = []

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3304/3304567.png", width=100)
    st.title("CareFlow Hospital")
    st.markdown("---")
    st.markdown("### 🏥 Equipe de Plantão")
    st.info("**Enfermeiro de Triagem**: Avaliação de sintomas e urgência.")
    st.success("**Médico Especialista**: Orientações e diagnósticos preliminares.")
    st.warning("**Secretaria**: Agendamentos e informações administrativas.")
    
    if st.button("Nova Consulta"):
        st.session_state.hospital_messages = []
        st.rerun()

# Interface Principal
st.markdown("<h1 class='main-header'>🏥 Pronto Atendimento Digital</h1>", unsafe_allow_html=True)
st.caption("Bem-vindo ao CareFlow Hospital. Descreva seus sintomas ou solicite um agendamento.")

# Mostrar chat
for msg in st.session_state.hospital_messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        agent_name = msg.additional_kwargs.get("agent_name", "CareFlow AI")
        icon = msg.additional_kwargs.get("icon", "🏥")
        with st.chat_message("assistant", avatar=icon):
            st.markdown(f"**{agent_name}**")
            st.markdown(msg.content)

# Input
if prompt := st.chat_input("Como você está se sentindo hoje?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.spinner("Nossa equipe médica está analisando seu caso..."):
        history = st.session_state.hospital_messages
        agent_name, response, icon = st.session_state.hospital_team.run(prompt, history)
        
        with st.chat_message("assistant", avatar=icon):
            st.markdown(f"**{agent_name}**")
            st.markdown(response)
        
        st.session_state.hospital_messages.append(HumanMessage(content=prompt))
        st.session_state.hospital_messages.append(
            AIMessage(
                content=response,
                additional_kwargs={"agent_name": agent_name, "icon": icon}
            )
        )
