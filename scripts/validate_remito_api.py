#!/usr/bin/env python
"""
Script de validación rápida del endpoint /API/1.1/remitoVentaBean
Verifica que devuelva JSON con Content-Type correcto
"""

import json
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from src.infrastructure.fastapi.api import app

def test_remito_list_endpoint():
    """Validar que GET /API/1.1/remitoVentaBean devuelve JSON"""
    client = TestClient(app)
    
    print("\n" + "="*80)
    print("TEST: GET /API/1.1/remitoVentaBean (Listado)")
    print("="*80)
    
    response = client.get("/API/1.1/remitoVentaBean")
    
    # Validar status code
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("✅ Status Code: 200 OK")
    
    # Validar Content-Type
    content_type = response.headers.get("content-type", "")
    print(f"Content-Type: {content_type}")
    assert "application/json" in content_type, f"Expected application/json, got {content_type}"
    print("✅ Content-Type: application/json")
    
    # Validar que es JSON válido
    try:
        data = response.json()
        print(f"Body: JSON válido")
        print(f"✅ Respuesta es JSON válido")
        print(f"   - Estructura: {list(data.keys())}")
        if "items" in data:
            print(f"   - Items: {len(data['items'])} remitos")
    except json.JSONDecodeError as e:
        print(f"❌ Error al parsear JSON: {e}")
        print(f"   Body: {response.text[:200]}...")
        raise
    
    print("\n" + "="*80)
    print("TEST: GET /API/1.1/remitoVentaBean/{id} (Detalle)")
    print("="*80)
    
    # Probar detalle si hay items
    if data.get("items"):
        response_detail = client.get("/API/1.1/remitoVentaBean/1", follow_redirects=True)
        print(f"Status Code: {response_detail.status_code}")
        content_type_detail = response_detail.headers.get("content-type", "")
        print(f"Content-Type: {content_type_detail}")
        if response_detail.status_code == 200:
            assert "application/json" in content_type_detail
            print("✅ Detalle también devuelve JSON")
    else:
        print("⚠️  No hay items para probar detalle")
    
    print("\n" + "="*80)
    print("VALIDACIÓN COMPLETADA EXITOSAMENTE")
    print("="*80 + "\n")

if __name__ == "__main__":
    try:
        test_remito_list_endpoint()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ FALLO: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
