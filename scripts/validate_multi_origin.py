#!/usr/bin/env python
"""
Script de validación de endpoints desde múltiples orígenes.
Detecta inconsistencias de Content-Type, caché, headers, etc.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from src.infrastructure.fastapi.api import app

def validate_endpoint(
    client: TestClient,
    path: str,
    origin: str = None,
    referer: str = None,
    extra_headers: Dict[str, str] = None,
) -> Dict[str, Any]:
    """Validar endpoint con headers customizados"""
    headers = {}
    if origin:
        headers["origin"] = origin
    if referer:
        headers["referer"] = referer
    if extra_headers:
        headers.update(extra_headers)
    
    response = client.get(path, headers=headers)
    
    result = {
        "path": path,
        "origin": origin or "none",
        "status": response.status_code,
        "content_type": response.headers.get("content-type", "not-set"),
        "is_json": "application/json" in response.headers.get("content-type", ""),
        "headers": dict(response.headers),
    }
    
    # Intentar parsear JSON
    try:
        result["body"] = response.json()
        result["parse_status"] = "✅ JSON válido"
    except Exception as e:
        result["body_preview"] = response.text[:200]
        result["parse_status"] = f"❌ {str(e)}"
    
    return result

def test_multi_origin_consistency():
    """Validar que el endpoint es consistente desde múltiples orígenes"""
    client = TestClient(app)
    
    print("\n" + "="*90)
    print("VALIDACIÓN MULTI-ORIGEN: GET /API/1.1/remitoVentaBean")
    print("="*90 + "\n")
    
    test_cases = [
        {
            "name": "Origen: xubio.madygraf.com (navegador)",
            "path": "/API/1.1/remitoVentaBean",
            "origin": "https://xubio.madygraf.com",
            "referer": "https://xubio.madygraf.com/panel",
        },
        {
            "name": "Origen: localhost (desarrollo)",
            "path": "/API/1.1/remitoVentaBean",
            "origin": "http://127.0.0.1:5173",
            "referer": "http://127.0.0.1:5173/",
        },
        {
            "name": "Sin origen (curl)",
            "path": "/API/1.1/remitoVentaBean",
            "origin": None,
            "referer": None,
        },
        {
            "name": "Endpoint /API/health",
            "path": "/API/health",
            "origin": "https://xubio.madygraf.com",
            "referer": "https://xubio.madygraf.com/panel",
        },
    ]
    
    results = []
    for test in test_cases:
        print(f"🔍 Test: {test['name']}")
        result = validate_endpoint(
            client,
            test["path"],
            origin=test.get("origin"),
            referer=test.get("referer"),
        )
        results.append(result)
        
        # Print resultado
        print(f"   Path: {result['path']}")
        print(f"   Status: {result['status']}")
        print(f"   Content-Type: {result['content_type']}")
        print(f"   JSON Parse: {result['parse_status']}")
        
        if result["is_json"]:
            if "items" in result.get("body", {}):
                print(f"   Items: {len(result['body']['items'])} remitos")
            else:
                print(f"   Body keys: {list(result.get('body', {}).keys())}")
        else:
            print(f"   ⚠️  NO es application/json!")
            print(f"   Preview: {result.get('body_preview', 'N/A')[:100]}...")
        
        print()
    
    # Análisis de consistencia
    print("="*90)
    print("ANÁLISIS DE CONSISTENCIA")
    print("="*90 + "\n")
    
    remito_list_results = [r for r in results if r["path"] == "/API/1.1/remitoVentaBean"]
    
    # Verificar Content-Type
    content_types = {r["content_type"] for r in remito_list_results}
    if len(content_types) == 1 and "application/json" in content_types:
        print("✅ Content-Type CONSISTENTE: application/json en todos los orígenes")
    else:
        print(f"❌ Content-Type INCONSISTENTE:")
        for r in remito_list_results:
            print(f"   - {r['origin']}: {r['content_type']}")
    
    # Verificar Status
    status_codes = {r["status"] for r in remito_list_results}
    if len(status_codes) == 1 and 200 in status_codes:
        print("✅ Status Code CONSISTENTE: 200 en todos los orígenes")
    else:
        print(f"❌ Status Code INCONSISTENTE:")
        for r in remito_list_results:
            print(f"   - {r['origin']}: {r['status']}")
    
    # Verificar parseable JSON
    parse_statuses = {r["parse_status"] for r in remito_list_results}
    if len(parse_statuses) == 1 and "✅" in list(parse_statuses)[0]:
        print("✅ Parsing JSON CONSISTENTE: válido en todos los orígenes")
    else:
        print(f"❌ Parsing JSON INCONSISTENTE:")
        for r in remito_list_results:
            print(f"   - {r['origin']}: {r['parse_status']}")
    
    print("\n" + "="*90)
    print("VALIDACIÓN COMPLETADA")
    print("="*90 + "\n")
    
    # Retornar exitoso si todo es consistente
    all_json = all(r["is_json"] for r in remito_list_results)
    all_200 = all(r["status"] == 200 for r in remito_list_results)
    
    return all_json and all_200

if __name__ == "__main__":
    try:
        success = test_multi_origin_consistency()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
