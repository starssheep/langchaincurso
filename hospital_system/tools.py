import random
from datetime import datetime, timedelta

def check_symptoms(symptoms_text: str):
    """Analisa sintomas e retorna uma avaliação inicial de triagem."""
    symptoms_db = {
        "febre": "Possível infecção ou inflamação. Recomenda-se repouso e hidratação.",
        "dor de cabeça": "Pode ser estresse, desidratação ou enxaqueca.",
        "tosse": "Avaliar se é seca ou com secreção. Pode ser resfriado ou alergia.",
        "dor no peito": "URGENTE: Procure uma unidade de emergência imediatamente.",
    }
    
    findings = []
    text_lower = symptoms_text.lower()
    for symptom, advice in symptoms_db.items():
        if symptom in text_lower:
            findings.append(f"- {symptom.capitalize()}: {advice}")
    
    if not findings:
        return "Sintomas não conclusivos para triagem automática. Por favor, fale com nosso enfermeiro."
    
    return "Avaliação de Triagem:\n" + "\n".join(findings)

def schedule_appointment(specialty: str, patient_name: str, date_str: str):
    """Agenda uma consulta para uma especialidade específica."""
    # Simulação de agendamento
    appointment_id = random.randint(1000, 9999)
    return f"Consulta de {specialty} agendada para {patient_name} em {date_str}. Protocolo: HOS-{appointment_id}."

def get_clinic_hours(department: str):
    """Retorna o horário de funcionamento de um departamento."""
    hours = {
        "Pediatria": "Segunda a Sexta, 08:00 - 18:00",
        "Cardiologia": "Segunda a Quinta, 09:00 - 17:00",
        "Clínica Geral": "24 Horas",
        "Ortopedia": "Segunda a Sexta, 08:00 - 20:00"
    }
    return hours.get(department, "Departamento não encontrado ou fechado para manutenção.")

# Dicionário de ferramentas
TOOLS = {
    "check_symptoms": check_symptoms,
    "schedule_appointment": schedule_appointment,
    "get_clinic_hours": get_clinic_hours
}
