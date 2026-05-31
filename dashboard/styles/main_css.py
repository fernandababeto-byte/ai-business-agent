MAIN_CSS = """
<style>
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header[data-testid="stHeader"] {
    visibility: visible !important;
    background: rgba(2, 6, 23, 0.82) !important;
    backdrop-filter: blur(14px);
    border-bottom: 1px solid rgba(255,255,255,0.08);
}

[data-testid="collapsedControl"] {
    visibility: visible !important;
    display: flex !important;
    opacity: 1 !important;
    z-index: 999999 !important;
}

[data-testid="collapsedControl"] button {
    background: linear-gradient(135deg, #2563EB, #7C3AED) !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
    border-radius: 14px !important;
    width: 48px !important;
    height: 48px !important;
    box-shadow:
        0 0 0 3px rgba(37,99,235,0.22),
        0 12px 30px rgba(37,99,235,0.45) !important;
}

[data-testid="collapsedControl"] button:hover {
    transform: scale(1.06);
    box-shadow:
        0 0 0 4px rgba(124,58,237,0.28),
        0 16px 36px rgba(124,58,237,0.55) !important;
}

[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapseButton"] svg,
button[kind="header"] svg {
    color: white !important;
    fill: white !important;
    stroke: white !important;
    width: 26px !important;
    height: 26px !important;
}

button[kind="header"],
[data-testid="stSidebarCollapseButton"] {
    visibility: visible !important;
    display: flex !important;
    opacity: 1 !important;
    color: white !important;
    background: linear-gradient(135deg, #2563EB, #7C3AED) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
    box-shadow:
        0 0 0 3px rgba(37,99,235,0.22),
        0 12px 30px rgba(37,99,235,0.45) !important;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(37,99,235,0.16), transparent 32%),
        radial-gradient(circle at top right, rgba(124,58,237,0.14), transparent 32%),
        linear-gradient(180deg, #020617 0%, #081028 100%);
    color: #F8FAFC;
}

.block-container {
    padding-top: 4rem;
    padding-bottom: 3rem;
    max-width: 1600px;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020817 0%, #020617 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}

h1, h2, h3 {
    color: #F8FAFC !important;
    font-weight: 800 !important;
    letter-spacing: -0.5px;
}

p, label, span {
    color: #CBD5E1;
}

hr {
    border-color: rgba(255,255,255,0.08);
}

.stButton button {
    width: 100%;
    height: 52px;
    border-radius: 16px;
    border: none;

    background:
        linear-gradient(
            135deg,
            #2563EB,
            #7C3AED
        ) !important;

    color: #111827 !important;

    font-weight: 900 !important;
    font-size: 15px;

    box-shadow:
        0 12px 30px rgba(37,99,235,0.35),
        0 0 18px rgba(124,58,237,0.25);

    transition: all 0.3s ease;
}

.stButton button p,
.stButton button span {
    color: #111827 !important;
    font-weight: 900 !important;
}

.stButton button:hover {
    transform: translateY(-2px);
    color: white !important;
    box-shadow:
        0 16px 36px rgba(37,99,235,0.45),
        0 0 24px rgba(124,58,237,0.35);
}

button[kind="primary"],
button[kind="secondary"] {
    background: linear-gradient(135deg, #2563EB, #7C3AED) !important;
    color: #111827 !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 800 !important;
    min-height: 48px !important;
    box-shadow:
        0 12px 30px rgba(37,99,235,0.35),
        0 0 18px rgba(124,58,237,0.25) !important;
}

button[kind="primary"] p,
button[kind="secondary"] p,
button[kind="primary"] span,
button[kind="secondary"] span {
    color: #111827 !important;
    font-weight: 900 !important;
}

.stDownloadButton button {
    width: 100%;
    height: 50px;
    border-radius: 16px;
    border: none;
    background: linear-gradient(135deg, #10B981, #059669) !important;
    color: white !important;
    font-weight: 700;
}

div[data-testid="stMetric"] {
    position: relative;
    overflow: visible;
    background:
        radial-gradient(circle at top left, rgba(37,99,235,0.22), transparent 36%),
        linear-gradient(145deg, rgba(15,23,42,0.98), rgba(30,41,59,0.96));
    min-height: 150px;
    padding: 24px 22px;
    border-radius: 26px;
    border: 1px solid rgba(147,197,253,0.14);
    backdrop-filter: blur(14px);
    box-shadow:
        0 16px 42px rgba(0,0,0,0.38),
        0 0 28px rgba(37,99,235,0.10);
    transition: all 0.3s ease;
}

div[data-testid="stMetric"]::after {
    content: "";
    position: absolute;
    left: 0;
    top: 18%;
    width: 4px;
    height: 64%;
    border-radius: 999px;
    background: linear-gradient(180deg, #2563EB, #7C3AED);
    box-shadow: 0 0 18px rgba(37,99,235,0.55);
}

div[data-testid="stMetric"] label {
    color: #94A3B8 !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

div[data-testid="stMetricValue"] {
    color: white !important;
    font-size: 28px !important;
    font-weight: 900 !important;
    letter-spacing: -0.6px;
    line-height: 1.15 !important;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    max-width: 100% !important;
}

div[data-testid="stMetricValue"] * {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
}

div[data-testid="stMetric"] label,
div[data-testid="stMetric"] p,
div[data-testid="stMetric"] span {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
}

div[data-testid="stMetricDelta"] {
    color: #38BDF8 !important;
    font-weight: 700 !important;
    font-size: 13px !important;
}

div[data-testid="stFileUploader"] {
    background-color: rgba(17,24,39,0.95);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 22px;
    padding: 20px;
}

div[data-testid="stFileUploader"] label {
    color: white !important;
    font-weight: 700 !important;
    font-size: 15px !important;
}

div[data-testid="stFileUploader"] small {
    color: #D1D5DB !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}

div[data-testid="stFileUploaderDropzone"] {
    background-color: #1E293B !important;
    border: 2px dashed rgba(148,163,184,0.35) !important;
    border-radius: 18px !important;
    padding: 34px !important;
}

div[data-testid="stFileUploaderDropzone"] * {
    color: white !important;
}

div[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.08);
    background: rgba(15,23,42,0.92);
    box-shadow:
        0 10px 30px rgba(0,0,0,0.30),
        0 0 20px rgba(37,99,235,0.06);
}

div[data-testid="stTextInput"],
div[data-testid="stPasswordInput"] {
    background: linear-gradient(135deg, rgba(15,23,42,0.98), rgba(30,41,59,0.96));
    border: 1px solid rgba(147,197,253,0.22);
    border-radius: 18px;
    padding: 10px 14px;
    box-shadow:
        0 12px 35px rgba(0,0,0,0.30),
        0 0 24px rgba(37,99,235,0.08);
}

div[data-testid="stTextInput"] label,
div[data-testid="stPasswordInput"] label {
    color: white !important;
    font-weight: 700 !important;
}

div[data-testid="stTextInput"] input,
div[data-testid="stPasswordInput"] input {
    color: #0F172A !important;
    background: #F8FAFC !important;
    border: 1px solid rgba(147,197,253,0.35) !important;
    border-radius: 12px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    caret-color: #2563EB !important;
}

div[data-testid="stTextInput"] input::placeholder,
div[data-testid="stPasswordInput"] input::placeholder {
    color: #64748B !important;
    opacity: 1 !important;
}

.sidebar-card {
    background: linear-gradient(145deg, rgba(15,23,42,0.98), rgba(30,41,59,0.95));
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 28px;
    padding: 28px 24px;
    margin-bottom: 28px;
    box-shadow:
        0 18px 45px rgba(0,0,0,0.35),
        0 0 28px rgba(37,99,235,0.08);
}

.sidebar-logo {
    width: 74px;
    height: 74px;
    border-radius: 22px;
    background: linear-gradient(135deg, #2563EB, #7C3AED);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    font-weight: 800;
    color: white;
    margin-bottom: 24px;
    box-shadow: 0 14px 35px rgba(37,99,235,0.35);
}

.sidebar-title {
    color: white;
    font-size: 32px;
    font-weight: 800;
    line-height: 1.15;
    margin-bottom: 14px;
}

.sidebar-description {
    color: #CBD5E1;
    font-size: 14px;
    line-height: 1.7;
    margin-bottom: 22px;
}

.online-badge {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: rgba(16,185,129,0.12);
    border: 1px solid rgba(16,185,129,0.28);
    border-radius: 999px;
    padding: 10px 16px;
}

.online-dot {
    width: 10px;
    height: 10px;
    border-radius: 999px;
    background: #10B981;
    box-shadow: 0 0 10px #10B981;
}

.online-text {
    color: #A7F3D0;
    font-size: 13px;
    font-weight: 700;
}

.sidebar-menu-title {
    color: #94A3B8;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.5px;
    margin-top: 24px;
    margin-bottom: 12px;
}

.sidebar-menu-item {
    padding: 14px 16px;
    border-radius: 16px;
    margin-bottom: 10px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.04);
}

.sidebar-menu-text {
    color: white;
    font-size: 14px;
    font-weight: 600;
}

.hero-card,
.login-card,
.preview-card,
.chart-card,
.ai-card,
.agent-card,
.report-card,
.chat-card,
.insight-card {
    background: linear-gradient(145deg, rgba(15,23,42,0.96), rgba(30,41,59,0.92));
    border: 1px solid rgba(147,197,253,0.14);
    border-radius: 28px;
    padding: 28px;
    margin-top: 20px;
    margin-bottom: 24px;
    box-shadow:
        0 18px 50px rgba(0,0,0,0.35),
        0 0 28px rgba(37,99,235,0.08);
}

.hero-card {
    background: linear-gradient(135deg, rgba(37,99,235,0.18), rgba(124,58,237,0.12));
    padding: 45px;
}

.hero-badge,
.ai-badge {
    display: inline-block;
    background: rgba(37,99,235,0.18);
    color: #93C5FD;
    padding: 8px 18px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 800;
    margin-bottom: 20px;
    border: 1px solid rgba(147,197,253,0.25);
}

.hero-title {
    color: white;
    font-size: 58px;
    line-height: 1.1;
    margin-bottom: 18px;
    font-weight: 800;
}

.hero-subtitle,
.login-subtitle,
.preview-subtitle,
.chart-subtitle,
.ai-subtitle,
.agent-subtitle,
.report-subtitle,
.chat-subtitle {
    color: #94A3B8;
    font-size: 14px;
    line-height: 1.7;
    margin-bottom: 0;
}

.login-title,
.preview-title,
.chart-title,
.ai-title,
.agent-title,
.report-title,
.chat-title,
.insight-title {
    color: white;
    font-size: 24px;
    font-weight: 800;
    margin-bottom: 8px;
}

.ai-title,
.chat-title,
.login-title {
    font-size: 28px;
}

.ai-response-box {
    background: rgba(2,6,23,0.58);
    border: 1px solid rgba(147,197,253,0.12);
    border-radius: 22px;
    padding: 24px;
    margin-top: 18px;
    color: #E5E7EB;
    box-shadow: inset 0 0 18px rgba(37,99,235,0.04);
}

.insight-item {
    color: #CBD5E1;
    font-size: 15px;
    line-height: 1.7;
    margin-bottom: 12px;
}


.autonomous-response-box {
    background: linear-gradient(145deg, rgba(15,23,42,0.98), rgba(30,41,59,0.94));
    border: 1px solid rgba(147,197,253,0.18);
    border-radius: 22px;
    padding: 26px;
    margin-top: 18px;
    color: #E5E7EB !important;
    box-shadow:
        0 18px 45px rgba(0,0,0,0.28),
        inset 0 0 18px rgba(37,99,235,0.05);
}

.autonomous-response-title {
    color: #FFFFFF !important;
    font-size: 17px;
    font-weight: 900;
    margin-bottom: 18px;
}

.autonomous-response-item {
    color: #CBD5E1 !important;
    font-size: 15px;
    line-height: 1.8;
    margin-bottom: 14px;
}

.autonomous-response-item strong {
    color: #93C5FD !important;
}



.auto-section-title {
    background: linear-gradient(145deg, rgba(15,23,42,0.96), rgba(30,41,59,0.92));
    border: 1px solid rgba(147,197,253,0.14);
    border-radius: 28px;
    padding: 28px;
    margin-top: 20px;
    margin-bottom: 24px;
    box-shadow:
        0 18px 50px rgba(0,0,0,0.35),
        0 0 28px rgba(37,99,235,0.08);
}

.auto-section-badge {
    display: inline-block;
    background: rgba(37,99,235,0.18);
    color: #93C5FD !important;
    padding: 8px 18px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 900;
    margin-bottom: 18px;
    border: 1px solid rgba(147,197,253,0.25);
    letter-spacing: 0.8px;
}

.auto-section-title h2 {
    color: #FFFFFF !important;
    font-size: 30px;
    font-weight: 900;
    margin: 0 0 10px 0;
}

.auto-section-title p {
    color: #CBD5E1 !important;
    font-size: 15px;
    line-height: 1.7;
    margin: 0;
}

.auto-card {
    min-height: 180px;
    background:
        radial-gradient(circle at top left, rgba(37,99,235,0.16), transparent 36%),
        linear-gradient(145deg, rgba(15,23,42,0.98), rgba(30,41,59,0.94));
    border: 1px solid rgba(96,165,250,0.18);
    border-radius: 24px;
    padding: 24px;
    margin-bottom: 18px;
    box-shadow:
        0 12px 36px rgba(0,0,0,0.32),
        0 0 24px rgba(37,99,235,0.10);
    transition: all 0.25s ease;
}

.auto-card:hover {
    transform: translateY(-3px);
    border-color: rgba(124,58,237,0.45);
    box-shadow:
        0 18px 44px rgba(0,0,0,0.38),
        0 0 30px rgba(124,58,237,0.18);
}

.auto-icon {
    width: 54px;
    height: 54px;
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(37,99,235,0.22), rgba(124,58,237,0.22));
    border: 1px solid rgba(147,197,253,0.18);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    margin-bottom: 16px;
}

.auto-title {
    color: #FFFFFF !important;
    font-size: 16px;
    font-weight: 900;
    margin-bottom: 8px;
    letter-spacing: 0.4px;
}

.auto-desc {
    color: #CBD5E1 !important;
    font-size: 14px;
    line-height: 1.65;
    margin-bottom: 14px;
}

.auto-status {
    display: inline-block;
    background: linear-gradient(135deg, rgba(59,130,246,0.18), rgba(124,58,237,0.18));
    border: 1px solid rgba(96,165,250,0.25);
    color: #93C5FD !important;
    padding: 8px 14px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 900;
    letter-spacing: 0.6px;
}


.enterprise-section-title {
    background: linear-gradient(145deg, rgba(15,23,42,0.96), rgba(30,41,59,0.92));
    border: 1px solid rgba(147,197,253,0.14);
    border-radius: 28px;
    padding: 28px;
    margin-top: 24px;
    margin-bottom: 24px;
    box-shadow:
        0 18px 50px rgba(0,0,0,0.35),
        0 0 28px rgba(37,99,235,0.08);
}

.enterprise-section-badge {
    display: inline-block;
    background: rgba(37,99,235,0.18);
    color: #93C5FD !important;
    padding: 8px 18px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 900;
    margin-bottom: 18px;
    border: 1px solid rgba(147,197,253,0.25);
    letter-spacing: 0.8px;
}

.enterprise-section-title h2 {
    color: #FFFFFF !important;
    font-size: 30px;
    font-weight: 900;
    margin: 0 0 10px 0;
}

.enterprise-section-title p {
    color: #CBD5E1 !important;
    font-size: 15px;
    line-height: 1.7;
    margin: 0;
}

.enterprise-card {
    min-height: 155px;
    background:
        radial-gradient(circle at top left, rgba(37,99,235,0.18), transparent 34%),
        linear-gradient(145deg, rgba(15,23,42,0.98), rgba(30,41,59,0.94));
    border: 1px solid rgba(96,165,250,0.18);
    border-radius: 24px;
    padding: 24px;
    margin-bottom: 18px;
    box-shadow:
        0 12px 36px rgba(0,0,0,0.32),
        0 0 24px rgba(37,99,235,0.10);
    transition: all 0.25s ease;
}

.enterprise-card:hover {
    transform: translateY(-3px);
    border-color: rgba(124,58,237,0.45);
    box-shadow:
        0 18px 44px rgba(0,0,0,0.38),
        0 0 30px rgba(124,58,237,0.18);
}

.enterprise-value {
    color: #FFFFFF !important;
    font-size: 34px;
    font-weight: 900;
    margin-bottom: 10px;
    letter-spacing: -0.6px;
}

.enterprise-title {
    color: #93C5FD !important;
    font-size: 14px;
    font-weight: 900;
    letter-spacing: 1px;
    margin-bottom: 8px;
}

.enterprise-desc {
    color: #CBD5E1 !important;
    font-size: 14px;
    line-height: 1.6;
}

.stAlert {
    border-radius: 14px;
}

/* ===== ULTRA ENTERPRISE COMPACT MODE ===== */

.block-container {
    padding-top: 1.4rem !important;
    padding-bottom: 1rem !important;
    max-width: 1320px !important;
}

section[data-testid="stSidebar"] {
    width: 300px !important;
}

.sidebar-card {
    padding: 18px 18px !important;
    border-radius: 22px !important;
    margin-bottom: 16px !important;
}

.sidebar-logo {
    width: 52px !important;
    height: 52px !important;
    border-radius: 16px !important;
    font-size: 20px !important;
    margin-bottom: 14px !important;
}

.sidebar-title {
    font-size: 22px !important;
    margin-bottom: 8px !important;
}

.sidebar-description {
    font-size: 12px !important;
    line-height: 1.45 !important;
    margin-bottom: 14px !important;
}

.online-badge {
    padding: 7px 11px !important;
}

.sidebar-menu-title {
    margin-top: 14px !important;
    margin-bottom: 8px !important;
}

.sidebar-menu-item {
    padding: 10px 12px !important;
    border-radius: 12px !important;
    margin-bottom: 6px !important;
}

.sidebar-menu-text {
    font-size: 13px !important;
}

.hero-card {
    padding: 24px 28px !important;
    border-radius: 22px !important;
    margin-top: 6px !important;
    margin-bottom: 14px !important;
}

.hero-title {
    font-size: 34px !important;
    line-height: 1.04 !important;
    margin-bottom: 10px !important;
}

.hero-subtitle {
    font-size: 12.5px !important;
    line-height: 1.45 !important;
}

.hero-badge,
.ai-badge {
    padding: 6px 13px !important;
    font-size: 10px !important;
    margin-bottom: 12px !important;
}

.ai-card,
.preview-card,
.chart-card,
.insight-card,
.agent-card,
.report-card,
.chat-card,
.login-card {
    padding: 18px !important;
    border-radius: 20px !important;
    margin-top: 10px !important;
    margin-bottom: 14px !important;
}

.ai-title,
.chat-title,
.login-title {
    font-size: 21px !important;
}

.chart-title,
.preview-title,
.agent-title,
.report-title,
.insight-title {
    font-size: 19px !important;
}

div[data-testid="stMetric"] {
    min-height: 96px !important;
    padding: 15px 16px !important;
    border-radius: 18px !important;
}

div[data-testid="stMetricValue"] {
    font-size: 20px !important;
    line-height: 1.02 !important;
}

div[data-testid="stMetric"] label {
    font-size: 10px !important;
}

div[data-testid="stMetricDelta"] {
    font-size: 10px !important;
}

.enterprise-section-title,
.auto-section-title {
    padding: 18px !important;
    border-radius: 20px !important;
    margin-top: 12px !important;
    margin-bottom: 14px !important;
}

.enterprise-section-title h2,
.auto-section-title h2 {
    font-size: 22px !important;
}

.enterprise-section-title p,
.auto-section-title p {
    font-size: 12px !important;
}

.enterprise-card {
    min-height: 108px !important;
    padding: 16px !important;
    border-radius: 18px !important;
    margin-bottom: 10px !important;
}

.enterprise-value {
    font-size: 22px !important;
    margin-bottom: 4px !important;
}

.enterprise-title {
    font-size: 10px !important;
    margin-bottom: 4px !important;
}

.enterprise-desc {
    font-size: 11px !important;
    line-height: 1.35 !important;
}

.auto-card {
    min-height: 118px !important;
    padding: 16px !important;
    border-radius: 18px !important;
    margin-bottom: 10px !important;
}

.auto-icon {
    width: 38px !important;
    height: 38px !important;
    border-radius: 12px !important;
    font-size: 20px !important;
    margin-bottom: 10px !important;
}

.auto-title {
    font-size: 12px !important;
}

.auto-desc {
    font-size: 11px !important;
    line-height: 1.35 !important;
    margin-bottom: 8px !important;
}

.auto-status {
    padding: 5px 9px !important;
    font-size: 9px !important;
}

div[data-testid="stDataFrame"] {
    border-radius: 14px !important;
}

hr {
    margin-top: 0.7rem !important;
    margin-bottom: 0.7rem !important;
}


/* ===== FINAL ENTERPRISE DENSITY MODE ===== */

.block-container {
    padding-top: 1.15rem !important;
    padding-bottom: 0.85rem !important;
    max-width: 1320px !important;
}

.hero-card {
    padding: 20px 26px !important;
    border-radius: 20px !important;
    margin-top: 4px !important;
    margin-bottom: 10px !important;
}

.hero-title {
    font-size: 31px !important;
    line-height: 1.02 !important;
    margin-bottom: 8px !important;
}

.hero-subtitle {
    font-size: 12px !important;
    line-height: 1.38 !important;
}

.ai-card[style],
.ai-card {
    padding: 16px !important;
    border-radius: 18px !important;
    margin-top: 8px !important;
    margin-bottom: 10px !important;
}

.preview-card,
.chart-card,
.insight-card,
.agent-card,
.report-card,
.chat-card,
.login-card {
    padding: 16px !important;
    border-radius: 18px !important;
    margin-top: 8px !important;
    margin-bottom: 10px !important;
}

div[data-testid="stMetric"] {
    min-height: 82px !important;
    padding: 12px 14px !important;
    border-radius: 16px !important;
}

div[data-testid="stMetric"]::after {
    top: 22% !important;
    height: 56% !important;
}

div[data-testid="stMetricValue"] {
    font-size: 18px !important;
    line-height: 1 !important;
    letter-spacing: -0.35px !important;
}

div[data-testid="stMetric"] label {
    font-size: 9.5px !important;
    letter-spacing: 0.45px !important;
}

div[data-testid="stMetricDelta"] {
    font-size: 9.5px !important;
}

div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stMetric"]) {
    gap: 0.55rem !important;
}

.enterprise-section-title,
.auto-section-title {
    padding: 15px 16px !important;
    border-radius: 18px !important;
    margin-top: 8px !important;
    margin-bottom: 10px !important;
}

.enterprise-section-title h2,
.auto-section-title h2 {
    font-size: 20px !important;
    margin-bottom: 6px !important;
}

.enterprise-section-title p,
.auto-section-title p {
    font-size: 11.5px !important;
    line-height: 1.32 !important;
}

.enterprise-card {
    min-height: 92px !important;
    padding: 13px 14px !important;
    border-radius: 16px !important;
    margin-bottom: 8px !important;
}

.enterprise-value {
    font-size: 20px !important;
    margin-bottom: 3px !important;
}

.enterprise-title {
    font-size: 9.5px !important;
    margin-bottom: 3px !important;
}

.enterprise-desc {
    font-size: 10.5px !important;
    line-height: 1.28 !important;
}

.auto-card {
    min-height: 102px !important;
    padding: 13px 14px !important;
    border-radius: 16px !important;
    margin-bottom: 8px !important;
}

.auto-icon {
    width: 34px !important;
    height: 34px !important;
    border-radius: 11px !important;
    font-size: 18px !important;
    margin-bottom: 8px !important;
}

.auto-title {
    font-size: 11.5px !important;
    margin-bottom: 4px !important;
}

.auto-desc {
    font-size: 10.5px !important;
    line-height: 1.28 !important;
    margin-bottom: 6px !important;
}

.auto-status {
    padding: 4px 8px !important;
    font-size: 8.5px !important;
}

.chart-title,
.preview-title,
.agent-title,
.report-title,
.insight-title {
    font-size: 18px !important;
    margin-bottom: 5px !important;
}

.chart-subtitle,
.preview-subtitle,
.agent-subtitle,
.report-subtitle,
.chat-subtitle,
.ai-subtitle {
    font-size: 11.5px !important;
    line-height: 1.35 !important;
}

.sidebar-card {
    padding: 16px !important;
    border-radius: 20px !important;
    margin-bottom: 12px !important;
}

.sidebar-logo {
    width: 48px !important;
    height: 48px !important;
    font-size: 19px !important;
    margin-bottom: 12px !important;
}

.sidebar-title {
    font-size: 21px !important;
}

.sidebar-description {
    font-size: 11.5px !important;
    line-height: 1.38 !important;
}

.sidebar-menu-item {
    padding: 9px 11px !important;
    margin-bottom: 5px !important;
}

hr {
    margin-top: 0.45rem !important;
    margin-bottom: 0.45rem !important;
}


/* ===== FINAL SAAS POLISH MODE ===== */

.block-container {
    max-width: 1240px !important;
}

.stButton button {
    height: 46px !important;
    min-height: 46px !important;
    border-radius: 14px !important;
    font-size: 14px !important;
}

button[kind="primary"],
button[kind="secondary"] {
    min-height: 44px !important;
    border-radius: 13px !important;
    font-size: 14px !important;
}

.stDownloadButton button {
    height: 46px !important;
    min-height: 46px !important;
    border-radius: 14px !important;
    font-size: 14px !important;
}

div[data-testid="stFileUploader"] {
    padding: 16px !important;
    border-radius: 18px !important;
}

div[data-testid="stFileUploaderDropzone"] {
    padding: 22px !important;
    border-radius: 14px !important;
}

div[data-testid="stDataFrame"] {
    border-radius: 16px !important;
    border: 1px solid rgba(147,197,253,0.12) !important;
    box-shadow:
        0 12px 34px rgba(0,0,0,0.34),
        0 0 20px rgba(37,99,235,0.08) !important;
}

div[data-testid="stAlert"] {
    border-radius: 14px !important;
}


/* ===== ENTERPRISE AI CHAT PREMIUM ===== */

.enterprise-chat-shell {
    background:
        radial-gradient(circle at top left, rgba(37,99,235,0.16), transparent 34%),
        linear-gradient(145deg, rgba(15,23,42,0.98), rgba(30,41,59,0.94));
    border: 1px solid rgba(147,197,253,0.16);
    border-radius: 22px;
    padding: 20px;
    margin-top: 12px;
    margin-bottom: 14px;
    box-shadow:
        0 18px 46px rgba(0,0,0,0.34),
        0 0 28px rgba(37,99,235,0.10);
}

.enterprise-chat-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
    flex-wrap: wrap;
    margin-bottom: 14px;
}

.enterprise-chat-title {
    color: #FFFFFF !important;
    font-size: 20px;
    font-weight: 900;
    letter-spacing: -0.3px;
}

.enterprise-chat-subtitle {
    color: #94A3B8 !important;
    font-size: 12px;
    line-height: 1.45;
    margin-top: 4px;
}

.enterprise-chat-badge {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: linear-gradient(135deg, rgba(37,99,235,0.22), rgba(124,58,237,0.18));
    border: 1px solid rgba(147,197,253,0.22);
    color: #93C5FD !important;
    padding: 7px 12px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 900;
    letter-spacing: 0.8px;
}

.enterprise-chat-empty {
    background: rgba(2,6,23,0.42);
    border: 1px dashed rgba(147,197,253,0.18);
    border-radius: 18px;
    padding: 18px;
    color: #CBD5E1 !important;
    font-size: 13px;
    line-height: 1.55;
}

.enterprise-message-row {
    display: flex;
    width: 100%;
    margin: 12px 0;
}

.enterprise-message-row.user {
    justify-content: flex-end;
}

.enterprise-message-row.assistant {
    justify-content: flex-start;
}

.enterprise-message {
    max-width: 82%;
    border-radius: 20px;
    padding: 14px 16px;
    font-size: 13px;
    line-height: 1.58;
    white-space: pre-wrap;
    word-break: break-word;
}

.enterprise-message.user {
    background: linear-gradient(135deg, rgba(37,99,235,0.95), rgba(124,58,237,0.95));
    color: #FFFFFF !important;
    border: 1px solid rgba(191,219,254,0.20);
    box-shadow:
        0 12px 30px rgba(37,99,235,0.30),
        0 0 18px rgba(124,58,237,0.18);
}

.enterprise-message.assistant {
    background:
        radial-gradient(circle at top left, rgba(96,165,250,0.12), transparent 34%),
        rgba(2,6,23,0.64);
    color: #E5E7EB !important;
    border: 1px solid rgba(147,197,253,0.14);
    box-shadow: inset 0 0 18px rgba(37,99,235,0.05);
}

.enterprise-message-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #93C5FD !important;
    font-size: 10px;
    font-weight: 900;
    letter-spacing: 0.7px;
    margin-bottom: 8px;
    text-transform: uppercase;
}

.enterprise-avatar {
    width: 26px;
    height: 26px;
    border-radius: 9px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #2563EB, #7C3AED);
    color: #FFFFFF !important;
    font-size: 13px;
    font-weight: 900;
    box-shadow: 0 8px 20px rgba(37,99,235,0.28);
}

.enterprise-chat-input-card {
    background: linear-gradient(145deg, rgba(15,23,42,0.96), rgba(30,41,59,0.92));
    border: 1px solid rgba(147,197,253,0.16);
    border-radius: 20px;
    padding: 16px;
    margin-top: 12px;
    box-shadow:
        0 12px 34px rgba(0,0,0,0.30),
        0 0 22px rgba(37,99,235,0.08);
}

.enterprise-quick-prompts {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 10px;
}

.enterprise-prompt-pill {
    background: rgba(37,99,235,0.12);
    border: 1px solid rgba(147,197,253,0.18);
    color: #BFDBFE !important;
    padding: 7px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
}

.enterprise-history-card {
    background: rgba(37,99,235,0.08);
    border: 1px solid rgba(147,197,253,0.12);
    border-radius: 16px;
    padding: 12px 14px;
    color: #CBD5E1 !important;
    font-size: 13px;
}


/* ===== CLEAN LUXURY CHAT + AGENT REFINEMENT ===== */

.stButton button {
    height: 40px !important;
    min-height: 40px !important;
    border-radius: 13px !important;
    font-size: 13px !important;
    padding: 0 16px !important;
    box-shadow:
        0 10px 24px rgba(37,99,235,0.28),
        0 0 14px rgba(124,58,237,0.20) !important;
}

button[kind="primary"],
button[kind="secondary"] {
    min-height: 40px !important;
    height: 40px !important;
    border-radius: 13px !important;
    font-size: 13px !important;
}

.agent-card {
    min-height: 108px !important;
    padding: 16px 18px !important;
    margin-bottom: 8px !important;
    border-radius: 18px !important;
}

.agent-title {
    font-size: 18px !important;
    margin-bottom: 4px !important;
}

.agent-subtitle {
    font-size: 11.5px !important;
    line-height: 1.35 !important;
}

.enterprise-chat-shell {
    padding: 18px !important;
    border-radius: 20px !important;
    margin-top: 10px !important;
    margin-bottom: 10px !important;
    background:
        radial-gradient(circle at top left, rgba(37,99,235,0.18), transparent 32%),
        radial-gradient(circle at bottom right, rgba(124,58,237,0.12), transparent 36%),
        linear-gradient(145deg, rgba(15,23,42,0.98), rgba(30,41,59,0.94)) !important;
}

.enterprise-chat-header {
    align-items: flex-start !important;
    margin-bottom: 12px !important;
}

.enterprise-chat-title {
    font-size: 19px !important;
}

.enterprise-chat-subtitle {
    max-width: 720px !important;
    font-size: 11.5px !important;
    line-height: 1.38 !important;
}

.enterprise-chat-badge {
    padding: 8px 13px !important;
    font-size: 10.5px !important;
    border-radius: 999px !important;
    box-shadow: 0 0 18px rgba(37,99,235,0.12) !important;
}

.copilot-status-grid {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    justify-content: flex-end;
    min-width: 260px;
}

.copilot-mini-card {
    background:
        linear-gradient(145deg, rgba(37,99,235,0.14), rgba(124,58,237,0.12));
    border: 1px solid rgba(147,197,253,0.18);
    border-radius: 14px;
    padding: 9px 11px;
    min-width: 118px;
    box-shadow:
        0 10px 24px rgba(0,0,0,0.22),
        inset 0 0 14px rgba(37,99,235,0.04);
}

.copilot-mini-label {
    color: #93C5FD !important;
    font-size: 9px;
    font-weight: 900;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 3px;
}

.copilot-mini-value {
    color: #FFFFFF !important;
    font-size: 13px;
    font-weight: 900;
    line-height: 1.1;
}

.enterprise-chat-empty {
    padding: 16px 18px !important;
    border-radius: 16px !important;
    font-size: 12.5px !important;
    line-height: 1.45 !important;
    background:
        radial-gradient(circle at top left, rgba(37,99,235,0.10), transparent 35%),
        rgba(2,6,23,0.44) !important;
}

.enterprise-chat-input-card {
    padding: 14px 16px !important;
    border-radius: 18px !important;
    margin-top: 10px !important;
}

.enterprise-quick-prompts {
    margin-top: 9px !important;
    gap: 7px !important;
}

.enterprise-prompt-pill {
    padding: 6px 10px !important;
    font-size: 10.5px !important;
    background: rgba(37,99,235,0.14) !important;
}

div[data-testid="stTextInput"] {
    border: 1px solid rgba(96,165,250,0.30) !important;
    border-radius: 18px !important;
    box-shadow:
        0 12px 34px rgba(0,0,0,0.28),
        0 0 26px rgba(37,99,235,0.10) !important;
}

div[data-testid="stTextInput"] input {
    min-height: 44px !important;
    border-radius: 14px !important;
    font-size: 14px !important;
    font-weight: 700 !important;
}

div[data-testid="stTextInput"] input:focus {
    border-color: rgba(96,165,250,0.70) !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.16) !important;
}

.enterprise-history-card {
    padding: 14px 16px !important;
    border-radius: 16px !important;
    background:
        linear-gradient(145deg, rgba(37,99,235,0.10), rgba(124,58,237,0.08)) !important;
}

/* ===== ENTERPRISE ALERT CARDS - COMPACT EXECUTIVE GRID ===== */

.enterprise-alert-card {
    background:
        radial-gradient(circle at top left, rgba(37,99,235,0.12), transparent 32%),
        linear-gradient(145deg, rgba(15,23,42,0.98), rgba(30,41,59,0.94));
    border: 1px solid rgba(147,197,253,0.16);
    border-radius: 18px;
    padding: 16px;
    margin-bottom: 10px;
    min-height: 108px;
    box-shadow:
        0 12px 32px rgba(0,0,0,0.30),
        0 0 20px rgba(37,99,235,0.08);
    transition: all 0.22s ease;
}

.enterprise-alert-card:hover {
    transform: translateY(-2px);
    border-color: rgba(124,58,237,0.38);
    box-shadow:
        0 16px 36px rgba(0,0,0,0.34),
        0 0 24px rgba(124,58,237,0.14);
}

.enterprise-alert-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 8px;
}

.enterprise-alert-status {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 9px;
    font-weight: 900;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    white-space: nowrap;
}

.enterprise-alert-status.success {
    background: rgba(16,185,129,0.14);
    border: 1px solid rgba(16,185,129,0.28);
    color: #6EE7B7 !important;
}

.enterprise-alert-status.enterprise {
    background: rgba(37,99,235,0.14);
    border: 1px solid rgba(37,99,235,0.30);
    color: #93C5FD !important;
}

.enterprise-alert-status.priority {
    background: rgba(124,58,237,0.16);
    border: 1px solid rgba(124,58,237,0.30);
    color: #C4B5FD !important;
}

.enterprise-alert-status.risk {
    background: rgba(239,68,68,0.14);
    border: 1px solid rgba(239,68,68,0.28);
    color: #FCA5A5 !important;
}

.enterprise-alert-title {
    color: #FFFFFF !important;
    font-size: 16px;
    font-weight: 800;
    line-height: 1.25;
    text-align: right;
    margin: 0;
}

.enterprise-alert-description {
    color: #CBD5E1 !important;
    font-size: 12.5px;
    line-height: 1.45;
    margin-top: 6px;
}

/* ===== ENTERPRISE DARK TABLES + FINAL UX FIX ===== */

div[data-testid="stDataFrame"] {
    background:
        radial-gradient(circle at top left, rgba(37,99,235,0.10), transparent 35%),
        linear-gradient(145deg, rgba(15,23,42,0.98), rgba(30,41,59,0.94)) !important;
    border: 1px solid rgba(147,197,253,0.18) !important;
    border-radius: 18px !important;
    overflow: hidden !important;
    box-shadow:
        0 16px 42px rgba(0,0,0,0.38),
        0 0 22px rgba(37,99,235,0.10) !important;
}

div[data-testid="stDataFrame"] div,
div[data-testid="stDataFrame"] span,
div[data-testid="stDataFrame"] p {
    color: #E5E7EB !important;
}

div[data-testid="stDataFrame"] [role="grid"],
div[data-testid="stDataFrame"] [role="row"],
div[data-testid="stDataFrame"] [role="columnheader"],
div[data-testid="stDataFrame"] [role="gridcell"] {
    background-color: #0F172A !important;
    color: #E5E7EB !important;
    border-color: rgba(148,163,184,0.10) !important;
}

div[data-testid="stDataFrame"] [role="columnheader"] {
    background-color: #111827 !important;
    color: #93C5FD !important;
    font-weight: 900 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.45px !important;
}

div[data-testid="stDataFrame"] canvas {
    filter: brightness(0.72) contrast(1.18) saturate(1.12);
}

table {
    background: #0F172A !important;
    color: #E5E7EB !important;
    border-radius: 16px !important;
    overflow: hidden !important;
}

thead tr,
thead th {
    background: #111827 !important;
    color: #93C5FD !important;
    font-weight: 900 !important;
}

tbody tr,
tbody td,
tbody th {
    background: #0F172A !important;
    color: #E5E7EB !important;
    border-color: rgba(148,163,184,0.10) !important;
}

.live-signals-header {
    padding: 16px 18px !important;
    border-radius: 18px !important;
    margin-top: 8px !important;
    margin-bottom: 10px !important;
    background:
        radial-gradient(circle at top left, rgba(37,99,235,0.14), transparent 32%),
        linear-gradient(145deg, rgba(15,23,42,0.98), rgba(30,41,59,0.94)) !important;
    border: 1px solid rgba(147,197,253,0.16) !important;
}

.live-signals-badge {
    display: inline-block !important;
    padding: 6px 12px !important;
    border-radius: 999px !important;
    font-size: 9.5px !important;
    font-weight: 900 !important;
    letter-spacing: 0.75px !important;
    color: #93C5FD !important;
    background: rgba(37,99,235,0.18) !important;
    border: 1px solid rgba(147,197,253,0.24) !important;
    margin-bottom: 9px !important;
}

.live-signals-title {
    color: #FFFFFF !important;
    font-size: 20px !important;
    font-weight: 900 !important;
    margin-bottom: 5px !important;
}

.live-signals-subtitle {
    color: #CBD5E1 !important;
    font-size: 11.5px !important;
    line-height: 1.35 !important;
}

.live-signal-card {
    position: relative !important;
    overflow: hidden !important;
    padding: 14px 16px !important;
    border-radius: 17px !important;
    margin-bottom: 9px !important;
    min-height: 106px !important;
    background:
        radial-gradient(circle at top left, rgba(37,99,235,0.12), transparent 34%),
        linear-gradient(145deg, rgba(15,23,42,0.98), rgba(30,41,59,0.94)) !important;
    border: 1px solid rgba(147,197,253,0.16) !important;
    box-shadow:
        0 12px 32px rgba(0,0,0,0.32),
        0 0 18px rgba(37,99,235,0.08) !important;
}

.live-signal-card::before {
    content: "";
    position: absolute;
    left: 0;
    top: 14%;
    width: 3px;
    height: 72%;
    border-radius: 999px;
    background: linear-gradient(180deg, #2563EB, #7C3AED);
    box-shadow: 0 0 18px rgba(37,99,235,0.48);
}

.live-signal-top,
.live-signal-footer {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: 12px !important;
}

.live-signal-top {
    margin-bottom: 9px !important;
}

.live-signal-status,
.live-signal-tag {
    color: #BFDBFE !important;
    font-size: 10px !important;
    font-weight: 900 !important;
    letter-spacing: 0.75px !important;
    text-transform: uppercase !important;
}

.live-signal-tag {
    padding: 5px 10px !important;
    border-radius: 999px !important;
    background: rgba(37,99,235,0.16) !important;
    border: 1px solid rgba(147,197,253,0.20) !important;
}

.live-signal-title {
    color: #FFFFFF !important;
    font-size: 17px !important;
    font-weight: 900 !important;
    line-height: 1.22 !important;
    margin-bottom: 7px !important;
}

.live-signal-description {
    color: #CBD5E1 !important;
    font-size: 12px !important;
    line-height: 1.42 !important;
    margin-bottom: 9px !important;
}

.live-signal-confidence {
    color: #A7F3D0 !important;
    font-size: 10.5px !important;
    font-weight: 900 !important;
}

.live-signal-time {
    color: #94A3B8 !important;
    font-size: 10.5px !important;
    font-weight: 800 !important;
}

.signal-glow-blue {
    box-shadow: 0 12px 32px rgba(0,0,0,0.32), 0 0 22px rgba(37,99,235,0.14) !important;
}

.signal-glow-orange {
    box-shadow: 0 12px 32px rgba(0,0,0,0.32), 0 0 22px rgba(245,158,11,0.13) !important;
}

.signal-glow-green {
    box-shadow: 0 12px 32px rgba(0,0,0,0.32), 0 0 22px rgba(16,185,129,0.13) !important;
}

.js-plotly-plot,
.plot-container {
    border-radius: 18px !important;
}

.ai-response-box {
    padding: 18px !important;
    border-radius: 18px !important;
    margin-top: 10px !important;
}

.insight-card {
    padding: 18px !important;
    border-radius: 18px !important;
}

.monitoring-pill,
.enterprise-tag,
.revenue-risk,
.growth-opportunity,
.operational-priority {
    display: inline-flex;
    align-items: center;
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 9.5px;
    font-weight: 900;
    letter-spacing: 0.65px;
    text-transform: uppercase;
    color: #BFDBFE !important;
    background: rgba(37,99,235,0.14);
    border: 1px solid rgba(147,197,253,0.20);
}

section[data-testid="stSidebar"] {
    min-width: 300px !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background: rgba(248,250,252,0.96) !important;
    border-radius: 12px !important;
}

section[data-testid="stSidebar"] div[data-baseweb="tag"] {
    background: #EF4444 !important;
    color: white !important;
    border-radius: 8px !important;
}

[data-testid="stDataFrame"] iframe,
[data-testid="stDataFrame"] div[style*="background-color: white"],
[data-testid="stDataFrame"] div[style*="background-color: rgb(255"] {
    background-color: #0F172A !important;
}


/* ===== EXECUTIVE STATUS BAR FINAL ===== */

.executive-status-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 10px;
    margin-bottom: 14px;
    padding: 14px 18px;
    border-radius: 20px;

    background:
        radial-gradient(circle at top left, rgba(37,99,235,0.10), transparent 35%),
        linear-gradient(145deg, rgba(15,23,42,0.98), rgba(30,41,59,0.94));

    border: 1px solid rgba(147,197,253,0.16);

    box-shadow:
        0 12px 34px rgba(0,0,0,0.32),
        0 0 18px rgba(37,99,235,0.08);
}

.executive-status-item {
    display: inline-flex;
    align-items: center;
    gap: 8px;

    padding: 8px 14px;

    border-radius: 999px;

    background: rgba(37,99,235,0.12);

    border: 1px solid rgba(147,197,253,0.18);

    transition: all 0.22s ease;
}

.executive-status-item:hover {
    transform: translateY(-1px);
    border-color: rgba(124,58,237,0.34);

    box-shadow:
        0 0 18px rgba(124,58,237,0.12);
}

.executive-status-dot {
    width: 9px;
    height: 9px;
    border-radius: 999px;

    background: #10B981;

    box-shadow:
        0 0 10px #10B981;
}

.executive-status-text {
    color: #E2E8F0 !important;

    font-size: 10px;
    font-weight: 900;

    letter-spacing: 0.75px;

    text-transform: uppercase;
}

/* ===== EXECUTIVE STATUS BAR FINAL ===== */

.executive-status-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 10px;
    margin-bottom: 14px;
    padding: 14px 18px;
    border-radius: 20px;

    background:
        radial-gradient(circle at top left, rgba(37,99,235,0.10), transparent 35%),
        linear-gradient(145deg, rgba(15,23,42,0.98), rgba(30,41,59,0.94));

    border: 1px solid rgba(147,197,253,0.16);

    box-shadow:
        0 12px 34px rgba(0,0,0,0.32),
        0 0 18px rgba(37,99,235,0.08);
}

.executive-status-item {
    display: inline-flex;
    align-items: center;
    gap: 8px;

    padding: 8px 14px;

    border-radius: 999px;

    background: rgba(37,99,235,0.12);

    border: 1px solid rgba(147,197,253,0.18);

    transition: all 0.22s ease;
}

.executive-status-item:hover {
    transform: translateY(-1px);
    border-color: rgba(124,58,237,0.34);

    box-shadow:
        0 0 18px rgba(124,58,237,0.12);
}

.executive-status-dot {
    width: 9px;
    height: 9px;
    border-radius: 999px;

    background: #10B981;

    box-shadow:
        0 0 10px #10B981;
}

.executive-status-text {
    color: #E2E8F0 !important;

    font-size: 10px;
    font-weight: 900;

    letter-spacing: 0.75px;

    text-transform: uppercase;
}

/* ===== HERO EXECUTIVE REFINEMENT ===== */

.hero-card {
    position: relative;
    overflow: hidden;
}

.hero-card::before {
    content: "";

    position: absolute;

    top: -120px;
    right: -120px;

    width: 260px;
    height: 260px;

    border-radius: 999px;

    background:
        radial-gradient(circle,
        rgba(124,58,237,0.20),
        transparent 70%);
}

.hero-title {
    max-width: 920px;
}

.hero-subtitle {
    max-width: 900px;
}

/* ===== FINAL DARK TABLE FIX ===== */

[data-testid="stDataFrame"] * {
    color: #E5E7EB !important;
}

[data-testid="stTable"] * {
    color: #E5E7EB !important;
}

[data-testid="stDataFrame"] {
    background: #0F172A !important;
}

[data-testid="stDataFrame"] iframe {
    background: #0F172A !important;
}

.glideDataEditor {
    background: #0F172A !important;
}

.glideDataEditor div {
    background: #0F172A !important;
    color: #E5E7EB !important;
}

[data-testid="stDataFrame"] canvas {
    filter:
        brightness(0.72)
        contrast(1.15)
        saturate(1.05);
}

/* ===== COMPACT KPI EXECUTIVE MODE ===== */

div[data-testid="stMetric"] {
    min-height: 78px !important;
    padding: 11px 14px !important;
}

div[data-testid="stMetricValue"] {
    font-size: 17px !important;
}

div[data-testid="stMetric"] label {
    font-size: 9px !important;
}

</style>
"""
