import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import cm

from agent import AdaptiveIntegralAgent
from analyzer import IntegralAnalyzer
from explainer import AIExplainer
from senders import send_telegram, send_gmail, upload_to_drive

# ================= PAGE SETUP =================
st.set_page_config(layout="wide")
st.title("Adaptive Integral Agent — Dark Academic")

# Initialize session state
if "analyzer_ready" not in st.session_state:
    st.session_state.analyzer_ready = False

# ================= SIDEBAR =================
n_dim = st.sidebar.selectbox("Dimension", [1, 2])
symbols = sp.symbols(['x', 'y'][:n_dim])
func_str = st.sidebar.text_input("Function", value="x**2" if n_dim == 1 else "x**2 + y**2")
bounds = []
for i in range(n_dim):
    a = st.sidebar.number_input(f"Lower bound {symbols[i]}", value=0.0)
    b = st.sidebar.number_input(f"Upper bound {symbols[i]}", value=1.0)
    bounds.append((a, b))
n_samples = st.sidebar.slider("Monte Carlo samples", 500, 10000, 3000)
run = st.sidebar.button("Run Analysis")

# ================= HELPERS =================
def build_func(expr, symbols):
    f = sp.lambdify(symbols, expr, "numpy")
    return lambda arr: float(f(*arr)) if np.all(np.isfinite(arr)) else np.nan

def create_pdf(summary, simple_text, scientific_text, ieee_text, title="Adaptive Integral Analysis Report"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2.5*cm, leftMargin=2.5*cm, topMargin=2.5*cm, bottomMargin=2.5*cm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleStyle", fontSize=18, leading=22, alignment=TA_CENTER, spaceAfter=20))
    styles.add(ParagraphStyle(name="Section", fontSize=14, leading=18, spaceBefore=20, spaceAfter=10))
    styles.add(ParagraphStyle(name="Simple", fontSize=12, leading=16, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name="Scientific", fontSize=11, leading=15, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name="IEEE", fontName="Times-Roman", fontSize=10, leading=14, alignment=TA_JUSTIFY))

    story = []
    story.append(Paragraph(title, styles["TitleStyle"]))
    story.append(Spacer(1,12))
    story.append(Paragraph("Summary", styles["Section"]))
    for k,v in summary.items():
        story.append(Paragraph(f"<b>{k}:</b> {v}", styles["Scientific"]))
    story.append(PageBreak())
    story.append(Paragraph("Simple Explanation", styles["Section"]))
    story.append(Paragraph(simple_text, styles["Simple"]))
    story.append(PageBreak())
    story.append(Paragraph("Scientific Explanation", styles["Section"]))
    story.append(Paragraph(scientific_text, styles["Scientific"]))
    story.append(PageBreak())
    story.append(Paragraph("IEEE Style Explanation", styles["Section"]))
    story.append(Paragraph(ieee_text, styles["IEEE"]))
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def build_and_show_function_plot(n_dim, bounds, expr, symbols):
    if n_dim == 1:
        x = np.linspace(bounds[0][0], bounds[0][1], 800)
        y = np.array([build_func(expr, symbols)([xi]) for xi in x])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, fill="tozeroy"))
    else:
        x = np.linspace(bounds[0][0], bounds[0][1], 150)
        y = np.linspace(bounds[1][0], bounds[1][1], 150)
        X, Y = np.meshgrid(x, y)
        f = sp.lambdify((symbols[0], symbols[1]), expr, "numpy")
        Z = f(X, Y)
        Z = np.where(np.isfinite(Z), Z, np.nan)
        fig = go.Figure(data=go.Surface(x=X, y=Y, z=Z))
    return fig

