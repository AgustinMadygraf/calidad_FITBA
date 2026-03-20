#!/usr/bin/env bash

set -euo pipefail

STATE_DIR="${STATE_DIR:-/tmp/calidad_fitba_net}"
STATE_FILE="$STATE_DIR/ip_state.env"
HISTORY_FILE="$STATE_DIR/ip_history.log"
mkdir -p "$STATE_DIR"

now_utc="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
hostname_short="$(hostname)"
fqdn="$(hostname -f 2>/dev/null || hostname)"

default_iface="$(ip route show default 2>/dev/null | awk 'NR==1 {print $5}')"
default_gw="$(ip route show default 2>/dev/null | awk 'NR==1 {print $3}')"

if [[ -z "${default_iface:-}" ]]; then
  echo "ERROR: No se pudo detectar interfaz por ruta default." >&2
  exit 1
fi

lan_ip_cidr="$(ip -4 addr show dev "$default_iface" | awk '/inet / {print $2; exit}')"
lan_ip="${lan_ip_cidr%%/*}"
lan_cidr="$lan_ip_cidr"
mac_addr="$(cat "/sys/class/net/$default_iface/address" 2>/dev/null || echo "unknown")"

if [[ -z "${lan_ip:-}" ]]; then
  echo "ERROR: No se pudo detectar IPv4 en interfaz $default_iface." >&2
  exit 1
fi

public_ip="unknown"
if command -v curl >/dev/null 2>&1; then
  public_ip="$(curl -fsS --max-time 3 https://ifconfig.me 2>/dev/null || echo "unknown")"
fi

changed_ip="no"
changed_iface="no"
changed_gw="no"
prev_lan_ip=""
prev_iface=""
prev_gw=""

if [[ -f "$STATE_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$STATE_FILE"
  prev_lan_ip="${LAN_IP:-}"
  prev_iface="${DEFAULT_IFACE:-}"
  prev_gw="${DEFAULT_GW:-}"
  if [[ "$prev_lan_ip" != "$lan_ip" ]]; then
    changed_ip="yes"
  fi
  if [[ "$prev_iface" != "$default_iface" ]]; then
    changed_iface="yes"
  fi
  if [[ "$prev_gw" != "$default_gw" ]]; then
    changed_gw="yes"
  fi
fi

cat > "$STATE_FILE" <<EOF
TIMESTAMP_UTC="$now_utc"
HOSTNAME="$hostname_short"
FQDN="$fqdn"
DEFAULT_IFACE="$default_iface"
DEFAULT_GW="$default_gw"
LAN_IP="$lan_ip"
LAN_CIDR="$lan_cidr"
MAC_ADDR="$mac_addr"
PUBLIC_IP="$public_ip"
EOF

echo "$now_utc host=$hostname_short iface=$default_iface gw=$default_gw lan_ip=$lan_ip lan_cidr=$lan_cidr mac=$mac_addr public_ip=$public_ip changed_ip=$changed_ip changed_iface=$changed_iface changed_gw=$changed_gw" >> "$HISTORY_FILE"

echo "Diagnóstico IP estabilidad"
echo "- timestamp_utc: $now_utc"
echo "- hostname: $hostname_short"
echo "- fqdn: $fqdn"
echo "- default_iface: $default_iface"
echo "- default_gw: $default_gw"
echo "- lan_ip: $lan_ip"
echo "- lan_cidr: $lan_cidr"
echo "- mac_addr: $mac_addr"
echo "- public_ip: $public_ip"
echo "- changed_since_last_run:"
echo "  - lan_ip: $changed_ip"
echo "  - iface: $changed_iface"
echo "  - gw: $changed_gw"
echo "- state_file: $STATE_FILE"
echo "- history_file: $HISTORY_FILE"

if [[ "$changed_ip" == "yes" ]]; then
  echo
  echo "ALERTA: La IP LAN cambió desde la última ejecución."
  echo "Acción: validar reserva DHCP por MAC ($mac_addr) con IT."
fi
