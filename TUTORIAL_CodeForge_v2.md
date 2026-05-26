# 🛠️ CodeForge v2.0 — Tutoriel Complet
## *INGEN Systems Workstation · Guide Opérateur Autorisé*

---

```
╔═══════════════════════════════════════════════════════════════════╗
║  CODEFORGE v2.0  —  INGEN SYSTEMS WORKSTATION                    ║
║  OPERATOR FIELD MANUAL  //  CLASSIFICATION: INTERNAL USE         ║
║  *** PERSONNEL AUTORISÉ SEULEMENT ***                            ║
╚═══════════════════════════════════════════════════════════════════╝
```

> **Objectif de ce tutoriel**
> Conduire un opérateur, de zéro à un projet fonctionnel générant du code PowerShell propre, en passant par toutes les étapes de l'interface : chargement de la bibliothèque, composition du graphe nodal, connexions de flux, génération, et sauvegarde.
>
> **Cas d'usage fil rouge** : Créer un workflow d'**onboarding Active Directory** — vérification de prérequis, création d'un utilisateur AD, affectation de droits, envoi d'une notification, journalisation.

---

## Table des matières

1. [Prérequis & Installation](#1-prérequis--installation)
2. [Démarrage & Séquence de Boot](#2-démarrage--séquence-de-boot)
3. [Anatomie de l'Interface](#3-anatomie-de-linterface)
4. [Charger une Bibliothèque](#4-charger-une-bibliothèque)
5. [Explorer la Bibliothèque](#5-explorer-la-bibliothèque)
6. [Créer un Nouveau Projet](#6-créer-un-nouveau-projet)
7. [Ajouter des Blocs au Canvas](#7-ajouter-des-blocs-au-canvas)
8. [Connecter les Nœuds (Flux & Données)](#8-connecter-les-nœuds-flux--données)
9. [Ajouter des Variables Globales](#9-ajouter-des-variables-globales)
10. [Utiliser un Template](#10-utiliser-un-template)
11. [Auto-Layout du Graphe](#11-auto-layout-du-graphe)
12. [Inspecter un Bloc — Panneau Propriétés](#12-inspecter-un-bloc--panneau-propriétés)
13. [Générer le Code](#13-générer-le-code)
14. [Sauvegarder le Projet](#14-sauvegarder-le-projet)
15. [Rouvrir un Projet Existant](#15-rouvrir-un-projet-existant)
16. [Raccourcis Clavier](#16-raccourcis-clavier)
17. [Comprendre le Format `.cfproj`](#17-comprendre-le-format-cfproj)
18. [Étendre la Bibliothèque JSON](#18-étendre-la-bibliothèque-json)
19. [Bonnes Pratiques & Pièges Courants](#19-bonnes-pratiques--pièges-courants)
20. [Glossaire](#20-glossaire)

---

## 1. Prérequis & Installation

### Environnement recommandé

| Composant | Version minimale | Recommandé |
|---|---|---|
| Python | 3.8 | 3.11+ |
| PyQt5 | 5.12 | 5.15 |
| OS | Windows 10 / Linux | Manjaro / Windows 11 |
| RAM | 512 Mo libres | 2 Go |

### Installation des dépendances

```bash
# Via pip (tous OS)
pip install PyQt5

# Sur Manjaro / Arch Linux (recommandé)
sudo pacman -S python-pyqt5

# Sur Ubuntu / Debian
sudo apt install python3-pyqt5

# Vérification
python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')"
```

### Structure des fichiers attendue

Placez tous les fichiers dans le même répertoire de travail :

```
ingen-workstation/
├── codeforge_v2.py      ← Application principale
├── library.json         ← Catalogue de briques (fonctions + variables)
├── templates.json       ← Templates d'enchaînements pré-configurés
└── templates/           ← Dossier de templates additionnels (optionnel)
```

> **⚠️ Important** : `library.json` doit être dans le même dossier que `codeforge_v2.py`. L'application le charge automatiquement au démarrage.

---

## 2. Démarrage & Séquence de Boot

### Lancement

```bash
cd ingen-workstation/
python codeforge_v2.py
```

### Séquence de boot CRT

Au lancement, l'interface exécute une **séquence d'initialisation animée** dans la barre de statut, mimant le boot d'un terminal industriel :

```
INGEN SYSTEMS :: WORKSTATION BOOT SEQUENCE v3.1
Initializing CODEFORGE kernel...
Loading element parser... OK
Loading code generator... OK
Checking canvas subsystem... OK
Mounting library interface... OK
System ready. Welcome, operator.
```

Si `library.json` est trouvé dans le répertoire courant, il est chargé silencieusement pendant ce processus. La barre de statut affiche le nombre de fonctions et variables détectées.

> **💡 Tip** : L'horloge en temps réel dans la toolbar (`[ 2026-05-26 14:32:17 ]`) confirme que l'application est active et répond.

---

## 3. Anatomie de l'Interface

L'écran est organisé en **quatre zones fonctionnelles** :

```
┌─────────────────────────────────────────────────────────────────────┐
│  TOOLBAR  [⊞ LOAD LIB] [⊕ CTRL] [⚡ GENERATE] [↓ SAVE] [🗑 CLEAR] │
├──────────────┬──────────────────────────────┬───────────────────────┤
│              │                              │                       │
│   LIBRARY    │        CANVAS                │    PROPERTIES         │
│   EXPLORER   │    (Zone de composition)     │    (Inspecteur)       │
│              │                              │                       │
│  ⚙ FUNCTIONS│  [ Blocs draggables ]        │  onglet INFO          │
│  ◈ VARIABLES │  [ Connexions nodales ]      │  onglet SOURCE        │
│              │  [ Grille + scanline ]       │                       │
│  [SEARCH...] │                              │                       │
│  [ADD >]     │                              │                       │
│              ├──────────────────────────────┤                       │
│              │  OUTPUT / GENERATED CODE     │                       │
│              │  [LANG ▼] [NAME____] [⚡GEN] │                       │
│              │  < code colorisé >           │                       │
└──────────────┴──────────────────────────────┴───────────────────────┘
│  STATUSBAR : message système                    CANVAS: N blocks    │
└─────────────────────────────────────────────────────────────────────┘
```

### Zones détaillées

**① Library Explorer (gauche, ~300px)**
Arbre hiérarchique des éléments disponibles. Divisé en deux racines : `⚙ FUNCTIONS` et `◈ VARIABLES`. Filtrable par langue et par recherche textuelle.

**② Canvas (centre haut)**
L'espace de travail principal. Fond noir avec grille de points et scanline animée (effet phosphore CRT). Les blocs y sont positionnés librement et connectés par des arêtes orientées.

**③ Output Panel (centre bas)**
Éditeur de code avec colorisation syntaxique. Affiche le résultat de la génération. Permet de choisir la langue cible et le nom du programme.

**④ Properties Panel (droite, ~280px)**
Inspecteur contextuel du bloc sélectionné. Deux onglets : `INFO` (métadonnées, paramètres, types) et `SOURCE` (code source de la fonction avec highlight).

**⑤ Toolbar**
Accès rapide aux actions principales. La barre de menu (`FILE`, `EDIT`, `VIEW`, `HELP`) offre les mêmes fonctions avec raccourcis clavier.

---

## 4. Charger une Bibliothèque

La bibliothèque est le **catalogue de briques atomiques** à partir desquelles les workflows sont composés.

### Chargement automatique

Si `library.json` est dans le même répertoire que `codeforge_v2.py`, il est chargé automatiquement au démarrage. La barre de statut confirme :

```
✓  Library loaded: 8 functions, 6 variables
```

### Chargement manuel

Si vous avez plusieurs catalogues (ex: un par équipe ou domaine métier) :

1. Cliquez sur **`⊞ LOAD LIB`** dans la toolbar  
   *ou* menu **`FILE → Load Library...`**  
   *ou* raccourci **`Ctrl+L`**

2. Dans la boîte de dialogue, naviguez vers votre fichier `.json`

3. Sélectionnez et ouvrez — la bibliothèque se charge et remplace la précédente

> **⚠️ Attention** : Charger une nouvelle bibliothèque **ne supprime pas** les blocs déjà posés sur le canvas. Les blocs existants conservent leurs données intégrées.

---

## 5. Explorer la Bibliothèque

### Filtres disponibles

En haut du panneau Library, deux contrôles permettent de cibler les éléments :

```
[ / search elements...  ]   ← Recherche par nom ou famille (temps réel)
[ ALL          ▼        ]   ← Filtre par langage : ALL / CSharp / PowerShell / JavaScript
```

### Lire les informations d'un élément

**Survoler** un élément dans l'arbre affiche sa description en tooltip.

**Sélectionner** un élément (clic simple) met à jour le panneau Properties à droite avec ses métadonnées complètes :

- Pour une **fonction** : paramètres (requis/optionnels), types, valeur de retour, exceptions levées, tags
- Pour une **variable** : type de données, portée (local/global), valeur par défaut, tags

### Exemple d'inspection

Sélectionnez `New-ADUserDSI` dans l'arbre. Le panneau Properties affiche :

```
TYPE    : FUNCTION
NAME    : New-ADUserDSI
LANG    : PowerShell
FAMILY  : ActiveDirectory
DESC    : Crée un compte utilisateur Active Directory standardisé DSI

PARAMETERS (5):
  ✓ SamAccountName  : string
  ✓ DisplayName     : string
  ✓ Department      : string
  ○ OU              : string  = "OU=Users,DC=ingen,DC=local"
  ○ Credential      : PSCredential

RETURNS : bool
  True si la création a réussi

THROWS  : ActiveDirectoryException, UnauthorizedAccessException

TAGS    : activedirectory, users, creation, dsi
```

---

## 6. Créer un Nouveau Projet

### Depuis zéro

Menu **`FILE → New Project`** ou **`Ctrl+N`**.

Si le canvas contient des blocs, une confirmation est demandée :
```
Clear current canvas and start a new project?
[Yes]  [No]
```

Le canvas se vide, le panneau output est réinitialisé, et le titre de la fenêtre passe en `[New Project]`.

### Nommer le projet

Dans le panneau Output (bas du canvas), le champ **`NAME:`** définit le nom du programme généré. Entrez un nom PascalCase sans espaces :

```
NAME: [ OnboardingAD_Workflow ]
```

Ce nom sera utilisé comme nom de classe (C#), nom du script (`.ps1`), ou nom de la fonction principale (JavaScript).

### Choisir la langue cible

Le sélecteur **`LANG:`** détermine la syntaxe de génération :

```
LANG: [ PowerShell ▼ ]
```

> **💡 Tip** : La langue cible peut être changée à tout moment avant la génération. Seuls les blocs compatibles avec cette langue seront inclus dans le code généré.

---

## 7. Ajouter des Blocs au Canvas

### Méthode 1 — Double-clic dans la bibliothèque

Double-cliquez sur n'importe quel élément dans l'arbre Library. Le bloc apparaît sur le canvas à une position automatique calculée en grille.

### Méthode 2 — Sélection + bouton ADD

1. Cliquez (sélection simple) sur l'élément dans l'arbre
2. Cliquez sur le bouton **`⊕  ADD TO CANVAS`** en bas du panneau Library

### Méthode 3 — Glisser-déposer

Cliquez sur un élément dans l'arbre et glissez-le directement vers la position souhaitée sur le canvas.

### Déplacer un bloc

Cliquez et maintenez sur un bloc (le curseur passe en `✋`), puis faites-le glisser vers sa nouvelle position. Le bloc reste dans les limites du canvas.

### Supprimer un bloc

Cliquez sur le bouton **`✕`** en haut à droite du bloc, ou sélectionnez-le et appuyez sur **`Suppr`**.

### Anatomie d'un bloc

```
┌─── ⚙ New-ADUserDSI ─────────────────── [✕] ──┐
│  PowerShell  │  ActiveDirectory               │
│  → bool                                       │
│                                               │
│  ○ flow_in                      flow_out ○   │
│  ○ SamAccountName (string)                    │
│  ○ DisplayName (string)                       │
│  ○ Department (string)                        │
│  ○ OU (string)                                │
│                                               │
│  [ FUNCTION ]                                 │
└───────────────────────────────────────────────┘
```

- **Bande colorée gauche** : verte pour les fonctions, ambre pour les variables, cyan pour les structures de contrôle
- **Ports ronds (○)** : points de connexion — `flow_in`/`flow_out` pour l'ordonnancement, paramètres pour les données
- **Badge type** : rappel visuel du type de bloc

---

## 8. Connecter les Nœuds (Flux & Données)

C'est l'opération centrale de CodeForge. Les connexions transforment une collection de blocs isolés en un **graphe d'exécution orienté (DAG)**.

### Deux types de connexions

| Type | Port | Couleur | Rôle |
|---|---|---|---|
| **Flux d'exécution** | `flow_out` → `flow_in` | Rose/Magenta | Définit l'ordre d'exécution |
| **Données** | param sortie → param entrée | Vert/Ambre | Passe une valeur d'un bloc à l'autre |

### Créer une connexion de flux

1. Repérez le port `flow_out` (côté droit du bloc source)
2. **Cliquez** dessus — le port s'illumine, indiquant qu'une connexion est en cours
3. **Glissez** vers le port `flow_in` du bloc cible (côté gauche)
4. **Relâchez** — une courbe de Bézier apparaît entre les deux ports

```
┌─────────────────┐              ┌─────────────────┐
│  Write-SysLog   │              │ New-ADUserDSI   │
│                 │              │                 │
│      flow_out ●─┼──────────────┼─● flow_in       │
└─────────────────┘              └─────────────────┘
     "Log START"       exécuté       puis ceci
```

### Créer une connexion de données

Même principe, mais entre un **port de retour** d'un bloc et un **port de paramètre** d'un autre :

```
┌─────────────────────┐              ┌──────────────────────────┐
│  Get-ADCredential   │              │  New-ADUserDSI           │
│                     │              │                          │
│  returns: Credential●──────────────●─ Credential (param)     │
└─────────────────────┘              └──────────────────────────┘
```

### Supprimer une connexion

Cliquez sur la courbe de connexion pour la sélectionner (elle change de couleur), puis appuyez sur **`Suppr`**.

### Règles de validation

Le moteur refuse les connexions incompatibles :

| Situation | Comportement |
|---|---|
| Type source ≠ type destination | Port clignote en rouge, connexion refusée |
| Connexion créerait un cycle | Avertissement dans la status bar |
| Port `flow_in` déjà connecté | La connexion existante est remplacée |

---

## 9. Ajouter des Variables Globales

Les variables définissent les **paramètres d'environnement** du script : chemins, URLs, credentials, seuils.

### Depuis la bibliothèque

Dans l'arbre Library, dépliez **`◈ VARIABLES`** et double-cliquez sur la variable souhaitée. Elle apparaît sur le canvas avec un bloc ambre :

```
┌─── ◈ adminCredential ──────────────── [✕] ─┐
│  PSCredential  │  global                    │
│  = [Prompt]                                 │
│                                             │
│  [ VARIABLE ]                               │
└─────────────────────────────────────────────┘
```

### Connecter une variable à un paramètre

Le port de sortie de la variable (son "valeur") se connecte directement au port de paramètre d'une fonction qui attend ce type :

```
◈ adminCredential ●────────────────● Credential (New-ADUserDSI)
```

### Valeur par défaut vs. valeur connectée

- Si un paramètre est **connecté** à une variable, le générateur utilise la référence à la variable
- Si un paramètre est **non connecté**, le générateur utilise la valeur `default` définie dans `library.json`
- Si requis et non connecté, un commentaire `# TODO: provide value` est inséré

---

## 10. Utiliser un Template

Les templates sont des **enchaînements pré-composés**, prêts à l'emploi ou à personnaliser.

### Charger un template

Menu **`FILE → Open Template...`** (ou via la toolbar si disponible).

Sélectionnez `templates.json`. Un dialogue liste les templates disponibles :

```
▸ ONBOARDING (ActiveDirectory)
  Crée un utilisateur AD, affecte les droits, notifie, journalise

▸ AUDIT & DURCISSEMENT (Security)
  Scan ports, audit privilèges, rapport HTML

▸ DÉPLOIEMENT AUTOMATISÉ (DevOps/CI-CD)
  Clone Git, valide signatures, déploie sur IIS, notifie Teams

▸ SUPERVISION DE MODÈLE (MLOps)
  Vérifie data drift, réentraîne modèle, archive versions
```

Sélectionnez **`ONBOARDING (ActiveDirectory)`** et cliquez **`LOAD`**.

Le canvas se peuple automatiquement avec les blocs du template, déjà connectés dans le bon ordre d'exécution. Le tout est prêt à être personnalisé.

### Personnaliser un template

Après chargement, vous pouvez :
- **Ajouter** des blocs supplémentaires depuis la bibliothèque
- **Supprimer** des blocs non pertinents (le reste du graphe se reconnecte)
- **Modifier** les valeurs de paramètres en éditant les variables
- **Exécuter** un Auto-Layout pour réorganiser proprement le graphe

---

## 11. Auto-Layout du Graphe

Quand le canvas devient dense ou qu'un template a été chargé, l'Auto-Layout réorganise les blocs automatiquement.

### Déclenchement

- Toolbar : bouton **`Auto-Layout`**
- Raccourci : **`Ctrl+L`**
- Menu : **`VIEW → Auto-Layout`**

### Algorithme de tri topologique

L'Auto-Layout applique un **tri topologique (Kahn's algorithm)** sur le DAG :

1. Identifie les nœuds sans `flow_in` (racines du graphe) → colonne 0
2. Pour chaque racine, suit les connexions `flow_out` → nœuds suivants → colonne 1
3. Continue jusqu'aux nœuds terminaux (sans `flow_out`)
4. Positionne les colonnes de gauche à droite avec un espacement régulier

**Résultat visuel** :

```
Avant Auto-Layout :          Après Auto-Layout :

  [LogStart]  [CreateUser]   [LogStart] → [CreateUser] → [SetRights]
        [SetRights]                              ↓
   [Notify]  [LogEnd]              [Notify] → [LogEnd]
```

> **💡 Tip** : Exécutez l'Auto-Layout **avant** la génération de code pour vérifier visuellement que l'ordre d'exécution est correct.

---

## 12. Inspecter un Bloc — Panneau Propriétés

Cliquez sur n'importe quel bloc du canvas pour l'inspecter dans le panneau droit.

### Onglet INFO

Affiche toutes les métadonnées structurées :

```
TYPE    : FUNCTION
NAME    : Send-AlertMail
ID      : fn_205
LANG    : PowerShell
FAMILY  : Notification
DESC    : Envoie un email d'alerte SMTP

PARAMETERS (4):
  ✓ To          : string
  ✓ Subject     : string
  ○ Body        : string  = ""
  ○ Credential  : PSCredential

RETURNS : bool
  True si l'envoi a réussi

THROWS  : SmtpException

TAGS    : email, smtp, notification, alerting
```

### Onglet SOURCE

Affiche le code source de la fonction avec **colorisation syntaxique** (mots-clés en cyan, chaînes en ambre, nombres en ambre clair, commentaires en vert foncé) :

```powershell
function Send-AlertMail {
    param(
        [string]$To,
        [string]$Subject,
        [string]$Body = "",
        [PSCredential]$Credential
    )
    try {
        Send-MailMessage -To $To -Subject $Subject `
            -Body $Body -Credential $Credential `
            -SmtpServer "smtp.ingen.local"
        return $true
    } catch {
        Write-Error $_.Exception.Message
        return $false
    }
}
```

---

## 13. Générer le Code

### Étape 1 — Configurer la génération

Dans le panneau Output :

```
LANG: [ PowerShell ▼ ]    NAME: [ OnboardingAD_Workflow ]
```

### Étape 2 — Lancer la génération

- Bouton **`⚡ GENERATE`** dans le panneau Output
- *ou* toolbar **`⚡ GENERATE`**
- *ou* touche **`F5`**

### Ce que fait le moteur

1. **Tri topologique** du DAG selon les connexions `flow_out` → `flow_in`
2. **Résolution des dépendances de données** : quels paramètres sont fournis par des connexions vs. des valeurs par défaut
3. **Injection des variables globales** en tête de script
4. **Émission des fonctions** dans l'ordre topologique
5. **Génération du bloc principal** (`Main()` en C#, bloc d'exécution en PS1, IIFE en JS)
6. **Insertion des structures de contrôle** aux bonnes positions dans le flux

### Exemple de sortie PowerShell

```powershell
# ═══════════════════════════════════════════════════
# OnboardingAD_Workflow.ps1  —  Generated by CODEFORGE v2.0
# INGEN Systems Workstation  /  2026-05-26 14:32:17
# ═══════════════════════════════════════════════════
#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ─── Variables ───────────────────────────────────
# Credential administrateur DSI
$adminCredential = [System.Management.Automation.PSCredential]::Empty

# ─── Functions ───────────────────────────────────
<#
.SYNOPSIS
    Journalise un message horodaté dans un fichier texte.
#>
function Write-SysLog { ... }

<#
.SYNOPSIS
    Crée un compte utilisateur Active Directory standardisé DSI.
#>
function New-ADUserDSI { ... }

# ─── Main Execution ──────────────────────────────
Write-Host "[INFO] Starting OnboardingAD_Workflow" -ForegroundColor Green

Write-SysLog -Message "ONBOARDING START" -Level "INFO"

$result = New-ADUserDSI `
    -SamAccountName $samAccountName `
    -DisplayName $displayName `
    -Department $department `
    -Credential $adminCredential

if ($result) {
    Set-ADUserRightsDSI -SamAccountName $samAccountName
    Send-AlertMail -To "admin@ingen.local" -Subject "Onboarding OK"
    Write-SysLog -Message "ONBOARDING COMPLETE" -Level "INFO"
} else {
    Write-SysLog -Message "ONBOARDING FAILED" -Level "ERROR"
}

Write-Host "[INFO] OnboardingAD_Workflow completed." -ForegroundColor Green
```

### Indicateurs de statut

Après génération, la barre de statut du panneau Output affiche :

```
Lines: 87  /  Chars: 3241  /  Lang: PowerShell
```

### Copier le code

Bouton **`⎘ COPY`** — copie l'intégralité du code dans le presse-papiers.

### Sauvegarder le code seul

Bouton **`↓ SAVE CODE`** ou menu `FILE → Save Code` — ouvre une boîte de dialogue pour sauvegarder le fichier `.ps1`, `.cs`, ou `.js` directement.

---

## 14. Sauvegarder le Projet

La sauvegarde de projet (`.cfproj`) préserve **l'intégralité de l'état** : bibliothèque, positions des blocs sur le canvas, connexions, et dernier code généré.

### Sauvegarde rapide

**`Ctrl+S`** ou toolbar **`↓ SAVE PROJ`**.

Si aucun chemin n'est défini (nouveau projet), la boîte `Save As` s'ouvre automatiquement.

### Sauvegarde sous un nouveau nom

Menu **`FILE → Save As...`** — permet de créer une variante du projet.

### Bonne pratique de nommage

```
projets/
├── onboarding_ad_v1.cfproj
├── onboarding_ad_v2_avec_validation.cfproj
└── audit_securite_q2_2026.cfproj
```

> **💡 Tip** : Sauvegardez avant chaque génération importante. Le format `.cfproj` est du JSON lisible — vous pouvez le versionner dans Git.

---

## 15. Rouvrir un Projet Existant

Menu **`FILE → Open Project...`** ou **`Ctrl+O`**.

Sélectionnez un fichier `.cfproj`. Le chargement :

1. Recharge la bibliothèque qui était active lors de la sauvegarde
2. Recrée tous les blocs à leurs positions exactes
3. Recrée toutes les connexions
4. Restaure la langue et le nom dans le panneau Output
5. Réaffiche le dernier code généré

Le titre de la fenêtre passe à `CODEFORGE v2.0  —  nom_du_fichier.cfproj`.

---

## 16. Raccourcis Clavier

| Raccourci | Action |
|---|---|
| `Ctrl+N` | Nouveau projet |
| `Ctrl+O` | Ouvrir projet |
| `Ctrl+S` | Sauvegarder projet |
| `Ctrl+L` | Charger bibliothèque / Auto-Layout |
| `Ctrl+Z` | Annuler (Undo-Tree) |
| `Ctrl+Y` | Rétablir (Undo-Tree) |
| `F5` | Générer le code |
| `Ctrl+Shift+C` | Copier le code généré |
| `Suppr` | Supprimer bloc ou connexion sélectionné(e) |
| `Clic + Drag` | Déplacer un bloc |
| `Double-clic` (library) | Ajouter un bloc au canvas |

---

## 17. Comprendre le Format `.cfproj`

Le fichier projet est du **JSON structuré**, versable dans Git et lisible à la main :

```json
{
  "codeforge_version": "2.0",
  "saved_at": "2026-05-26T14:32:17",

  "library": {
    "metadata": { ... },
    "functions": [ ... ],
    "variables": [ ... ]
  },

  "canvas": [
    {
      "block_id": "a1b2c3d4",
      "block_type": "function",
      "data": { "id": "fn_100", "name": "Write-SysLog", ... },
      "pos": { "x": 40, "y": 30 },
      "connections": {
        "flow_out": "e5f6g7h8",
        "params": {}
      }
    },
    {
      "block_id": "e5f6g7h8",
      "block_type": "function",
      "data": { "id": "fn_201", "name": "New-ADUserDSI", ... },
      "pos": { "x": 340, "y": 30 },
      "connections": {
        "flow_in": "a1b2c3d4",
        "flow_out": "i9j0k1l2",
        "params": {
          "Credential": "var_block_007"
        }
      }
    }
  ],

  "output": {
    "language": "PowerShell",
    "name": "OnboardingAD_Workflow",
    "code": "# ... dernier code généré ..."
  }
}
```

### Points clés du format

- `block_id` : UUID court généré à la création du bloc, stable pour les connexions
- `connections.flow_out` : référence le `block_id` du nœud suivant dans le flux
- `connections.params` : map `nom_param → block_id_source` pour les données
- `pos` : coordonnées pixels sur le canvas (origine = coin haut-gauche)

---

## 18. Étendre la Bibliothèque JSON

Ajouter une nouvelle fonction dans `library.json` suffit à la rendre disponible au prochain chargement.

### Structure minimale d'une fonction

```json
{
  "id": "fn_999",
  "type": "function",
  "name": "Invoke-SecurityScan",
  "language": "PowerShell",
  "famille": "Security",
  "description": "Lance un scan de vulnérabilités sur un hôte cible",
  "validation_status": "APPROVED",
  "parameters": [
    {
      "name": "TargetHost",
      "datatype": "string",
      "required": true,
      "description": "Nom FQDN ou IP de la cible"
    },
    {
      "name": "Depth",
      "datatype": "int",
      "required": false,
      "default": "2",
      "description": "Profondeur du scan (1=surface, 3=complet)"
    }
  ],
  "returns": {
    "datatype": "hashtable",
    "description": "Rapport de vulnérabilités"
  },
  "source": "function Invoke-SecurityScan {\n    param(\n        [string]$TargetHost,\n        [int]$Depth = 2\n    )\n    # TODO: implementation\n    return @{}\n}",
  "tags": ["security", "scan", "audit"],
  "throws": ["TimeoutException"]
}
```

### Structure minimale d'une variable

```json
{
  "id": "var_099",
  "type": "variable",
  "name": "smtpServer",
  "language": "PowerShell",
  "famille": "Network",
  "datatype": "string",
  "default_value": "\"smtp.company.local\"",
  "description": "Serveur SMTP pour les notifications",
  "scope": "global",
  "tags": ["smtp", "email", "network"]
}
```

### Datatypes acceptés (politique DSI)

| Datatype | Langage | Usage |
|---|---|---|
| `string` | Tous | Textes, chemins, noms |
| `int` | Tous | Entiers, compteurs, ports |
| `bool` | Tous | Flags, switches |
| `PSCredential` | PowerShell | Credentials sécurisés |
| `string[]` | PowerShell/C# | Listes de chaînes |
| `hashtable` | PowerShell | Structures clé-valeur |
| `object` | C# | Type générique |
| `Action` | C# | Délégués, callbacks |
| `Promise<object>` | JavaScript | Résultats async |

> **🔒 Règle de sécurité** : Ne jamais inclure de mots de passe, tokens ou secrets dans `default_value`. Utilisez `PSCredential` ou `"[SecureString]"` comme valeur symbolique.

---

## 19. Bonnes Pratiques & Pièges Courants

### ✅ Bonnes pratiques

**Commencer par définir les variables** avant les fonctions sur le canvas. Les variables en colonne 0 du DAG facilitent la lecture du graphe.

**Un template comme point de départ** : même si votre cas d'usage est différent, charger un template proche et le modifier est plus rapide que partir de zéro.

**Sauvegarder souvent** : `Ctrl+S` après chaque connexion importante. Le format `.cfproj` est léger et le versionnement Git est simple.

**Vérifier l'Auto-Layout avant génération** : si l'ordre visuel des blocs de gauche à droite correspond à l'ordre d'exécution souhaité, le code généré sera correct.

**Utiliser des noms de projet descriptifs** : `OnboardingAD_v2_WithValidation` plutôt que `Programme1`.

### ⚠️ Pièges courants

**Mélanger les langages** : le générateur filtre les blocs selon la langue cible. Un bloc PowerShell dans un projet C# sera ignoré. Assurez-vous que tous vos blocs partagent la même langue, ou utilisez le filtre de bibliothèque avant de composer.

**Oublier de connecter les flux** : des blocs non connectés par `flow_out`/`flow_in` sont techniquement des nœuds isolés. Le générateur les inclut mais leur ordre d'apparition dans le code sera déterminé par leur position spatiale — pas par une logique d'exécution. Connectez toujours les flux explicitement.

**Paramètres requis non fournis** : si une fonction a un paramètre `required: true` non connecté à une variable, le code généré contiendra un `# TODO: provide value` — le script ne sera pas exécutable en l'état.

**Cycles dans le DAG** : si A → B → A, le tri topologique échoue. Un message d'erreur apparaît dans la status bar. Supprimez la connexion créant le cycle.

**Noms de variables avec espaces** : dans `library.json`, les noms de variables ne doivent pas contenir d'espaces — ils seront utilisés directement comme identifiants dans le code généré.

---

## 20. Glossaire

| Terme | Définition |
|---|---|
| **DAG** | Directed Acyclic Graph — graphe orienté sans cycle. Structure de données sous-jacente du canvas CodeForge. |
| **Kata** | Dans la philosophie du framework, une brique atomique et immuable de la bibliothèque (fonction ou variable). |
| **Enchaînement** | Combinaison logique de plusieurs Katas pour accomplir un processus métier. Correspond à un projet ou template. |
| **Port** | Point de connexion sur un bloc. `flow_in`/`flow_out` pour l'ordonnancement, ports de paramètres pour les données. |
| **Connexion** | Arête orientée du DAG reliant deux ports compatibles. |
| **Auto-Layout** | Algorithme de réorganisation spatiale des blocs basé sur le tri topologique du DAG. |
| **Undo-Tree** | Système d'historique non-linéaire permettant d'annuler ou rétablir n'importe quelle action graphique. |
| **CodeGen Engine** | Moteur de génération de code : parcourt le DAG, résout les dépendances, émet le code cible. |
| **`.cfproj`** | Format de fichier projet CodeForge (JSON). Contient bibliothèque, état du canvas, connexions, et code généré. |
| **Validation APPROVED** | Statut de validation d'un composant de la bibliothèque DSI — indique un code audité et conforme aux normes. |
| **Scanline** | Effet visuel CRT sur le canvas — ligne horizontale animée simulant un écran phosphore. |
| **Tri topologique** | Algorithme ordonnant les nœuds d'un DAG tel que tout nœud apparaît avant ses successeurs. |

---

```
╔═══════════════════════════════════════════════════════════════════╗
║  FIN DU DOCUMENT                                                  ║
║  INGEN Systems · DSI · Documentation Technique Interne           ║
║  "Life... finds a way."                                           ║
╚═══════════════════════════════════════════════════════════════════╝
```

*© 2026 INGEN Systems. Propriété exclusive de la DSI. Usage interne uniquement.*
*Dernière mise à jour : 2026-05-26*
