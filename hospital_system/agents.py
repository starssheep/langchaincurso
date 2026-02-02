import os
import functools
import operator
from typing import Annotated, Sequence, TypedDict, Union, Literal

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Carrega chaves
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts/.env"))

# 1. Definição das Ferramentas (Wrapper para LangChain)
import hospital_system.tools as hospital_tools

@tool
def check_symptoms(symptoms_text: str):
    """Analisa sintomas e retorna uma avaliação inicial de triagem. Use isso para entender a gravidade."""
    return hospital_tools.check_symptoms(symptoms_text)

@tool
def schedule_appointment(specialty: str, patient_name: str, date_str: str):
    """Agenda uma consulta médica. Peça o nome do paciente e a data desejada."""
    return hospital_tools.schedule_appointment(specialty, patient_name, date_str)

@tool
def get_clinic_hours(department: str):
    """Fornece os horários de funcionamento de cada departamento (Pediatria, Cardiologia, Clínica Geral, Ortopedia)."""
    return hospital_tools.get_clinic_hours(department)

# 2. Estado
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str

# 3. Helper para criar agentes
def create_agent(llm: ChatGoogleGenerativeAI, tools: list, system_prompt: str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    return prompt | llm.bind_tools(tools)

# 4. Instância do LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# Agentes Especialistas
triage_agent = create_agent(
    llm, [check_symptoms],
    "Você é o Enfermeiro de Triagem do CareFlow. Ouça os sintomas do paciente e use a ferramenta de triagem."
)

medical_agent = create_agent(
    llm, [check_symptoms],
    "Você é o Médico Especialista do CareFlow. Explique as condições de saúde de forma técnica mas acolhedora."
)

admin_agent = create_agent(
    llm, [schedule_appointment, get_clinic_hours],
    "Você é o Secretário do CareFlow. Ajude com agendamentos e horários de funcionamento."
)

# 5. Supervisor (Diretor Clínico)
members = ["Triage", "Medical", "Admin"]
system_prompt = (
    "Você é o Diretor Clínico do CareFlow Hospital. Sua função é encaminhar o paciente para o profissional correto."
    " Se for sintomas iniciais, envie para Triage."
    " Se for uma dúvida médica profunda, envie para Medical."
    " Se for agendamento ou horários, envie para Admin."
    " Se a solicitação foi resolvida, responda FINISH."
)

class Router(BaseModel):
    """Encaminhamento do paciente."""
    next: Literal["FINISH", "Triage", "Medical", "Admin"] = Field(
        description="O próximo profissional a atender ou FINISH."
    )

def supervisor_agent(state):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "Quem deve atender o paciente agora? (FINISH, Triage, Medical, Admin)"),
    ])
    chain = prompt | llm.with_structured_output(Router)
    result = chain.invoke(state)
    return {"next": result.next if hasattr(result, 'next') else "FINISH"}

# 6. Classe de Gerenciamento para o Streamlit
class HospitalCareTeam:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        self.agents = {
            "Triage": {"agent": triage_agent, "icon": "🏥"},
            "Medical": {"agent": medical_agent, "icon": "🩺"},
            "Admin": {"agent": admin_agent, "icon": "📅"}
        }
    
    def run(self, user_input, history=[]):
        try:
            state = {"messages": history + [HumanMessage(content=user_input)]}
            route = supervisor_agent(state)
            next_agent = route["next"]
            
            if next_agent == "FINISH" or next_agent not in self.agents:
                resp = self.llm.invoke(state["messages"])
                return "Diretor Clínico", resp.content, "👨‍⚕️"
            
            agent_data = self.agents[next_agent]
            tools_list = [check_symptoms, schedule_appointment, get_clinic_hours]
            llm_with_tools = self.llm.bind_tools(tools_list)
            
            resp = llm_with_tools.invoke(state["messages"])
            
            if hasattr(resp, 'tool_calls') and resp.tool_calls:
                for tool_call in resp.tool_calls:
                    t_name = tool_call['name']
                    t_args = tool_call['args']
                    if t_name in hospital_tools.TOOLS:
                        f_resp = hospital_tools.TOOLS[t_name](**t_args)
                        final_resp = self.llm.invoke(state["messages"] + [resp, HumanMessage(content=f"Resultado da ferramenta {t_name}: {f_resp}. Por favor, responda ao paciente.")])
                        return next_agent, final_resp.content, agent_data["icon"]
            
            return next_agent, resp.content, agent_data["icon"]
        except Exception as e:
            return "Erro", f"Ocorreu um erro no sistema hospitalar: {e}", "⚠️"
