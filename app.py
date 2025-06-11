import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import calendar

# Configuration du thème
st.set_page_config(
    page_title="Analyse de Trading",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style personnalisé
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stMetric > div {
        color: #2c3e50;
    }
    .stMetric > div > div {
        font-size: 1.5rem;
        font-weight: bold;
    }
    .stMetric > div > div[data-testid="stMetricValue"] {
        color: #2ecc71;
    }
    .stMetric > div > div[data-testid="stMetricValue"][style*="color: rgb(231, 76, 60)"] {
        color: #e74c3c !important;
    }
    .css-1d391kg {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

def format_pnl(value):
    """Formate le PnL avec un + pour les valeurs positives"""
    return f"+{value:.2f}" if value > 0 else f"{value:.2f}"

def format_percentage(value):
    """Formate un pourcentage"""
    return f"{value:.1f}%"

def load_data(uploaded_file):
    """Charge les données depuis un fichier Excel ou CSV"""
    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)
    
    # Renommer les colonnes pour correspondre à notre format
    column_mapping = {
        'Heure': 'Date',
        'Paire de cc': 'Asset',
        'Montant': 'PnL'
    }
    
    # Ne renommer que les colonnes qui existent
    existing_columns = {k: v for k, v in column_mapping.items() if k in df.columns}
    df = df.rename(columns=existing_columns)
    
    # Convertir la date en format datetime
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
    
    return df

def calculate_monthly_pnl(df, selected_year=None):
    """Calcule le PnL mensuel avec tous les mois de l'année"""
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    
    # Si une année est sélectionnée, filtrer les données
    if selected_year:
        df = df[df['Year'] == selected_year]
    
    # Créer un DataFrame avec tous les mois
    all_months = pd.DataFrame({
        'Month': range(1, 13),
        'Month_Name': [calendar.month_name[i] for i in range(1, 13)]
    })
    
    # Calculer le PnL par mois
    monthly_pnl = df.groupby('Month')['PnL'].sum().reset_index()
    
    # Fusionner avec tous les mois
    monthly_pnl = all_months.merge(monthly_pnl, on='Month', how='left')
    monthly_pnl['PnL'] = monthly_pnl['PnL'].fillna(0)
    
    return monthly_pnl

def calculate_daily_pnl(df):
    """Calcule le PnL journalier"""
    daily_pnl = df.groupby('Date')['PnL'].sum().reset_index()
    return daily_pnl

def calculate_asset_pnl(df):
    """Calcule le PnL par asset"""
    if 'Asset' not in df.columns:
        return None
    asset_pnl = df.groupby('Asset')['PnL'].sum().reset_index()
    return asset_pnl

def create_pnl_bar_chart(df, x, y, title, labels=None):
    """Crée un graphique en barres avec couleurs conditionnelles"""
    colors = ['#2ecc71' if val >= 0 else '#e74c3c' for val in df[y]]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df[x],
        y=df[y],
        marker_color=colors,
        text=[format_pnl(val) for val in df[y]],
        textposition='auto',
    ))
    
    fig.update_layout(
        title=title,
        showlegend=False,
        xaxis_title=labels.get(x, x) if labels else x,
        yaxis_title=labels.get(y, y) if labels else y,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(
            family="Arial",
            size=12,
            color="#2c3e50"
        ),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig

def calculate_win_loss_stats(df):
    """Calcule les statistiques de gains/pertes"""
    stats = {}
    
    # Séparer les trades gagnants et perdants
    winning_trades = df[df['PnL'] > 0]
    losing_trades = df[df['PnL'] < 0]
    neutral_trades = df[df['PnL'] == 0]
    
    # Nombre de trades
    stats['total_trades'] = len(df)
    stats['winning_trades'] = len(winning_trades)
    stats['losing_trades'] = len(losing_trades)
    stats['neutral_trades'] = len(neutral_trades)
    
    # Win rate
    stats['win_rate'] = (stats['winning_trades'] / stats['total_trades'] * 100) if stats['total_trades'] > 0 else 0
    
    # PnL moyen
    stats['avg_win'] = winning_trades['PnL'].mean() if len(winning_trades) > 0 else 0
    stats['avg_loss'] = losing_trades['PnL'].mean() if len(losing_trades) > 0 else 0
    
    # PnL maximum et minimum
    stats['max_win'] = winning_trades['PnL'].max() if len(winning_trades) > 0 else 0
    stats['max_loss'] = losing_trades['PnL'].min() if len(losing_trades) > 0 else 0
    
    # Profit factor (somme des gains / somme des pertes en valeur absolue)
    total_wins = winning_trades['PnL'].sum()
    total_losses = abs(losing_trades['PnL'].sum())
    stats['profit_factor'] = total_wins / total_losses if total_losses != 0 else float('inf')
    
    return stats

def main():
    st.title("📊 Analyse de Trading")
    
    uploaded_file = st.file_uploader("Choisissez un fichier Excel ou CSV", type=['xlsx', 'csv'])
    
    if uploaded_file is not None:
        try:
            df = load_data(uploaded_file)
            
            # Afficher les données brutes dans une carte
            with st.expander("Données brutes", expanded=False):
                st.dataframe(df)
            
            # Statistiques générales dans une carte
            st.subheader("📈 Statistiques générales")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "PnL Total",
                    format_pnl(df['PnL'].sum()),
                    delta=None
                )
            
            with col2:
                st.metric(
                    "Nombre d'opérations",
                    len(df),
                    delta=None
                )
            
            with col3:
                st.metric(
                    "PnL Moyen par opération",
                    format_pnl(df['PnL'].mean()),
                    delta=None
                )
            
            # Analyse des gains/pertes dans une carte
            st.subheader("📊 Analyse des Gains/Pertes")
            stats = calculate_win_loss_stats(df)
            
            # Première ligne de statistiques
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Win Rate",
                    format_percentage(stats['win_rate']),
                    delta=None
                )
            
            with col2:
                st.metric(
                    "Profit Factor",
                    f"{stats['profit_factor']:.2f}",
                    delta=None
                )
            
            with col3:
                st.metric(
                    "Trades Gagnants",
                    f"{stats['winning_trades']}",
                    f"({format_percentage(stats['winning_trades']/stats['total_trades']*100)})"
                )
            
            with col4:
                st.metric(
                    "Trades Perdants",
                    f"{stats['losing_trades']}",
                    f"({format_percentage(stats['losing_trades']/stats['total_trades']*100)})"
                )
            
            # Deuxième ligne de statistiques
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Gain Moyen",
                    format_pnl(stats['avg_win']),
                    delta=None
                )
            
            with col2:
                st.metric(
                    "Perte Moyenne",
                    format_pnl(stats['avg_loss']),
                    delta=None
                )
            
            with col3:
                st.metric(
                    "Plus Gros Gain",
                    format_pnl(stats['max_win']),
                    delta=None
                )
            
            with col4:
                st.metric(
                    "Plus Grosse Perte",
                    format_pnl(stats['max_loss']),
                    delta=None
                )
            
            # Graphiques dans une carte
            st.subheader("📈 Visualisations")
            
            # Sélecteur d'année pour PnL Mensuel
            years = sorted(df['Date'].dt.year.unique())
            if len(years) > 1:
                selected_year = st.selectbox("Sélectionner l'année", years)
            else:
                selected_year = years[0] if years else None
            
            # PnL Mensuel
            monthly_pnl = calculate_monthly_pnl(df, selected_year)
            fig_monthly = create_pnl_bar_chart(
                monthly_pnl, 'Month_Name', 'PnL',
                f'PnL Mensuel {selected_year}',
                {'PnL': 'Profit/Perte', 'Month_Name': 'Mois'}
            )
            st.plotly_chart(fig_monthly, use_container_width=True)
            
            # PnL Journalier
            daily_pnl = calculate_daily_pnl(df)
            fig_daily = create_pnl_bar_chart(
                daily_pnl, 'Date', 'PnL',
                'PnL Journalier',
                {'PnL': 'Profit/Perte', 'Date': 'Date'}
            )
            st.plotly_chart(fig_daily, use_container_width=True)
            
            # PnL par Asset
            asset_pnl = calculate_asset_pnl(df)
            if asset_pnl is not None:
                fig_asset = create_pnl_bar_chart(
                    asset_pnl, 'Asset', 'PnL',
                    'PnL par Asset',
                    {'PnL': 'Profit/Perte', 'Asset': 'Paire'}
                )
                st.plotly_chart(fig_asset, use_container_width=True)
            
        except Exception as e:
            st.error(f"Une erreur est survenue lors du traitement du fichier : {str(e)}")

if __name__ == "__main__":
    main() 