# ================= MAIN LOGIC =================
if run:
    SAFE = {"sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "sqrt": sp.sqrt, "log": sp.log, "exp": sp.exp, "pi": sp.pi, "e": sp.E}
    try:
        expr = sp.sympify(func_str, locals=SAFE)
        func = build_func(expr, symbols)
        st.latex(sp.latex(expr))

        agent = AdaptiveIntegralAgent(bounds, n_samples)
        result, method, cumulative = agent.integrate(func, expr)
        if np.isnan(result):
            st.error("No valid samples! Check function or bounds.")
            st.session_state.analyzer_ready = False
        else:
            analyzer = IntegralAnalyzer.from_agent(agent, func, result)
            stats = analyzer.summarize(method, n_dim, agent.stats["valid_ratio"], result)

            # Save everything to session state
            st.session_state.update({
                "result": result,
                "method": method,
                "stats": stats,
                "analyzer": analyzer,
                "expr": expr,
                "symbols": symbols,
                "n_dim": n_dim,
                "bounds": bounds,
                "analyzer_ready": True
            })

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Estimated Integral", f"{result:.6f}")
                st.info(f"Method: {method}")
            with col2:
                confidence = round(100 / (1 + stats["mean_error"] * 1e6), 2)
                st.metric("Confidence Score", f"{confidence}%")

            st.plotly_chart(analyzer.plot_convergence(), use_container_width=True)
            st.plotly_chart(analyzer.plot_absolute_error(), use_container_width=True)
            st.plotly_chart(analyzer.plot_error_histogram(), use_container_width=True)

            fig = build_and_show_function_plot(n_dim, bounds, expr, symbols)
            st.plotly_chart(fig, use_container_width=True)

            explainer = AIExplainer()
            ai_simple = explainer.explain(stats, "simple")
            ai_scientific = explainer.explain(stats, "medium")
            ai_ieee = explainer.explain_ieee(stats)

            st.subheader("AI Explanation")
            c1, c2 = st.columns(2)
            c1.write(ai_simple)
            c2.write(ai_scientific)
            st.subheader("IEEE-style Report")
            st.text_area("IEEE", ai_ieee, height=280)

            pdf_bytes = create_pdf(stats, ai_simple, ai_scientific, ai_ieee)
            st.session_state["pdf_bytes"] = pdf_bytes
            st.download_button("📄 Download PDF", data=pdf_bytes, file_name="integral_report.pdf", mime="application/pdf")

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.exception(e)
        st.session_state.analyzer_ready = False

# ================= SEND SECTION (always shown if ready) =================
if st.session_state.get("analyzer_ready", False):
    st.subheader("📤 Send PDF")
    with st.expander("🔐 Configure Delivery Services", expanded=False):
        st.warning("⚠️ Credentials are NOT stored. Enter them each session.")
        col_tg, col_gmail, col_drive = st.columns(3)

        with col_tg:
            use_telegram = st.checkbox("Telegram")
            tg_id = st.text_input("Chat ID", key="tg_id")
            tg_tok = st.text_input("Bot Token", type="password", key="tg_tok")

        with col_gmail:
            use_gmail = st.checkbox("Gmail")
            gmail_to = st.text_input("To", key="gmail_to")
            gmail_from = st.text_input("From", key="gmail_from")
            gmail_pass = st.text_input("App Password", type="password", key="gmail_pass")

        with col_drive:
            use_drive = st.checkbox("Google Drive")
            st.info("Requires service_account.json in root folder")

    if st.button("📤 Send PDF Now", use_container_width=True):
        pdf = st.session_state.get("pdf_bytes")
        results = {}
        if not pdf:
            st.error("PDF not found!")
        else:
            if use_telegram and tg_id and tg_tok:
                try:
                    send_telegram(pdf, tg_id, tg_tok)
                    results["Telegram"] = "✅ Sent"
                except Exception as e:
                    results["Telegram"] = f"❌ {str(e)[:100]}"

            if use_gmail and gmail_to and gmail_from and gmail_pass:
                try:
                    send_gmail(
                        to_email=gmail_to,
                        subject="Integral Report",
                        body="Your analysis report is attached.",
                        file_bytes=pdf,
                        filename="integral_report.pdf",
                        gmail_user=gmail_from,
                        app_password=gmail_pass
                    )
                    results["Gmail"] = "✅ Sent"
                except Exception as e:
                    results["Gmail"] = f"❌ {str(e)[:100]}"

            if use_drive:
                try:
                    file_id = upload_to_drive(pdf, "integral_report.pdf")
                    results["Google Drive"] = f"✅ Uploaded (ID: {file_id[:10]}...)"
                except Exception as e:
                    results["Google Drive"] = f"❌ {str(e)[:100]}"

            if results:
                st.subheader("📋 Delivery Results")
                for svc, msg in results.items():
                    st.write(f"**{svc}**: {msg}")
            else:
                st.info("Select a delivery method above.")