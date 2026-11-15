# Runbook — Portail de visualisation distante 2D/3D

**Périmètre** : déploiement et validation d'un portail web de visualisation
scientifique sur Linux, exposé via AWS ALB, avec clients Linux et Windows.

> Ce runbook est une procédure de POC. Il ne remplace pas la documentation de
> l'instance cliente ni les procédures de changement UCit.

## 1. Architecture cible

```text
Navigateur Linux/Windows
        │ HTTPS 443
        ▼
AWS ALB (TLS, WAF, plages IP autorisées)
        │ HTTP 8080
        ▼
Nginx (WebSocket, reverse proxy, en-têtes)
        │ HTTP 6080
        ▼
noVNC → TurboVNC → session graphique
                         │
                         └── vglrun → VirtualGL → GPU NVIDIA
```

Le portail ne doit jamais exposer directement TurboVNC ou noVNC sur Internet.
Seul l'ALB est public ; Nginx et le serveur de session restent dans un sous-réseau
privé.

## 2. Prérequis

### Serveur Linux

- Ubuntu 22.04/24.04 ou RHEL 9, Python 3.11+ ;
- pilote NVIDIA et `nvidia-smi` fonctionnels ;
- TurboVNC, VirtualGL, noVNC, Nginx, OpenSSL ;
- compte de service non privilégié, répertoires de session dédiés ;
- certificat TLS géré par l'ALB ou par Nginx selon l'architecture retenue ;
- accès sortant limité aux dépôts de paquets et au serveur d'authentification.

### Poste client Windows

- Edge ou Chrome à jour, WebGL activé ;
- accès réseau au port 443 du portail (VPN ou plage IP autorisée) ;
- proxy d'entreprise configuré pour ne pas intercepter le WebSocket ;
- pilote graphique à jour, même si le rendu 3D est serveur.

## 3. Déploiement Linux

### 3.1 Vérifier la GPU

```bash
nvidia-smi
nvidia-smi --query-gpu=name,driver_version --format=csv,noheader
```

La GPU doit être visible avant d'installer VirtualGL. En cas d'échec, corriger
le pilote ou l'attachement GPU de l'instance avant de continuer.

### 3.2 Installer les composants

```bash
# Exemple Ubuntu — adapter les dépôts à l'image cliente
sudo apt-get update
sudo apt-get install -y turbovnc virtualgl novnc nginx openssl curl
```

### 3.3 Valider VirtualGL

```bash
vglrun glxinfo -B | grep -E "OpenGL renderer|OpenGL version"
```

Attendu : un renderer NVIDIA. Si `llvmpipe` ou `softpipe` apparaît, la session
3D sera dégradée : ne pas poursuivre la mise en production.

### 3.4 Lancer une session TurboVNC

```bash
/opt/TurboVNC/bin/vncserver :1 -geometry 1920x1080 -depth 24
/opt/TurboVNC/bin/vncserver -list
```

Le lanceur du portail doit exécuter les applications OpenGL avec VirtualGL :

```bash
vglrun /usr/bin/paraview
```

Ne pas se contenter de démarrer le bureau distant : c'est l'application 3D qui
doit être lancée dans l'environnement VirtualGL.

### 3.5 Configurer Nginx

Utiliser `nginx-remote-viz.conf` comme base. Points obligatoires :

- `proxy_http_version 1.1` ;
- `proxy_set_header Upgrade $http_upgrade` ;
- `proxy_set_header Connection $connection_upgrade` ;
- `proxy_read_timeout` et `proxy_send_timeout` supérieurs à la durée des sessions ;
- `X-Forwarded-Proto https` pour que le portail génère des URL correctes.

Valider puis recharger :

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 3.6 Configurer l'ALB AWS

- écouteur public 443 avec certificat ACM ;
- groupe cible HTTP vers Nginx sur le port 8080 ;
- health check sur `/health` ;
- `idle_timeout.timeout_seconds = 300` (ou plus selon les sessions) ;
- règles WAF et groupe de sécurité limités aux plages du laboratoire ;
- conservation des en-têtes `X-Forwarded-*` ;
- pas d'accès public direct au port 6080.

### 3.7 Personnaliser le portail

Partir de `portal-config.example.yaml` et adapter :

- logo, couleurs, message d'accueil et langue ;
- URL publique et routes ;
- groupes LDAP/SSO autorisés ;
- durée maximale et timeout d'inactivité des sessions ;
- pool GPU et taille des sessions ;
- activation de VirtualGL pour les applications 3D.

Les secrets (client OIDC, mot de passe LDAP, token) ne doivent jamais être
committés : utiliser un coffre-fort ou des variables d'environnement injectées
par le déploiement.

## 4. Validation

### 4.1 Contrôles automatisés

```bash
PORTAL_URL=https://viz.example.org \
VNC_SERVICE=turbovncserver \
bash check_remote_viz.sh
```

Côté Windows :

```powershell
.\Test-RemoteViz.ps1 -PortalUrl https://viz.example.org
```

### 4.2 Tests manuels d'acceptation

| Test | Résultat attendu |
|---|---|
| Page de connexion depuis une IP autorisée | Affichage du branding client |
| Page de connexion depuis une IP hors plage | Refus 403 |
| Session 2D noVNC | Affichage et interaction souris/clavier |
| Session 3D ParaView | Renderer NVIDIA, pas de `llvmpipe` |
| Session inactive 5 minutes | Toujours connectée |
| Session depuis Windows | Pas de fermeture WebSocket 1006 |
| Redémarrage Nginx | Sessions nouvelles opérationnelles |
| Health check ALB | `healthy` sur tous les nœuds |

## 5. Intégration CCME

Lorsque le portail est fédéré par CCME :

- vérifier la matrice de compatibilité CCME/OKA et la version du connecteur ;
- aligner les groupes CCME et les rôles du portail (administrateur, utilisateur,
  lecture seule) ;
- valider l'authentification SSO/LDAP de bout en bout, y compris la déconnexion ;
- contrôler la licence et la connectivité avec OKA ;
- consigner la procédure de rollback avant toute mise à jour.

La checklist générique est dans `docs/ccme_deployment_checklist.md`.

## 6. Rollback

1. Conserver l'ancienne image ou le snapshot du nœud de visualisation.
2. Sauvegarder la configuration Nginx, le fichier portail et les règles ALB.
3. En cas d'échec 3D, revenir à l'image précédente et rétablir le groupe cible.
4. Vérifier `/health`, une session 2D et une session 3D après rollback.
5. Documenter l'incident et l'écart dans `lessons.md`.

## 7. Preuves à joindre au ticket

- sortie de `nvidia-smi` et de `vglrun glxinfo -B` ;
- sortie de `check_remote_viz.sh` ;
- sortie de `Test-RemoteViz.ps1` ;
- capture ou horodatage d'une session 3D Linux et Windows ;
- valeur du timeout ALB et extrait Nginx ;
- confirmation de la restriction IP et du branding.
