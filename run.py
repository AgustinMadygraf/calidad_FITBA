import argparse
import os
import socket
from typing import List

import uvicorn

from src.infrastructure.sqlite3.network_audit_repository import SqliteNetworkAuditRepository
from src.infrastructure.system.network_snapshot_provider import SystemNetworkSnapshotProvider
from src.shared.config import get_host, get_network_audit_db_path, get_port, load_env
from src.shared.logger import get_logger
from src.use_cases.network_audit import record_network_audit


def _ensure_port_available(host: str, port: int) -> None:
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


def _resolve_bind_port(host: str, preferred_port: int, *, max_tries: int = 20) -> int:
    for offset in range(max_tries + 1):
        candidate = preferred_port + offset
        try:
            _ensure_port_available(host, candidate)
            return candidate
        except RuntimeError:
            continue
    raise RuntimeError(
        f"No se encontro puerto disponible entre {preferred_port} y {preferred_port + max_tries}. "
        f"Sugerencia: lsof -i :{preferred_port}"
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run FastAPI backend.")
    parser.add_argument(
        "--mode",
        choices=["ngrok", "red-interna", "full"],
        default="ngrok",
        help=(
            "Modo de exposición del backend: "
            "ngrok (127.0.0.1), red-interna (0.0.0.0), full (0.0.0.0)."
        ),
    )
    return parser


def _resolve_host_for_mode(default_host: str, mode: str) -> str:
    if mode in {"red-interna", "full"}:
        return "0.0.0.0"
    return default_host


def _detect_lan_ips() -> List[str]:
    try:
        ips = [
            ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
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


def main() -> int:
    logger = get_logger(__name__)
    parser = _build_parser()
    args = parser.parse_args()

    if not load_env():
        logger.warning(".env no cargado (archivo inexistente o falta python-dotenv)")

    try:
        configured_host = get_host()
        host = _resolve_host_for_mode(configured_host, args.mode)
        port = get_port()
    except ValueError as exc:
        logger.error("Configuracion invalida: %s", exc)
        return 2

    try:
        resolved_port = _resolve_bind_port(host, port)
    except RuntimeError as exc:
        logger.error("%s", exc)
        return 1
    if resolved_port != port:
        logger.warning(
            "Puerto %d ocupado. Se usara automaticamente el puerto %d.",
            port,
            resolved_port,
        )
    port = resolved_port

    reload_enabled = os.getenv("FASTAPI_RELOAD", "true").lower() == "true"
    logger.info("Modo backend: %s", args.mode)
    logger.info("Iniciando FastAPI en %s:%d", host, port)
    lan_access_url = None
    if host == "0.0.0.0":
        lan_ips = _detect_lan_ips()
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
    if args.mode in {"ngrok", "full"}:
        logger.info(
            "Nota: run_server.py no inicia ngrok. Para túnel automático usar ./run.sh --mode %s",
            args.mode,
        )
    if args.mode in {"red-interna", "full"}:
        try:
            audit = record_network_audit(
                SystemNetworkSnapshotProvider(),
                SqliteNetworkAuditRepository(get_network_audit_db_path()),
            )
            ip_status = "IP CAMBIO" if audit.changed_ip else "IP SIN CAMBIOS"
            iface_status = "IFACE CAMBIO" if audit.changed_iface else "IFACE SIN CAMBIOS"
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
            logger.info("XUBIO BACKEND | Modo %s", args.mode)
            logger.info("============================================================")
            logger.info("Estado general: OK")
            if lan_access_url is not None:
                logger.info("URL interna:    %s", lan_access_url)
            logger.info("Salud API:      LISTA")
            logger.info("Red (auditoria):")
            logger.info("- IP LAN actual: %s", audit.current.lan_ip)
            logger.info("- Estado IP:     %s", "CAMBIO DETECTADO" if audit.changed_ip else "SIN CAMBIOS")
            logger.info("- Interfaz:      %s", "CAMBIO DETECTADO" if audit.changed_iface else "SIN CAMBIOS")
            logger.info("- Gateway:       %s", "CAMBIO DETECTADO" if audit.changed_gw else "SIN CAMBIOS")
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
    uvicorn.run(
        "src.infrastructure.fastapi.api:app",
        host=host,
        port=port,
        reload=reload_enabled,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
