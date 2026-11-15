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
# Vérification côté client Windows du portail de visualisation.
# Lecture seule : aucune configuration n'est modifiée.

[CmdletBinding()]
param(
    [string]$PortalUrl = "https://viz.example.org",
    [int]$TimeoutSec = 10
)

$ErrorActionPreference = "Stop"
$script:Failures = 0
$script:Warnings = 0

function Write-Pass {
    param([string]$Message)
    Write-Host "PASS  $Message" -ForegroundColor Green
}

function Write-Fail {
    param([string]$Message)
    Write-Host "FAIL  $Message" -ForegroundColor Red
    $script:Failures++
}

function Write-Warn {
    param([string]$Message)
    Write-Host "WARN  $Message" -ForegroundColor Yellow
    $script:Warnings++
}

Write-Host "== Portail de visualisation — pré-flight Windows =="
Write-Host "URL      : $PortalUrl"
Write-Host "Timeout  : $TimeoutSec s"
Write-Host

$uri = [Uri]$PortalUrl
if ($uri.Scheme -ne "https") {
    Write-Warn "URL non HTTPS : le portail de production doit utiliser TLS"
}

Write-Host "-- DNS et connectivité --"
try {
    Resolve-DnsName -Name $uri.Host -ErrorAction Stop | Out-Null
    Write-Pass "DNS résolu : $($uri.Host)"
}
catch {
    Write-Fail "DNS non résolu : $($uri.Host)"
}

try {
    $tcpOk = Test-NetConnection `
        -ComputerName $uri.Host `
        -Port $uri.Port `
        -InformationLevel Quiet `
        -WarningAction SilentlyContinue
    if ($tcpOk) {
        Write-Pass "TCP $($uri.Port) accessible"
    }
    else {
        Write-Fail "TCP $($uri.Port) inaccessible"
    }
}
catch {
    Write-Fail "Test TCP impossible : $($_.Exception.Message)"
}

Write-Host
Write-Host "-- Santé HTTP et TLS --"
try {
    $healthUrl = $PortalUrl.TrimEnd("/") + "/health"
    $health = Invoke-WebRequest `
        -Uri $healthUrl `
        -UseBasicParsing `
        -TimeoutSec $TimeoutSec
    if ($health.StatusCode -eq 200) {
        Write-Pass "Health check HTTP 200"
    }
    else {
        Write-Fail "Health check HTTP $($health.StatusCode)"
    }
}
catch {
    Write-Fail "Health check en échec : $($_.Exception.Message)"
}

Write-Host
Write-Host "-- Poste Windows --"
try {
    $os = Get-CimInstance Win32_OperatingSystem
    Write-Pass "Windows : $($os.Caption) $($os.Version)"
}
catch {
    Write-Warn "Version Windows non disponible"
}

try {
    $gpu = Get-CimInstance Win32_VideoController | Select-Object -First 1
    if ($null -ne $gpu) {
        Write-Pass "GPU client : $($gpu.Name) (pilote $($gpu.DriverVersion))"
    }
    else {
        Write-Warn "Aucune GPU client détectée"
    }
}
catch {
    Write-Warn "Informations GPU indisponibles"
}

Write-Host
Write-Host "-- Vérifications manuelles --"
Write-Host "  - Ouvrir $PortalUrl dans Edge ou Chrome à jour."
Write-Host "  - Vérifier WebGL sur edge://gpu ou chrome://gpu."
Write-Host "  - Lancer une session 3D et la laisser inactive plus de 2 minutes."
Write-Host "  - Vérifier que le proxy d'entreprise ne coupe pas les WebSockets."
Write-Host

Write-Host "Résultat : $($script:Failures) échec(s), $($script:Warnings) avertissement(s)"
if ($script:Failures -gt 0) {
    exit 1
}
exit 0
