# 🛠️ CodeForge v2.0 — INGEN Systems Workstation

> **Visual Program Composer & Node-Based CodeGen Engine** > *⚠️ ACCÈS RÉSERVÉ AU PERSONNEL AUTORISÉ — SECURE ENVIRONMENT*

## 🎯 Introduction, Buts et Concepts Fondamentaux

### 1. Pourquoi CodeForge v2.0 ? (Les Objectifs)

Dans les environnements d'infrastructure modernes (Hybride, Cloud, On-Premises), la gestion des scripts d'automatisation devient rapidement un défi critique. Les administrateurs système et ingénieurs DevOps se retrouvent souvent confrontés à :

* Des scripts "spaghetti" redondants, mal documentés ou contenant des identifiants en dur.
* Un manque de standardisation dans l'application des modules de sécurité et de journalisation.
* Une barrière à l'entrée pour les équipes de support (Niveau 1/2) qui doivent exécuter ou comprendre des automatisations complexes sans maîtriser la syntaxe pure de PowerShell ou C#.

**CodeForge v2.0** a été conçu par la DSI d'**INGEN Systems** pour résoudre ces problématiques. Son but principal est de **passer d'une approche de scripting textuel et isolé à une ingénierie de workflows standardisée, visuelle et assistée**.

En combinant la puissance de la programmation par blocs et la rigueur d'un compilateur piloté par les données, CodeForge permet de concevoir graphiquement des architectures de scripts robustes, 100 % conformes aux normes de sécurité de l'entreprise.

---

### 2. Les Concepts Clés du Framework

Pour utiliser et étendre CodeForge efficacement, il est essentiel de comprendre ses 4 piliers conceptuels :

#### A. Le Dataflow Orienté Graphe (DAG)

Au lieu d'écrire des lignes de code séquentielles, l'utilisateur assemble un **Graphe Orienté Acyclique (DAG)**.

