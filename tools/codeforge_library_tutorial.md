# CODEFORGE — Création d'une bibliothèque de code

> **De zéro à une fonction utilisable dans CodeForge**
>
> INGEN Systems · DSI · Documentation Technique Interne — *Validation approuvée*

---

## Table des matières

1. [Introduction](#1-introduction)
2. [Structure d'une bibliothèque CodeForge](#2-structure-dune-bibliothèque-codeforge)
3. [Méthode 1 — Création manuelle (sans outils)](#3-méthode-1--création-manuelle-sans-outils)
4. [Méthode 2 — Création avec cf_lib_manager (CLI)](#4-méthode-2--création-avec-cf_lib_manager-cli)
5. [Méthode 3 — Création avec QwEdit (GUI)](#5-méthode-3--création-avec-qwedit-gui)
6. [Cas pratique — Fonction "Invoke-SecurityScan"](#6-cas-pratique--fonction-invoke-securityscan)
7. [Création de variables associées](#7-création-de-variables-associées)
8. [Validation de la bibliothèque](#8-validation-de-la-bibliothèque)
9. [Test dans CodeForge](#9-test-dans-codeforge)
10. [Bonnes pratiques & Checklist](#10-bonnes-pratiques--checklist)
11. [Dépannage](#11-dépannage)

---

## 1. Introduction

Une bibliothèque CodeForge est un fichier `library.json` qui contient :

| Section | Contenu | Rôle |
|---------|---------|------|
| `metadata` | Infos générales | Identification et versioning |
| `functions` | Liste des fonctions | Les briques d'automatisation |
| `variables` | Liste des variables globales | Paramètres d'environnement |

L'objectif de ce tutoriel est de vous guider dans la création d'une **fonction complète** et de ses **variables associées**, prête à être utilisée dans CodeForge v2.0.

---

## 2. Structure d'une bibliothèque CodeForge

### 2.1 Structure minimale

```json
{
  "metadata": {
    "version": "1.0",
    "description": "Ma bibliothèque",
    "created": "2026-06-04",
    "author": "Votre Nom",
    "validation_status": "APPROVED",
    "languages": ["PowerShell", "CSharp"]
  },
  "functions": [],
  "variables": []
}
```

### 2.2 Structure d'une fonction

```json
{
  "id": "fn_001",
  "type": "function",
  "name": "MaFonction",
  "language": "PowerShell",
  "famille": "MaFamille",
  "description": "Description courte",
  "parameters": [
    {
      "name": "Param1",
      "datatype": "string",
      "required": true,
      "description": "Description du paramètre"
    }
  ],
  "returns": {
    "datatype": "bool",
    "description": "Description de la valeur retournée"
  },
  "source": "function MaFonction { param([string]$Param1) return $true }",
  "tags": ["tag1", "tag2"],
  "throws": ["ExceptionType"]
}
```

### 2.3 Structure d'une variable

```json
{
  "id": "var_001",
  "type": "variable",
  "name": "MaVariable",
  "language": "PowerShell",
  "datatype": "string",
  "default_value": "\"valeur par défaut\"",
  "scope": "global",
  "description": "Description",
  "tags": ["config"]
}
```

---

## 3. Méthode 1 — Création manuelle (sans outils)

### Étape 1 — Créer le fichier JSON

```bash
touch my_library.json
```

### Étape 2 — Écrire le squelette

```json
{
  "metadata": {
    "version": "1.0",
    "description": "Ma bibliothèque personnelle",
    "created": "2026-06-04",
    "author": "Administrateur",
    "validation_status": "APPROVED",
    "languages": ["PowerShell", "CSharp"]
  },
  "functions": [],
  "variables": []
}
```

### Étape 3 — Ajouter une fonction

```json
{
  "metadata": { ... },
  "functions": [
    {
      "id": "fn_001",
      "type": "function",
      "name": "Write-CustomLog",
      "language": "PowerShell",
      "famille": "Logging",
      "description": "Écrit un message personnalisé dans un fichier log",
      "parameters": [
        {
          "name": "Message",
          "datatype": "string",
          "required": true,
          "description": "Message à journaliser"
        },
        {
          "name": "Level",
          "datatype": "string",
          "required": false,
          "default": "INFO",
          "description": "Niveau de sévérité"
        },
        {
          "name": "LogPath",
          "datatype": "string",
          "required": false,
          "default": "$CustomLogPath",
          "description": "Chemin du fichier log"
        }
      ],
      "returns": {
        "datatype": "void",
        "description": "Aucune valeur retournée"
      },
      "source": "function Write-CustomLog {\n    param(\n        [string]$Message,\n        [ValidateSet('INFO','WARN','ERROR','DEBUG')]\n        [string]$Level = 'INFO',\n        [string]$LogPath = $CustomLogPath\n    )\n    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'\n    $entry = \"[$timestamp] [$Level] $Message\"\n    if (-not (Test-Path (Split-Path $LogPath))) {\n        New-Item -ItemType Directory -Path (Split-Path $LogPath) -Force | Out-Null\n    }\n    Add-Content -Path $LogPath -Value $entry -Encoding UTF8\n    Write-Host $entry -ForegroundColor $(switch($Level) {\n        'ERROR' { 'Red' }\n        'WARN'  { 'Yellow' }\n        'DEBUG' { 'Gray' }\n        default { 'Cyan' }\n    })\n}",
      "tags": ["logging", "filesystem", "custom"],
      "throws": []
    }
  ],
  "variables": []
}
```

### Étape 4 — Ajouter une variable associée

```json
{
  "metadata": { ... },
  "functions": [ ... ],
  "variables": [
    {
      "id": "var_001",
      "type": "variable",
      "name": "CustomLogPath",
      "language": "PowerShell",
      "datatype": "string",
      "default_value": "\"C:\\\\Logs\\\\Custom\\\\app.log\"",
      "scope": "global",
      "description": "Chemin par défaut pour les logs personnalisés",
      "tags": ["logging", "config"]
    }
  ]
}
```

### Étape 5 — Valider avec `jq` (optionnel)

```bash
jq . my_library.json > /dev/null && echo "✓ JSON valide"
```

---

## 4. Méthode 2 — Création avec cf_lib_manager (CLI)

### Installation

```bash
# Télécharger le script
wget https://raw.githubusercontent.com/ingen/cf_lib_manager_black.py

# Rendre exécutable
chmod +x cf_lib_manager_black.py
```

### Étape 1 — Initialiser une nouvelle bibliothèque

```bash
python cf_lib_manager_black.py init my_library.json --name "Security Toolkit"
```

### Étape 2 — Ajouter une fonction

```bash
python cf_lib_manager_black.py my_library.json add \
    --type function \
    --name "Invoke-SecurityScan" \
    --lang PowerShell \
    --family Security \
    --desc "Lance un scan de sécurité sur un hôte cible" \
    --datatype "PSObject"
```

### Étape 3 — Ajouter des paramètres à la fonction (édition)

```bash
python cf_lib_manager_black.py my_library.json batch-set \
    "Invoke-SecurityScan" \
    --field parameters \
    --value '[{"name":"TargetHost","datatype":"string","required":true},{"name":"Depth","datatype":"int","required":false,"default":"2"},{"name":"Credential","datatype":"PSCredential","required":false}]' \
    --field-type name
```

### Étape 4 — Ajouter le code source

```bash
python cf_lib_manager_black.py my_library.json batch-set \
    "Invoke-SecurityScan" \
    --field source \
    --value 'function Invoke-SecurityScan { param([string]$TargetHost,[int]$Depth=2,[PSCredential]$Credential) Write-Host "Scanning $TargetHost..." }' \
    --field-type name
```

### Étape 5 — Ajouter des tags

```bash
python cf_lib_manager_black.py my_library.json batch-set \
    "Invoke-SecurityScan" \
    --field tags \
    --value "security,scan,audit,nmap" \
    --field-type name
```

### Étape 6 — Ajouter une variable associée

```bash
python cf_lib_manager_black.py my_library.json add \
    --type variable \
    --name "DefaultScanDepth" \
    --lang PowerShell \
    --datatype int \
    --desc "Profondeur de scan par défaut" \
    --family Security
```

### Étape 7 — Visualiser le résultat

```bash
python cf_lib_manager_black.py my_library.json show
```

---

## 5. Méthode 3 — Création avec QwEdit (GUI)

### Lancement

```bash
python QwEdit.py
```

### Étape 1 — Créer une nouvelle bibliothèque

Cliquez sur **📂 LOAD** pour charger un fichier existant, ou sauvegardez directement un nouveau fichier via **💾 SAVE AS**.

### Étape 2 — Ajouter une fonction

1. Allez dans l'onglet **⚙ FUNCTIONS**
2. Cliquez sur **➕ ADD**
3. Remplissez le formulaire :

| Champ | Valeur |
|-------|--------|
| ID | *(auto-généré)* |
| NAME | `Invoke-SecurityScan` |
| LANGUAGE | `PowerShell` |
| FAMILLE | `Security` |
| DESCRIPTION | `Lance un scan de sécurité sur un hôte cible` |
| PARAMETERS (JSON) | `[{"name":"TargetHost","datatype":"string","required":true},{"name":"Depth","datatype":"int","required":false,"default":"2"}]` |
| RETURNS (JSON) | `{"datatype":"PSObject","description":"Résultats du scan"}` |
| TAGS | `security,scan,audit` |
| SOURCE CODE | *(voir section 6.4)* |

4. Cliquez sur **✓ VALIDATE SCHEMA** puis **OK**

### Étape 3 — Ajouter une variable associée

1. Allez dans l'onglet **◈ VARIABLES**
2. Cliquez sur **➕ ADD**
3. Remplissez le formulaire :

| Champ | Valeur |
|-------|--------|
| NAME | `DefaultScanDepth` |
| LANGUAGE | `PowerShell` |
| DATATYPE | `int` |
| DEFAULT VALUE | `2` |
| SCOPE | `global` |
| DESCRIPTION | `Profondeur de scan par défaut` |

4. Cliquez sur **OK**

### Étape 4 — Sauvegarder

Cliquez sur **💾 SAVE** et choisissez un emplacement.

---

## 6. Cas pratique — Fonction "Invoke-SecurityScan"

Prenons l'exemple d'une fonction **complète, prête pour la production**.

### 6.1 Spécifications

| Propriété | Valeur |
|-----------|--------|
| Nom | `Invoke-SecurityScan` |
| Langage | PowerShell |
| Famille | Security |
| Description | Lance un scan de sécurité réseau avec options avancées |

### 6.2 Paramètres

| Nom | Datatype | Requis | Défaut | Description |
|-----|----------|--------|--------|-------------|
| `TargetHost` | string | ✓ | — | IP ou FQDN cible |
| `Ports` | string | ✗ | `"22,80,443,3389"` | Ports à scanner |
| `Depth` | int | ✗ | `2` | Profondeur (1=rapide, 3=complet) |
| `Credential` | PSCredential | ✗ | `$null` | Credentials pour auth |
| `TimeoutSec` | int | ✗ | `30` | Timeout par opération |
| `OutputPath` | string | ✗ | `$ScanReportPath` | Chemin rapport |

### 6.3 Retour

| Datatype | Description |
|----------|-------------|
| `PSObject` | Objet contenant les résultats (`OpenPorts`, `Vulnerabilities`, `Duration`, `Status`) |

### 6.4 Code source complet

```powershell
function Invoke-SecurityScan {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true, Position=0)]
        [string]$TargetHost,

        [Parameter(Mandatory=$false)]
        [string]$Ports = "22,80,443,3389",

        [Parameter(Mandatory=$false)]
        [int]$Depth = 2,

        [Parameter(Mandatory=$false)]
        [PSCredential]$Credential = $null,

        [Parameter(Mandatory=$false)]
        [int]$TimeoutSec = 30,

        [Parameter(Mandatory=$false)]
        [string]$OutputPath = $ScanReportPath
    )

    $startTime = Get-Date
    $results = [PSCustomObject]@{
        TargetHost      = $TargetHost
        StartTime       = $startTime
        OpenPorts       = @()
        Vulnerabilities = @()
        DurationSec     = 0
        Status          = "Pending"
        Error           = $null
    }

    try {
        Write-Host "[*] Starting security scan on $TargetHost (Depth=$Depth)"

        # Étape 1 : Test de connectivité
        $ping = Test-Connection -ComputerName $TargetHost -Count 2 -Quiet -ErrorAction Stop
        if (-not $ping) {
            throw "Host $TargetHost is not reachable"
        }
        $results | Add-Member -NotePropertyName "Reachable" -NotePropertyValue $true

        # Étape 2 : Scan des ports
        $portList = $Ports -split ',' | ForEach-Object { [int]$_ }
        $openPorts = @()
        foreach ($port in $portList) {
            $tcpClient = New-Object System.Net.Sockets.TcpClient
            $connect = $tcpClient.BeginConnect($TargetHost, $port, $null, $null)
            $success = $connect.AsyncWaitHandle.WaitOne($TimeoutSec * 1000)
            if ($success -and $tcpClient.Connected) {
                $openPorts += $port
                Write-Host "  [+] Port $port : OPEN"
            }
            $tcpClient.Close()
        }
        $results.OpenPorts = $openPorts

        # Étape 3 : Analyses selon profondeur
        if ($Depth -ge 2) {
            Write-Host "[*] Performing deeper analysis..."
            # Tentative de banner grabbing
            $banners = @{}
            foreach ($port in $openPorts | Where-Object { $_ -in @(21,22,25,80,443,3306,3389,8080) }) {
                try {
                    $client = New-Object System.Net.Sockets.TcpClient
                    $client.Connect($TargetHost, $port)
                    $stream = $client.GetStream()
                    $stream.ReadTimeout = 3000
                    $buffer = New-Object byte[] 256
                    $stream.Read($buffer, 0, 256) | Out-Null
                    $banner = [System.Text.Encoding]::ASCII.GetString($buffer).TrimEnd([char]0)
                    if ($banner) { $banners[$port] = $banner }
                    $client.Close()
                } catch { }
            }
            $results | Add-Member -NotePropertyName "Banners" -NotePropertyValue $banners
        }

        if ($Depth -ge 3) {
            Write-Host "[*] Performing comprehensive analysis (this may take a while)..."
            # Simulation de détection de vulnérabilités
            $vulns = @()
            if (80 -in $openPorts -or 443 -in $openPorts) {
                $vulns += [PSCustomObject]@{ Port=80; Severity="Medium"; Description="Web server exposed" }
            }
            if (3389 -in $openPorts) {
                $vulns += [PSCustomObject]@{ Port=3389; Severity="Low"; Description="RDP exposed" }
            }
            $results.Vulnerabilities = $vulns
        }

        $duration = (Get-Date) - $startTime
        $results.DurationSec = [Math]::Round($duration.TotalSeconds, 2)
        $results.Status = "Completed"

        Write-Host "[✓] Scan completed in $($results.DurationSec) seconds"

        # Export du rapport si demandé
        if ($OutputPath) {
            $reportDir = Split-Path $OutputPath
            if (-not (Test-Path $reportDir)) {
                New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
            }
            $results | Export-Clixml -Path $OutputPath
            Write-Host "[*] Report saved to $OutputPath"
        }

        return $results
    }
    catch {
        $results.Status = "Failed"
        $results.Error = $_.Exception.Message
        Write-Error "Scan failed: $($_.Exception.Message)"
        return $results
    }
}
```

### 6.5 Fichier JSON final

```json
{
  "id": "fn_sec_001",
  "type": "function",
  "name": "Invoke-SecurityScan",
  "language": "PowerShell",
  "famille": "Security",
  "description": "Lance un scan de sécurité réseau avec options avancées (ports, banners, vulnérabilités)",
  "parameters": [
    {
      "name": "TargetHost",
      "datatype": "string",
      "required": true,
      "description": "IP ou FQDN cible"
    },
    {
      "name": "Ports",
      "datatype": "string",
      "required": false,
      "default": "\"22,80,443,3389\"",
      "description": "Ports à scanner (séparés par des virgules)"
    },
    {
      "name": "Depth",
      "datatype": "int",
      "required": false,
      "default": "2",
      "description": "Profondeur de scan (1=rapide, 2=moyen, 3=complet)"
    },
    {
      "name": "Credential",
      "datatype": "PSCredential",
      "required": false,
      "default": "$null",
      "description": "Credentials pour authentification"
    },
    {
      "name": "TimeoutSec",
      "datatype": "int",
      "required": false,
      "default": "30",
      "description": "Timeout en secondes par opération"
    },
    {
      "name": "OutputPath",
      "datatype": "string",
      "required": false,
      "default": "$ScanReportPath",
      "description": "Chemin pour sauvegarder le rapport (format XML)"
    }
  ],
  "returns": {
    "datatype": "PSObject",
    "description": "Objet contenant les résultats : TargetHost, OpenPorts, Vulnerabilities, DurationSec, Status"
  },
  "source": "function Invoke-SecurityScan { ... }",
  "tags": ["security", "scan", "audit", "network", "vulnerability"],
  "throws": ["TimeoutException", "ConnectionException"]
}
```

---

## 7. Création de variables associées

Les variables associées permettent de **paramétrer globalement** le comportement des fonctions.

### 7.1 Variables pour l'exemple

| Variable | Datatype | Default | Description |
|----------|----------|---------|-------------|
| `ScanReportPath` | string | `"C:\\Reports\\scan.xml"` | Chemin par défaut des rapports |
| `DefaultScanDepth` | int | `2` | Profondeur de scan par défaut |
| `SecurityScanTimeout` | int | `30` | Timeout global pour les scans |
| `KnownVulnerablePorts` | string[] | `["21","23","135","445"]` | Ports considérés comme dangereux |

### 7.2 Code JSON des variables

```json
{
  "id": "var_sec_001",
  "type": "variable",
  "name": "ScanReportPath",
  "language": "PowerShell",
  "datatype": "string",
  "default_value": "\"C:\\\\Reports\\\\security_scan.xml\"",
  "scope": "global",
  "description": "Chemin par défaut pour les rapports de scan",
  "tags": ["security", "reporting"]
},
{
  "id": "var_sec_002",
  "type": "variable",
  "name": "DefaultScanDepth",
  "language": "PowerShell",
  "datatype": "int",
  "default_value": "2",
  "scope": "global",
  "description": "Profondeur de scan par défaut (1=rapide, 2=moyen, 3=complet)",
  "tags": ["security", "config"]
},
{
  "id": "var_sec_003",
  "type": "variable",
  "name": "SecurityScanTimeout",
  "language": "PowerShell",
  "datatype": "int",
  "default_value": "30",
  "scope": "global",
  "description": "Timeout en secondes pour les opérations de scan",
  "tags": ["security", "timeout"]
},
{
  "id": "var_sec_004",
  "type": "variable",
  "name": "KnownVulnerablePorts",
  "language": "PowerShell",
  "datatype": "string[]",
  "default_value": "@('21','23','135','445','1433','3306')",
  "scope": "global",
  "description": "Liste des ports considérés comme potentiellement vulnérables",
  "tags": ["security", "vulnerability"]
}
```

---

## 8. Validation de la bibliothèque

### 8.1 Validation manuelle (jq)

```bash
# Vérifier la structure JSON
jq . my_library.json > /dev/null && echo "✓ JSON valide"

# Compter les fonctions
jq '.functions | length' my_library.json

# Compter les variables
jq '.variables | length' my_library.json

# Vérifier les IDs uniques
jq '[.functions[].id, .variables[].id] | group_by(.) | map(select(length>1))[]' my_library.json
```

### 8.2 Validation avec cf_lib_manager

```bash
# Validation simple
python cf_lib_manager_black.py my_library.json validate

# Validation stricte (paramètres, types, etc.)
python cf_lib_manager_black.py my_library.json validate --strict

# Audit complet (références cassées)
python cf_lib_manager_black.py my_library.json audit

# Nettoyage automatique
python cf_lib_manager_black.py my_library.json clean --deep --fix-ids
```

### 8.3 Validation avec QwEdit

1. Ouvrez votre bibliothèque dans QwEdit
2. Cliquez sur **🔍 VALIDATE ALL** dans la toolbar
3. Corrigez les erreurs affichées

---

## 9. Test dans CodeForge

### 9.1 Charger la bibliothèque

1. Lancez CodeForge v2.0
2. Menu **FILE → Load Library** (ou `Ctrl+L`)
3. Sélectionnez votre `my_library.json`

### 9.2 Tester la fonction

1. Dans le panneau Library, double-cliquez sur `Invoke-SecurityScan`
2. Ajoutez une variable `ScanReportPath` depuis la bibliothèque
3. Connectez les ports :

```
[Variable] ScanReportPath   ●────● OutputPath  (Invoke-SecurityScan)
[Variable] DefaultScanDepth ●────● Depth       (Invoke-SecurityScan)
```

4. Créez un flux d'exécution :

```
[Début] → [Invoke-SecurityScan] → [Fin]
```

5. Générez le code (**F5**)

### 9.3 Code généré (exemple)

```powershell
# GeneratedProgram.ps1 — Generated by CODEFORGE v2.0
#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Variables
$ScanReportPath   = "C:\\Reports\\security_scan.xml"
$DefaultScanDepth = 2

# Functions
function Invoke-SecurityScan { ... }

# Main Execution
Write-Host "[INFO] Starting GeneratedProgram"

$result = Invoke-SecurityScan -TargetHost "192.168.1.10" `
    -Depth $DefaultScanDepth `
    -OutputPath $ScanReportPath

if ($result.Status -eq "Completed") {
    Write-Host "✅ Scan completed. Open ports: $($result.OpenPorts -join ', ')"
} else {
    Write-Error "Scan failed: $($result.Error)"
}

Write-Host "[INFO] GeneratedProgram completed."
```

---

## 10. Bonnes pratiques & Checklist

### Checklist avant publication

- [ ] `metadata.validation_status` = `"APPROVED"`
- [ ] Tous les `id` sont uniques
- [ ] Chaque fonction a une `description` claire
- [ ] Les `parameters` ont des noms explicites et des `datatype` valides
- [ ] Les paramètres requis (`required: true`) ont une valeur par défaut ou seront fournis
- [ ] Le code `source` est syntaxiquement correct
- [ ] Les `tags` sont pertinents
- [ ] Les `variables` associées sont définies dans la même bibliothèque
- [ ] La bibliothèque passe `validate --strict`

### Conventions de nommage

| Élément | Convention | Exemple |
|---------|------------|---------|
| ID fonction | `fn_{famille}_{numéro}` | `fn_sec_001` |
| ID variable | `var_{famille}_{numéro}` | `var_sec_001` |
| Nom fonction | Verbe-Nom (PascalCase) | `Invoke-SecurityScan` |
| Nom variable | PascalCase | `ScanReportPath` |
| Famille | Capitalized | `Security`, `Logging`, `Network` |

### Datatypes autorisés

| Datatype | PowerShell | C# | JavaScript |
|----------|------------|----|------------|
| string | ✓ | ✓ | ✓ |
| int | ✓ | ✓ | ✓ |
| bool | ✓ | ✓ | ✓ |
| PSCredential | ✓ | ✗ | ✗ |
| string[] | ✓ | ✓ | ✓ |
| hashtable | ✓ | ✗ | ✗ |
| object | ✓ | ✓ | ✓ |
| DateTime | ✓ | ✓ | ✓ |
| void | ✓ | ✓ | ✗ |

---

## 11. Dépannage

### Problème : "JSON decode error"

**Cause :** Fichier mal formé (virgule en trop, guillemets manquants)

**Solution :**

```bash
# Avec Python
python -m json.tool my_library.json > /dev/null

# Avec jq
jq . my_library.json > /dev/null
```

### Problème : "ID already exists"

**Cause :** ID dupliqué dans `functions` ou `variables`

**Solution :**

```bash
python cf_lib_manager_black.py my_library.json clean --fix-ids
```

### Problème : "Unknown datatype 'xxx'"

**Cause :** Utilisation d'un type non standard

**Solution :** Remplacer par un type de la liste autorisée (section 10), ou l'ajouter à `VALID_DATATYPES`

### Problème : La fonction n'apparaît pas dans CodeForge

**Cause :** Mauvaise structure ou filtre de langue actif

**Solution :**

1. Vérifier que `language` correspond à la langue sélectionnée dans CodeForge
2. Vérifier que `"type": "function"` est présent
3. Recharger la bibliothèque (`Ctrl+L`)

---

## Conclusion

Vous savez maintenant créer une bibliothèque CodeForge complète :

- ✅ Manuellement (JSON brut)
- ✅ Via `cf_lib_manager` (CLI)
- ✅ Via `QwEdit` (GUI)

La fonction `Invoke-SecurityScan` et ses variables associées sont prêtes à être utilisées dans vos workflows CodeForge.

---

*INGEN Systems · DSI · CodeForge Library Creation*
