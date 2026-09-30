\# Supervision Réseau



Application web de supervision réseau développée en \*\*Python/Flask\*\*. Elle permet de surveiller en temps réel l'état de disponibilité d'équipements réseau (serveurs, routeurs, switches, imprimantes...) via un système de ping intelligent avec fallback TCP.



!\[Python](https://img.shields.io/badge/Python-3.13-blue)

!\[Flask](https://img.shields.io/badge/Flask-3.1-green)

!\[License](https://img.shields.io/badge/License-MIT-yellow)



\---



\## Fonctionnalités



\- \*\*Ping intelligent\*\* : test ICMP + fallback automatique TCP (443 puis 80) pour fonctionner même sur les réseaux qui bloquent l'ICMP

\- \*\*Tableau de bord\*\* : vue d'ensemble avec statistiques (total, en ligne, hors ligne, taux de disponibilité)

\- \*\*Vérification automatique\*\* : scheduler qui vérifie tous les équipements toutes les 5 minutes

\- \*\*Historique\*\* : consultation de toutes les vérifications passées avec filtres (équipement, période)

\- \*\*Alertes\*\* : notification automatique lors des changements d'état (up/down), avec système de lecture

\- \*\*Base de données SQLite\*\* : stockage persistant via SQLAlchemy

\- \*\*Interface moderne\*\* : Bootstrap 5, responsive, badges colorés



\---



\## Stack technique



| Composant | Technologie |

|-----------|-------------|

| \*\*Langage\*\* | Python 3.13 |

| \*\*Framework web\*\* | Flask 3.1 |

| \*\*Base de données\*\* | SQLite + SQLAlchemy |

| \*\*Scheduler\*\* | `schedule` |

| \*\*Templates\*\* | Jinja2 + Bootstrap 5 |

| \*\*Ping\*\* | `subprocess` (ICMP) + `socket` (TCP) |



\---



\## Installation



\### Prérequis

\- Python 3.10+

\- pip



\### Étapes



```bash

\# 1. Cloner le projet

git clone https://github.com/A-SIDIKI/supervision-reseau.git

cd supervision-reseau



\# 2. Créer un environnement virtuel

python -m venv venv



\# Windows

venv\\Scripts\\activate



\# Mac/Linux

source venv/bin/activate



\# 3. Installer les dépendances

pip install -r requirements.txt



\# 4. Lancer l'application

python app.py

