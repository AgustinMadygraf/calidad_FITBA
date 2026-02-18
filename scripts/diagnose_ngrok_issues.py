#!/usr/bin/env python
"""
Script para diagnosticar inconsistencias en ngrok/producción.

Detecta:
- Si ngrok está sirviendo HTML intermedio (error pages, CAPTCHA, etc.)
- Discrepancias entre User-Agent (navegador vs curl)
- Problemas de caché/versioning
- Redirecciones silenciosas
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from src.infrastructure.fastapi.api import app


def simulate_browser_request():
    """Simular request exacto que hace navegador desde Xubio"""
    client = TestClient(app)
    
    print("\n" + "="*90)
    print("SIMULACIÓN: Request desde navegador en https://xubio.madygraf.com")
    print("="*90 + "\n")
    
    # Headers exactos que envía navegador moderno
    headers = {
        "origin": "https://xubio.madygraf.com",
        "referer": "https://xubio.madygraf.com/panel",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "accept": "application/json",
        "accept-language": "es-ES,es;q=0.9",
        "accept-encoding": "gzip, deflate, br",
    }
    
    print("📤 Headers del navegador:")
    for k, v in headers.items():
        print(f"   {k}: {v}")
    
    print("\n📍 Endpoint: GET /API/1.1/remitoVentaBean")
    
    response = client.get(
        "/API/1.1/remitoVentaBean",
        headers=headers,
        follow_redirects=True,
    )
    
    print(f"\n📥 Status Response:")
    print(f"   HTTP Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('content-type', 'NOT SET')}")
    print(f"   Content-Length: {len(response.content)}")
    
    # CORS Headers
    print(f"\n🔒 CORS Headers:")
    print(f"   Access-Control-Allow-Origin: {response.headers.get('access-control-allow-origin', 'NOT SET')}")
    print(f"   Access-Control-Allow-Methods: {response.headers.get('access-control-allow-methods', 'NOT SET')}")
    print(f"   Access-Control-Allow-Headers: {response.headers.get('access-control-allow-headers', 'NOT SET')}")
    
    # Parse response
    print(f"\n📋 Body Parsing:")
    try:
        data = response.json()
        print(f"   ✅ JSON válido")
        print(f"   Keys: {list(data.keys())}")
        if "items" in data:
            print(f"   Items: {len(data['items'])} remitos")
            if data['items']:
                print(f"   First item keys: {list(data['items'][0].keys())}")
        return True, response
    except Exception as e:
        print(f"   ❌ NO es JSON válido: {e}")
        print(f"   Preview: {response.text[:300]}...")
        return False, response


def check_inconsistencies():
    """Detectar problemas comunes que causan HTML en lugar de JSON"""
    client = TestClient(app)
    
    print("\n" + "="*90)
    print("CHEQUEOS DE PROBLEMAS COMUNES")
    print("="*90 + "\n")
    
    checks = []
    
    # 1. ¿ReRedireccionamientos?
    print("🔍 Check 1: Redirecciones")
    response = client.get("/API/1.1/remitoVentaBean", follow_redirects=False)
    if response.status_code in [301, 302, 303, 307, 308]:
        print(f"   ⚠️  Hay redirección: {response.status_code} -> {response.headers.get('location')}")
        checks.append(("Redirección detectada", False))
    else:
        print(f"   ✅ Sin redirecciones (status {response.status_code})")
        checks.append(("Redirecciones", True))
    
    # 2. ¿Diferentes Content-Type por path/query?
    print("\n🔍 Check 2: Variación de Content-Type por path")
    paths = [
        "/API/1.1/remitoVentaBean",
        "/API/1.1/remitoVentaBean/",
        "/API/1.1/remitoVentaBean?page=1",
    ]
    content_types = set()
    for path in paths:
        resp = client.get(path)
        ct = resp.headers.get("content-type", "")
        content_types.add(ct)
        print(f"   {path}: {ct}")
    
    if len(content_types) == 1:
        print(f"   ✅ Content-Type consistente")
        checks.append(("Content-Type consistente", True))
    else:
        print(f"   ⚠️  Content-Type VARÍA: {content_types}")
        checks.append(("Content-Type consistente", False))
    
    # 3. ¿Interfiere StaticFiles?
    print("\n🔍 Check 3: Posible interferencia StaticFiles")
    resp_api = client.get("/API/1.1/remitoVentaBean")
    resp_root = client.get("/")
    print(f"   /API/1.1/remitoVentaBean: {resp_api.headers.get('content-type', '')}")
    print(f"   /: {resp_root.headers.get('content-type', '')}")
    
    if "application/json" in resp_api.headers.get("content-type", ""):
        print(f"   ✅ API devuelve JSON (no HTML)")
        checks.append(("StaticFiles interference", True))
    else:
        print(f"   ❌ API devuelve HTML (StaticFiles interfiriendo?)")
        checks.append(("StaticFiles interference", False))
    
    # 4. ¿Endpoint /API/health funciona?
    print("\n🔍 Check 4: Health check endpoint")
    resp_health = client.get("/API/health")
    if resp_health.status_code == 200 and "application/json" in resp_health.headers.get("content-type", ""):
        try:
            data = resp_health.json()
            print(f"   ✅ /API/health disponible: {data.get('status')}")
            checks.append(("Health endpoint", True))
        except:
            print(f"   ❌ /API/health no devuelve JSON")
            checks.append(("Health endpoint", False))
    else:
        print(f"   ❌ /API/health status {resp_health.status_code}")
        checks.append(("Health endpoint", False))
    
    # Resumen
    print("\n" + "="*90)
    print("RESUMEN DE CHEQUEOS")
    print("="*90)
    
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
    
    all_passed = all(passed for _, passed in checks)
    return all_passed


if __name__ == "__main__":
    try:
        success1, _ = simulate_browser_request()
        success2 = check_inconsistencies()
        
        print("\n" + "="*90)
        if success1 and success2:
            print("✅ DIAGNÓSTICO EXITOSO: No hay problemas detectados")
            print("="*90 + "\n")
            sys.exit(0)
        else:
            print("⚠️  DIAGNÓSTICO CON ADVERTENCIAS: Ver resultados arriba")
            print("="*90 + "\n")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
