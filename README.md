# Analyse de Trading

Cette application permet d'analyser des fichiers Excel ou CSV contenant des données de trading et de générer des statistiques détaillées.

## Fonctionnalités

- Import de fichiers Excel (.xlsx) ou CSV
- Calcul du PnL total
- Statistiques par mois
- Statistiques journalières
- Analyse par asset
- Visualisations graphiques

## Prérequis

- Python 3.8 ou supérieur
- Les dépendances listées dans `requirements.txt`

## Installation

1. Clonez ce dépôt
2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

1. Lancez l'application :
```bash
streamlit run app.py
```

2. Dans l'interface web :
   - Cliquez sur "Choisissez un fichier" pour sélectionner votre fichier Excel ou CSV
   - Les données seront automatiquement analysées et les statistiques affichées

## Format des données

Le fichier d'entrée doit contenir au minimum les colonnes suivantes :
- Date
- Asset
- PnL

## Exemple de structure de données

| Date       | Asset | PnL   |
|------------|-------|-------|
| 2023-01-01 | BTC   | 100   |
| 2023-01-02 | ETH   | -50   | 