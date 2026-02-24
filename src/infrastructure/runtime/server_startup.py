from __future__ import annotations

import os
import socket
import subprocess
from dataclasses import dataclass
from typing import List
from urllib.parse import urlparse

from src.infrastructure.sqlite3.network_audit_repository import SqliteNetworkAuditRepository
from src.infrastructure.system.network_snapshot_provider import SystemNetworkSnapshotProvider
from src.shared.config import get_host, get_network_audit_db_path, get_port
from src.use_cases.network_audit import record_network_audit


@dataclass(frozen=True)
class StartupRuntime:
    host: str
    port: int
    reload_enabled: bool


def ensure_port_available(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError as exc:
            if exc.errno == 98:
                raise RuntimeError(
                    "Puerto ocupado. Libera el puerto o cambia APP_PORT. "
                    f"Sugerencia: lsof -i :{port}"
                ) from exc
            raise


def resolve_bind_port(host: str, preferred_port: int, *, max_tries: int = 20) -> int:
    for offset in range(max_tries + 1):
        candidate = preferred_port + offset
        try:
            ensure_port_available(host, candidate)
            return candidate
        except RuntimeError:
            continue
    raise RuntimeError(
        f"No se encontro puerto disponible entre {preferred_port} y {preferred_port + max_tries}. "
        f"Sugerencia: lsof -i :{preferred_port}"
    )


def resolve_host_for_mode(default_host: str, mode: str) -> str:
    if mode in {"red-interna", "full"}:
        return "0.0.0.0"
    return default_host


def bootstrap_runtime(mode: str, logger) -> StartupRuntime:
    configured_host = get_host()
    host = resolve_host_for_mode(configured_host, mode)
    configured_port = get_port()
    resolved_port = resolve_bind_port(host, configured_port)
    if resolved_port != configured_port:
        logger.warning(
            "Puerto %d ocupado. Se usara automaticamente el puerto %d.",
            configured_port,
            resolved_port,
        )
    port = resolved_port
    reload_enabled = os.getenv("FASTAPI_RELOAD", "true").lower() == "true"

    logger.info("Modo backend: %s", mode)
    logger.info("Iniciando FastAPI en %s:%d", host, port)

    lan_access_url = None
    lan_ips: List[str] = []
    if host == "0.0.0.0":
        lan_ips = detect_lan_ips()
        if lan_ips:
            lan_access_url = f"http://{lan_ips[0]}:{port}"
            logger.info(
                "Acceso LAN detectado (usar desde fábrica): %s",
                ", ".join(f"http://{ip}:{port}" for ip in lan_ips),
            )
            logger.info(
                "Recomendación fábrica: usar una IP fija/reservada para este servidor."
            )
        else:
            logger.warning(
                "No se pudieron detectar IPs LAN automaticamente. "
                "Verifica con: hostname -I"
            )
    if mode in {"ngrok", "full"}:
        logger.info(
            "Nota: run_server.py no inicia ngrok. Para túnel automático usar ./run.sh --mode %s",
            mode,
        )

    apply_runtime_cors_origins(mode, port, lan_ips)
    logger.info(
        "CORS runtime origins efectivos: %s",
        os.getenv("FRONTEND_CORS_ORIGINS", ""),
    )

    if mode in {"red-interna", "full"}:
        run_optional_https_prepare(logger)
        try:
            audit = record_network_audit(
                SystemNetworkSnapshotProvider(),
                SqliteNetworkAuditRepository(get_network_audit_db_path()),
            )
            ip_status = "IP CAMBIO" if audit.changed_ip else "IP SIN CAMBIOS"
            iface_status = (
                "IFACE CAMBIO" if audit.changed_iface else "IFACE SIN CAMBIOS"
            )
            gw_status = "GW CAMBIO" if audit.changed_gw else "GW SIN CAMBIOS"
            logger.info(
                "SQLite audit guardado: db=%s lan_ip=%s | %s | %s | %s",
                audit.db_path,
                audit.current.lan_ip,
                ip_status,
                iface_status,
                gw_status,
            )
            logger.info("============================================================")
            logger.info("XUBIO BACKEND | Modo %s", mode)
            logger.info("============================================================")
            logger.info("Estado general: OK")
            if lan_access_url is not None:
                logger.info("URL interna:    %s", lan_access_url)
            logger.info("Salud API:      LISTA")
            logger.info("Red (auditoria):")
            logger.info("- IP LAN actual: %s", audit.current.lan_ip)
            logger.info(
                "- Estado IP:     %s",
                "CAMBIO DETECTADO" if audit.changed_ip else "SIN CAMBIOS",
            )
            logger.info(
                "- Interfaz:      %s",
                "CAMBIO DETECTADO" if audit.changed_iface else "SIN CAMBIOS",
            )
            logger.info(
                "- Gateway:       %s",
                "CAMBIO DETECTADO" if audit.changed_gw else "SIN CAMBIOS",
            )
            logger.info("Recomendacion:")
            logger.info("- Mantener reserva DHCP/IP fija para evitar cambios de URL.")
            logger.info("- Para produccion usar HTTPS en 443 con reverse proxy.")
            logger.info("DB auditoria:")
            logger.info("- %s", audit.db_path)
            logger.info("Servidor:")
            logger.info("- FastAPI escuchando en %s:%d", host, port)
            logger.info("- Startup completo")
            logger.info("============================================================")
        except Exception as exc:
            logger.warning("No se pudo guardar network audit en SQLite: %s", exc)

    return StartupRuntime(host=host, port=port, reload_enabled=reload_enabled)


def detect_lan_ips() -> List[str]:
    try:
        ips = [
            ip
            for ip in socket.gethostbyname_ex(socket.gethostname())[2]
            if not ip.startswith("127.")
        ]
        if ips:
            return sorted(set(ips))
    except OSError:
        pass
    try:
        output = os.popen("hostname -I 2>/dev/null").read().strip()
        if output:
            return sorted(set(ip for ip in output.split() if not ip.startswith("127.")))
    except OSError:
        pass
    return []


def normalize_origin(value: str) -> str:
    raw = (value or "").strip().rstrip("/")
    if not raw:
        return ""
    parsed = urlparse(raw)
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}"
    return raw


