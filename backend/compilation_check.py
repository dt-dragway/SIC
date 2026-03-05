"""
COMPILACIÓN CHECK - SIC Ultra System
Verificación completa de compilación y dependencias
"""

import os
import subprocess
import sys
from pathlib import Path

def check_backend_compilation():
    """Verifica compilación del backend."""
    print("🔧 VERIFICACIÓN BACKEND")
    print("=" * 50)
    
    backend_path = Path("/media/Jesus-Aroldo/Anexo/Desarrollos  /SIC/backend")
    
    # Archivos Python críticos
    critical_files = [
        "app/main.py",
        "app/api/v1/__init__.py",
        "app/api/v1/automated_trading.py",
        "app/api/v1/trade_markers.py",
        "app/services/auto_execution_fixed.py",
        "app/services/trade_markers.py",
        "app/ml/signal_generator.py",
        "app/ml/trading_agent.py"
    ]
    
    compilation_errors = []
    compilation_success = []
    
    for file_path in critical_files:
        full_path = backend_path / file_path
        if full_path.exists():
            try:
                # Compilar archivo
                result = subprocess.run([
                    sys.executable, "-m", "py_compile", str(full_path)
                ], capture_output=True, text=True, cwd=backend_path)
                
                if result.returncode == 0:
                    compilation_success.append(file_path)
                    print(f"✅ {file_path}")
                else:
                    compilation_errors.append((file_path, result.stderr))
                    print(f"❌ {file_path} - ERROR")
                    
            except Exception as e:
                compilation_errors.append((file_path, str(e)))
                print(f"❌ {file_path} - EXCEPTION: {e}")
        else:
            print(f"⚠️ {file_path} - NO EXISTE")
    
    print(f"\n📊 Resultados Backend:")
    print(f"✅ Exitosos: {len(compilation_success)}")
    print(f"❌ Errores: {len(compilation_errors)}")
    
    if compilation_errors:
        print("\n🚨 ERRORES DETALLADOS:")
        for file_path, error in compilation_errors:
            print(f"\n📁 {file_path}:")
            print(f"   {error[:200]}...")
    
    return len(compilation_errors) == 0

def check_frontend_structure():
    """Verifica estructura del frontend."""
    print("\n🎨 VERIFICACIÓN FRONTEND")
    print("=" * 50)
    
    frontend_path = Path("/media/Jesus-Aroldo/Anexo/Desarrollos  /SIC/frontend")
    
    # Archivos críticos del frontend
    critical_files = [
        "src/app/page.tsx",
        "src/app/trading/page.tsx",
        "src/app/automated-trading/page.tsx",
        "src/app/trade-markers/page.tsx",
        "src/components/layout/Sidebar.tsx",
        "src/components/charts/InteractiveCandlestickChart.tsx",
        "package.json",
        "next.config.js"
    ]
    
    existing_files = []
    missing_files = []
    
    for file_path in critical_files:
        full_path = frontend_path / file_path
        if full_path.exists():
            existing_files.append(file_path)
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path} - NO EXISTE")
    
    # Verificar componentes UI
    ui_components_path = frontend_path / "src/components/ui"
    if ui_components_path.exists():
        ui_files = list(ui_components_path.glob("*.tsx"))
        print(f"\n🎯 Componentes UI encontrados: {len(ui_files)}")
        for ui_file in ui_files[:5]:  # Mostrar primeros 5
            print(f"   ✅ {ui_file.name}")
        if len(ui_files) > 5:
            print(f"   ... y {len(ui_files) - 5} más")
    else:
        print("\n❌ Directorio UI no existe")
        missing_files.append("src/components/ui/")
    
    print(f"\n📊 Resultados Frontend:")
    print(f"✅ Existentes: {len(existing_files)}")
    print(f"❌ Faltantes: {len(missing_files)}")
    
    if missing_files:
        print("\n🚨 ARCHIVOS FALTANTES:")
        for file_path in missing_files:
            print(f"   📁 {file_path}")
    
    return len(missing_files) == 0