* **Les Flux (`Flow`) :** Représentés par les ports verticaux (`flow_in` et `flow_out`). Ils dictent l'ordre d'exécution logique (l'ordonnancement) des blocs.
* **Les Données (`Data`) :** Représentés par les paramètres d'entrée et de sortie. Ils permettent de faire passer des valeurs (chaînes de caractères, entiers, objets complexes, identifiants) d'un bloc à un autre sans risque d'effets de bord ou de variables orphelines.

#### B. La Philosophie du "Kata" et de "l'Enchaînement"

Inspiré des arts martiaux, le framework applique une métrique de réutilisation stricte :

* **Le Kata (La Fonction / Variable) :** C'est la brique élémentaire immuable définie dans `library.json`. Une fonction (ex: `New-ADUserDSI`) fait une seule chose, mais elle la fait parfaitement, de manière sécurisée et validée.
* **L'Enchaînement (Le Template / Projet) :** C'est la combinaison logique de plusieurs Katas pour accomplir un processus métier complet (ex: *Onboarding*, *Audit de sécurité*). La puissance ne réside pas dans le script isolé, mais dans la flexibilité de l'assemblage.

#### C. Le Compilateur Temps Réel (*CodeGen Engine*)

Le moteur de CodeForge n'est pas un simple éditeur graphique : c'est un compilateur d'état. À chaque déplacement de bloc ou création de lien, le moteur analyse topologiquement le graphe pour vérifier la cohérence des types de données et régénérer instantanément un code propre, indenté, et directement exécutable en production (PowerShell ou C#).

#### D. L'Environnement Sécurisé et Validé (`APPROVED`)

Tout composant présent dans la bibliothèque possède un statut de validation. Le framework agit comme une barrière de sécurité : un opérateur ne peut pas injecter de code malveillant ou non conforme, car il est restreint aux composants audités par l'équipe d'architecture de la DSI.


## 📋 Présentation Générale

**CodeForge v2.0** est une station de travail avancée de composition visuelle de programmes et de génération de code orientée flux de données (*Dataflow*). Développée par la **DSI d'INGEN Systems**, elle permet aux administrateurs système, ingénieurs DevOps et professionnels MLOps d'assembler graphiquement des scripts et processus complexes sous forme de **blocs interconnectés (Noeuds/DAG)**.

Inspiré de la philosophie du judo, CodeForge applique le principe suivant :  
> *« Chaque fonction est un kata, chaque template est un enchaînement. C'est la combinaison qui fait la victoire. »*

L'application automatise la génération de code propre, typé et documenté en **PowerShell** et **C#**, tout en intégrant des fonctionnalités d'ergonomie avancées (Arbre de commandes Undo/Redo, Auto-Layout par solveur de graphes, et une interface rétro-futuriste à effet CRT).

---

## 🚀 Fonctionnalités Majeures

* **Éditeur de Graphes Nodal (Canvas) :** Glissez-déposez des fonctions et des variables, puis connectez leurs ports de flux (`flow_in` / `flow_out`) ou de données pour modéliser vos enchaînements logiques.
* **Génération de Code Temps Réel :** Compilateur dataflow intégré qui convertit instantanément le graphe visuel en script PowerShell ou code C# structuré, sans variables orphelines ni conflits de portée.
* **Bibliothèque de Composants (Library) :** Chargement dynamique de catalogues de fonctions et variables d'infrastructure validées (Gestion Active Directory, Sécurité, Réseau, Droits, Backups, etc.).
* **Solveur Auto-Layout DAG :** Algorithme de tri topologique intégré permettant de réorganiser automatiquement et proprement la disposition spatiale des blocs en un clic.
* **Arbre d'Annulation (Undo-Tree System) :** Système d'historique de commandes non-linéaire permettant d'annuler ou de rétablir n'importe quelle action graphique sans perte d'état.
* **Interface Terminal Spécialisée :** Esthétique "Cyberpunk/CRT Monitor" avec animations de chargement système au démarrage, monitoring de la mémoire et journalisation des événements de compilation.

---

## 📂 Structure du Dépôt

Le framework s'articule autour de trois composants principaux :


```text
├── codeforge_v2.py      # Code source de l'application principale (Interface PyQt5 & Moteur de Génération)
├── library.json         # Catalogue des briques de base (Fonctions et variables globales approuvées par la DSI)
├── templates.json       # Modèles d'enchaînements types prêts à l'emploi (Onboarding AD, Audit, CI/CD, MLOps)
└── README.md            # Cette documentation détaillée

```


## 🛠️ Installation et Démarrage

### Prérequis

* **Python 3.8+**
* **PyQt5** (Bibliothèque graphique)

### Installation des dépendances

Installez les dépendances nécessaires via `pip` :

```bash
pip install PyQt5

```

### Lancement de l'application

Exécutez simplement le script principal :

```bash
python codeforge_v2.py

```

*Note : Au lancement, l'application cherche automatiquement le fichier `library.json` dans son répertoire pour précharger la bibliothèque système DSI.*

---

## 📖 Guide d'Utilisation

### 1. Composants de l'Interface

L'écran est divisé en quatre zones clés :

1. **Panneau Latéral Gauche (Library Explorer) :** Liste les variables globales et les fonctions disponibles, classées par familles (ActiveDirectory, Security, Network, Logging...).
2. **Zone Centrale (Le Canvas) :** Espace de travail interactif où vous déposez vos blocs et créez les liaisons graphiques.
3. **Panneau Latéral Droit (Génération de code & Propriétés) :** Affiche l'inspecteur du bloc sélectionné ainsi que l'onglet **"Generated Code"** mis à jour dynamiquement.
4. **Barre de Statut (Console Terminal) :** Affiche l'état du compilateur et les messages système.

### 2. Manipulation des Blocs

* **Ajouter un bloc :** Double-cliquez sur une fonction ou une variable dans l'explorateur de gauche, ou faites un glisser-déposer vers le canvas.
* **Créer une connexion :** Cliquez sur le port de sortie d'un bloc (ex: `flow_out`) et glissez votre souris vers le port d'entrée d'un autre bloc (ex: `flow_in`).
* **Supprimer un élément :** Sélectionnez un bloc ou un lien et appuyez sur la touche `Suppr` (ou via le clic droit).
* **Auto-Layout :** Si votre graphe devient confus, cliquez sur le bouton **"Auto-Layout"** de la barre d'outils pour réaligner automatiquement vos blocs de gauche à droite selon l'ordre d'exécution logique.

---

## 📊 Modèle de Données (Library & Templates)

Le framework est entièrement basé sur une architecture JSON pilotée par les données.

### Exemple de Fonction (`library.json`)

Chaque fonction expose ses paramètres entrants, son type de retour, sa famille et ses tags :

```json
{
  "id": "fn_100",
  "type": "function",
  "name": "Write-SysLog",
  "language": "PowerShell",
  "famille": "Logging",
  "description": "Journalise un message horodaté dans un fichier texte.",
  "parameters": [
    { "name": "Message", "datatype": "string", "required": true },
    { "name": "Level", "datatype": "string", "required": false, "default": "INFO" }
  ],
  "returns": { "datatype": "void", "description": "" }
}

```

### Exemples de Templates Inclus (`templates.json`)

Le catalogue fournit des scénarios pré-configurés pour accélérer les opérations courantes :

* **ONBOARDING (ActiveDirectory) :** Enchaînement complet créant un utilisateur AD (`New-ADUserDSI`), lui affectant ses droits, envoyant un email de bienvenue (`Send-AlertMail`) et journalisant l'action (`Write-SysLog`).
* **AUDIT & DURCISSEMENT (Security) :** Scanne les ports ouverts, liste les privilèges administrateurs locaux et génère un rapport HTML d'anomalies.
* **DÉPLOIEMENT AUTOMATISÉ (DevOps/CI-CD) :** Clône un dépôt Git, valide la signature des scripts, déploie sur IIS/Serveurs cibles et notifie l'équipe sur Teams/Slack.
* **SUPERVISION DE MODÈLE (MLOps) :** Vérifie la dérive des données (*Data Drift*), réentraîne un modèle local en cas de besoin et archive les anciennes versions.

---

## 💻 Raccourcis Clavier Utiles

| Raccourci | Action |
| --- | --- |
| `Ctrl + Z` | Annuler la dernière action graphique |
| `Ctrl + Y` | Rétablir l'action annulée |
| `Ctrl + L` | Exécuter l'Auto-Layout automatique (Solveur DAG) |
| `Ctrl + S` | Sauvegarder le projet actuel au format `.cfproj` |
| `Ctrl + O` | Ouvrir un projet existant |
| `Suppr` / `Delete` | Supprimer le bloc ou la connexion sélectionné(e) |

---

## 🔒 Spécifications de Sécurité & Validation

Le catalogue de fonctions (`library.json`) porte la mention **`"validation_status": "APPROVED"`**. Toute modification ou ajout de fonction dans le référentiel doit respecter les règles suivantes :

1. **Strict Typage :** Les types de données (`datatype`) acceptés sont restreints à : `string`, `int`, `bool`, `PSCredential`, `string[]`, `hashtable`.
2. **Gestion des Erreurs :** Toutes les fonctions de la bibliothèque intègrent des blocs `try/catch` natifs avec remontée d'alertes centralisée.
3. **Aucun Hardcoding :** Les valeurs sensibles (mots de passe, tokens) doivent obligatoirement transiter via des variables de type `PSCredential` ou être lues depuis le gestionnaire de secrets d'infrastructure.

---

## 🤝 Contribution & Maintenance

Ce framework est maintenu par la **DSI — INGEN Systems**.

Pour toute demande de mise à jour du catalogue de fonctions globales ou signalement de bug sur le moteur de rendu graphique, veuillez ouvrir une *Issue* sur ce dépôt ou contacter l'équipe d'architecture DevOps.

---

*© 2026 INGEN Systems. Propriété exclusive de la DSI. Usage interne uniquement.*