def apply_runtime_cors_origins(mode: str, port: int, lan_ips: List[str]) -> None:
    current = os.getenv("FRONTEND_CORS_ORIGINS", "").strip()
    seen: set[str] = set()
    merged: list[str] = []

    def _add(origin: str) -> None:
        normalized = normalize_origin(origin)
        if not normalized or normalized in seen:
            return
        seen.add(normalized)
        merged.append(normalized)

    if current:
        for item in current.split(","):
            _add(item)

    _add("http://localhost")
    _add("http://localhost:5173")
    _add("http://127.0.0.1")
    _add("http://127.0.0.1:5173")
    _add(f"http://127.0.0.1:{port}")
    _add(f"http://localhost:{port}")

    if mode in {"red-interna", "full"}:
        for ip in lan_ips:
            _add(f"http://{ip}:{port}")

    if mode in {"ngrok", "full"}:
        ngrok_domain = os.getenv("NGROK_DOMAIN", "").strip()
        if ngrok_domain:
            if "://" not in ngrok_domain:
                ngrok_domain = f"https://{ngrok_domain}"
            _add(ngrok_domain)

    if merged:
        os.environ["FRONTEND_CORS_ORIGINS"] = ",".join(merged)


def is_port_listening(port: int) -> bool:
    try:
        output = subprocess.check_output(
            ["ss", "-ltn"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return f":{port} " in output


def run_optional_https_prepare(logger) -> None:
    auto_prepare = os.getenv("AUTO_PREPARE_HTTPS", "false").strip().lower() == "true"
    domain = os.getenv("HTTPS_DOMAIN", "api.madygraf.local").strip()
    cert = f".runtime/tls/{domain}.crt"
    key = f".runtime/tls/{domain}.key"
    conf = f".runtime/nginx/{domain}.conf"

    nginx_installed = (
        subprocess.run(
            ["bash", "-lc", "command -v nginx >/dev/null 2>&1"],
            check=False,
        ).returncode
        == 0
    )
    port_443_busy = is_port_listening(443)

    logger.info("HTTPS readiness:")
    logger.info("- domain: %s", domain)
    logger.info("- nginx instalado: %s", "si" if nginx_installed else "no")
    logger.info("- puerto 443 en uso: %s", "si" if port_443_busy else "no")
    logger.info(
        "- cert local presente: %s (%s)",
        "si" if os.path.exists(cert) else "no",
        cert,
    )
    logger.info(
        "- key local presente: %s (%s)", "si" if os.path.exists(key) else "no", key
    )
    logger.info(
        "- nginx conf presente: %s (%s)",
        "si" if os.path.exists(conf) else "no",
        conf,
    )
    blockers: list[str] = []
    if not nginx_installed:
        blockers.append("Nginx no instalado")
    if port_443_busy:
        blockers.append("Puerto 443 ocupado")
    if not os.path.exists(cert):
        blockers.append("Certificado TLS ausente")
    if not os.path.exists(key):
        blockers.append("Clave TLS ausente")
    if not os.path.exists(conf):
        blockers.append("Configuracion Nginx ausente")

    if blockers:
        logger.warning("HTTPS bloqueado por:")
        for item in blockers:
            logger.warning("- %s", item)
        logger.info("Comandos sugeridos para resolver:")
        logger.info("- ./scripts/detect_443_owner.sh")
        logger.info("- DOMAIN=%s ./scripts/generate_local_tls_cert.sh", domain)
        logger.info("- DOMAIN=%s ./scripts/setup_nginx_https_local.sh", domain)
        logger.info("- sudo apt-get install -y nginx")
        logger.info("- sudo nginx -t && sudo systemctl reload nginx")
    else:
        logger.info("HTTPS readiness sin bloqueantes locales detectados.")

    if not auto_prepare:
        logger.info(
            "AUTO_PREPARE_HTTPS=false. Para generar cert/conf local automatico: export AUTO_PREPARE_HTTPS=true"
        )
        return

    try:
        subprocess.run(
            ["bash", "-lc", f"DOMAIN={domain} ./scripts/generate_local_tls_cert.sh"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            ["bash", "-lc", f"DOMAIN={domain} ./scripts/setup_nginx_https_local.sh"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logger.info(
            "AUTO_PREPARE_HTTPS=true: cert/conf local generados en .runtime para %s",
            domain,
        )
    except subprocess.CalledProcessError:
        logger.warning("No se pudo auto-generar artefactos HTTPS locales.")
