import os
import sys
import json
import html
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from dotenv import load_dotenv

from styles.main_css import MAIN_CSS
from agents.executive_agent import ExecutiveAgent
from agents.finance_agent import FinanceAgent
from agents.sales_agent import SalesAgent
from agents.shopify_ai_agent import ShopifyAIAgent
from ml.sales_forecast import SalesForecast
from ml.forecast_chart import ForecastChart
from database.db import create_tables, create_tenant, create_user
from services.auth_service import (
    authenticate_user,
    bootstrap_admin_user,
    create_access_token,
    hash_password,
)
from services.plan_catalog import PLAN_CATALOG, TRIAL_DAYS, get_plan
from services.pdf_service import PDFService


st.set_page_config(
    page_title="AI Shopify Revenue Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv(BASE_DIR / ".env")

try:
    st.set_option("client.showErrorDetails", False)
except Exception:
    pass

PLOTLY_CONFIG = {
    "staticPlot": True,
    "displayModeBar": False,
    "responsive": True,
}


API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")
API_CONSULT_URL = f"{API_BASE_URL}/consult"
API_HISTORY_URL = f"{API_BASE_URL}/history"

REPORT_PATH = BASE_DIR / "reports" / "relatorio_executivo.pdf"

CHART_COLORS = [
    "#2563EB",
    "#7C3AED",
    "#06B6D4",
    "#10B981",
    "#F59E0B",
    "#EF4444",
]

st.markdown(
    """
    <meta name="google" content="notranslate">
    <div class="notranslate" translate="no"></div>
    """,
    unsafe_allow_html=True,
)

st.markdown(MAIN_CSS, unsafe_allow_html=True)

APP_FALLBACK_CSS = r"""
<style>
html, body, .stApp {
    translate: no;
}
.notranslate {
    translate: no;
}
.executive-status-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 10px;
    margin-bottom: 14px;
    padding: 12px 14px;
    border-radius: 16px;
    background:
        radial-gradient(circle at top left, rgba(37,99,235,0.13), transparent 34%),
        linear-gradient(135deg, rgba(15,23,42,0.96), rgba(30,41,59,0.92));
    border: 1px solid rgba(96,165,250,0.16);
    box-shadow: 0 10px 26px rgba(0,0,0,0.24), 0 0 20px rgba(37,99,235,0.06);
}
.executive-status-item {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 11px;
    border-radius: 999px;
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.06);
}
.executive-status-dot {
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: #4ADE80;
    box-shadow: 0 0 12px rgba(74,222,128,0.90);
}
.executive-status-text {
    color: #E2E8F0 !important;
    font-size: 10.5px;
    font-weight: 900;
    letter-spacing: 0.85px;
    text-transform: uppercase;
    white-space: nowrap;
}
.nav-card {
    background: rgba(15,23,42,0.72);
    border: 1px solid rgba(147,197,253,0.12);
    border-radius: 18px;
    padding: 12px;
    margin: 12px 0;
}
.nav-title {
    color: #93C5FD !important;
    font-size: 10px;
    font-weight: 900;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

/* ===== HARDENED APP PATCH ===== */
.enterprise-card .enterprise-desc,
.enterprise-card .enterprise-title,
.enterprise-card .enterprise-value {
    background: transparent !important;
    color: inherit !important;
    border: none !important;
}
div[data-testid="stMarkdownContainer"] code {
    white-space: normal !important;
}

/* ===== STATIC CHARTS: NO PLOTLY DOM ===== */
.static-chart-card {
    background: linear-gradient(145deg, rgba(15,23,42,0.96), rgba(30,41,59,0.92));
    border: 1px solid rgba(147,197,253,0.14);
    border-radius: 22px;
    padding: 18px;
    margin-top: 10px;
    box-shadow: 0 12px 32px rgba(0,0,0,0.28);
}
.static-bar-row {
    display: grid;
    grid-template-columns: 130px 1fr 110px;
    gap: 12px;
    align-items: center;
    margin: 12px 0;
}
.static-bar-label {
    color: #CBD5E1;
    font-size: 12px;
    font-weight: 800;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.static-bar-track {
    height: 16px;
    border-radius: 999px;
    background: rgba(148,163,184,0.14);
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.05);
}
.static-bar-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #2563EB, #7C3AED, #06B6D4);
    box-shadow: 0 0 18px rgba(96,165,250,0.25);
}
.static-bar-value {
    color: #E5E7EB;
    font-size: 12px;
    font-weight: 900;
    text-align: right;
}
.static-donut-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 312px;
}
.static-donut {
    width: 238px;
    height: 238px;
    border-radius: 50%;
    position: relative;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.08), 0 0 34px rgba(37,99,235,0.15);
}
.static-donut::after {
    content: "Revenue\A Distribution";
    white-space: pre;
    position: absolute;
    inset: 62px;
    border-radius: 50%;
    background: #0F172A;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #F8FAFC;
    font-size: 15px;
    font-weight: 900;
    text-align: center;
    line-height: 1.25;
    box-shadow: inset 0 0 20px rgba(0,0,0,0.34);
}
.static-legend {
    margin-top: 14px;
}
.static-legend-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    margin: 9px 0;
    color: #CBD5E1;
    font-size: 12px;
}
.static-legend-left {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
}
.static-dot {
    width: 10px;
    height: 10px;
    border-radius: 999px;
    flex: 0 0 auto;
}
.static-gauge {
    width: 230px;
    height: 230px;
    border-radius: 50%;
    margin: 0 auto;
    position: relative;
    box-shadow: 0 0 34px rgba(96,165,250,0.15), inset 0 0 0 1px rgba(255,255,255,0.08);
}
.static-gauge::after {
    content: "";
    position: absolute;
    inset: 26px;
    border-radius: 50%;
    background: #0F172A;
    box-shadow: inset 0 0 20px rgba(0,0,0,0.36);
}
.static-gauge-value {
    position: absolute;
    inset: 0;
    z-index: 2;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #FFFFFF;
    font-size: 34px;
    font-weight: 950;
}
.static-gauge-label {
    color: #93C5FD;
    font-size: 10px;
    font-weight: 900;
    letter-spacing: 1px;
    margin-top: 6px;
    text-transform: uppercase;
}


/* ===== ENTERPRISE BUTTON REFINEMENT ===== */
div[data-testid="stButton"] > button,
div[data-testid="stFormSubmitButton"] > button,
div[data-testid="stDownloadButton"] > button {
    min-height: 40px !important;
    height: 40px !important;
    padding: 0 18px !important;
    border-radius: 12px !important;
    border: 1px solid rgba(96,165,250,0.36) !important;
    background: linear-gradient(135deg, #2563EB 0%, #6D28D9 100%) !important;
    color: #F8FAFC !important;
    font-size: 13px !important;
    font-weight: 800 !important;
    letter-spacing: 0.1px !important;
    line-height: 1 !important;
    white-space: nowrap !important;
    box-shadow: 0 8px 18px rgba(37,99,235,0.18) !important;
    transition: all 140ms ease !important;
}
div[data-testid="stButton"] > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover,
div[data-testid="stDownloadButton"] > button:hover {
    transform: translateY(-1px) !important;
    border-color: rgba(147,197,253,0.52) !important;
    box-shadow: 0 10px 22px rgba(37,99,235,0.24) !important;
    color: #FFFFFF !important;
}
div[data-testid="stButton"] > button:active,
div[data-testid="stFormSubmitButton"] > button:active,
div[data-testid="stDownloadButton"] > button:active {
    transform: translateY(0) !important;
}
div[data-testid="stButton"] > button:disabled,
div[data-testid="stFormSubmitButton"] > button:disabled {
    background: rgba(148,163,184,0.14) !important;
    color: rgba(226,232,240,0.48) !important;
    border-color: rgba(148,163,184,0.18) !important;
    box-shadow: none !important;
}


/* Compact Executive Advisor Actions */
.copilot-prompt-label {
    color: #94A3B8 !important;
    font-size: 11px !important;
    font-weight: 800 !important;
    margin: 6px 0 8px 0 !important;
    letter-spacing: 0.3px !important;
    text-transform: uppercase !important;
}
.copilot-input-shell {
    background: linear-gradient(145deg, rgba(15,23,42,0.82), rgba(30,41,59,0.76));
    border: 1px solid rgba(147,197,253,0.16);
    border-radius: 16px;
    padding: 12px 14px;
    margin-top: 8px;
    margin-bottom: 12px;
    box-shadow: 0 10px 24px rgba(0,0,0,0.18);
}
div[data-testid="stButton"] > button {
    font-size: 12px !important;
    font-weight: 850 !important;
    min-height: 36px !important;
    height: 36px !important;
    border-radius: 10px !important;
    padding: 0 14px !important;
}

/* ===== ENTERPRISE DONUT ENHANCEMENT ===== */

.static-donut-card {
    position: relative;
    overflow: hidden;
}
.static-donut-card::before {
    content: "";
    position: absolute;
    inset: -80px;
    background:
        radial-gradient(circle at 50% 35%, rgba(96,165,250,0.14), transparent 28%),
        radial-gradient(circle at 80% 20%, rgba(124,58,237,0.12), transparent 24%);
    opacity: 0.55;
    pointer-events: none;
}
.static-donut-wrap,
.static-legend {
    position: relative;
    z-index: 1;
}
.static-donut {
    transition: transform 180ms ease, filter 180ms ease, box-shadow 180ms ease;
}
.static-donut-card:hover .static-donut {
    transform: scale(1.025);
    filter: saturate(1.08) brightness(1.04);
    box-shadow:
        inset 0 0 0 1px rgba(255,255,255,0.10),
        0 0 44px rgba(96,165,250,0.24),
        0 0 70px rgba(124,58,237,0.16);
}
.static-donut::after {
    transition: box-shadow 180ms ease, transform 180ms ease;
}
.static-donut-card:hover .static-donut::after {
    transform: scale(0.985);
    box-shadow:
        inset 0 0 24px rgba(0,0,0,0.42),
        0 0 24px rgba(96,165,250,0.16);
}
.static-legend {
    padding: 4px 2px 0 2px;
}
.static-legend-row {
    min-height: 34px;
    padding: 6px 8px;
    border-radius: 12px;
    background: rgba(255,255,255,0.015);
    border: 1px solid transparent;
    transition: background 140ms ease, border-color 140ms ease, transform 140ms ease;
}
.static-legend-row:hover {
    background: rgba(96,165,250,0.065);
    border-color: rgba(147,197,253,0.12);
    transform: translateX(2px);
}
.static-legend-left {
    flex: 1;
}
.static-category-icon {
    width: 22px;
    height: 22px;
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    background: rgba(15,23,42,0.68);
    border: 1px solid rgba(255,255,255,0.07);
    box-shadow: inset 0 0 10px rgba(255,255,255,0.03);
}
.static-legend-name {
    min-width: 84px;
    color: #E2E8F0;
    font-size: 12.5px;
    font-weight: 750;
}
.static-mini-track {
    flex: 1;
    height: 5px;
    min-width: 54px;
    border-radius: 999px;
    background: rgba(148,163,184,0.14);
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.04);
}
.static-mini-fill {
    height: 100%;
    width: var(--pct);
    border-radius: 999px;
    box-shadow: 0 0 12px rgba(96,165,250,0.20);
    animation: enterpriseMiniBar 700ms ease-out both;
}
.static-legend-percent {
    min-width: 48px;
    text-align: right;
    color: #DBEAFE;
    font-size: 12.5px;
    font-weight: 950;
    font-variant-numeric: tabular-nums;
}
@keyframes enterpriseMiniBar {
    from { width: 0; opacity: 0.55; }
    to { width: var(--pct); opacity: 1; }
}


/* ===== BUILD TO SELL: CANADA SHOPIFY CONVERSION LAYER ===== */
.hero-card {
    position: relative !important;
    overflow: hidden !important;
    padding: 22px 24px !important;
    border-radius: 26px !important;
    background:
        radial-gradient(circle at 18% 20%, rgba(96,165,250,0.20), transparent 28%),
        radial-gradient(circle at 84% 10%, rgba(124,58,237,0.18), transparent 24%),
        linear-gradient(145deg, rgba(2,6,23,0.98), rgba(15,23,42,0.96) 52%, rgba(30,41,59,0.92)) !important;
    border: 1px solid rgba(147,197,253,0.18) !important;
    box-shadow: 0 24px 60px rgba(0,0,0,0.42), 0 0 44px rgba(37,99,235,0.12) !important;
}
.hero-card::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.035), transparent);
    transform: translateX(-120%);
    animation: heroRevenueSweep 7s ease-in-out infinite;
    pointer-events: none;
}
@keyframes heroRevenueSweep {
    0%, 58% { transform: translateX(-120%); opacity: 0; }
    68% { opacity: 1; }
    100% { transform: translateX(120%); opacity: 0; }
}
.hero-title {
    font-size: clamp(30px, 3.4vw, 44px) !important;
    line-height: 1.02 !important;
    letter-spacing: -1px !important;
    max-width: 940px !important;
}
.hero-subtitle {
    max-width: 760px !important;
    font-size: 15.5px !important;
    line-height: 1.55 !important;
    color: #CBD5E1 !important;
}
.revenue-command-grid {
    display: grid;
    grid-template-columns: 1.45fr 0.85fr;
    gap: 18px;
    align-items: stretch;
}
.revenue-command-panel {
    position: relative;
    z-index: 1;
}
.revenue-proof-stack {
    display: grid;
    gap: 10px;
    align-content: center;
}
.revenue-proof-card {
    background: rgba(15,23,42,0.66);
    border: 1px solid rgba(147,197,253,0.14);
    border-radius: 16px;
    padding: 12px 14px;
    box-shadow: inset 0 0 20px rgba(255,255,255,0.018);
}
.revenue-proof-label {
    color: #93C5FD;
    font-size: 9.5px;
    font-weight: 950;
    letter-spacing: 1.1px;
    text-transform: uppercase;
}
.revenue-proof-value {
    color: #F8FAFC;
    font-size: 22px;
    font-weight: 950;
    margin-top: 4px;
    letter-spacing: -0.4px;
}
.revenue-proof-desc {
    color: #94A3B8;
    font-size: 11.5px;
    margin-top: 2px;
    font-weight: 650;
}
.ai-pulse-dot {
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: #22C55E;
    display: inline-block;
    margin-right: 8px;
    box-shadow: 0 0 0 rgba(34,197,94,0.65);
    animation: aiPulse 1.8s infinite;
}
@keyframes aiPulse {
    0% { box-shadow: 0 0 0 0 rgba(34,197,94,0.55); }
    70% { box-shadow: 0 0 0 9px rgba(34,197,94,0); }
    100% { box-shadow: 0 0 0 0 rgba(34,197,94,0); }
}
.ai-live-pulse-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin: 10px 0 2px 0;
}
.ai-live-pulse-card {
    position: relative;
    overflow: hidden;
    min-height: 116px;
    border-radius: 18px;
    padding: 15px 16px;
    background: linear-gradient(145deg, rgba(15,23,42,0.94), rgba(30,41,59,0.86));
    border: 1px solid rgba(147,197,253,0.13);
    box-shadow: 0 14px 30px rgba(0,0,0,0.25);
    transition: transform 150ms ease, border-color 150ms ease, box-shadow 150ms ease;
}
.ai-live-pulse-card:hover {
    transform: translateY(-2px);
    border-color: rgba(147,197,253,0.24);
    box-shadow: 0 18px 36px rgba(0,0,0,0.30), 0 0 24px rgba(37,99,235,0.10);
}
.ai-live-pulse-status {
    color: #93C5FD;
    font-size: 9px;
    font-weight: 950;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 9px;
}
.ai-live-pulse-title {
    color: #F8FAFC;
    font-size: 15px;
    font-weight: 900;
    letter-spacing: -0.15px;
    margin-bottom: 7px;
}
.ai-live-pulse-desc {
    color: #CBD5E1;
    font-size: 12px;
    line-height: 1.42;
    font-weight: 620;
}
.ai-live-pulse-meta {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    margin-top: 10px;
    color: #94A3B8;
    font-size: 10px;
    font-weight: 850;
    text-transform: uppercase;
    letter-spacing: 0.55px;
}
.enterprise-card {
    min-height: 132px !important;
    transition: transform 140ms ease, border-color 140ms ease, box-shadow 140ms ease !important;
}
.enterprise-card:hover {
    transform: translateY(-2px) !important;
    border-color: rgba(147,197,253,0.22) !important;
    box-shadow: 0 18px 36px rgba(0,0,0,0.28), 0 0 22px rgba(37,99,235,0.10) !important;
}
.enterprise-card-green,
.enterprise-card-blue,
.enterprise-card-cyan,
.enterprise-card-amber {
    overflow: hidden;
    border-width: 1px !important;
    border-style: solid !important;
    box-shadow: 0 16px 34px rgba(0,0,0,0.28) !important;
}
.enterprise-card-green { border-color: rgba(52,211,153,0.52) !important; background: linear-gradient(145deg, rgba(6,78,59,0.42), rgba(15,23,42,0.96)) !important; }
.enterprise-card-blue { border-color: rgba(96,165,250,0.52) !important; background: linear-gradient(145deg, rgba(30,64,175,0.36), rgba(15,23,42,0.96)) !important; }
.enterprise-card-cyan { border-color: rgba(34,211,238,0.50) !important; background: linear-gradient(145deg, rgba(14,116,144,0.34), rgba(15,23,42,0.96)) !important; }
.enterprise-card-amber { border-color: rgba(251,191,36,0.50) !important; background: linear-gradient(145deg, rgba(146,64,14,0.34), rgba(15,23,42,0.96)) !important; }
.enterprise-card-green .enterprise-value { color: #6EE7B7 !important; }
.enterprise-card-blue .enterprise-value { color: #93C5FD !important; }
.enterprise-card-cyan .enterprise-value { color: #67E8F9 !important; }
.enterprise-card-amber .enterprise-value { color: #FCD34D !important; }
.enterprise-card-green .enterprise-title,
.enterprise-card-blue .enterprise-title,
.enterprise-card-cyan .enterprise-title,
.enterprise-card-amber .enterprise-title {
    color: #F8FAFC !important;
}
.enterprise-card-green:hover { box-shadow: 0 18px 38px rgba(0,0,0,0.30), 0 0 26px rgba(52,211,153,0.16) !important; }
.enterprise-card-blue:hover { box-shadow: 0 18px 38px rgba(0,0,0,0.30), 0 0 26px rgba(96,165,250,0.16) !important; }
.enterprise-card-cyan:hover { box-shadow: 0 18px 38px rgba(0,0,0,0.30), 0 0 26px rgba(34,211,238,0.14) !important; }
.enterprise-card-amber:hover { box-shadow: 0 18px 38px rgba(0,0,0,0.30), 0 0 26px rgba(251,191,36,0.14) !important; }
.saas-plan-card {
    position: relative;
    min-height: 172px;
    overflow: hidden;
    border: 1px solid rgba(148,163,184,0.20);
    border-radius: 8px;
    padding: 18px;
    background: rgba(15,23,42,0.94);
    box-shadow: 0 15px 32px rgba(0,0,0,0.22);
}
.saas-plan-card::before {
    content: "";
    position: absolute;
    inset: 0 0 auto 0;
    height: 3px;
    background: var(--plan-accent);
}
.saas-plan-card-current {
    border-color: var(--plan-accent);
    box-shadow: 0 18px 40px rgba(0,0,0,0.30), 0 0 24px var(--plan-glow);
}
.saas-plan-card-green {
    --plan-accent: #34D399;
    --plan-soft: #A7F3D0;
    --plan-glow: rgba(52,211,153,0.15);
    background: linear-gradient(145deg, rgba(6,78,59,0.38), rgba(15,23,42,0.97));
}
.saas-plan-card-blue {
    --plan-accent: #60A5FA;
    --plan-soft: #BFDBFE;
    --plan-glow: rgba(96,165,250,0.15);
    background: linear-gradient(145deg, rgba(30,64,175,0.34), rgba(15,23,42,0.97));
}
.saas-plan-card-amber {
    --plan-accent: #FBBF24;
    --plan-soft: #FDE68A;
    --plan-glow: rgba(251,191,36,0.15);
    background: linear-gradient(145deg, rgba(146,64,14,0.34), rgba(15,23,42,0.97));
}
.saas-plan-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
}
.saas-plan-name {
    color: var(--plan-soft);
    font-size: 12px;
    font-weight: 900;
    text-transform: uppercase;
}
.saas-plan-badge {
    color: #D1FAE5;
    border: 1px solid rgba(52,211,153,0.42);
    border-radius: 999px;
    padding: 4px 8px;
    background: rgba(6,78,59,0.40);
    font-size: 10px;
    font-weight: 900;
}
.saas-plan-price {
    margin-top: 17px;
    color: #F8FAFC;
    font-size: 26px;
    font-weight: 950;
}
.saas-plan-desc {
    margin-top: 9px;
    color: #CBD5E1;
    font-size: 13px;
    line-height: 1.55;
}
@media (max-width: 1100px) {
    .revenue-command-grid { grid-template-columns: 1fr; }
    .ai-live-pulse-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 760px) {
    .ai-live-pulse-grid { grid-template-columns: 1fr; }
}



/* ===== AI LIVE OPERATING SYSTEM LAYER - SAFE TICKER ===== */
.live-executive-ticker {
    position: relative;
    display: grid;
    grid-template-columns: auto minmax(0, 1fr);
    align-items: center;
    gap: 14px;
    overflow: hidden;
    min-height: 52px;
    margin: 12px 0 10px 0;
    padding: 0 14px;
    border-radius: 16px;
    border: 1px solid rgba(147,197,253,0.14);
    background: linear-gradient(90deg, rgba(15,23,42,0.96), rgba(30,41,59,0.84), rgba(15,23,42,0.96));
    box-shadow: 0 12px 28px rgba(0,0,0,0.24), inset 0 0 28px rgba(96,165,250,0.025);
}
.live-ticker-label {
    position: relative;
    z-index: 3;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex: 0 0 auto;
    height: 28px;
    padding: 0 12px;
    border-radius: 999px;
    background: linear-gradient(135deg, rgba(37,99,235,0.34), rgba(124,58,237,0.24));
    border: 1px solid rgba(147,197,253,0.24);
    color: #DBEAFE;
    font-size: 9px;
    font-weight: 950;
    letter-spacing: 1px;
    text-transform: uppercase;
    white-space: nowrap;
    box-shadow: 0 0 18px rgba(37,99,235,0.12);
}
.live-ticker-window {
    position: relative;
    overflow: hidden;
    min-width: 0;
    height: 52px;
    display: flex;
    align-items: center;
    -webkit-mask-image: linear-gradient(90deg, transparent 0%, #000 7%, #000 93%, transparent 100%);
    mask-image: linear-gradient(90deg, transparent 0%, #000 7%, #000 93%, transparent 100%);
}
.live-ticker-track {
    display: inline-flex;
    align-items: center;
    gap: 36px;
    width: max-content;
    min-width: max-content;
    white-space: nowrap;
    will-change: transform;
    animation: liveTickerMove 42s linear infinite;
}
.live-executive-ticker:hover .live-ticker-track {
    animation-play-state: paused;
}
.live-ticker-item {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: #CBD5E1;
    font-size: 12px;
    font-weight: 800;
    white-space: nowrap;
}
.live-ticker-dot {
    width: 7px;
    height: 7px;
    border-radius: 999px;
    flex: 0 0 auto;
    background: #22C55E;
    box-shadow: 0 0 12px rgba(34,197,94,0.75);
}
@keyframes liveTickerMove {
    0% { transform: translate3d(0,0,0); }
    100% { transform: translate3d(-50%,0,0); }
}
.revenue-risk-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin-top: 10px;
}
.revenue-risk-card {
    position: relative;
    overflow: hidden;
    min-height: 132px;
    border-radius: 18px;
    padding: 15px 16px;
    background:
        radial-gradient(circle at top right, rgba(96,165,250,0.10), transparent 26%),
        linear-gradient(145deg, rgba(15,23,42,0.96), rgba(30,41,59,0.86));
    border: 1px solid rgba(147,197,253,0.13);
    box-shadow: 0 14px 30px rgba(0,0,0,0.26);
    transition: transform 150ms ease, border-color 150ms ease, box-shadow 150ms ease;
}
.revenue-risk-card:hover {
    transform: translateY(-2px);
    border-color: rgba(147,197,253,0.25);
    box-shadow: 0 18px 38px rgba(0,0,0,0.32), 0 0 26px rgba(37,99,235,0.10);
}
.revenue-risk-level {
    color: #93C5FD;
    font-size: 9px;
    font-weight: 950;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.revenue-risk-title {
    color: #F8FAFC;
    font-size: 15px;
    font-weight: 950;
    letter-spacing: -0.2px;
    margin-bottom: 8px;
}
.revenue-risk-value {
    color: #FFFFFF;
    font-size: 25px;
    font-weight: 950;
    letter-spacing: -0.8px;
    margin-bottom: 7px;
}
.revenue-risk-desc {
    color: #CBD5E1;
    font-size: 12px;
    line-height: 1.42;
    font-weight: 650;
}
.revenue-risk-track {
    height: 5px;
    border-radius: 999px;
    background: rgba(148,163,184,0.16);
    margin-top: 12px;
    overflow: hidden;
}
.revenue-risk-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #60A5FA, #7C3AED);
    width: var(--risk);
    animation: enterpriseMiniBar 800ms ease-out both;
}
.ai-decision-timeline {
    position: relative;
    margin-top: 10px;
    padding: 14px 16px;
    border-radius: 20px;
    background: linear-gradient(145deg, rgba(15,23,42,0.94), rgba(30,41,59,0.82));
    border: 1px solid rgba(147,197,253,0.13);
    box-shadow: 0 14px 32px rgba(0,0,0,0.26);
}
.ai-decision-row {
    display: grid;
    grid-template-columns: 92px 1fr 118px;
    gap: 14px;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid rgba(148,163,184,0.10);
}
.ai-decision-row:last-child { border-bottom: none; }
.ai-decision-time {
    color: #94A3B8;
    font-size: 10px;
    font-weight: 900;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}
.ai-decision-main {
    color: #F8FAFC;
    font-size: 13.5px;
    font-weight: 850;
    line-height: 1.36;
}
.ai-decision-tag {
    justify-self: end;
    padding: 6px 9px;
    border-radius: 999px;
    background: rgba(37,99,235,0.16);
    border: 1px solid rgba(147,197,253,0.15);
    color: #DBEAFE;
    font-size: 9px;
    font-weight: 950;
    letter-spacing: 0.85px;
    text-transform: uppercase;
}
.enterprise-card::before,
.ai-live-pulse-card::before,
.revenue-risk-card::before {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 18% 0%, rgba(96,165,250,0.10), transparent 28%);
    opacity: 0.68;
    pointer-events: none;
}
.enterprise-card .enterprise-title,
.enterprise-card .enterprise-value,
.enterprise-card .enterprise-desc {
    position: relative;
    z-index: 1;
}
@media (max-width: 1100px) {
    .revenue-risk-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .ai-decision-row { grid-template-columns: 80px 1fr; }
    .ai-decision-tag { justify-self: start; grid-column: 2; }
}
@media (max-width: 760px) {
    .revenue-risk-grid { grid-template-columns: 1fr; }
    .live-executive-ticker { grid-template-columns: 1fr; padding: 8px 12px; gap: 6px; }
    .live-ticker-label { justify-self: start; }
    .live-ticker-window { height: 42px; }
}


/* ===== APP 95+ CANADA CONVERSION PREMIUM LAYER ===== */
.hero-card {
    isolation: isolate !important;
    min-height: 232px !important;
}
.hero-card::before {
    content: "";
    position: absolute;
    inset: -1px;
    border-radius: 26px;
    background:
        radial-gradient(circle at 12% 18%, rgba(34,197,94,0.11), transparent 22%),
        radial-gradient(circle at 78% 12%, rgba(96,165,250,0.18), transparent 24%),
        radial-gradient(circle at 92% 88%, rgba(124,58,237,0.18), transparent 30%);
    opacity: 0.85;
    z-index: 0;
    pointer-events: none;
}
.hero-card > * {
    position: relative;
    z-index: 1;
}
.hero-badge {
    background: rgba(37,99,235,0.18) !important;
    border-color: rgba(147,197,253,0.24) !important;
    box-shadow: 0 0 22px rgba(37,99,235,0.10) !important;
}
.hero-title {
    max-width: 980px !important;
    text-wrap: balance;
}
.revenue-proof-card {
    position: relative;
    overflow: hidden;
    transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
}
.revenue-proof-card:hover {
    transform: translateY(-2px);
    border-color: rgba(147,197,253,0.26);
    box-shadow: 0 16px 28px rgba(0,0,0,0.22), 0 0 24px rgba(96,165,250,0.09);
}
.revenue-proof-card::after {
    content: "";
    position: absolute;
    left: 0;
    top: 14px;
    bottom: 14px;
    width: 3px;
    border-radius: 999px;
    background: linear-gradient(180deg, #22C55E, #60A5FA, #7C3AED);
    opacity: 0.9;
}
.executive-conversion-strip {
    display: grid;
    grid-template-columns: 1.15fr repeat(3, minmax(0, 0.62fr));
    gap: 12px;
    margin: 12px 0 12px 0;
}
.executive-conversion-main,
.executive-conversion-mini {
    position: relative;
    overflow: hidden;
    border-radius: 18px;
    background:
        radial-gradient(circle at top left, rgba(96,165,250,0.10), transparent 30%),
        linear-gradient(145deg, rgba(15,23,42,0.96), rgba(30,41,59,0.86));
    border: 1px solid rgba(147,197,253,0.14);
    box-shadow: 0 14px 30px rgba(0,0,0,0.24);
}
.executive-conversion-main {
    padding: 17px 18px;
    min-height: 126px;
}
.executive-conversion-mini {
    padding: 15px 15px;
    min-height: 126px;
}
.executive-conversion-label {
    color: #93C5FD;
    font-size: 9px;
    font-weight: 950;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.executive-conversion-title {
    color: #F8FAFC;
    font-size: 18px;
    font-weight: 950;
    letter-spacing: -0.35px;
    line-height: 1.18;
}
.executive-conversion-desc {
    color: #CBD5E1;
    font-size: 12.5px;
    line-height: 1.42;
    margin-top: 8px;
    font-weight: 650;
}
.executive-conversion-value {
    color: #FFFFFF;
    font-size: 25px;
    font-weight: 950;
    letter-spacing: -0.75px;
    margin-top: 4px;
}
.executive-conversion-trend {
    display: inline-flex;
    align-items: center;
    margin-top: 9px;
    padding: 5px 8px;
    border-radius: 999px;
    background: rgba(34,197,94,0.10);
    border: 1px solid rgba(34,197,94,0.18);
    color: #86EFAC;
    font-size: 9.5px;
    font-weight: 950;
    letter-spacing: 0.65px;
    text-transform: uppercase;
}
.enterprise-card,
.ai-live-pulse-card,
.revenue-risk-card {
    animation: executiveBreath 5.8s ease-in-out infinite;
}
.enterprise-card:nth-child(2n),
.ai-live-pulse-card:nth-child(2n),
.revenue-risk-card:nth-child(2n) {
    animation-delay: 700ms;
}
@keyframes executiveBreath {
    0%, 100% { box-shadow: 0 14px 30px rgba(0,0,0,0.24), 0 0 0 rgba(96,165,250,0); }
    50% { box-shadow: 0 16px 34px rgba(0,0,0,0.27), 0 0 22px rgba(96,165,250,0.055); }
}
.live-ticker-label::before {
    content: "";
    width: 7px;
    height: 7px;
    margin-right: 7px;
    border-radius: 999px;
    background: #22C55E;
    box-shadow: 0 0 13px rgba(34,197,94,0.9);
}
.ai-decision-timeline {
    overflow: hidden;
}
.ai-decision-timeline::before {
    content: "";
    position: absolute;
    left: 19px;
    top: 22px;
    bottom: 22px;
    width: 1px;
    background: linear-gradient(180deg, rgba(96,165,250,0.0), rgba(96,165,250,0.45), rgba(124,58,237,0.0));
}
.ai-decision-row {
    position: relative;
}
.ai-decision-row::before {
    content: "";
    position: absolute;
    left: -2px;
    top: 50%;
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: #60A5FA;
    box-shadow: 0 0 12px rgba(96,165,250,0.8);
    transform: translateY(-50%);
}
@media (max-width: 1100px) {
    .executive-conversion-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 760px) {
    .executive-conversion-strip { grid-template-columns: 1fr; }
}


/* ===== APP 101 REVENUE THREAT + EXECUTIVE RADAR LAYER ===== */
.money-moment-card {
    position: relative;
    overflow: hidden;
    margin: 12px 0 10px 0;
    padding: 20px 22px;
    border-radius: 22px;
    background:
        radial-gradient(circle at 12% 18%, rgba(34,197,94,0.16), transparent 24%),
        radial-gradient(circle at 88% 14%, rgba(96,165,250,0.15), transparent 28%),
        linear-gradient(145deg, rgba(2,6,23,0.98), rgba(15,23,42,0.94));
    border: 1px solid rgba(34,197,94,0.18);
    box-shadow: 0 18px 42px rgba(0,0,0,0.32), 0 0 38px rgba(34,197,94,0.08);
}
.money-moment-label { color: #86EFAC; font-size: 9.5px; font-weight: 950; letter-spacing: 1.25px; text-transform: uppercase; margin-bottom: 8px; }
.money-moment-title { color: #FFFFFF; font-size: clamp(22px, 3vw, 34px); font-weight: 950; letter-spacing: -0.9px; line-height: 1.08; max-width: 880px; }
.money-moment-desc { color: #CBD5E1; font-size: 13px; line-height: 1.45; margin-top: 8px; max-width: 820px; font-weight: 650; }
.money-moment-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin-top: 14px; }
.money-moment-mini { padding: 12px 13px; border-radius: 16px; background: rgba(15,23,42,0.70); border: 1px solid rgba(147,197,253,0.12); }
.money-moment-mini-label { color: #93C5FD; font-size: 8.8px; font-weight: 950; letter-spacing: 0.95px; text-transform: uppercase; }
.money-moment-mini-value { color: #F8FAFC; font-size: 20px; font-weight: 950; margin-top: 4px; }
.threat-grid, .radar-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; margin-top: 10px; }
.threat-card, .radar-card { position: relative; overflow: hidden; min-height: 122px; border-radius: 18px; padding: 14px 14px; background: linear-gradient(145deg, rgba(15,23,42,0.96), rgba(30,41,59,0.84)); border: 1px solid rgba(147,197,253,0.13); box-shadow: 0 12px 28px rgba(0,0,0,0.25); }
.threat-label, .radar-label { color: #93C5FD; font-size: 8.5px; font-weight: 950; letter-spacing: 0.95px; text-transform: uppercase; margin-bottom: 8px; }
.threat-title, .radar-title { color: #F8FAFC; font-size: 13.5px; font-weight: 950; line-height: 1.2; }
.threat-value, .radar-value { color: #FFFFFF; font-size: 21px; font-weight: 950; margin: 7px 0 5px 0; }
.threat-desc, .radar-desc { color: #CBD5E1; font-size: 11.5px; line-height: 1.35; font-weight: 650; }
.radar-track { height: 5px; border-radius: 999px; background: rgba(148,163,184,0.16); overflow: hidden; margin-top: 10px; }
.radar-fill { height: 100%; width: var(--radar); border-radius: 999px; background: linear-gradient(90deg, #22C55E, #60A5FA, #7C3AED); }
.ai-advisor-action { margin-top: 10px; padding: 16px 18px; border-radius: 20px; background: radial-gradient(circle at top left, rgba(124,58,237,0.12), transparent 28%), linear-gradient(145deg, rgba(15,23,42,0.96), rgba(30,41,59,0.86)); border: 1px solid rgba(147,197,253,0.14); box-shadow: 0 14px 30px rgba(0,0,0,0.24); }
.ai-advisor-action-title { color: #F8FAFC; font-size: 18px; font-weight: 950; letter-spacing: -0.25px; }
.ai-advisor-action-desc { color: #CBD5E1; font-size: 13px; line-height: 1.45; margin-top: 7px; font-weight: 650; }
.live-signal-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
@media (max-width: 1100px) { .threat-grid, .radar-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .money-moment-grid { grid-template-columns: 1fr; } }
@media (max-width: 900px) { .live-signal-grid { grid-template-columns: 1fr; } }
@media (max-width: 760px) { .threat-grid, .radar-grid { grid-template-columns: 1fr; } }

</style>
"""
st.markdown(APP_FALLBACK_CSS, unsafe_allow_html=True)


def vertical_spacer(height=18):
    st.markdown(
        f"<div style=\"height:{height}px\"></div>",
        unsafe_allow_html=True,
    )


def render_metric_card(title, value, delta=None, description=None, accent=None):
    """Stable HTML metric card used instead of st.metric.

    Important:
    The HTML is intentionally rendered as a compact single-line string.
    Indented multiline HTML can be interpreted by Streamlit/Markdown as a code block,
    which makes tags like <div class="enterprise-desc"> appear visibly on screen.
    """
    safe_title = html.escape(str(title))
    safe_value = html.escape(str(value))
    safe_delta = html.escape(str(delta)) if delta is not None else ""
    safe_description = html.escape(str(description)) if description is not None else ""

    delta_html = f'<div class="enterprise-desc">↗ {safe_delta}</div>' if safe_delta else ""
    desc_html = f'<div class="enterprise-desc">{safe_description}</div>' if safe_description else ""

    accent_class = f" enterprise-card-{accent}" if accent else ""
    card_html = (
        f'<div class="enterprise-card{accent_class}">'
        f'<div class="enterprise-title">{safe_title}</div>'
        f'<div class="enterprise-value">{safe_value}</div>'
        f'{delta_html}'
        f'{desc_html}'
        '</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)


def render_plan_card(plan_item, accent, is_current=False):
    safe_name = html.escape(str(plan_item["name"]))
    safe_price = html.escape(str(plan_item["price"]))
    safe_tagline = html.escape(str(plan_item["tagline"]))
    current_class = " saas-plan-card-current" if is_current else ""
    current_badge = '<div class="saas-plan-badge">CURRENT PLAN</div>' if is_current else ""
    st.markdown(
        (
            f'<div class="saas-plan-card saas-plan-card-{accent}{current_class}">'
            '<div class="saas-plan-top">'
            f'<div class="saas-plan-name">{safe_name}</div>'
            f'{current_badge}'
            '</div>'
            f'<div class="saas-plan-price">US${safe_price}/mo</div>'
            f'<div class="saas-plan-desc">{safe_tagline}</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def render_static_bar_chart(dataframe):
    chart_df = (
        dataframe.groupby("setor", as_index=False)["vendas"]
        .sum()
        .sort_values("vendas", ascending=False)
        .head(8)
    )

    if chart_df.empty:
        st.info("No data available for chart.")
        return

    max_value = float(chart_df["vendas"].max()) or 1.0
    rows_html = ""

    for _, row in chart_df.iterrows():
        label = html.escape(str(row["setor"]))
        value = float(row["vendas"])
        width = max(4, min(100, (value / max_value) * 100))
        rows_html += (
            '<div class="static-bar-row">'
            f'<div class="static-bar-label">{label}</div>'
            '<div class="static-bar-track">'
            f'<div class="static-bar-fill" style="width:{width:.1f}%"></div>'
            '</div>'
            f'<div class="static-bar-value">{format_currency(value)}</div>'
            '</div>'
        )

    st.markdown(
        f'<div class="static-chart-card">{rows_html}</div>',
        unsafe_allow_html=True,
    )


def get_category_icon(label):
    """Small executive icons for static donut legend."""
    label_lower = str(label).lower()
    if "tec" in label_lower or "tech" in label_lower:
        return "⚙️"
    if "log" in label_lower:
        return "🚚"
    if "varejo" in label_lower or "retail" in label_lower:
        return "🛒"
    if "industrial" in label_lower or "industry" in label_lower:
        return "🏭"
    if "text" in label_lower or "têxtil" in label_lower or "textil" in label_lower:
        return "🧵"
    if "finance" in label_lower:
        return "💰"
    return "◆"


def render_static_donut_chart(dataframe):
    chart_df = (
        dataframe.groupby("setor", as_index=False)["vendas"]
        .sum()
        .sort_values("vendas", ascending=False)
        .head(6)
    )

    if chart_df.empty:
        st.info("No data available for chart.")
        return

    total = float(chart_df["vendas"].sum()) or 1.0
    colors = CHART_COLORS
    start = 0.0
    segments = []
    legend_html = ""

    for i, row in chart_df.reset_index(drop=True).iterrows():
        value = float(row["vendas"])
        pct = (value / total) * 100
        end = start + pct
        color = colors[i % len(colors)]
        icon = html.escape(get_category_icon(row["setor"]))
        segments.append(f"{color} {start:.2f}% {end:.2f}%")
        label = html.escape(str(row["setor"]))
        legend_html += (
            '<div class="static-legend-row">'
            '<div class="static-legend-left">'
            f'<span class="static-category-icon" style="color:{color};">{icon}</span>'
            f'<span class="static-dot" style="background:{color};"></span>'
            f'<span class="static-legend-name">{label}</span>'
            f'<span class="static-mini-track"><span class="static-mini-fill" style="--pct:{pct:.1f}%; background:{color};"></span></span>'
            '</div>'
            f'<span class="static-legend-percent">{pct:.1f}%</span>'
            '</div>'
        )
        start = end

    gradient = ", ".join(segments)
    donut_html = (
        '<div class="static-chart-card static-donut-card">'
        '<div class="static-donut-wrap">'
        f'<div class="static-donut" style="background: conic-gradient({gradient});"></div>'
        '</div>'
        f'<div class="static-legend">{legend_html}</div>'
        '</div>'
    )
    st.markdown(donut_html, unsafe_allow_html=True)


def render_static_health_gauge(score):
    score = max(0, min(100, float(score)))
    gauge_html = (
        '<div class="static-chart-card">'
        f'<div class="static-gauge" style="background: conic-gradient(#60A5FA 0% {score:.1f}%, rgba(148,163,184,0.16) {score:.1f}% 100%);">'
        '<div class="static-gauge-value">'
        f'{score:.1f}%'
        '<div class="static-gauge-label">AI Health Score</div>'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(gauge_html, unsafe_allow_html=True)


def render_kpi_section_stable(total_revenue, avg_ticket, forecast_value, growth_rate, shopify_snapshot=None):
    """Conversion-focused KPI section for Shopify SaaS positioning."""
    section_header(
        "EXECUTIVE REVENUE PROTECTION ENGINE",
        "Revenue KPIs Built to Drive Decisions",
        "Financial indicators derived from synchronized Shopify revenue, orders and inventory.",
    )

    if shopify_snapshot:
        revenue_total = float(shopify_snapshot.get("revenue_total") or 0)
        currency_code = shopify_snapshot.get("currency_code") or "BRL"
        order_count = int(shopify_snapshot.get("order_count") or 0)
        growth_rate = shopify_snapshot.get("growth_rate")
        forecast_revenue = float(shopify_snapshot.get("forecast_revenue") or revenue_total)
        risk_score = float(shopify_snapshot.get("risk_score") or 0)
        growth_value = f"{float(growth_rate):+.1f}%" if growth_rate is not None else "Collecting"
        kpi_items = [
            ("Revenue", format_shopify_currency(revenue_total, currency_code), f"Live Shopify revenue from {order_count} synced orders", "green"),
            ("Growth", growth_value, "Change between the two most recent orders", "blue"),
            ("Forecast", format_shopify_currency(forecast_revenue, currency_code), "Initial next-order revenue projection", "cyan"),
            ("Risk", f"{risk_score:.0f}/100", "Operational risk from concentration and inventory", "amber"),
        ]
    else:
        kpi_items = [
            ("Revenue", "Awaiting sync", "Connect and sync Shopify to activate this indicator", None),
            ("Growth", "Not tracked", "Requires synchronized Shopify order history", None),
            ("Forecast", "Not tracked", "Requires synchronized Shopify order values", None),
            ("Risk", "Not tracked", "Requires synchronized products and inventory", None),
        ]

    cols = st.columns(4, gap="large")
    for i, (title, value, desc, accent) in enumerate(kpi_items):
        with cols[i]:
            render_metric_card(title, value, description=desc, accent=accent)


def render_forecast_section_stable(current_revenue, forecast_revenue, forecast_growth, best_category, risk_category):
    """Stable forecast cards replacing external forecast component."""

    cols = st.columns(3, gap="large")
    with cols[0]:
        render_metric_card("Forecast Lift", f"{forecast_growth:.1f}%", description="Next-order scenario")
    with cols[1]:
        render_metric_card("Projected Revenue", format_currency(forecast_revenue), description="Synced order-value scenario")
    with cols[2]:
        render_metric_card("Scale Category", best_category, description="Highest potential")

    st.markdown(
        f"""
        <div class="ai-response-box">
            <b>Predictive Shopify Analysis:</b><br><br>
            • Current imported revenue: <b>{format_currency(current_revenue)}</b>.<br><br>
            • <b>{html.escape(str(best_category))}</b> should be prioritized as the current growth opportunity.<br><br>
            • <b>{html.escape(str(risk_category))}</b> should remain under operational review.<br><br>
            • Next-order scenario: <b>{format_currency(forecast_revenue)}</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_currency(value):
    try:
        return f"R$ {float(value):,.2f}"
    except Exception:
        return "R$ 0,00"


def format_shopify_currency(value, currency_code="BRL"):
    try:
        return f"{currency_code} {float(value):,.2f}"
    except Exception:
        return f"{currency_code} 0.00"


def get_trial_days_left(user):
    trial_ends_at = user.get("tenant_trial_ends_at")
    if not trial_ends_at:
        return TRIAL_DAYS

    try:
        now = pd.Timestamp.utcnow()
        end = pd.Timestamp(trial_ends_at)
        if end.tzinfo is None:
            end = end.tz_localize("UTC")
        return max(0, int((end - now).days) + 1)
    except Exception:
        return TRIAL_DAYS


def safe_text(value):
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def render_text_result(title, value):
    """Render agent/chat outputs without dynamic st.container blocks."""
    safe_title = html.escape(str(title))
    safe_value = html.escape(safe_text(value)).replace("\n", "<br>")
    st.markdown(
        f"""
        <div class="ai-response-box">
            <b>{safe_title}</b><br><br>
            {safe_value}
        </div>
        """,
        unsafe_allow_html=True,
    )




def normalize_dataframe(dataframe):
    dataframe = dataframe.copy()
    dataframe.columns = [str(column).strip().lower() for column in dataframe.columns]
    return dataframe


def find_text_column(dataframe):
    possible_columns = [
        "setor",
        "categoria",
        "produto",
        "cliente",
        "departamento",
        "area",
        "área",
        "nome",
    ]
    for column in possible_columns:
        if column in dataframe.columns:
            return column
    object_columns = dataframe.select_dtypes(include=["object"]).columns
    if len(object_columns) > 0:
        return object_columns[0]
    return None


def find_numeric_column(dataframe):
    numeric_columns = dataframe.select_dtypes(include="number").columns
    if len(numeric_columns) > 0:
        return numeric_columns[0]
    return None


def prepare_business_dataframe(dataframe):
    dataframe = normalize_dataframe(dataframe)
    text_column = find_text_column(dataframe)
    numeric_column = find_numeric_column(dataframe)

    if text_column is None or numeric_column is None:
        return None, None, None

    prepared_df = dataframe[[text_column, numeric_column]].copy()
    prepared_df = prepared_df.rename(columns={text_column: "setor", numeric_column: "vendas"})
    prepared_df["vendas"] = pd.to_numeric(prepared_df["vendas"], errors="coerce")
    prepared_df = prepared_df.dropna(subset=["setor", "vendas"])
    return prepared_df, text_column, numeric_column


def build_shopify_category_dataframe(snapshot, is_connected=False):
    if not snapshot:
        if is_connected:
            return pd.DataFrame([{"setor": "Shopify sync pending", "vendas": 0.0}])
        return pd.DataFrame(columns=["setor", "vendas"])

    payload = snapshot.get("payload") or {}
    category_rows = payload.get("category_revenue") or []
    prepared_rows = []
    for row in category_rows:
        category = str(row.get("category") or "").strip() or "Uncategorized"
        try:
            revenue = float(row.get("revenue") or 0)
        except (TypeError, ValueError):
            continue
        if revenue > 0:
            prepared_rows.append({"setor": category, "vendas": revenue})

    if prepared_rows:
        return pd.DataFrame(prepared_rows)

    return pd.DataFrame(
        [
            {
                "setor": "No Shopify sales synced yet",
                "vendas": float(snapshot.get("revenue_total") or 0),
            }
        ]
    )


def premium_dataframe(dataframe, height=290, key=None):
    styled_dataframe = (
        dataframe.style
        .set_table_styles(
            [
                {
                    "selector": "thead th",
                    "props": [
                        ("background-color", "#111827"),
                        ("color", "#93C5FD"),
                        ("font-weight", "800"),
                    ],
                },
                {
                    "selector": "tbody td",
                    "props": [
                        ("background-color", "#0F172A"),
                        ("color", "#E5E7EB"),
                    ],
                },
                {
                    "selector": "tbody th",
                    "props": [
                        ("background-color", "#0F172A"),
                        ("color", "#94A3B8"),
                    ],
                },
            ]
        )
        .format(precision=2)
    )
    st.dataframe(styled_dataframe, use_container_width=True, height=height, key=key)


def create_premium_bar_chart(dataframe):
    chart_df = (
        dataframe.groupby("setor", as_index=False)["vendas"]
        .sum()
        .sort_values("vendas", ascending=False)
    )
    fig = px.bar(
        chart_df,
        x="setor",
        y="vendas",
        color="setor",
        text="vendas",
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_traces(
        texttemplate="R$ %{text:,.0f}",
        textposition="outside",
        marker_line_width=0,
        opacity=0.95,
        hovertemplate="<b>%{x}</b><br>Receita: R$ %{y:,.2f}<extra></extra>",
    )
    fig.update_layout(
        height=340,
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white", size=14),
        margin=dict(l=10, r=10, t=30, b=10),
        hoverlabel=dict(bgcolor="#111827", bordercolor="#374151", font_size=14, font_color="white"),
        xaxis=dict(showgrid=False, linecolor="rgba(255,255,255,0.12)", tickfont=dict(color="#CBD5E1")),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", zeroline=False, tickfont=dict(color="#CBD5E1")),
        bargap=0.42,
    )
    return fig


def create_premium_donut_chart(dataframe):
    chart_df = (
        dataframe.groupby("setor", as_index=False)["vendas"]
        .sum()
        .sort_values("vendas", ascending=False)
    )
    fig = go.Figure(
        data=[
            go.Pie(
                labels=chart_df["setor"],
                values=chart_df["vendas"],
                hole=0.64,
                marker=dict(colors=CHART_COLORS, line=dict(color="rgba(15,23,42,1)", width=5)),
                textinfo="label+percent",
                texttemplate="%{label}<br>%{percent}",
                textposition="inside",
                insidetextorientation="auto",
                textfont=dict(color="#FFFFFF", size=13, family="Arial Black"),
                hovertemplate="<b>%{label}</b><br>Receita: R$ %{value:,.2f}<extra></extra>",
                sort=False,
            )
        ]
    )
    fig.update_layout(
        height=420,
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=20, b=20),
        font=dict(color="#FFFFFF", size=13, family="Arial"),
        annotations=[
            dict(
                text="<b>Revenue<br>Distribution</b>",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=17, color="#F8FAFC", family="Arial Black"),
            )
        ],
    )
    return fig


def section_header(badge, title, subtitle):
    st.markdown(
        f"""
        <div class="ai-card">
            <div class="ai-badge">{html.escape(badge)}</div>
            <div class="ai-title">{html.escape(title)}</div>
            <div class="ai-subtitle">{html.escape(subtitle)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero():
    hero_html = """
    <div class="hero-card">
        <div class="revenue-command-grid">
            <div class="revenue-command-panel">
                <div class="hero-badge">SHOPIFY AI REVENUE OPERATING SYSTEM</div>
                <div class="hero-title">Protect Shopify Revenue Before Growth Leaks Become Expensive</div>
                <div class="hero-subtitle">
                    An AI revenue operating system built to detect leakage, forecast growth, prioritize opportunities and monitor Shopify performance before hidden risks become lost profit.
                </div>
            </div>
            <div class="revenue-proof-stack">
                <div class="revenue-proof-card">
                    <div class="revenue-proof-label"><span class="ai-pulse-dot"></span>Operating Layer</div>
                    <div class="revenue-proof-value">Shopify Sync</div>
                    <div class="revenue-proof-desc">Orders, products and inventory</div>
                </div>
                <div class="revenue-proof-card">
                    <div class="revenue-proof-label">Revenue Intelligence</div>
                    <div class="revenue-proof-value">Activated on Sync</div>
                    <div class="revenue-proof-desc">Live signals only after import</div>
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)


def render_summary(best_sector, lowest_sector, total_sales, next_prediction):
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">Executive Summary</div>
            <div class="insight-item">Top performance category: <strong>{html.escape(str(best_sector))}</strong>.</div>
            <div class="insight-item">Operational risk category: <strong>{html.escape(str(lowest_sector))}</strong>.</div>
            <div class="insight-item">Revenue monitored: <strong>{format_currency(total_sales)}</strong>.</div>
            <div class="insight-item">AI forecast estimate: <strong>{format_currency(next_prediction)}</strong>.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_ai_live_pulse(ctx):
    """DOM-safe AI live pulse cards that create the feeling of an autonomous revenue system."""
    best = html.escape(str(ctx["shopify_best_category"]))
    risk = html.escape(str(ctx["shopify_risk_category"]))
    growth = float(ctx["shopify_growth_score"])
    revenue = format_currency(ctx["shopify_total_revenue"])

    section_header(
        "LIVE AI REVENUE PULSE",
        "Executive AI Revenue Signals",
        "Live AI monitoring designed to expose revenue leakage, growth windows, margin pressure and operational priorities.",
    )

    pulse_cards = [
        ("SHOPIFY SIGNAL", "Leading category", f"{best} currently leads synchronized category revenue.", "SHOPIFY DATA", "NOW"),
        ("OPERATIONAL REVIEW", "Lowest category revenue", f"{risk} is the current review category based on synchronized order line items.", "REVIEW REQUIRED", "SYNCED"),
        ("FORECAST UPDATE", "Next-order scenario", f"Latest synchronized order-value growth signal: {growth:.1f}%.", "SHOPIFY DATA", "LIVE"),
        ("REVENUE ENGINE", "Protection layer active", f"{revenue} is currently imported from Shopify.", "SHOPIFY DATA", "SYNCED"),
    ]

    cards_html = '<div class="ai-live-pulse-grid">'
    for status, title, desc, confidence, time_label in pulse_cards:
        cards_html += (
            '<div class="ai-live-pulse-card">'
            f'<div class="ai-live-pulse-status"><span class="ai-pulse-dot"></span>{html.escape(status)}</div>'
            f'<div class="ai-live-pulse-title">{html.escape(title)}</div>'
            f'<div class="ai-live-pulse-desc">{desc}</div>'
            '<div class="ai-live-pulse-meta">'
            f'<span>{html.escape(confidence)}</span><span>{html.escape(time_label)}</span>'
            '</div>'
            '</div>'
        )
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)




def render_live_executive_ticker(ctx):
    """Continuous DOM-safe ticker to create an autonomous operating-system feeling."""
    best = html.escape(str(ctx["shopify_best_category"]))
    risk = html.escape(str(ctx["shopify_risk_category"]))
    items = [
        "AI monitoring synchronized across Shopify revenue signals",
        f"Leading synchronized revenue category: {best}",
        "Next-order scenario updated from synchronized Shopify values",
        f"Operational review category: {risk}",
        "Opportunity engine active and scanning category performance",
        "Revenue protection layer synchronized",
    ]
    doubled = items + items
    html_items = "".join(
        f'<div class="live-ticker-item"><span class="live-ticker-dot"></span>{html.escape(item)}</div>'
        for item in doubled
    )
    st.markdown(
        f'<div class="live-executive-ticker"><div class="live-ticker-label">LIVE AI OPERATING FEED</div><div class="live-ticker-window"><div class="live-ticker-track">{html_items}</div></div></div>',
        unsafe_allow_html=True,
    )


def render_executive_conversion_strip(ctx):
    """High-conversion executive strip focused on SaaS buying psychology for Shopify operators."""
    total_revenue = float(ctx["shopify_total_revenue"])
    growth_score = float(ctx["shopify_growth_score"])
    best = html.escape(str(ctx["shopify_best_category"]))
    risk = html.escape(str(ctx["shopify_risk_category"]))
    protected_value = format_currency(total_revenue)
    opportunity_value = "Not tracked"
    risk_value = "Not tracked"

    strip_html = (
        '<div class="executive-conversion-strip">'
        '<div class="executive-conversion-main">'
        '<div class="executive-conversion-label"><span class="ai-pulse-dot"></span>EXECUTIVE REVENUE INTELLIGENCE</div>'
        '<div class="executive-conversion-title">Your Shopify snapshot is active for operational review.</div>'
        f'<div class="executive-conversion-desc"><b>{risk}</b> is the lowest synchronized category and <b>{best}</b> currently leads synchronized category revenue.</div>'
        '<div class="executive-conversion-trend">AI operating layer active</div>'
        '</div>'
        '<div class="executive-conversion-mini">'
        '<div class="executive-conversion-label">Revenue Under Watch</div>'
        f'<div class="executive-conversion-value">{protected_value}</div>'
        '<div class="executive-conversion-desc">Total revenue being monitored by the protection engine.</div>'
        '</div>'
        '<div class="executive-conversion-mini">'
        '<div class="executive-conversion-label">Estimated Opportunity</div>'
        f'<div class="executive-conversion-value">{opportunity_value}</div>'
        '<div class="executive-conversion-desc">Requires attributed acquisition and conversion data.</div>'
        '</div>'
        '<div class="executive-conversion-mini">'
        '<div class="executive-conversion-label">Potential Leakage</div>'
        f'<div class="executive-conversion-value">{risk_value}</div>'
        '<div class="executive-conversion-desc">Requires cost, margin and attribution data.</div>'
        '</div>'
        '</div>'
    )
    st.markdown(strip_html, unsafe_allow_html=True)


def render_revenue_risk_center(ctx):
    """Risk-oriented section focused on what Shopify operators pay to avoid."""
    risk_category = html.escape(str(ctx["shopify_risk_category"]))
    live_risk_score = ctx.get("shopify_live_risk_score")
    operational_risk = min(100, max(0, float(live_risk_score or 0)))
    snapshot = ctx.get("shopify_live_snapshot") or {}
    payload = snapshot.get("payload") or {}
    comparison = payload.get("sync_comparison") or {}
    products = payload.get("products") or []
    currency_code = snapshot.get("currency_code") or "BRL"
    low_inventory_products = sum(
        int(product.get("totalInventory") or 0) <= 10
        for product in products
    )
    low_inventory_rate = (
        (low_inventory_products / len(products)) * 100
        if products
        else 0
    )
    has_baseline = bool(comparison.get("has_baseline"))
    new_orders = int(comparison.get("new_orders") or 0)
    revenue_delta = float(comparison.get("revenue_delta") or 0)
    inventory_delta = int(comparison.get("inventory_delta") or 0)
    inventory_change_rate = float(comparison.get("inventory_change_rate") or 0)
    average_change_rate = float(
        comparison.get("new_order_average_change_rate") or 0
    )
    recent_sync_count = len(ctx.get("shopify_recent_syncs") or [])

    if has_baseline:
        movement_prefix = "+" if revenue_delta > 0 else ""
        revenue_movement = (
            f"{movement_prefix}{format_shopify_currency(revenue_delta, currency_code)}"
        )
        movement_desc = (
            f"Revenue change since the previous synchronization. "
            f"New-order average movement: {average_change_rate:+.1f}%. "
            f"{recent_sync_count} snapshots available."
        )
        orders_value = f"+{new_orders}"
        orders_desc = "New Shopify orders imported since the previous synchronization."
        inventory_desc = (
            f"{low_inventory_products} low-stock products. Inventory movement since "
            f"the previous sync: {inventory_delta:+d} units ({inventory_change_rate:+.1f}%)."
        )
    else:
        revenue_movement = "Baseline pending"
        movement_desc = "Run another synchronization to activate historical anomaly detection."
        orders_value = "Baseline pending"
        orders_desc = "The first synchronized snapshot is establishing the comparison baseline."
        inventory_desc = (
            f"{low_inventory_products} low-stock products are currently monitored. "
            "Historical movement activates after the next synchronization."
        )

    section_header(
        "REVENUE RISK CENTER",
        "Revenue Risk Center",
        "Measured operational signals from synchronized Shopify orders, products, inventory and snapshot history.",
    )

    risk_cards = [
        ("SHOPIFY SIGNAL", "Operational Risk", f"{operational_risk:.0f}/100", f"Risk score derived from revenue concentration and inventory exposure in {risk_category}.", operational_risk),
        ("INVENTORY", "Stock Exposure", f"{low_inventory_products} low-stock", inventory_desc, low_inventory_rate),
        ("HISTORY", "Revenue Movement", revenue_movement, movement_desc, min(100, abs(average_change_rate))),
        ("ORDERS", "Orders Since Prior Sync", orders_value, orders_desc, min(100, new_orders * 10)),
    ]

    cards_html = '<div class="revenue-risk-grid">'
    for level, title, value, desc, score in risk_cards:
        cards_html += (
            '<div class="revenue-risk-card">'
            f'<div class="revenue-risk-level"><span class="ai-pulse-dot"></span>{html.escape(level)}</div>'
            f'<div class="revenue-risk-title">{html.escape(title)}</div>'
            f'<div class="revenue-risk-value">{html.escape(value)}</div>'
            f'<div class="revenue-risk-desc">{html.escape(desc)}</div>'
            '<div class="revenue-risk-track">'
            f'<div class="revenue-risk-fill" style="--risk:{score:.1f}%"></div>'
            '</div>'
            '</div>'
        )
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    open_alerts = [
        alert
        for alert in ctx.get("revenue_alerts", [])
        if alert.get("status") == "open"
    ]
    st.markdown(
        '<div style="margin:18px 0 8px; color:#93C5FD; font-size:10px; font-weight:950;">ACTIVE RISK SIGNALS</div>',
        unsafe_allow_html=True,
    )
    if not open_alerts:
        st.success("No open Shopify risk signals. Monitoring remains active after every synchronization.")
    else:
        alerts_html = '<div class="ai-decision-timeline">'
        for alert in open_alerts[:4]:
            severity = str(alert.get("severity") or "medium").upper()
            title = html.escape(str(alert.get("title") or "Revenue signal detected"))
            message = html.escape(str(alert.get("message") or ""))
            alerts_html += (
                '<div class="ai-decision-row">'
                f'<div class="ai-decision-time"><span class="ai-pulse-dot"></span>{html.escape(severity)}</div>'
                f'<div class="ai-decision-main"><b>{title}</b><br><span style="color:#CBD5E1;">{message}</span></div>'
                '<div class="ai-decision-tag">OPEN</div>'
                '</div>'
            )
        alerts_html += '</div>'
        st.markdown(alerts_html, unsafe_allow_html=True)

    st.caption("Margin and retention signals remain locked until cost and customer-history integrations are activated.")


def render_ai_decision_feed(ctx):
    """Executive decision feed that makes the AI feel continuously active."""
    best = html.escape(str(ctx["shopify_best_category"]))
    risk = html.escape(str(ctx["shopify_risk_category"]))
    snapshot = ctx.get("shopify_live_snapshot") or {}
    growth_rate = snapshot.get("growth_rate")
    if growth_rate is None:
        momentum_message = f"{best} leads synchronized Shopify category revenue. Growth history is still collecting."
    elif float(growth_rate) >= 0:
        momentum_message = f"Latest synchronized Shopify order value increased {float(growth_rate):.1f}%. {best} remains the leading revenue category."
    else:
        momentum_message = f"Latest synchronized Shopify order value decreased {abs(float(growth_rate)):.1f}%. {risk} remains under operational review."
    live_alerts = [
        alert
        for alert in ctx.get("revenue_alerts", [])
        if alert.get("status") == "open"
    ]
    if live_alerts:
        top_alert = live_alerts[0]
        risk_message = (
            f"{html.escape(str(top_alert.get('title') or 'Revenue signal detected'))}: "
            f"{html.escape(str(top_alert.get('message') or ''))}"
        )
        risk_tag = "REVIEW"
    else:
        risk_message = "No open Shopify risk signals. Monitoring remains active after each synchronization."
        risk_tag = "CLEAR"

    section_header(
        "AI DECISION FEED",
        "Autonomous Executive Decisions",
        "A live-style decision layer showing what the AI is detecting, prioritizing and monitoring.",
    )

    rows = [
        ("NOW", momentum_message, "SHOPIFY SIGNAL"),
        ("SYNC", "Next-order forecast scenario refreshed from synchronized Shopify order values.", "FORECAST"),
        ("RISK", risk_message, risk_tag),
        ("LIVE", "Revenue protection layer synchronized with executive KPI engine.", "SYNCED"),
    ]
    rows_html = '<div class="ai-decision-timeline">'
    for time_label, main, tag in rows:
        rows_html += (
            '<div class="ai-decision-row">'
            f'<div class="ai-decision-time"><span class="ai-pulse-dot"></span>{html.escape(time_label)}</div>'
            f'<div class="ai-decision-main">{main}</div>'
            f'<div class="ai-decision-tag">{html.escape(tag)}</div>'
            '</div>'
        )
    rows_html += '</div>'
    st.markdown(rows_html, unsafe_allow_html=True)



def render_money_moment(ctx):
    """High-impact ROI block to make the SaaS feel financially indispensable."""
    total_revenue = float(ctx["shopify_total_revenue"])
    growth_score = float(ctx["shopify_growth_score"])
    risk = html.escape(str(ctx["shopify_risk_category"]))
    best = html.escape(str(ctx["shopify_best_category"]))
    live_snapshot = ctx.get("shopify_live_snapshot")

    if live_snapshot:
        order_count = int(live_snapshot.get("order_count") or 0)
        currency_code = live_snapshot.get("currency_code") or "BRL"
        average_order_value = float(live_snapshot.get("average_order_value") or 0)
        inventory_units = int(live_snapshot.get("inventory_units") or 0)
        forecast_revenue = float(live_snapshot.get("forecast_revenue") or total_revenue)
        st.markdown(
            (
                '<div class="money-moment-card">'
                '<div class="money-moment-label"><span class="ai-pulse-dot"></span>LIVE SHOPIFY REVENUE MOMENT</div>'
                f'<div class="money-moment-title">{format_shopify_currency(total_revenue, currency_code)} imported from {order_count} Shopify orders.</div>'
                '<div class="money-moment-desc">The operating layer is collecting live order history. Revenue, ticket size and inventory are already monitored; deeper leakage and category recommendations will activate as the store accumulates more sales data.</div>'
                '<div class="money-moment-grid">'
                f'<div class="money-moment-mini"><div class="money-moment-mini-label">Average Order Value</div><div class="money-moment-mini-value">{format_shopify_currency(average_order_value, currency_code)}</div></div>'
                f'<div class="money-moment-mini"><div class="money-moment-mini-label">Initial Forecast</div><div class="money-moment-mini-value">{format_shopify_currency(forecast_revenue, currency_code)}</div></div>'
                f'<div class="money-moment-mini"><div class="money-moment-mini-label">Inventory Visibility</div><div class="money-moment-mini-value">{inventory_units} units</div></div>'
                '</div>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        """
        <div class="money-moment-card">
            <div class="money-moment-label"><span class="ai-pulse-dot"></span>SHOPIFY DATA REQUIRED</div>
            <div class="money-moment-title">Connect and sync Shopify to activate live revenue intelligence.</div>
            <div class="money-moment-desc">
                Operational recommendations remain locked until a synchronized Shopify snapshot is available.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_revenue_threat_engine(ctx):
    """Compact executive threat layer focused on Shopify Plus buying psychology."""
    section_header(
        "REVENUE THREAT DETECTION",
        "Executive Threat Engine",
        "AI threat layer designed to expose campaign waste, conversion risk, inventory pressure, margin compression and retention decay.",
    )

    threats = [
        ("CAMPAIGN WASTE", "Paid traffic waste", "Not tracked", "Connect campaign attribution data to activate this indicator."),
        ("CONVERSION SIGNAL", "Conversion drop risk", "Not tracked", "Connect checkout conversion history to activate this indicator."),
        ("INVENTORY BURN", "Inventory pressure", "Tracked", "Low-stock products are reviewed during Shopify synchronization."),
        ("MARGIN RISK", "Margin compression", "Not tracked", "Connect cost and margin data to activate this indicator."),
        ("RETENTION", "Retention decay", "Not tracked", "Connect repeat-purchase history to activate this indicator."),
    ]

    html_cards = '<div class="threat-grid">'
    for label, title, value, desc in threats:
        html_cards += (
            '<div class="threat-card">'
            f'<div class="threat-label"><span class="ai-pulse-dot"></span>{html.escape(label)}</div>'
            f'<div class="threat-title">{html.escape(title)}</div>'
            f'<div class="threat-value">{html.escape(value)}</div>'
            f'<div class="threat-desc">{html.escape(desc)}</div>'
            '</div>'
        )
    html_cards += '</div>'
    st.markdown(html_cards, unsafe_allow_html=True)


def render_executive_radar(ctx):
    """Operational radar showing only measurable Shopify indicators."""
    snapshot = ctx.get("shopify_live_snapshot") or {}
    risk_score = min(100, max(0, float(snapshot.get("risk_score") or 0)))
    order_count = int(snapshot.get("order_count") or 0)
    product_count = int(snapshot.get("product_count") or 0)
    inventory_units = int(snapshot.get("inventory_units") or 0)

    section_header(
        "EXECUTIVE RADAR",
        "Shopify Operating Radar",
        "Measured Shopify visibility from synchronized revenue, orders, products and inventory.",
    )

    radar_items = [
        ("Operational Risk", f"{risk_score:.0f}/100", "Revenue concentration and inventory exposure"),
        ("Orders Synced", str(order_count), "Imported Shopify orders"),
        ("Products Synced", str(product_count), "Imported Shopify products"),
        ("Inventory Units", str(inventory_units), "Current inventory visibility"),
        ("Margin Data", "Not tracked", "Requires cost integration"),
    ]

    html_cards = '<div class="radar-grid">'
    for title, value, desc in radar_items:
        html_cards += (
            '<div class="radar-card">'
            '<div class="radar-label">SHOPIFY SNAPSHOT</div>'
            f'<div class="radar-title">{html.escape(title)}</div>'
            f'<div class="radar-value">{html.escape(value)}</div>'
            f'<div class="radar-desc">{html.escape(desc)}</div>'
            '</div>'
        )
    html_cards += '</div>'
    st.markdown(html_cards, unsafe_allow_html=True)


def render_ai_advisor_action(ctx):
    """One executive recommendation that makes the AI feel consultative and premium."""
    best = html.escape(str(ctx["shopify_best_category"]))
    risk = html.escape(str(ctx["shopify_risk_category"]))
    growth = float(ctx["shopify_growth_score"])

    section_header(
        "AI REVENUE ADVISOR ACTION",
        "Next Best Executive Move",
        "A concise AI recommendation designed to guide Shopify operators toward revenue protection and growth capture.",
    )

    st.markdown(
        f"""
        <div class="ai-advisor-action">
            <div class="ai-advisor-action-title">Review {best} as the leading revenue category while keeping {risk} under operational review.</div>
            <div class="ai-advisor-action-desc">
                The synchronized Shopify snapshot shows stronger category revenue in {best}. Keep {risk} under monitoring and validate the next-order scenario against new sales. Latest order-value growth signal: <b>{growth:.1f}%</b>.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_charts(filtered_df):
    chart_col, donut_col = st.columns([2, 1], gap="large")

    with chart_col:
        section_header(
            "REVENUE PERFORMANCE",
            "Executive Category Performance",
            "Consolidated revenue by category with premium static visualization.",
        )
        render_static_bar_chart(filtered_df)

    with donut_col:
        section_header(
            "REVENUE MIX",
            "Distribution",
            "Revenue share by category.",
        )
        render_static_donut_chart(filtered_df)


def render_shopify_metrics(shopify_average_revenue):
    section_header(
        "SHOPIFY ENTERPRISE METRICS ENGINE",
        "Strategic Shopify Metrics",
        "Advanced indicators for growth, retention, acquisition, profitability and commercial performance.",
    )
    enterprise_metrics = [
        {"title": "ROAS", "value": "Not tracked", "desc": "Connect campaign data to activate this indicator."},
        {"title": "CAC", "value": "Not tracked", "desc": "Requires attributed acquisition cost data."},
        {"title": "LTV", "value": "Not tracked", "desc": "Requires repeat purchase history."},
        {"title": "CHURN", "value": "Not tracked", "desc": "Requires customer retention history."},
        {"title": "AOV", "value": format_currency(shopify_average_revenue), "desc": "Average revenue analyzed by category."},
        {"title": "VIP CUSTOMERS", "value": "Not tracked", "desc": "Requires customer segmentation history."},
    ]
    for index in range(0, len(enterprise_metrics), 3):
        metric_columns = st.columns(3, gap="large")
        for column_index, metric in enumerate(enterprise_metrics[index:index + 3]):
            with metric_columns[column_index]:
                st.markdown(
                    f'<div class="enterprise-card"><div class="enterprise-value">{html.escape(str(metric["value"]))}</div><div class="enterprise-title">{html.escape(str(metric["title"]))}</div><div class="enterprise-desc">{html.escape(str(metric["desc"]))}</div></div>',
                    unsafe_allow_html=True,
                )


def render_health_score(shopify_growth_score, shopify_total_revenue, forecast_growth, shopify_best_category, shopify_risk_category):
    section_header(
        "EXECUTIVE AI HEALTH ENGINE",
        "Executive AI Health Score",
        "Executive score based on growth, revenue, operational risk and Shopify performance.",
    )
    health_score = 0

    gauge_col1, gauge_col2 = st.columns([1.08, 1], gap="large")
    with gauge_col1:
        render_static_health_gauge(health_score)

    with gauge_col2:
        health_status = "NOT TRACKED"
        health_color = "#94A3B8"

        st.markdown(
            f"""
            <div class="ai-response-box" style="padding:18px 20px; margin-top:8px; min-height:210px; display:flex; flex-direction:column; justify-content:center;">
                <div style="font-size:16px; font-weight:900; color:{health_color}; margin-bottom:12px; letter-spacing:0.5px;">{health_status}</div>
                <div style="font-size:14px; line-height:1.48; color:#CBD5E1;">
                    • Executive composite score: <b>Not tracked</b>.<br><br>
                    • Connect margin, campaign and retention data to activate a composite score.<br><br>
                    • Strongest operational category: <b>{html.escape(str(shopify_best_category))}</b>.<br><br>
                    • Main attention area: <b>{html.escape(str(shopify_risk_category))}</b>.<br><br>
                    • Recommendation: progressive expansion with continuous monitoring.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def build_autonomous_card(alert_text):
    alert_lower = str(alert_text).lower()
    if "risco" in alert_lower:
        return {"icon": "⚠️", "title": "OPERATIONAL RISK", "desc": alert_text, "status": "HIGH PRIORITY"}
    if "crescimento" in alert_lower or "escalar" in alert_lower:
        return {"icon": "🚀", "title": "GROWTH OPPORTUNITY", "desc": alert_text, "status": "EXPANSION DETECTED"}
    if "receita" in alert_lower or "enterprise" in alert_lower:
        return {"icon": "💰", "title": "ENTERPRISE REVENUE", "desc": alert_text, "status": "SCALE READY"}
    if "forecast" in alert_lower or "projeção" in alert_lower:
        return {"icon": "📈", "title": "POSITIVE FORECAST", "desc": alert_text, "status": "FORECAST STABLE"}
    if "estratégico" in alert_lower or "estrategico" in alert_lower:
        return {"icon": "🧠", "title": "STRATEGIC LEVEL", "desc": alert_text, "status": "ENTERPRISE READY"}
    return {"icon": "✅", "title": "STABLE OPERATION", "desc": alert_text, "status": "MONITORING ACTIVE"}


def render_autonomous_monitoring(shopify_growth_score, shopify_total_revenue, shopify_best_category, shopify_risk_category, forecast_growth, strategic_level):
    section_header(
        "SHOPIFY AUTONOMOUS AI ANALYST",
        "Autonomous Executive Analyst",
        "Autonomous AI for continuous monitoring, executive alerts, operational risks and Shopify opportunities.",
    )

    autonomous_alerts = [
        "Shopify synchronization active. Review imported revenue, orders, products and inventory for measurable signals."
    ]

    alert_col1, alert_col2, alert_col3 = st.columns(3, gap="large")
    with alert_col1:
        render_metric_card("AI Alerts", len(autonomous_alerts), description="AI monitoring")
    with alert_col2:
        executive_level = "ENTERPRISE" if len(autonomous_alerts) >= 4 else "GROWTH" if len(autonomous_alerts) >= 2 else "STABLE"
        render_metric_card("Operational Level", executive_level, description="AI system")
    with alert_col3:
        render_metric_card("Priority Action", shopify_best_category, description="Focus category")

    st.markdown(
        """
        <div class="auto-section-title">
            <div class="auto-section-badge">AUTONOMOUS AI OPERATIONS CENTER</div>
            <h2>Autonomous AI Monitoring</h2>
            <p>Executive intelligence system monitoring risks, growth, opportunities and Shopify expansion.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    autonomous_cards = [build_autonomous_card(alert) for alert in autonomous_alerts]
    autonomous_cards.extend(
        [
            {"icon": "🧠", "title": "CONTINUOUS MONITORING", "desc": "AI will continue monitoring revenue patterns, growth, operational risk and scale opportunities.", "status": "AI ACTIVE"},
            {"icon": "🚨", "title": "CRITICAL ALERTS", "desc": "Critical alerts should be prioritized for executive decision-making.", "status": "EXECUTIVE ACTION"},
            {"icon": "📊", "title": "RECURRING REVIEW", "desc": "The system recommends recurring review of lower-performing categories and progressive investment in categories with stronger revenue response.", "status": "CONTINUOUS OPTIMIZATION"},
        ]
    )

    for index in range(0, len(autonomous_cards), 2):
        card_columns = st.columns(2, gap="large")
        for column_index, card in enumerate(autonomous_cards[index:index + 2]):
            with card_columns[column_index]:
                st.markdown(
                    f'<div class="auto-card"><div class="auto-icon">{html.escape(str(card["icon"]))}</div><div class="auto-title">{html.escape(str(card["title"]))}</div><div class="auto-desc">{html.escape(str(card["desc"]))}</div><div class="auto-status">{html.escape(str(card["status"]))}</div></div>',
                    unsafe_allow_html=True,
                )


def render_executive_dashboard(ctx):
    render_hero()
    if ctx.get("shopify_live_snapshot"):
        st.markdown(
            (
                '<div style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; '
                'margin:10px 0 14px; padding:11px 14px; border-radius:14px; background:rgba(6,78,59,0.24); '
                'border:1px solid rgba(52,211,153,0.34);">'
                '<div style="color:#6EE7B7; font-size:12px; font-weight:900;"><span class="ai-pulse-dot"></span>LIVE SHOPIFY DATA</div>'
                f'<div style="color:#D1FAE5; font-size:12px; font-weight:800;">{html.escape(str(ctx.get("shopify_shop_domain")))}</div>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )
    render_money_moment(ctx)
    vertical_spacer(14)
    render_kpi_section_stable(
        total_revenue=ctx["total_sales"],
        avg_ticket=ctx["average_sales"],
        forecast_value=ctx["next_prediction"],
        growth_rate=ctx["basic_growth_rate"],
        shopify_snapshot=ctx.get("shopify_live_snapshot"),
    )
    if ctx.get("shopify_live_snapshot") and int(ctx["shopify_live_snapshot"].get("order_count") or 0) < 3:
        st.caption("Growth and forecast signals are collecting history. Add more test orders to activate trend-based Shopify intelligence.")
    vertical_spacer(12)
    render_charts(ctx["filtered_df"])
    vertical_spacer(14)
    render_revenue_risk_center(ctx)
    vertical_spacer(12)
    render_ai_decision_feed(ctx)
    vertical_spacer(12)
    render_ai_advisor_action(ctx)


def render_ai_monitoring(ctx):
    render_revenue_risk_center(ctx)
    vertical_spacer()

    section_header(
        "ALERTS",
        "Operational Alert Feed",
        "Compact revenue alerts for leakage, growth opportunities and operational priority.",
    )

    revenue = format_currency(ctx["shopify_total_revenue"])

    monitoring_cards = [
        {
            "status": "SHOPIFY SYNC",
            "title": "No open operational alerts",
            "desc": f"Revenue monitored: {revenue}. New alerts will appear after a Shopify synchronization detects a measurable signal.",
            "confidence": "LIVE SHOPIFY MONITORING",
            "tag": "MONITORING ACTIVE",
            "time": "Updated after last sync",
        },
    ]
    live_alerts = [
        alert
        for alert in ctx.get("revenue_alerts", [])
        if alert.get("status") == "open"
    ]
    if live_alerts:
        monitoring_cards = []
        severity_labels = {
            "high": "HIGH PRIORITY",
            "medium": "REVIEW REQUIRED",
            "info": "OPPORTUNITY",
        }
        for alert in live_alerts[:6]:
            updated_at = alert.get("updated_at") or alert.get("created_at")
            try:
                updated_label = datetime.fromisoformat(str(updated_at)).strftime("%b %d at %H:%M")
            except (TypeError, ValueError):
                updated_label = "Updated recently"
            severity = str(alert.get("severity") or "medium").lower()
            signal_type = str(alert.get("alert_type") or "operational_signal")
            monitoring_cards.append(
                {
                    "status": signal_type.replace("_", " ").upper(),
                    "title": str(alert.get("title") or "Revenue signal detected"),
                    "desc": html.escape(str(alert.get("message") or "")),
                    "confidence": f"SHOPIFY SIGNAL: {severity.upper()}",
                    "tag": severity_labels.get(severity, "REVIEW REQUIRED"),
                    "time": updated_label,
                }
            )

    alerts_html = '<div class="live-signal-grid">'
    for card in monitoring_cards:
        alerts_html += (
            '<div class="live-signal-card">'
            '<div class="live-signal-top">'
            f'<div class="live-signal-status">{html.escape(card["tag"])}</div>'
            f'<div class="live-signal-tag">{html.escape(card["status"])}</div>'
            '</div>'
            f'<div class="live-signal-title">{html.escape(card["title"])}</div>'
            f'<div class="live-signal-description">{card["desc"]}</div>'
            '<div class="live-signal-footer">'
            f'<div class="live-signal-confidence">{html.escape(card["confidence"])}</div>'
            f'<div class="live-signal-time">{html.escape(card["time"])}</div>'
            '</div>'
            '</div>'
        )
    alerts_html += '</div>'
    st.markdown(alerts_html, unsafe_allow_html=True)

    vertical_spacer()
    render_ai_decision_feed(ctx)


def render_forecast_intelligence(ctx):
    section_header(
        "FORECAST",
        "Growth Forecast",
        "Predictive revenue view for expansion, downside monitoring and category planning.",
    )

    trend_col1, trend_col2 = st.columns([2, 1], gap="large")
    with trend_col1:
        projected_now = float(ctx["shopify_total_revenue"])
        projected_future = float(ctx["shopify_forecast_revenue"])
        trend_df = pd.DataFrame(
            {
                "setor": ["Current baseline", "AI projected"],
                "vendas": [projected_now, projected_future],
            }
        )
        render_static_bar_chart(trend_df)

    with trend_col2:
        render_metric_card(
            "Forecast Sync",
            "Active",
            description="Synced Shopify order values",
        )
        render_metric_card(
            "Projected Lift",
            f"{float(ctx['forecast_growth']):.1f}%",
            description="Next-order revenue scenario",
        )

    vertical_spacer()
    render_forecast_section_stable(
        current_revenue=ctx["shopify_total_revenue"],
        forecast_revenue=ctx["shopify_forecast_revenue"],
        forecast_growth=ctx["forecast_growth"],
        best_category=ctx["shopify_best_category"],
        risk_category=ctx["shopify_risk_category"],
    )
    vertical_spacer()
    render_executive_radar(ctx)


def render_strategic_decisions(ctx):
    section_header(
        "SHOPIFY STRATEGIC AI ENGINE",
        "Strategic Decisions with AI",
        "Strategic intelligence for expansion, growth, operational risk and Shopify opportunities.",
    )
    strategy_col1, strategy_col2, strategy_col3 = st.columns(3, gap="large")
    with strategy_col1:
        render_metric_card("Strategic Score", "Not tracked", description="Requires margin, campaign and retention data")
    with strategy_col2:
        render_metric_card("Strategic Level", ctx["strategic_level"], description="Shopify synchronization status")
    with strategy_col3:
        render_metric_card("Leading Category", ctx["shopify_best_category"], description="Highest synchronized category revenue")

    st.markdown(
        f"""
        <div class="ai-response-box">
            <b>Shopify Operational Review:</b><br><br>
            &bull; <b>{html.escape(str(ctx['shopify_best_category']))}</b> leads synchronized category revenue and should be reviewed first.<br><br>
            &bull; <b>{html.escape(str(ctx['shopify_risk_category']))}</b> has the lowest synchronized category revenue and requires operational review.<br><br>
            &bull; Margin, campaign attribution and retention data are not connected yet.<br><br>
            &bull; Review inventory availability and new orders before changing acquisition spend.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_ai_agents(ctx):
    if "shopify_insights_result" not in st.session_state:
        st.session_state.shopify_insights_result = None
    if "executive_report_result" not in st.session_state:
        st.session_state.executive_report_result = None
    if "executive_report_pdf_path" not in st.session_state:
        st.session_state.executive_report_pdf_path = None
    if "sales_agent_result" not in st.session_state:
        st.session_state.sales_agent_result = None
    if "finance_agent_result" not in st.session_state:
        st.session_state.finance_agent_result = None

    render_strategic_decisions(ctx)
    vertical_spacer()

    section_header(
        "SHOPIFY AI INSIGHTS ENGINE",
        "Intelligent Shopify Analysis",
        "Specialized e-commerce agent for winners, risks, scale opportunities and growth recommendations.",
    )

    if st.button("Generate Shopify AI Insights", key="btn_generate_shopify_ai_insights"):
        try:
            with st.spinner("Analyzing data with Shopify AI agent..."):
                shopify_agent = ShopifyAIAgent()
                st.session_state.shopify_insights_result = shopify_agent.generate_shopify_insights(ctx["filtered_df"])
            st.success("Shopify insights generated successfully.")
        except Exception as error:
            st.session_state.shopify_insights_result = f"Erro ao gerar insights Shopify: {error}"

    if st.session_state.shopify_insights_result is not None:
        render_text_result("Shopify AI Insights", st.session_state.shopify_insights_result)

    vertical_spacer()
    section_header(
        "EXECUTIVE AI REPORT",
        "Executive AI Report",
        "Generate a strategic report with executive data reading, opportunities, risks and recommendations.",
    )

    if st.button("Generate Executive AI Report", key="btn_generate_executive_ai_report"):
        try:
            with st.spinner("Generating premium executive report..."):
                executive_agent = ExecutiveAgent()
                report = executive_agent.generate_executive_report(ctx["filtered_df"])
            st.session_state.executive_report_result = report

            pdf_service = PDFService()
            pdf_path = pdf_service.generate_pdf(str(report), str(REPORT_PATH))
            st.session_state.executive_report_pdf_path = pdf_path
            st.success("Executive report generated successfully.")
        except Exception as error:
            st.session_state.executive_report_result = f"Erro: {error}"
            st.session_state.executive_report_pdf_path = None

    if st.session_state.executive_report_result is not None:
        render_text_result("Executive AI Report", st.session_state.executive_report_result)

    if st.session_state.executive_report_pdf_path:
        try:
            with open(st.session_state.executive_report_pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="Download Executive Report PDF",
                    data=pdf_file,
                    file_name="relatorio_executivo.pdf",
                    mime="application/pdf",
                    key="download_executive_report_pdf",
                )
        except Exception:
            pass

    vertical_spacer()
    agent_col1, agent_col2 = st.columns(2, gap="large")

    with agent_col1:
        st.markdown(
            '<div class="agent-card"><div class="ai-badge">SALES AGENT</div><div class="agent-title">Sales Agent</div><div class="agent-subtitle">Analyzes sales performance, growth opportunities and high-potential categories.</div></div>',
            unsafe_allow_html=True,
        )
        if st.button("Run Sales Agent", key="btn_run_sales_agent"):
            try:
                with st.spinner("Running sales agent..."):
                    sales_agent = SalesAgent()
                    st.session_state.sales_agent_result = sales_agent.analyze_sales(ctx["filtered_df"])
                st.success("Sales analysis completed.")
            except Exception as error:
                st.session_state.sales_agent_result = f"Erro: {error}"

        if st.session_state.sales_agent_result is not None:
            render_text_result("Sales Agent Report", st.session_state.sales_agent_result)

    with agent_col2:
        st.markdown(
            '<div class="agent-card"><div class="ai-badge">FINANCE AGENT</div><div class="agent-title">Finance Agent</div><div class="agent-subtitle">Evaluates financial indicators, operational efficiency, risks and attention points.</div></div>',
            unsafe_allow_html=True,
        )
        if st.button("Run Finance Agent", key="btn_run_finance_agent"):
            try:
                with st.spinner("Running finance agent..."):
                    finance_agent = FinanceAgent()
                    st.session_state.finance_agent_result = finance_agent.analyze_finance(ctx["filtered_df"])
                st.success("Financial analysis completed.")
            except Exception as error:
                st.session_state.finance_agent_result = f"Erro: {error}"

        if st.session_state.finance_agent_result is not None:
            render_text_result("Finance Agent Report", st.session_state.finance_agent_result)

def render_ai_copilot(ctx):
    section_header(
        "REVENUE ADVISOR",
        "AI Revenue Advisor",
        "Operational revenue guidance for leakage, scale, protection and retention decisions.",
    )

    if "copilot_messages" not in st.session_state:
        st.session_state.copilot_messages = []

    st.markdown('<div class="copilot-prompt-label">Revenue questions designed for Shopify operators</div>', unsafe_allow_html=True)
    prompt_cols = st.columns(4, gap="small")
    quick_prompts = [
        "Revenue Leakage",
        "Scale Opportunities",
        "Revenue Protection",
        "Retention Stability",
    ]
    for i, prompt in enumerate(quick_prompts):
        with prompt_cols[i]:
            if st.button(prompt, key=f"copilot_quick_prompt_{i}", use_container_width=True):
                st.session_state.copilot_question_prefill = prompt

    default_question = st.session_state.pop("copilot_question_prefill", "")

    with st.form("copilot_question_form", clear_on_submit=True):
        question = st.text_input(
            "Revenue operating question",
            value=default_question,
            placeholder="Ask where revenue is leaking, what should scale, or how to protect growth...",
            key="copilot_question_input",
        )
        submitted = st.form_submit_button("Run AI Revenue Analysis")

    if submitted and question.strip():
        best = str(ctx["best_sector"])
        risk = str(ctx["lowest_sector"])
        total = format_currency(ctx["shopify_total_revenue"])
        forecast = format_currency(ctx["shopify_forecast_revenue"])
        question_text = question.strip()
        normalized_question = question_text.lower()

        if "leak" in normalized_question or "vaz" in normalized_question:
            focus = "Revenue leakage"
            answer = (
                f"Signal: {risk} is the lowest synchronized revenue category. This is a review signal, not confirmed leakage. "
                f"Why it matters: lower category revenue can indicate a merchandising, inventory or fulfillment issue. "
                f"Next move: review synchronized orders and inventory for {risk} before changing budget."
            )
        elif "scale" in normalized_question or "opportun" in normalized_question:
            focus = "Scale opportunity"
            answer = (
                f"Signal: {best} currently leads synchronized category revenue. "
                f"Why it matters: it is the first category to review for a controlled scale test. "
                f"Next move: validate stock availability and compare new orders before increasing acquisition spend."
            )
        elif "protect" in normalized_question or "protection" in normalized_question:
            focus = "Revenue protection"
            answer = (
                f"Signal: {total} is imported from Shopify, with a next-order scenario of {forecast}. "
                f"Why it matters: revenue protection begins with synchronized order and inventory visibility. "
                f"Next move: keep {risk} under operational review and check new alerts after each sync."
            )
        elif "retention" in normalized_question or "stability" in normalized_question:
            focus = "Retention stability"
            answer = (
                "Signal: retention stability is not tracked yet. "
                "Why it matters: synchronized order totals alone do not prove repeat customer behavior. "
                "Next move: connect customer repeat-purchase history before making retention decisions."
            )
        else:
            focus = "Executive revenue decision"
            answer = (
                f"Signal: {best} leads synchronized category revenue while {risk} is the lowest revenue category. "
                f"Why it matters: these are operational review signals derived from the Shopify snapshot. "
                f"Next move: review inventory, new orders and the next-order scenario of {forecast} before acting."
            )

        st.session_state.copilot_messages.insert(
            0,
            {"question": question_text, "focus": focus, "answer": answer},
        )

    if not st.session_state.copilot_messages:
        st.info("AI continuously analyzes revenue leakage, growth acceleration, retention stability and operational risk across your Shopify operation.")
    else:
        for i, message in enumerate(st.session_state.copilot_messages[:8]):
            st.markdown(
                f'''<div class="enterprise-history-card">
                    <div class="ai-badge">{html.escape(message.get("focus", "Revenue Decision"))}</div>
                    <b>Question:</b> {html.escape(message["question"])}<br><br>
                    <b>Operating brief:</b> {html.escape(message["answer"])}
                </div>''',
                unsafe_allow_html=True,
            )


def render_data_center(ctx):
    if ctx.get("is_shopify_connected"):
        section_header(
            "SHOPIFY DATA AUDIT",
            "Live Shopify Import",
            "Revenue categories derived from synchronized Shopify order line items.",
        )
        st.markdown("### Shopify category revenue")
        premium_dataframe(ctx["shopify_category_df"], height=300, key="shopify_category_revenue")
        st.info(
            "Shopify is the active operating source. CSV and XLSX uploads remain available "
            "in the left sidebar for isolated file analysis."
        )
        if ctx.get("isolated_upload_df") is not None:
            st.markdown("### Isolated file analysis")
            st.caption("This uploaded file is visible for audit only. It does not affect live Shopify dashboards, forecasts or recommendations.")
            premium_dataframe(ctx["isolated_upload_df"], height=300, key="isolated_upload_analysis")
        return

    if not ctx.get("has_uploaded_file"):
        section_header(
            "DATA CENTER",
            "Connect Shopify to begin",
            "Operational dashboards activate only after a Shopify connection and synchronized snapshot.",
        )
        st.info("Connect Shopify in this area. CSV and XLSX uploads remain available in the left sidebar for isolated file analysis.")
        return

    section_header(
        "DATA CENTER",
        "Raw Data & Upload Preview",
        "Technical area for audit, upload validation, treated data and operational filters.",
    )
    st.markdown("### Upload source")
    st.info("Use the left sidebar Data Source area to upload CSV or XLSX files.")
    st.markdown("### Raw Preview")
    premium_dataframe(ctx["original_df"].head(20), height=300, key="data_center_raw_preview")
    st.markdown("### Treated Data")
    premium_dataframe(ctx["filtered_df"], height=300, key="data_center_treated_data")


def render_shopify_setup(ctx):
    plan = get_plan(st.session_state.saas_user.get("tenant_plan"))
    trial_days_left = get_trial_days_left(st.session_state.saas_user)
    access_token = st.session_state.get("saas_access_token")

    shopify_status = {"status": "not_connected"}
    if access_token:
        try:
            status_response = requests.get(
                f"{API_BASE_URL}/shopify/status",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=8,
            )
            if status_response.ok:
                shopify_status = status_response.json()
        except Exception:
            shopify_status = {"status": "not_connected"}

    section_header(
        "SHOPIFY SETUP",
        "Shopify Connection",
        "Simple onboarding path for a 14-day trial: connect Shopify, wait for sync, then operate from the revenue dashboard.",
    )

    is_shopify_connected = shopify_status.get("status") == "connected"
    if is_shopify_connected:
        title = "Dashboard ready"
        desc = f"{shopify_status.get('shop_domain')} is connected. Revenue, product and order signals can now power the operating dashboard."
    else:
        title = "Store not connected"
        desc = "Start the 14-day trial without a card and connect the Shopify store."

    st.markdown(
        f"""
        <div class="ai-card">
            <div class="ai-badge">14-DAY TRIAL - NO CARD</div>
            <div class="ai-title">{html.escape(title)}</div>
            <div class="ai-subtitle">{html.escape(desc)}</div>
            <div style="margin-top:12px; color:#DBEAFE; font-size:13px; font-weight:800;">
                Current plan: {html.escape(plan["name"])} - US${plan["price"]}/mo after trial - {trial_days_left} trial days left.
            </div>
            <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top:14px;">
                <span class="auto-status">Connect Shopify</span>
                <span class="auto-status">Initial Sync</span>
                <span class="auto-status">Dashboard Ready</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if is_shopify_connected:
        connected_at = shopify_status.get("connected_at")
        last_sync_at = shopify_status.get("last_sync_at")
        latest_sync = shopify_status.get("latest_sync") or {}
        auto_sync_interval_minutes = 15
        try:
            automation_response = requests.get(
                f"{API_BASE_URL}/shopify/sync/automation",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=8,
            )
            if automation_response.ok:
                automation_status = automation_response.json()
                auto_sync_interval_minutes = max(1, int(automation_status["interval_seconds"]) // 60)
        except Exception:
            pass
        try:
            connected_at_label = datetime.fromisoformat(str(connected_at)).strftime("%b %d, %Y at %H:%M")
        except (TypeError, ValueError):
            connected_at_label = "Connected recently"
        try:
            last_sync_label = datetime.fromisoformat(str(last_sync_at)).strftime("%b %d, %Y at %H:%M")
        except (TypeError, ValueError):
            last_sync_label = "Initial sync pending"
        revenue_total = float(latest_sync.get("revenue_total") or 0)
        sync_summary_html = ""
        if latest_sync:
            sync_summary_html = (
                '<div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); gap:10px; margin-top:18px;">'
                f'<div><div style="color:#94A3B8; font-size:11px; font-weight:800;">ORDERS</div><div style="color:#F8FAFC; font-size:20px; font-weight:900;">{int(latest_sync.get("order_count") or 0)}</div></div>'
                f'<div><div style="color:#94A3B8; font-size:11px; font-weight:800;">PRODUCTS</div><div style="color:#F8FAFC; font-size:20px; font-weight:900;">{int(latest_sync.get("product_count") or 0)}</div></div>'
                f'<div><div style="color:#94A3B8; font-size:11px; font-weight:800;">INVENTORY UNITS</div><div style="color:#F8FAFC; font-size:20px; font-weight:900;">{int(latest_sync.get("inventory_units") or 0)}</div></div>'
                f'<div><div style="color:#94A3B8; font-size:11px; font-weight:800;">REVENUE IMPORTED</div><div style="color:#F8FAFC; font-size:20px; font-weight:900;">{html.escape(str(latest_sync.get("currency_code") or ""))} {revenue_total:,.2f}</div></div>'
                '</div>'
            )

        st.markdown(
            f"""
            <div style="background:linear-gradient(145deg,rgba(6,78,59,0.34),rgba(15,23,42,0.96)); border:1px solid rgba(52,211,153,0.42); border-radius:18px; padding:22px; margin-top:14px; margin-bottom:14px; box-shadow:0 14px 36px rgba(0,0,0,0.18);">
                <div style="display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap;">
                    <div>
                        <div style="display:flex; align-items:center; gap:9px; margin-bottom:10px;">
                            <span style="width:10px; height:10px; border-radius:50%; background:#34D399; box-shadow:0 0 14px rgba(52,211,153,0.95);"></span>
                            <span style="color:#6EE7B7; font-size:12px; font-weight:900;">CONNECTED</span>
                        </div>
                        <div style="color:#FFFFFF; font-size:22px; font-weight:900;">Shopify store connected</div>
                        <div style="color:#D1FAE5; font-size:15px; font-weight:800; margin-top:7px;">{html.escape(str(shopify_status.get("shop_domain")))}</div>
                    </div>
                    <div style="min-width:260px; color:#CBD5E1; font-size:13px; line-height:1.75;">
                        <div><strong style="color:#F8FAFC;">Connected:</strong> {html.escape(connected_at_label)}</div>
                        <div><strong style="color:#F8FAFC;">Last sync:</strong> {html.escape(last_sync_label)}</div>
                    </div>
                </div>
                {sync_summary_html}
            </div>
            """,
            unsafe_allow_html=True,
        )
        sync_cols = st.columns([1, 1], gap="small")
        with sync_cols[0]:
            if st.button("Sync Now", key="btn_run_shopify_sync", use_container_width=True):
                try:
                    with st.spinner("Importing Shopify orders, products and inventory..."):
                        response = requests.post(
                            f"{API_BASE_URL}/shopify/sync",
                            headers={"Authorization": f"Bearer {access_token}"},
                            timeout=60,
                        )
                    if not response.ok:
                        raise ValueError(response.json().get("detail", response.text))
                    st.success("Shopify synchronization completed.")
                    st.rerun()
                except Exception as error:
                    st.error(f"Shopify synchronization failed: {error}")
        with sync_cols[1]:
            if st.button("Refresh Sync Status", key="btn_refresh_shopify_sync_status", use_container_width=True):
                st.rerun()
        st.success(f"Automatic sync active. Shopify data refreshes every {auto_sync_interval_minutes} minutes.")
        st.caption("Use Sync Now for an immediate refresh. Use the control below only if you need to connect a different Shopify store.")

    def render_connection_controls():
        shop_domain = st.text_input(
            "Shopify store domain",
            placeholder="your-store.myshopify.com",
            key="shopify_store_domain_input",
        )

        setup_cols = st.columns([1, 1], gap="small")
        with setup_cols[0]:
            if st.button("Connect Shopify", key="btn_connect_shopify", use_container_width=True):
                try:
                    if not shop_domain.strip():
                        raise ValueError("Enter your Shopify store domain.")
                    response = requests.post(
                        f"{API_BASE_URL}/shopify/install",
                        headers={"Authorization": f"Bearer {access_token}"},
                        json={"shop": shop_domain.strip()},
                        timeout=10,
                    )
                    if not response.ok:
                        raise ValueError(response.json().get("detail", response.text))
                    st.link_button(
                        "Open Shopify Authorization",
                        response.json()["install_url"],
                        use_container_width=True,
                    )
                    st.info("Shopify will ask the merchant to authorize the app. After approval, the dashboard will become ready.")
                except Exception as error:
                    st.error(f"Shopify connection is not ready: {error}")
        with setup_cols[1]:
            if st.button("Refresh Status", key="btn_refresh_shopify_status", use_container_width=True):
                st.rerun()

    if is_shopify_connected:
        with st.expander("Connect a different Shopify store"):
            render_connection_controls()
    else:
        render_connection_controls()

    vertical_spacer()
    section_header(
        "MOBILE ALERTS",
        "Notification Center",
        "Choose how urgent Shopify revenue signals reach the operating team.",
    )
    notification_preferences = {}
    notification_deliveries = []
    if access_token:
        try:
            preferences_response = requests.get(
                f"{API_BASE_URL}/notifications/preferences",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=8,
            )
            if preferences_response.ok:
                notification_preferences = preferences_response.json()
            deliveries_response = requests.get(
                f"{API_BASE_URL}/notifications/deliveries?limit=8",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=8,
            )
            if deliveries_response.ok:
                notification_deliveries = deliveries_response.json().get("deliveries", [])
        except Exception:
            pass

    with st.form("notification_preferences_form"):
        notification_cols = st.columns(3, gap="small")
        with notification_cols[0]:
            email_enabled = st.toggle(
                "Email alerts",
                value=bool(notification_preferences.get("email_enabled")),
            )
            email_recipients = st.text_input(
                "Email recipients",
                value=str(notification_preferences.get("email_recipients") or ""),
                placeholder="owner@store.com, ops@store.com",
            )
        with notification_cols[1]:
            whatsapp_enabled = st.toggle(
                "WhatsApp alerts",
                value=bool(notification_preferences.get("whatsapp_enabled")),
            )
            whatsapp_phone = st.text_input(
                "WhatsApp number",
                value=str(notification_preferences.get("whatsapp_phone") or ""),
                placeholder="+14165550123",
            )
            whatsapp_opt_in = st.checkbox(
                "Recipient consent confirmed",
                value=bool(notification_preferences.get("whatsapp_opt_in")),
            )
        with notification_cols[2]:
            sms_enabled = st.toggle(
                "SMS fallback",
                value=bool(notification_preferences.get("sms_enabled")),
            )
            sms_phone = st.text_input(
                "SMS number",
                value=str(notification_preferences.get("sms_phone") or ""),
                placeholder="+14165550123",
            )
            severity_options = ["critical", "high", "medium", "info"]
            current_severity = str(notification_preferences.get("minimum_severity") or "high")
            minimum_severity = st.selectbox(
                "Minimum priority",
                options=severity_options,
                index=severity_options.index(current_severity),
            )
        save_notifications = st.form_submit_button(
            "Save notification settings",
            use_container_width=True,
        )

    if save_notifications:
        try:
            response = requests.put(
                f"{API_BASE_URL}/notifications/preferences",
                headers={"Authorization": f"Bearer {access_token}"},
                json={
                    "email_enabled": email_enabled,
                    "email_recipients": email_recipients,
                    "whatsapp_enabled": whatsapp_enabled,
                    "whatsapp_phone": whatsapp_phone,
                    "whatsapp_opt_in": whatsapp_opt_in,
                    "sms_enabled": sms_enabled,
                    "sms_phone": sms_phone,
                    "minimum_severity": minimum_severity,
                },
                timeout=8,
            )
            if not response.ok:
                raise ValueError(response.json().get("detail", response.text))
            st.success("Notification settings saved.")
            st.rerun()
        except Exception as error:
            st.error(f"Notification settings were not saved: {error}")

    st.caption(
        "Channels remain inactive until enabled. WhatsApp requires confirmed recipient consent. "
        "Provider credentials are configured securely in the server environment."
    )
    if notification_deliveries:
        delivery_rows = [
            {
                "Alert": delivery.get("alert_title"),
                "Priority": str(delivery.get("alert_severity") or "").upper(),
                "Channel": str(delivery.get("channel") or "").upper(),
                "Status": str(delivery.get("status") or "").replace("_", " ").upper(),
                "Updated": str(delivery.get("updated_at") or ""),
            }
            for delivery in notification_deliveries
        ]
        st.markdown("#### Delivery history")
        st.dataframe(delivery_rows, use_container_width=True, hide_index=True)
    else:
        st.info("No mobile or email notifications have been queued yet.")

    vertical_spacer()
    plan_cols = st.columns(3, gap="small")
    plan_accents = ["green", "blue", "amber"]
    current_plan_key = st.session_state.saas_user.get("tenant_plan")
    for col, (plan_key, plan_item), accent in zip(
        plan_cols,
        PLAN_CATALOG.items(),
        plan_accents,
    ):
        with col:
            render_plan_card(
                plan_item,
                accent=accent,
                is_current=plan_key == current_plan_key,
            )

    vertical_spacer()
    render_data_center(ctx)


# Sidebar shell
SIDEBAR_HTML = """
<div class="sidebar-card">
    <div class="sidebar-logo">IA</div>
    <div class="sidebar-title">Shopify AI</div>
    <div class="sidebar-description">Revenue intelligence for Shopify stores, forecasts and growth signals.</div>
    <div class="online-badge"><div class="online-dot"></div><div class="online-text">System Online</div></div>
</div>
"""
with st.sidebar:
    st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)


try:
    create_tables()
    bootstrap_admin_user()
except Exception as error:
    st.error(f"Error preparing SaaS authentication: {error}")
    st.stop()

if "saas_user" not in st.session_state:
    st.session_state.saas_user = None

if st.session_state.saas_user is None:
    login_html = """
    <div class="login-card">
        <div class="ai-badge">MULTI-CLIENT SAAS</div>
        <div class="login-title">Company Access</div>
        <div class="login-subtitle">Sign in with your business email to access your company's isolated revenue workspace.</div>
    </div>
    """
    st.markdown(login_html, unsafe_allow_html=True)

    with st.form("saas_login_form"):
        login_email = st.text_input("Email", key="saas_login_email")
        login_password = st.text_input("Password", type="password", key="saas_login_password")
        submitted_login = st.form_submit_button("Sign in")

    if submitted_login:
        user = authenticate_user(login_email, login_password)
        if user:
            st.session_state.saas_user = dict(user)
            st.session_state.saas_access_token = create_access_token(user)
            st.rerun()
        else:
            st.error("Invalid email or password.")

    st.info("Use the bootstrap user configured in .env to access the first tenant.")
    st.stop()

current_user = st.session_state.saas_user
if not st.session_state.get("saas_access_token"):
    st.session_state.saas_access_token = create_access_token(current_user)
name = current_user["name"]
current_plan = get_plan(current_user.get("tenant_plan"))
trial_days_left = get_trial_days_left(current_user)
shopify_dashboard_status = {"status": "not_connected", "latest_sync": None, "recent_syncs": []}
revenue_alerts = []
try:
    dashboard_status_response = requests.get(
        f"{API_BASE_URL}/shopify/status",
        headers={"Authorization": f"Bearer {st.session_state.saas_access_token}"},
        timeout=8,
    )
    if dashboard_status_response.ok:
        shopify_dashboard_status = dashboard_status_response.json()
except Exception:
    pass
try:
    alerts_response = requests.get(
        f"{API_BASE_URL}/alerts?limit=12",
        headers={"Authorization": f"Bearer {st.session_state.saas_access_token}"},
        timeout=8,
    )
    if alerts_response.ok:
        revenue_alerts = alerts_response.json().get("alerts", [])
except Exception:
    pass

if st.sidebar.button("Sign out", key="saas_logout"):
    st.session_state.saas_user = None
    st.session_state.saas_access_token = None
    st.rerun()

st.sidebar.success(f"Welcome, {name}")
st.sidebar.caption(f"Company: {current_user['tenant_name']}")
st.sidebar.caption(f"Plan: {current_plan['name']} - US${current_plan['price']}/mo")
st.sidebar.caption(f"Trial: {trial_days_left} days left, no card")

if current_user["role"] in {"owner", "admin"}:
    with st.sidebar.expander("New SaaS Client", expanded=False):
        with st.form("new_tenant_form"):
            new_tenant_name = st.text_input("Company")
            new_tenant_slug = st.text_input("Slug")
            new_admin_name = st.text_input("Admin name")
            new_admin_email = st.text_input("Admin email")
            new_admin_password = st.text_input("Initial password", type="password")
            create_client_submitted = st.form_submit_button("Create client")

        if create_client_submitted:
            try:
                required_fields = [
                    new_tenant_name,
                    new_tenant_slug,
                    new_admin_name,
                    new_admin_email,
                    new_admin_password,
                ]
                if not all(field.strip() for field in required_fields):
                    raise ValueError("Fill all new client fields.")
                if len(new_admin_password) < 8:
                    raise ValueError("Initial password must have at least 8 characters.")

                tenant = create_tenant(new_tenant_name, new_tenant_slug)
                create_user(
                    tenant_id=tenant["id"],
                    name=new_admin_name,
                    email=new_admin_email,
                    password_hash=hash_password(new_admin_password),
                    role="owner",
                )
                st.success("Client created successfully.")
            except Exception as error:
                st.error(f"Error creating client: {error}")

with st.sidebar.expander("Data Source", expanded=False):
    uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"], key="sidebar_data_uploader")

is_shopify_connected = shopify_dashboard_status.get("status") == "connected"
shopify_live_snapshot = shopify_dashboard_status.get("latest_sync")
shopify_category_df = build_shopify_category_dataframe(
    shopify_live_snapshot,
    is_connected=is_shopify_connected,
)

try:
    if uploaded_file is not None:
        file_name = uploaded_file.name.lower()
        if file_name.endswith(".csv"):
            original_df = pd.read_csv(uploaded_file)
        elif file_name.endswith(".xlsx"):
            original_df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported format. Upload CSV or Excel.")
            st.stop()
    elif is_shopify_connected:
        original_df = shopify_category_df.copy()
    else:
        original_df = pd.DataFrame(
            [{"setor": "Connect Shopify to activate revenue analysis", "vendas": 0.0}]
        )
except Exception as error:
    st.error(f"Error loading file: {error}")
    st.stop()

original_df = normalize_dataframe(original_df)
filtered_df, detected_text_column, detected_numeric_column = prepare_business_dataframe(original_df)
if filtered_df is None or filtered_df.empty:
    st.error("The file must contain one text column and one numeric column.")
    st.stop()

isolated_upload_df = filtered_df.copy() if uploaded_file is not None else None

if is_shopify_connected:
    filtered_df = shopify_category_df.copy()

st.sidebar.markdown("## Operating Areas")
selected_page = st.sidebar.selectbox(
    "Area",
    options=[
        "Revenue Command Center",
        "Risk Center",
        "Forecast",
        "AI Revenue Advisor",
        "Data & Setup",
    ],
    index=0,
    key="sidebar_operating_area_v3",
)

st.sidebar.markdown("## Operating Filters")
available_sectors = sorted(filtered_df["setor"].unique())
selected_sector = st.sidebar.selectbox(
    "Category",
    options=["All"] + available_sectors,
    index=0,
    key="sidebar_category_filter_v3",
)

min_revenue = int(filtered_df["vendas"].min())
max_revenue = int(filtered_df["vendas"].max())
if min_revenue == max_revenue:
    selected_min_revenue = min_revenue
else:
    selected_min_revenue = st.sidebar.slider(
        "Minimum revenue",
        min_revenue,
        max_revenue,
        min_revenue,
        key="sidebar_min_revenue_filter_v3",
    )

if selected_sector != "All":
    filtered_df = filtered_df[filtered_df["setor"] == selected_sector]

filtered_df = filtered_df[filtered_df["vendas"] >= selected_min_revenue]
if filtered_df.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
    st.stop()

# Shared business context
total_sales = filtered_df["vendas"].sum()
average_sales = filtered_df["vendas"].mean()
best_sector = filtered_df.loc[filtered_df["vendas"].idxmax(), "setor"]
lowest_sector = filtered_df.loc[filtered_df["vendas"].idxmin(), "setor"]

next_prediction = 0
forecast_chart = None

basic_growth_rate = 0
if total_sales > 0:
    basic_growth_rate = ((float(filtered_df["vendas"].max()) - float(filtered_df["vendas"].min())) / float(filtered_df["vendas"].max())) * 100

shopify_total_revenue = filtered_df["vendas"].sum()
shopify_average_revenue = filtered_df["vendas"].mean()
shopify_max_revenue = filtered_df["vendas"].max()
shopify_min_revenue = filtered_df["vendas"].min()
shopify_best_category = filtered_df.loc[filtered_df["vendas"].idxmax(), "setor"]
shopify_risk_category = filtered_df.loc[filtered_df["vendas"].idxmin(), "setor"]
if shopify_live_snapshot:
    shopify_total_revenue = float(shopify_live_snapshot.get("revenue_total") or 0)
    synced_order_count = int(shopify_live_snapshot.get("order_count") or 0)
    if synced_order_count:
        shopify_average_revenue = shopify_total_revenue / synced_order_count
if shopify_max_revenue > 0:
    shopify_growth_score = ((shopify_max_revenue - shopify_min_revenue) / shopify_max_revenue) * 100
else:
    shopify_growth_score = 0
if shopify_live_snapshot:
    shopify_growth_score = float(shopify_live_snapshot.get("growth_rate") or 0)

shopify_forecast_revenue = shopify_total_revenue
if shopify_live_snapshot:
    shopify_forecast_revenue = float(
        shopify_live_snapshot.get("forecast_revenue") or shopify_total_revenue
    )
forecast_growth = 0
if shopify_total_revenue > 0:
    forecast_growth = (
        (shopify_forecast_revenue - shopify_total_revenue)
        / shopify_total_revenue
    ) * 100

strategic_score = None
strategic_level = "SNAPSHOT ACTIVE" if shopify_live_snapshot else "AWAITING SYNC"

ctx = {
    "original_df": original_df,
    "filtered_df": filtered_df,
    "isolated_upload_df": isolated_upload_df,
    "shopify_category_df": shopify_category_df,
    "total_sales": total_sales,
    "average_sales": average_sales,
    "best_sector": best_sector,
    "lowest_sector": lowest_sector,
    "next_prediction": next_prediction,
    "forecast_chart": forecast_chart,
    "basic_growth_rate": basic_growth_rate,
    "shopify_total_revenue": shopify_total_revenue,
    "shopify_average_revenue": shopify_average_revenue,
    "shopify_forecast_revenue": shopify_forecast_revenue,
    "shopify_best_category": shopify_best_category,
    "shopify_risk_category": shopify_risk_category,
    "shopify_growth_score": shopify_growth_score,
    "forecast_growth": forecast_growth,
    "strategic_score": strategic_score,
    "strategic_level": strategic_level,
    "shopify_live_snapshot": shopify_live_snapshot,
    "is_shopify_connected": is_shopify_connected,
    "has_uploaded_file": uploaded_file is not None,
    "revenue_alerts": revenue_alerts,
    "shopify_recent_syncs": shopify_dashboard_status.get("recent_syncs") or [],
    "shopify_shop_domain": shopify_dashboard_status.get("shop_domain"),
    "shopify_live_risk_score": (
        float(shopify_live_snapshot.get("risk_score") or 0)
        if shopify_live_snapshot
        else None
    ),
}

if "last_selected_page_v3" not in st.session_state:
    st.session_state.last_selected_page_v3 = selected_page

if st.session_state.last_selected_page_v3 != selected_page:
    st.session_state.last_selected_page_v3 = selected_page
    st.session_state.pop("copilot_question_prefill", None)

if selected_page != "Data & Setup" and not shopify_live_snapshot:
    section_header(
        "SHOPIFY DATA REQUIRED",
        "Connect and sync Shopify to activate this area",
        "Operational intelligence stays locked until the store has a synchronized Shopify snapshot.",
    )
    if is_shopify_connected:
        st.info("The store is connected. Open Data & Setup and run Sync Now.")
    else:
        st.info("Open Data & Setup and connect the Shopify store first.")
elif selected_page == "Revenue Command Center":
    render_executive_dashboard(ctx)
elif selected_page == "Risk Center":
    render_ai_monitoring(ctx)
elif selected_page == "Forecast":
    render_forecast_intelligence(ctx)
elif selected_page == "AI Revenue Advisor":
    render_ai_copilot(ctx)
elif selected_page == "Data & Setup":
    render_shopify_setup(ctx)
