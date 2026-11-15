#!/usr/bin/env bash
# Copyright 2026 UCit
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Pré-flight Linux du portail de visualisation distante.
# Lecture seule : aucune configuration n'est modifiée.

set -uo pipefail

PORTAL_URL="${PORTAL_URL:-https://viz.example.org}"
PORTAL_HEALTH="${PORTAL_HEALTH:-${PORTAL_URL%/}/health}"
VNC_SERVICE="${VNC_SERVICE:-turbovncserver}"
VNC_PORT="${VNC_PORT:-6080}"
FAILURES=0
WARNINGS=0

pass() { printf 'PASS  %s\n' "$*"; }
fail() { printf 'FAIL  %s\n' "$*"; FAILURES=$((FAILURES + 1)); }
warn() { printf 'WARN  %s\n' "$*"; WARNINGS=$((WARNINGS + 1)); }
have() { command -v "$1" >/dev/null 2>&1; }

echo "== Portail de visualisation — pré-flight Linux =="
echo "URL       : $PORTAL_URL"
echo "Santé     : $PORTAL_HEALTH"
echo "Service   : $VNC_SERVICE"
echo "Port VNC  : $VNC_PORT"
echo

echo "-- Système et GPU --"
if [ "$(uname -s)" = "Linux" ]; then
  pass "Système Linux : $(uname -r)"
else
  fail "Ce script cible Linux (détecté : $(uname -s))"
fi

if have nvidia-smi; then
  gpu_info="$(nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>/dev/null || true)"
  if [ -n "$gpu_info" ]; then
    pass "GPU visible : $gpu_info"
  else
    fail "nvidia-smi ne retourne aucune GPU"
  fi
else
  fail "nvidia-smi introuvable : pilote NVIDIA absent ou PATH incomplet"
fi

echo
echo "-- VirtualGL / OpenGL --"
if have vglrun && have glxinfo; then
  renderer="$(vglrun glxinfo -B 2>/dev/null | awk -F': ' '/OpenGL renderer string/{print $2; exit}')"
  case "$renderer" in
    *llvmpipe*|*softpipe*|"")
      fail "Renderer logiciel détecté (${renderer:-inconnu}) : VirtualGL n'est pas actif"
      ;;
    *)
      pass "Renderer OpenGL : $renderer"
      ;;
  esac
else
  fail "vglrun et/ou glxinfo introuvable(s)"
fi

echo
echo "-- TurboVNC / noVNC --"
if have systemctl; then
  if systemctl is-active --quiet "$VNC_SERVICE"; then
    pass "Service $VNC_SERVICE actif"
  else
    fail "Service $VNC_SERVICE inactif"
  fi
else
  warn "systemctl indisponible : vérifier le service manuellement"
fi

if have ss; then
  if ss -ltn "sport = :$VNC_PORT" 2>/dev/null | grep -q LISTEN; then
    pass "Port $VNC_PORT en écoute"
  else
    fail "Aucun listener sur le port $VNC_PORT"
  fi
else
  warn "ss indisponible : vérifier le port $VNC_PORT manuellement"
fi

echo
echo "-- Portail et TLS --"
if have curl; then
  http_code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 10 "$PORTAL_HEALTH" 2>/dev/null || true)"
  if [ "$http_code" = "200" ]; then
    pass "Health check HTTP 200"
  else
    fail "Health check HTTP ${http_code:-inaccessible}"
  fi
else
  fail "curl introuvable"
fi

host="$(printf '%s' "$PORTAL_URL" | sed -E 's#^https?://([^/:]+).*#\1#')"
if have openssl && [ -n "$host" ]; then
  tls_output="$(printf '' | openssl s_client -servername "$host" -connect "${host}:443" -brief 2>/dev/null || true)"
  if printf '%s' "$tls_output" | grep -q "Verification: OK"; then
    pass "Certificat TLS valide pour $host"
  else
    warn "Vérification TLS à confirmer manuellement pour $host"
  fi
else
  warn "openssl indisponible ou hôte non déterminé"
fi

echo
echo "-- Nginx --"
if have nginx; then
  if nginx -t >/dev/null 2>&1; then
    pass "Configuration Nginx valide"
  else
    fail "Configuration Nginx invalide (exécuter nginx -t)"
  fi
else
  warn "nginx indisponible : tester depuis le conteneur ou le nœud cible"
fi

echo
echo "Résultat : ${FAILURES} échec(s), ${WARNINGS} avertissement(s)"
if [ "$FAILURES" -gt 0 ]; then
  exit 1
fi