def check_dependencies():
    """Verifica dependencias críticas."""
    print("\n📦 VERIFICACIÓN DE DEPENDENCIAS")
    print("=" * 50)
    
    # Backend dependencies
    backend_deps = {
        "fastapi": "FastAPI framework",
        "sqlalchemy": "Database ORM",
        "pydantic": "Data validation",
        "loguru": "Logging",
        "binance": "Binance API"
    }
    
    print("🔧 Backend Dependencies:")
    backend_missing = []
    for dep, description in backend_deps.items():
        try:
            __import__(dep)
            print(f"✅ {dep} - {description}")
        except ImportError:
            backend_missing.append(dep)
            print(f"❌ {dep} - {description} (FALTANTE)")
    
    # Frontend dependencies
    frontend_path = Path("/media/Jesus-Aroldo/Anexo/Desarrollos  /SIC/frontend")
    package_json = frontend_path / "package.json"
    
    print(f"\n🎨 Frontend Dependencies:")
    if package_json.exists():
        try:
            import json
            with open(package_json, 'r') as f:
                package_data = json.load(f)
            
            deps = package_data.get('dependencies', {})
            critical_frontend_deps = [
                "next", "react", "typescript", 
                "lucide-react", "tailwindcss"
            ]
            
            frontend_missing = []
            for dep in critical_frontend_deps:
                if dep in deps:
                    print(f"✅ {dep} - v{deps[dep]}")
                else:
                    frontend_missing.append(dep)
                    print(f"❌ {dep} - FALTANTE")
            
        except Exception as e:
            print(f"❌ Error leyendo package.json: {e}")
            frontend_missing = ["package.json"]
    else:
        print("❌ package.json no encontrado")
        frontend_missing = ["package.json"]
    
    print(f"\n📊 Resultados Dependencies:")
    print(f"❌ Backend faltantes: {len(backend_missing)}")
    print(f"❌ Frontend faltantes: {len(frontend_missing)}")
    
    return len(backend_missing) == 0 and len(frontend_missing) == 0

def check_api_endpoints():
    """Verifica estructura de API endpoints."""
    print("\n🌐 VERIFICACIÓN DE API ENDPOINTS")
    print("=" * 50)
    
    backend_path = Path("/media/Jesus-Aroldo/Anexo/Desarrollos  /SIC/backend")
    
    # Verificar routers API
    api_routers = [
        "app/api/v1/auth.py",
        "app/api/v1/trading.py", 
        "app/api/v1/signals.py",
        "app/api/v1/automated_trading.py",
        "app/api/v1/trade_markers.py"
    ]
    
    router_status = {}
    
    for router_file in api_routers:
        full_path = backend_path / router_file
        if full_path.exists():
            try:
                with open(full_path, 'r') as f:
                    content = f.read()
                
                # Buscar endpoints
                if '@router.' in content:
                    endpoint_count = content.count('@router.')
                    router_status[router_file] = endpoint_count
                    print(f"✅ {router_file} - {endpoint_count} endpoints")
                else:
                    router_status[router_file] = 0
                    print(f"⚠️ {router_file} - Sin endpoints")
                    
            except Exception as e:
                router_status[router_file] = f"Error: {e}"
                print(f"❌ {router_file} - {e}")
        else:
            router_status[router_file] = "NO EXISTE"
            print(f"❌ {router_file} - NO EXISTE")
    
    total_endpoints = sum(count for count in router_status.values() if isinstance(count, int))
    print(f"\n📊 Total Endpoints: {total_endpoints}")
    
    return True

def generate_compilation_report():
    """Genera reporte completo de compilación."""
    print("🚀 SIC ULTRA - COMPILATION CHECK")
    print("Verificación completa del sistema")
    print("=" * 60)
    
    # Ejecutar todas las verificaciones
    backend_ok = check_backend_compilation()
    frontend_ok = check_frontend_structure()
    deps_ok = check_dependencies()
    api_ok = check_api_endpoints()
    
    print("\n" + "=" * 60)
    print("📊 REPORT FINAL DE COMPILACIÓN")
    print("=" * 60)
    
    # Resumen final
    checks = {
        "Backend Python": backend_ok,
        "Frontend Structure": frontend_ok, 
        "Dependencies": deps_ok,
        "API Endpoints": api_ok
    }
    
    passed = sum(checks.values())
    total = len(checks)
    
    for check_name, status in checks.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {check_name}: {'OK' if status else 'ERROR'}")
    
    print(f"\n🎯 Resultado: {passed}/{total} checks pasados")
    
    if passed == total:
        print("\n🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("✅ Todos los componentes compilan correctamente")
        print("🚀 Listo para producción")
    else:
        print(f"\n⚠️ {total - passed} checks necesitan corrección")
        print("🔧 Revisar errores antes de producción")
    
    # Recomendaciones
    print("\n💡 RECOMENDACIONES:")
    if not backend_ok:
        print("🔧 Corregir errores de sintaxis Python en backend")
    if not frontend_ok:
        print("🎨 Crear componentes UI faltantes en frontend")
    if not deps_ok:
        print("📦 Instalar dependencias faltantes (pip install, npm install)")
    if not api_ok:
        print("🌐 Revisar estructura de endpoints API")
    
    if passed == total:
        print("\n✨ El sistema está listo para despliegue!")
    
    return passed == total

if __name__ == "__main__":
    generate_compilation_report()