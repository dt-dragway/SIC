from app.services.auto_execution import get_auto_execution_service

auto = get_auto_execution_service()
print("PROPIEDAD RUNNING:", auto.running)
print("STATUS COMPLETO:", auto.get_automation_status())

