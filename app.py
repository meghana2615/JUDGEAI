import streamlit as st
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from database import init_db, create_user, authenticate_user, save_evaluation, get_history, delete_evaluation, update_profile, update_preferences, get_user
from judge import evaluate_answer, generate_answer, run_consistency_test, detect_failures, ollama_status

st.set_page_config(page_title="JUDGEAI | Evaluation Intelligence", page_icon="⚖️", layout="wide", initial_sidebar_state="expanded")
init_db()

BG = "#10071E"
PANEL = "#1E1030"
BORDER = "#38204F"
PURPLE = "#8B5CF6"
CYAN = "#36C8F4"
GREEN = "#35D6A0"
MUTED = "#AA98C1"

st.markdown("""
<style>
/* Password visibility toggle */
[data-testid="stTextInput"] button[aria-label="Show password"],
[data-testid="stTextInput"] button[aria-label="Hide password"] {
    font-size: 0 !important;
    color: transparent !important;
}

[data-testid="stTextInput"] button[aria-label="Show password"]::after,
[data-testid="stTextInput"] button[aria-label="Hide password"]::after {
    content: "👁️";
    font-size: 18px !important;
    color: white !important;
}
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root{--bg:#10071E;--panel:#1E1030;--border:#38204F;--text:#F2EAFB;--muted:#AA98C1;--purple:#8B5CF6;--cyan:#36C8F4;--green:#35D6A0}
.stApp{background:radial-gradient(ellipse at 78% 0%,rgba(105,48,160,.14),transparent 34%),#10071E;color:var(--text);font-family:'DM Sans',sans-serif}
html,body,[class*="st-"]{font-family:'DM Sans',sans-serif}
/* Fix Streamlit Material Icons */
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded');

.material-symbols-rounded,
[data-testid="stIconMaterial"] {
    font-family: 'Material Symbols Rounded' !important;
    font-weight: normal !important;
    font-style: normal !important;
    font-size: 24px;
    line-height: 1;
    letter-spacing: normal;
    text-transform: none;
    white-space: nowrap;
    direction: ltr;
    font-feature-settings: 'liga';
    -webkit-font-feature-settings: 'liga';
    -webkit-font-smoothing: antialiased;
}
.block-container{max-width:1500px;padding-top:1.45rem;padding-bottom:2.5rem}
h1,h2,h3,h4{font-family:'Space Grotesk',sans-serif!important;color:#F2EAFB!important;letter-spacing:-.45px}
h1{font-size:30px!important;line-height:1.18!important} h2{font-size:22px!important} h3{font-size:17px!important}
@media(max-width:760px){.block-container{padding:1rem .8rem 2rem}.auth-wrap{margin:2vh auto;padding:22px 18px}h1{font-size:25px!important}h2{font-size:20px!important}[data-testid="stMetricValue"]{font-size:22px!important}}
p,label,li{color:#D0C1E0;font-size:13px}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#24103D,#180B2A)!important;border-right:1px solid #38204F}
[data-testid="stSidebar"]>div:first-child{padding:1.25rem .9rem}
[data-testid="stSidebar"] [data-testid="stRadio"] label{padding:9px 12px;border-radius:10px;border:1px solid transparent}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked){background:linear-gradient(100deg,#7029D9,#35BDEB);color:white}
[data-testid="stMetric"]{background:linear-gradient(145deg,#26143B,#1B0D2B);border:1px solid #402657;border-radius:15px;padding:16px}
[data-testid="stMetricLabel"]{color:#BCA8D0!important;font-size:11px!important;letter-spacing:.8px}
[data-testid="stMetricValue"]{color:#F3E9FF!important;font-family:'Space Grotesk';font-size:27px!important}
.stButton>button{border-radius:10px;border:1px solid #7543BD;background:linear-gradient(105deg,#7029D9,#31BCEB);color:white;font-weight:650;min-height:40px}
.stButton>button:hover{border-color:#A98BFF;box-shadow:0 0 20px #7543BD55;transform:translateY(-1px)}
.stTextInput input,.stTextArea textarea,.stNumberInput input{background:#170B27!important;color:#F3E9FF!important;border:1px solid #49305F!important;border-radius:9px!important}
.stSelectbox>div>div,.stMultiSelect>div>div{background:#1B0D2B;border-radius:9px}
.stTabs [aria-selected="true"]{color:#C5A4FF!important}
[data-testid="stDataFrame"]{border:1px solid #402657;border-radius:12px}
[data-testid="stExpander"]{background:#1B0D2B;border:1px solid #402657;border-radius:11px}
hr{border-color:#38204F!important}
.eyebrow{color:#B48AFF;font-size:10px;font-weight:700;letter-spacing:1.8px;margin-bottom:5px}
.subcopy{color:#AA98C1;font-size:13px;margin-top:-8px;margin-bottom:22px}
.brand{font-family:'Space Grotesk';font-size:22px;font-weight:700;letter-spacing:1px;color:#F4EAFE}
.brand span{color:#47D2F1}
.brandtag{font-size:9px;letter-spacing:2px;color:#B18BCF}
.panel{background:linear-gradient(145deg,#241339,#1B0D2B);border:1px solid #402657;border-radius:15px;padding:17px}
.smallmuted{color:#AA98C1;font-size:11px}
.st-key-auth_card{
    max-width:520px;
    margin:4vh auto;
    background:linear-gradient(145deg,#27133F,#190B29);
    border:1px solid #49305F;
    border-radius:22px;
    padding:30px 34px;
    box-shadow:0 25px 80px #0005;
}
div[data-testid="stProgressBar"]>div>div{background:linear-gradient(90deg,#8B5CF6,#36C8F4)}
</style>
""", unsafe_allow_html=True)

def page_header(kicker, title, desc):
    st.markdown(
        f'<div class="eyebrow" style="padding-top: 18px;">{kicker}</div>',
        unsafe_allow_html=True
    )
    st.title(title)
    st.markdown(f'<div class="subcopy">{desc}</div>', unsafe_allow_html=True)

def show_result(result):
    st.divider()
    st.subheader("Evaluation report")
    a,b,c=st.columns([1,1,2])
    a.metric("Overall quality", f"{result['overall_score']:.2f}/10")
    b.metric("Risk level", result.get("risk", "—"))
    c.progress(max(0,min(result["overall_score"]/10,1)))
    cols=st.columns(4)
    for col,key in zip(cols,["accuracy","relevance","clarity","completeness"]):
        col.metric(key.title(),f"{result[key]:.1f}/10")
    x,y=st.columns(2)
    with x:
        with st.expander("Strengths",True): st.write(result.get("strengths","—"))
        with st.expander("Weaknesses",True): st.write(result.get("weaknesses","—"))
    with y:
        with st.expander("Improvement suggestions",True): st.write(result.get("improvements","—"))
        with st.expander("Judge verdict",True): st.write(result.get("verdict","—"))
    failures=detect_failures(result)
    st.markdown("#### Failure and risk signals")
    if failures["failures"]:
        for f in failures["failures"]:
            (st.error if f["severity"]=="Critical" else st.warning)(f"{f['category']} · {f['score']}/10 — {f['message']}")
    else: st.success("No threshold-based quality failures detected.")

def apply_rubric_weights(result, weights):
    keys=["accuracy","relevance","clarity","completeness"]
    total=sum(float(weights.get(k,25)) for k in keys)
    if total <= 0: return result
    result=dict(result)
    result["overall_score"]=round(sum(result[k]*float(weights.get(k,25)) for k in keys)/total,2)
    return result

def chart_theme(fig, height=340):
    fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10,r=10,t=35,b=10),height=height,font=dict(family="DM Sans",color="#D9CBE8"),
        hoverlabel=dict(bgcolor="#241339",font_color="#FFFFFF"),legend_title_text="")
    fig.update_xaxes(showgrid=False,zeroline=False)
    fig.update_yaxes(gridcolor="rgba(180,150,210,.12)",zeroline=False)
    return fig


def auth_screen():
    with st.container(key="auth_card"):
        st.markdown("""
        <div class="brand">JUDGE<span>AI</span></div>
        <div class="brandtag">AI RESPONSE INTELLIGENCE</div>
        <div style="font-size:10px;color:#A5A0B5;margin-top:5px;">
        AI Response Intelligence & Quality Evaluation Platform
        </div>
        <div style="font-size:10px;color:#8B5CF6;margin-top:12px;">
        Created by: chereddy.meghana@gmail.com
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        st.title("Your evaluation workspace")
        st.caption("Sign in or create a secure, personal workspace.")

        tab1, tab2 = st.tabs(["Sign in", "Create account"])

        with tab1:
            login = st.text_input(
                "Username or email",
                key="login_identity",
                placeholder="you@example.com"
            )
            password = st.text_input(
                "Password",
                type="password",
                key="login_password"
            )

            if st.button("Sign in to JUDGEAI", use_container_width=True):
                user = authenticate_user(login, password)
                if user:
                    st.session_state.user_id = user["id"]
                    st.session_state.username = user["username"]
                    st.session_state.email = user["email"]
                    st.rerun()
                else:
                    st.error("Login failed. Check your username/email and password.")

        with tab2:
            username = st.text_input(
                "Username",
                key="reg_username",
                placeholder="Choose a username"
            )
            email = st.text_input(
                "Email address",
                key="reg_email",
                placeholder="you@example.com"
            )
            p1 = st.text_input(
                "Password",
                type="password",
                key="reg_password"
            )
            p2 = st.text_input(
                "Confirm password",
                type="password",
                key="reg_confirm"
            )

            if st.button("Create secure account", use_container_width=True):
                if not username.strip() or not email.strip() or not p1:
                    st.error("Complete all fields.")
                elif not re.fullmatch(r"[A-Za-z0-9_.-]{3,32}", username.strip()):
                    st.error("Username must be 3–32 characters using letters, numbers, dots, underscores or hyphens.")
                elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()):
                    st.error("Enter a valid email address.")
                elif not 8 <= len(p1) <= 128:
                    st.error("Use a password between 8 and 128 characters.")
                elif p1 != p2:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = create_user(
                        username.strip(),
                        email.strip().lower(),
                        p1
                    )
                    if ok:
                        st.success("Account created. Sign in using your username or email.")
                    else:
                        st.error(msg)

        st.caption(
            "Private workspace · Passwords are stored as salted PBKDF2 hashes · "
            "Evaluation records are scoped to your account"
        )


if "user_id" not in st.session_state:
    auth_screen()
    st.stop()

user=get_user(st.session_state.user_id)
if not user:
    for key in ["user_id","username","email"]: st.session_state.pop(key,None)
    st.rerun()

weights={k:float(user.get(k+"_weight",25) or 25) for k in ["accuracy","relevance","clarity","completeness"]}
user_accent=user.get("accent_color") or PURPLE
st.markdown(f"<style>:root{{--user-accent:{user_accent}}} .stButton>button{{border-color:{user_accent}}} [data-testid='stProgressBar']>div>div{{background:{user_accent}}}</style>",unsafe_allow_html=True)


with st.sidebar:
    st.markdown("""
    <div class="brand">JUDGE<span>AI</span></div>
    <div class="brandtag">AI RESPONSE INTELLIGENCE</div>
    <div style="font-size:10px;color:#A5A0B5;margin-top:5px;">
        AI Response Intelligence & Quality Evaluation Platform
    </div>
    <div style="font-size:10px;color:#8B5CF6;margin-top:12px;">
        Created by: chereddy.meghana@gmail.com
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.markdown("---")
    st.caption("WORKSPACE")

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Evaluate Answer",
            "Model Arena",
            "Analytics",
            "Insight Studio",
            "Evaluation History",
            "Judge Consistency",
            "Failure Detection",
            "Dataset Lab",
            "Benchmark Lab",
            "Settings"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    online, engine_msg = ollama_status()

    st.markdown(
        f'<div class="panel"><div style="color:{"#35D6A0" if online else "#F6B94A"};font-weight:700;font-size:11px">● {"ENGINE ONLINE" if online else "ENGINE OFFLINE"}</div><div class="smallmuted">{engine_msg}</div></div>',
        unsafe_allow_html=True
    )

    st.write("")
    st.caption("SIGNED IN AS")
    st.markdown(f"**{user.get('display_name') or user['username']}**")
    st.caption(f"{user.get('role') or 'AI Quality Analyst'} · {user['email']}")

    if st.button("Log out", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

history=get_history(user["id"])
cols=["ID","Question","Answer","Accuracy","Relevance","Clarity","Completeness","Overall Score","Strengths","Weaknesses","Improvements","Verdict","Date","Model"]
df=pd.DataFrame(history,columns=cols)
if not df.empty:
    for c in ["Accuracy","Relevance","Clarity","Completeness","Overall Score"]: df[c]=pd.to_numeric(df[c],errors="coerce")
    df["Date Parsed"]=pd.to_datetime(df["Date"],errors="coerce")


if page=="Dashboard":

    page_header(
        "01 / INTELLIGENCE OVERVIEW",
        "Systems Overview",
        "Monitor answer quality, model behaviour and evaluation activity across your personal workspace."
    )

    total = len(df)
    avg = df["Overall Score"].mean() if total else 0
    best = df["Overall Score"].max() if total else 0
    models = df["Model"].nunique() if total else 0

    a, b, c, d = st.columns(4)

    a.metric("TOTAL EVALUATIONS", total)
    b.metric("AVERAGE QUALITY", f"{avg:.2f}/10")
    c.metric("BEST SCORE", f"{best:.2f}/10")
    d.metric("MODELS TESTED", models)


    
    st.divider()
    st.subheader("〰️ AI Signal Frequency")
    st.caption("MULTI-CHANNEL SIGNAL MONITOR · CONTINUOUS ANIMATION")

    
    signal_result = st.session_state.get("last_result", {})

    accuracy = float(signal_result.get("accuracy", 5))
    relevance = float(signal_result.get("relevance", 5))
    clarity = float(signal_result.get("clarity", 5))        

    a = 25 + accuracy * 7
    b = 25 + relevance * 7
    c = 25 + clarity * 7

    wave_html = f"""
    <html>
    <body style="margin:0;background:#100B20;border-radius:18px;overflow:hidden;">
    <svg viewBox="0 0 1200 300" width="100%" height="260"
         preserveAspectRatio="none"
         xmlns="http://www.w3.org/2000/svg">

      <defs>
        <filter id="glow">
          <feGaussianBlur stdDeviation="6"/>
        </filter>
      </defs>

      <g fill="none" stroke-linecap="round">

        <path d="M0 150 C150 {150-a} 250 {150-a} 400 150 S650 {150+a} 800 150 S1050 {150-a} 1200 150"
              stroke="#A855F7" stroke-width="12" opacity=".35" filter="url(#glow)"/>
        <path d="M0 150 C150 {150-a} 250 {150-a} 400 150 S650 {150+a} 800 150 S1050 {150-a} 1200 150"
              stroke="#A855F7" stroke-width="4">
          <animate attributeName="d"
            values="M0 150 C150 {150-a} 250 {150-a} 400 150 S650 {150+a} 800 150 S1050 {150-a} 1200 150;
                    M0 150 C150 {150+a} 250 {150+a} 400 150 S650 {150-a} 800 150 S1050 {150+a} 1200 150;
                    M0 150 C150 {150-a} 250 {150-a} 400 150 S650 {150+a} 800 150 S1050 {150-a} 1200 150"
            dur="5s" repeatCount="indefinite"/>
        </path>

        <path d="M0 155 C150 {155-b} 250 {155-b} 400 155 S650 {155+b} 800 155 S1050 {155-b} 1200 155"
              stroke="#22D3EE" stroke-width="12" opacity=".3" filter="url(#glow)"/>
        <path d="M0 155 C150 {155-b} 250 {155-b} 400 155 S650 {155+b} 800 155 S1050 {155-b} 1200 155"
              stroke="#22D3EE" stroke-width="4">
          <animate attributeName="d"
            values="M0 155 C150 {155-b} 250 {155-b} 400 155 S650 {155+b} 800 155 S1050 {155-b} 1200 155;
                    M0 155 C150 {155+b} 250 {155+b} 400 155 S650 {155-b} 800 155 S1050 {155+b} 1200 155;
                    M0 155 C150 {155-b} 250 {155-b} 400 155 S650 {155+b} 800 155 S1050 {155-b} 1200 155"
            dur="7s" repeatCount="indefinite"/>
        </path>

        <path d="M0 150 C150 {150-c} 250 {150-c} 400 150 S650 {150+c} 800 150 S1050 {150-c} 1200 150"
              stroke="#F472B6" stroke-width="12" opacity=".3" filter="url(#glow)"/>
        <path d="M0 150 C150 {150-c} 250 {150-c} 400 150 S650 {150+c} 800 150 S1050 {150-c} 1200 150"
              stroke="#F472B6" stroke-width="4">
          <animate attributeName="d"
            values="M0 150 C150 {150-c} 250 {150-c} 400 150 S650 {150+c} 800 150 S1050 {150-c} 1200 150;
                    M0 150 C150 {150+c} 250 {150+c} 400 150 S650 {150-c} 800 150 S1050 {150+c} 1200 150;
                    M0 150 C150 {150-c} 250 {150-c} 400 150 S650 {150+c} 800 150 S1050 {150-c} 1200 150"
            dur="6s" repeatCount="indefinite"/>
        </path>

      </g>
    </svg>

    <div style="display:flex;justify-content:center;gap:28px;
                color:#D8CDEB;font:12px Arial;padding:8px;flex-wrap:wrap;">
      <span style="color:#A855F7">● ACCURACY · {accuracy:.1f}/10</span>
      <span style="color:#22D3EE">● RELEVANCE · {relevance:.1f}/10</span>
      <span style="color:#F472B6">● CLARITY · {clarity:.1f}/10</span>
    </div>
    </body>
    </html>
    """

    st.components.v1.html(wave_html, height=285, scrolling=False)



    if st.session_state.get("pipeline_complete", False):
        st.markdown("### Latest evaluation pipeline")

        stages = [
            "INPUT RECEIVED",
            "AI ANALYSIS",
            "QUALITY SCORING",
            "FAILURE DETECTION",
            "FINAL VERDICT"
        ]

        stage_cols = st.columns(5)

        for col, stage in zip(stage_cols, stages):
            col.markdown(
                f"""
                <div style="
                    background:linear-gradient(145deg,#241339,#1B0D2B);
                    border:1px solid #49305F;
                    border-radius:12px;
                    padding:12px 5px;
                    text-align:center;
                    min-height:76px;">
                    <div style="color:#35D6A0;font-size:20px;">✓</div>
                    <div style="color:#DCCCF0;font-size:10px;font-weight:700;">
                        {stage}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


    left, right = st.columns([1.8, 1])

    with left:
        st.subheader("Quality trajectory")

        if total:
            trend = df.dropna(subset=["Date Parsed"]).sort_values("Date Parsed").copy()
            trend["Moving average"] = trend["Overall Score"].rolling(5, min_periods=1).mean()

            chart = px.line(
                trend,
                x="Date Parsed",
                y="Overall Score",
                color="Model",
                markers=True,
                range_y=[0, 10],
                hover_data=["Question"]
            )

            chart.add_scatter(
                x=trend["Date Parsed"],
                y=trend["Moving average"],
                name="5-evaluation moving average",
                mode="lines",
                line=dict(color="#FFFFFF", width=3, dash="dot")
            )

            chart_theme(chart, 360)
            st.plotly_chart(chart, use_container_width=True)

        else:
            st.info("Your quality trajectory will appear after your first evaluation.")

    with right:
        st.subheader("Recent activity")

        if total:
            for _, r in df.head(5).iterrows():
                st.markdown(
                    f'<div class="panel" style="padding:11px;margin-bottom:8px">'
                    f'<b>{str(r["Question"])[:52]}</b>'
                    f'<div class="smallmuted">{r["Model"]} · {r["Date"]}</div>'
                    f'<div style="color:#35D6A0;font-weight:700">'
                    f'{r["Overall Score"]:.2f}/10</div></div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("Your recent evaluations will appear here.")

    st.divider()
    st.subheader("Quick launch")

    q1, q2, q3 = st.columns(3)

    q1.markdown(
        '<div class="panel"><b>Answer evaluation</b>'
        '<p class="smallmuted">Score a response across four quality dimensions.</p></div>',
        unsafe_allow_html=True
    )

    q2.markdown(
        '<div class="panel"><b>Model arena</b>'
        '<p class="smallmuted">Compare responses from multiple local models.</p></div>',
        unsafe_allow_html=True
    )

    q3.markdown(
        '<div class="panel"><b>Benchmark lab</b>'
        '<p class="smallmuted">Run repeatable tests from a CSV dataset.</p></div>',
        unsafe_allow_html=True
    )


elif page=="Evaluate Answer":
    page_header("02 / ANSWER ASSESSMENT","Evaluate an AI Answer","Submit a question and its generated answer for structured quality assessment.")
    question=st.text_area("Evaluation question",height=100,placeholder="Enter the original question...")
    answer=st.text_area("AI-generated answer",height=210,placeholder="Paste the answer you want JUDGEAI to assess...")
    model=st.text_input("Model label (optional)","Manual evaluation")
    
    if st.button("⚖ Run evaluation",type="primary",use_container_width=True):
        if not question.strip() or not answer.strip():
            st.warning("Enter both the question and answer.")
        else:
            try:
                with st.status("JUDGEAI evaluation pipeline running...", expanded=True) as pipeline:

                    pipeline.write("01 · Input received")
                    pipeline.write("02 · AI analysis in progress...")

                    result = apply_rubric_weights(
                        evaluate_answer(question, answer), weights
                    )

                    pipeline.write("03 · Quality scoring completed")

                    failures = detect_failures(result)
                    pipeline.write("04 · Failure detection completed")

                    save_evaluation(user["id"], question, answer, result, model)

                    st.session_state.last_result = result
                    st.session_state.last_failures = failures
                    st.session_state.pipeline_complete = True

                    pipeline.update(
                        label="05 · Final verdict generated",
                        state="complete",
                        expanded=True
                    )

                show_result(result)
                st.success("Evaluation saved to your private history.")

            except Exception as e:
                st.error(f"Evaluation could not run: {e}")


elif page=="Model Arena":
    page_header("03 / MODEL INTELLIGENCE","Model Arena","Generate and compare answers from two Ollama models using the same evaluation rubric.")
    models=st.text_input("Ollama model names, comma separated","llama3.2:3b, gemma3:1b")
    question=st.text_area("Test prompt",height=130)
    if st.button("Launch model comparison",type="primary",use_container_width=True):
        chosen=[x.strip() for x in models.split(",") if x.strip()][:4]
        if len(chosen)<2 or not question.strip(): st.warning("Enter a prompt and at least two model names.")
        else:
            results=[]
            bar=st.progress(0)
            for i,m in enumerate(chosen):
                try:
                    with st.spinner(f"Generating and judging {m}..."):
                        ans=generate_answer(question,m); res=apply_rubric_weights(evaluate_answer(question,ans),weights)
                        save_evaluation(user["id"],question,ans,res,m)
                        results.append({"Model":m,"Answer":ans,**res})
                except Exception as e: results.append({"Model":m,"Error":str(e)})
                bar.progress((i+1)/len(chosen))
            st.session_state.arena_results=results
    for r in st.session_state.get("arena_results",[]):
        with st.expander(r["Model"],expanded=True):
            if "Error" in r: st.error(r["Error"])
            else:
                st.metric("Overall score",f"{r['overall_score']:.2f}/10")
                st.write(r["Answer"])
                st.caption("Accuracy · Relevance · Clarity · Completeness")
                st.write({k:r[k] for k in ["accuracy","relevance","clarity","completeness"]})

elif page=="Analytics":
    page_header("04 / PERFORMANCE INTELLIGENCE","Analytics Command Centre","Filter your evaluation universe, replay model behaviour over time and inspect the dimensions that drive answer quality.")
    if df.empty:
        st.info("Your analytics will activate after your first evaluation.")
    else:
        f1,f2,f3=st.columns([1.1,1,1])
        with f1:
            selected_models=st.multiselect("Models",sorted(df["Model"].dropna().unique()),default=sorted(df["Model"].dropna().unique()))
        with f2:
            min_score=st.slider("Minimum score filter",0.0,10.0,0.0,0.5)
        with f3:
            moving_window=st.slider("Moving average window",2,15,5)
        filtered=df[df["Model"].isin(selected_models) & (df["Overall Score"]>=min_score)].copy()
        if filtered.empty: st.warning("No records match these filters.")
        else:
            k1,k2,k3,k4=st.columns(4)
            k1.metric("VISIBLE EVALUATIONS",len(filtered)); k2.metric("MEAN QUALITY",f"{filtered['Overall Score'].mean():.2f}/10")
            k3.metric("TOP RESULT",f"{filtered['Overall Score'].max():.2f}/10")
            k4.metric("QUALITY SPREAD",f"{filtered['Overall Score'].std():.2f}" if len(filtered)>1 else "—")
            t1,t2,t3,t4=st.tabs([
                "Quality over time",
                "Model intelligence",
                "Rubric diagnostics",
                "Neural network"
            ])            
            with t1:
                trend=filtered.dropna(subset=["Date Parsed"]).sort_values("Date Parsed").copy()
                trend["Moving average"]=trend["Overall Score"].rolling(moving_window,min_periods=1).mean()
                if not trend.empty:
                    fig=px.line(trend,x="Date Parsed",y="Overall Score",color="Model",markers=True,range_y=[0,10],hover_data=["Question","Accuracy","Relevance","Clarity","Completeness"])
                    fig.add_scatter(x=trend["Date Parsed"],y=trend["Moving average"],name=f"{moving_window}-record moving average",mode="lines",line=dict(color="#FFFFFF",width=3,dash="dot"))
                    chart_theme(fig,390); st.plotly_chart(fig,use_container_width=True,config={"scrollZoom":True})
                    st.caption("The dotted line is a rolling quality baseline. Hover over points to inspect the evaluation behind each score.")
                    daily=trend.assign(Day=trend["Date Parsed"].dt.strftime("%Y-%m-%d")).groupby(["Day","Model"],as_index=False).agg(Accuracy=("Accuracy","mean"),Relevance=("Relevance","mean"),Evaluations=("ID","count"))
                    if daily["Day"].nunique()>1:
                        st.subheader("Model behaviour replay")
                        st.caption("Use Play or the timeline slider to watch accuracy and relevance shift across evaluation dates.")
                        replay=px.scatter(daily,x="Accuracy",y="Relevance",size="Evaluations",color="Model",animation_frame="Day",animation_group="Model",range_x=[0,10],range_y=[0,10],size_max=34,hover_name="Model")
                        replay.update_layout(transition={"duration":450})
                        chart_theme(replay,470); st.plotly_chart(replay,use_container_width=True)
                    else: st.info("The animated replay unlocks when your history contains evaluations from at least two different dates.")
            with t2:
                summary=filtered.groupby("Model")[["Accuracy","Relevance","Clarity","Completeness","Overall Score"]].agg(["mean","count"]).round(2)
                st.dataframe(summary,use_container_width=True)
                means=filtered.groupby("Model",as_index=False)["Overall Score"].mean().sort_values("Overall Score",ascending=False)
                fig=px.bar(means,x="Model",y="Overall Score",color="Model",range_y=[0,10],text_auto=".2f")
                chart_theme(fig,330); st.plotly_chart(fig,use_container_width=True)
            with t3:
                criteria=["Accuracy","Relevance","Clarity","Completeness"]
                means=filtered[criteria].mean().reset_index(); means.columns=["Criterion","Average score"]
                radar=px.line_polar(means,r="Average score",theta="Criterion",line_close=True,range_r=[0,10])
                radar.update_traces(fill="toself",line_color="#B18AFF")
                chart_theme(radar,390); st.plotly_chart(radar,use_container_width=True)
                weakest=means.sort_values("Average score").iloc[0]
                st.info(f"Improvement opportunity: **{weakest['Criterion']}** currently has the lowest mean score ({weakest['Average score']:.2f}/10).")
            st.download_button("Export filtered analytics (CSV)",filtered[cols].to_csv(index=False).encode(),file_name="judgeai_filtered_analytics.csv",mime="text/csv")


            with t4:
                st.subheader("JUDGEAI Quality Neural Network")
                st.caption(
                    "CONNECTED INTELLIGENCE MAP · LIVE EVALUATION HISTORY"
                )

                criteria = ["Accuracy", "Relevance", "Clarity", "Completeness"]
                averages = filtered[criteria].mean()

                overall = filtered["Overall Score"].mean()

                flagged = (
                    filtered[criteria].min(axis=1) < 6
                ).sum()

                failure_rate = (
                    flagged / len(filtered) * 10
                )

                model_count = filtered["Model"].nunique()

                nodes = {
                    "Accuracy": (-1.2, 1.0, averages["Accuracy"]),
                    "Relevance": (0, 1.35, averages["Relevance"]),
                    "Clarity": (1.2, 1.0, averages["Clarity"]),
                    "Completeness": (-1.2, -0.7, averages["Completeness"]),
                    "Overall Quality": (0, 0, overall),
                    "Failure Detection": (1.2, -0.7, 10 - failure_rate),
                    "Model Intelligence": (0, -1.35, min(model_count, 10)),
                }

                connections = [
                    ("Accuracy", "Overall Quality"),
                    ("Relevance", "Overall Quality"),
                    ("Clarity", "Overall Quality"),
                    ("Completeness", "Overall Quality"),
                    ("Overall Quality", "Failure Detection"),
                    ("Overall Quality", "Model Intelligence"),
                    ("Accuracy", "Relevance"),
                    ("Relevance", "Clarity"),
                    ("Clarity", "Failure Detection"),
                    ("Completeness", "Model Intelligence"),
                    ("Failure Detection", "Model Intelligence")
                ]

                fig = go.Figure()

                # Connection lines
                for start, end in connections:
                    x1, y1, _ = nodes[start]
                    x2, y2, _ = nodes[end]

                    fig.add_trace(go.Scatter(
                        x=[x1, x2],
                        y=[y1, y2],
                        mode="lines",
                        line=dict(
                            color="rgba(139,92,246,0.38)",
                            width=1.7
                        ),
                        hoverinfo="skip",
                        showlegend=False
                    ))

                # Network nodes
                names = list(nodes.keys())
                x_values = [nodes[n][0] for n in names]
                y_values = [nodes[n][1] for n in names]
                scores = [nodes[n][2] for n in names]

                details = []

                for name in names:
                    value = nodes[name][2]

                    if name == "Failure Detection":
                        details.append(
                            f"{name}<br>Flagged evaluations: {flagged}<br>Healthy signal: {value:.2f}/10"
                        )
                    elif name == "Model Intelligence":
                        details.append(
                            f"{name}<br>Models tested: {model_count}"
                        )
                    else:
                        details.append(
                            f"{name}<br>Average score: {value:.2f}/10"
                        )

                fig.add_trace(go.Scatter(
                    x=x_values,
                    y=y_values,
                    mode="markers+text",
                    text=names,
                    textposition="bottom center",
                    textfont=dict(
                        color="#E9DDF8",
                        size=11
                    ),
                    hovertext=details,
                    hoverinfo="text",
                    marker=dict(
                        size=[34, 30, 30, 30, 43, 34, 32],
                        color=scores,
                        colorscale=[
                            [0, "#F472B6"],
                            [0.5, "#8B5CF6"],
                            [1, "#22D3EE"]
                        ],
                        cmin=0,
                        cmax=10,
                        line=dict(
                            color="#E9D5FF",
                            width=1.5
                        ),
                        opacity=0.95,
                        showscale=True,
                        colorbar=dict(
                            title=dict(
                                        text="Score",
                                        font=dict(color="#D9CBE8")
                            ),
                            tickfont=dict(color="#D9CBE8")
                        )
                    ),
                    showlegend=False
                ))

                fig.update_layout(
                    height=570,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=30, r=30, t=30, b=50),
                    xaxis=dict(
                        visible=False,
                        range=[-2, 2]
                    ),
                    yaxis=dict(
                        visible=False,
                        range=[-1.9, 1.9],
                        scaleanchor="x",
                        scaleratio=1
                    ),
                    hoverlabel=dict(
                        bgcolor="#241339",
                        font_color="white"
                    )
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"displayModeBar": False}
                )

                st.divider()

                n1, n2, n3 = st.columns(3)
                n1.metric("CONNECTED MODELS", model_count)
                n2.metric("FLAGGED EVALUATIONS", int(flagged))
                n3.metric("AVERAGE NETWORK QUALITY", f"{overall:.2f}/10")

                st.caption(
                    "Each connection represents a relationship in the JUDGEAI "
                    "evaluation pipeline. Hover over nodes to inspect their values."
                )

elif page=="Insight Studio":
    page_header("05 / EXPERIMENTAL INTELLIGENCE","Insight Studio","A personal quality cockpit: set a target, identify weak dimensions and turn evaluation history into an improvement plan.")
    if df.empty: st.info("Run a few evaluations to generate a meaningful quality improvement plan.")
    else:
        goal=int(user.get("weekly_goal",20) or 20); week_start=pd.Timestamp.now().normalize()-pd.Timedelta(days=6)
        weekly=int((df["Date Parsed"]>=week_start).sum())
        a,b,c=st.columns(3); a.metric("WEEKLY TARGET",f"{weekly} / {goal}",f"{max(0,goal-weekly)} to go")
        b.metric("TARGET PROGRESS",f"{min(100,weekly/goal*100):.0f}%"); c.metric("PERSONAL BEST",f"{df['Overall Score'].max():.2f}/10")
        st.progress(min(1,weekly/goal))
        criteria=["Accuracy","Relevance","Clarity","Completeness"]; means=df[criteria].mean().sort_values()
        st.subheader("Your quality fingerprint")
        fp=means.rename_axis("Criterion").reset_index(name="Mean score")
        fig=px.bar(fp,x="Mean score",y="Criterion",orientation="h",range_x=[0,10],color="Mean score",color_continuous_scale=["#F472B6","#8B5CF6","#36C8F4"])
        fig.update_layout(coloraxis_showscale=False); chart_theme(fig,310); st.plotly_chart(fig,use_container_width=True)
        weak=means.index[0]
        st.markdown(f'<div class="panel"><div class="eyebrow">NEXT IMPROVEMENT PRIORITY</div><h3>{weak}</h3><p class="smallmuted">This is currently your lowest-scoring rubric dimension. Review the lowest-scoring examples in Evaluation History and rerun them after improving the response.</p></div>',unsafe_allow_html=True)
        if len(df)>1:
            recent=df.head(min(10,len(df)))["Overall Score"].mean()
            previous=df.iloc[min(10,len(df)):min(20,len(df))]["Overall Score"].mean()
            delta=recent-previous if pd.notna(previous) else 0
            st.metric("Recent momentum · last 10 vs previous 10",f"{recent:.2f}/10",f"{delta:+.2f} points")

elif page=="Evaluation History":
    page_header("05 / AUDIT TRAIL","Evaluation History","Search, inspect, export and manage the evaluations saved to your account.")
    if df.empty: st.info("Your evaluation history is empty.")
    else:
        search=st.text_input("Search question, answer or model")
        filtered=df[df.apply(lambda row: search.lower() in " ".join(map(str,row.values)).lower(),axis=1)] if search else df
        st.dataframe(filtered[["ID","Question","Model","Overall Score","Date"]],use_container_width=True,hide_index=True)
        st.download_button("Download my evaluation history (CSV)",filtered[cols].to_csv(index=False).encode(),file_name="judgeai_history.csv",mime="text/csv")
        ids=filtered["ID"].tolist()
        if ids:
            selected=st.selectbox("Inspect evaluation ID",ids)
            record=filtered[filtered["ID"]==selected].iloc[0]
            st.markdown("#### Evaluation detail")
            st.write("**Question**",record["Question"]); st.write("**Answer**",record["Answer"])
            st.write({k:record[k] for k in ["Accuracy","Relevance","Clarity","Completeness","Overall Score","Verdict","Strengths","Weaknesses","Improvements"]})
            if st.button("Delete selected evaluation",type="secondary"):
                delete_evaluation(user["id"],int(selected)); st.success("Record deleted."); st.rerun()

elif page=="Judge Consistency":
    page_header("06 / RELIABILITY TESTING","Judge Consistency Lab","Repeat the same assessment to measure score stability and standard deviation.")
    q=st.text_area("Question",height=90); a=st.text_area("Answer to evaluate",height=170); runs=st.slider("Number of evaluation runs",2,5,3)
    if st.button("Run consistency test",type="primary"):
        if not q.strip() or not a.strip(): st.warning("Enter both question and answer.")
        else:
            try:
                with st.spinner("Repeating evaluations..."): result=run_consistency_test(q,a,runs)
                result["runs"]=[apply_rubric_weights(item,weights) for item in result["runs"]]
                weighted_scores=[item["overall_score"] for item in result["runs"]]
                result["statistics"]["overall_score"]={"average":round(float(pd.Series(weighted_scores).mean()),2),
                    "highest":max(weighted_scores),"lowest":min(weighted_scores),
                    "standard_deviation":round(float(pd.Series(weighted_scores).std(ddof=0)),2)}
                st.dataframe(pd.DataFrame(result["statistics"]).T,use_container_width=True)
                for i,r in enumerate(result["runs"],1): save_evaluation(user["id"],q,a,r,"Consistency run")
                st.success(f"{runs} runs completed and saved.")
            except Exception as e: st.error(str(e))

elif page=="Failure Detection":
    page_header("07 / RISK MONITORING","AI Failure Detection","Inspect low-scoring dimensions and classify quality risks from your evaluation history.")
    if df.empty: st.info("Run an evaluation before using failure detection.")
    else:
        threshold=st.slider("Flag scores below",0.0,9.0,6.0,0.5)
        bad=df[df[["Accuracy","Relevance","Clarity","Completeness"]].min(axis=1)<threshold]
        st.metric("Evaluations with at least one flagged criterion",len(bad))
        for _,r in bad.iterrows():
            with st.expander(f"#{r['ID']} · {r['Model']} · overall {r['Overall Score']:.1f}/10"):
                st.write(r["Question"])
                for k in ["Accuracy","Relevance","Clarity","Completeness"]:
                    if r[k]<threshold: st.warning(f"{k}: {r[k]:.1f}/10")

elif page=="Dataset Lab":
    page_header("08 / DATASET INTELLIGENCE","Dataset Lab","Upload a CSV with question and answer columns to evaluate a collection of responses.")
    file=st.file_uploader(
    "Upload CSV with a question column",
    type=["csv"],
    key="bench_csv",
    label_visibility="collapsed"
    )    
    if file:
        try:
            data=pd.read_csv(file); st.dataframe(data.head(10),use_container_width=True)
            if not {"question","answer"}.issubset(data.columns): st.error("CSV must contain columns named question and answer.")
            elif st.button("Evaluate dataset",type="primary"):
                rows=[]; bar=st.progress(0)
                for i,row in data.iterrows():
                    try:
                        res=apply_rubric_weights(evaluate_answer(str(row["question"]),str(row["answer"])),weights)
                        save_evaluation(user["id"],str(row["question"]),str(row["answer"]),res,"Dataset evaluation")
                        rows.append({"question":row["question"],"answer":row["answer"],**res,"error":""})
                    except Exception as e: rows.append({"question":row["question"],"answer":row["answer"],"error":str(e)})
                    bar.progress((i+1)/len(data))
                st.session_state.dataset_output=pd.DataFrame(rows)
            if "dataset_output" in st.session_state:
                st.dataframe(st.session_state.dataset_output,use_container_width=True)
                st.download_button("Download dataset evaluation report",st.session_state.dataset_output.to_csv(index=False).encode(),file_name="judgeai_dataset_report.csv")
        except Exception as e: st.error(f"Could not read CSV: {e}")

elif page=="Benchmark Lab":
    page_header("09 / CONTROLLED BENCHMARKING","Benchmark Lab","Compare selected models against the same set of test questions.")
    file=st.file_uploader(
    "Upload CSV with a question column",
    type=["csv"],
    key="dataset_csv",
    label_visibility="collapsed"
    )    
    models=st.text_input("Models to benchmark","llama3.2:3b, gemma3:1b")
    if file:
        data=pd.read_csv(file); st.dataframe(data.head(8),use_container_width=True)
        if "question" not in data.columns: st.error("CSV must include a question column.")
        elif st.button("Start benchmark",type="primary"):
            chosen=list(dict.fromkeys(m.strip() for m in models.split(",") if m.strip()))[:4]
            if not chosen: st.warning("Enter at least one Ollama model name.")
            elif data.empty: st.warning("The uploaded CSV has no test questions.")
            else:
                out=[]; tasks=len(data)*len(chosen); done=0; bar=st.progress(0)
                for m in chosen:
                    for _,r in data.iterrows():
                        try:
                            ans=generate_answer(str(r["question"]),m); res=apply_rubric_weights(evaluate_answer(str(r["question"]),ans),weights)
                            save_evaluation(user["id"],str(r["question"]),ans,res,m)
                            out.append({"Model":m,"Question":r["question"],"Answer":ans,**res})
                        except Exception as e: out.append({"Model":m,"Question":r["question"],"Error":str(e)})
                        done+=1; bar.progress(done/tasks)
                st.session_state.benchmark_output=pd.DataFrame(out)
    if "benchmark_output" in st.session_state:
        out=st.session_state.benchmark_output; st.dataframe(out,use_container_width=True)
        if "overall_score" in out.columns:
            st.subheader("Model score summary")
            valid=out.dropna(subset=["overall_score"])
            if not valid.empty:
                summary=valid.groupby("Model")["overall_score"].mean().round(2).reset_index()
                st.dataframe(summary,use_container_width=True)
        st.download_button("Download benchmark report",out.to_csv(index=False).encode(),file_name="judgeai_benchmark_report.csv")

elif page=="Settings":
    page_header("11 / PERSONAL WORKSPACE","Your Workspace","Make JUDGEAI feel like your own evaluation command centre. Your identity, visual accent, goals and scoring rubric are saved to your account.")
    st.subheader("Personal identity")
    with st.form("profile_form"):
        p1,p2=st.columns(2)
        with p1:
            display_name=st.text_input("Display name",value=user.get("display_name") or user["username"],max_chars=60)
            role=st.text_input("Professional role",value=user.get("role") or "AI Quality Analyst",max_chars=60)
            email_new=st.text_input("Email address",value=user["email"])
        with p2:
            accent_options={"Electric violet":"#8B5CF6","Signal cyan":"#36C8F4","Mint green":"#35D6A0","Amber":"#F2B85B","Rose":"#F472B6"}
            current_accent=user.get("accent_color") or "#8B5CF6"; labels=list(accent_options.keys())
            current_label=next((k for k,v in accent_options.items() if v==current_accent),labels[0])
            accent_label=st.selectbox("Workspace accent",labels,index=labels.index(current_label))
            weekly_goal=st.number_input("Weekly evaluation goal",min_value=1,max_value=500,value=int(user.get("weekly_goal") or 20))
            bio=st.text_area("Short workspace bio",value=user.get("bio") or "",max_chars=240,placeholder="What are you evaluating? What quality standard matters to you?")
        save_profile=st.form_submit_button("Save personal workspace",type="primary",use_container_width=True)
        if save_profile:
            ok,msg=update_profile(user["id"],email_new)
            if ok:
                ok2,msg2=update_preferences(user["id"],display_name,role,bio,accent_options[accent_label],weekly_goal,weights["accuracy"],weights["relevance"],weights["clarity"],weights["completeness"])
                if ok2: st.success("Workspace profile saved."); st.rerun()
                else: st.error(msg2)
            else: st.error(msg)
    st.divider()
    st.subheader("Personal evaluation rubric")
    st.caption("Choose how much each quality dimension contributes to your overall score. Weights are normalized automatically.")
    with st.form("rubric_form"):
        w1,w2=st.columns(2)
        with w1:
            wa=st.slider("Accuracy weight",0,100,int(weights["accuracy"]))
            wr=st.slider("Relevance weight",0,100,int(weights["relevance"]))
        with w2:
            wc=st.slider("Clarity weight",0,100,int(weights["clarity"]))
            wco=st.slider("Completeness weight",0,100,int(weights["completeness"]))
        save_rubric=st.form_submit_button("Save my scoring rubric",type="primary")
        if save_rubric:
            ok,msg=update_preferences(user["id"],user.get("display_name") or user["username"],user.get("role") or "AI Quality Analyst",user.get("bio") or "",user.get("accent_color") or "#8B5CF6",int(user.get("weekly_goal") or 20),wa,wr,wc,wco)
            if ok: st.success("Your weighted rubric is saved. New evaluations will use it."); st.rerun()
            else: st.error(msg)
    st.info("Security: passwords are stored as salted PBKDF2 hashes. Username and email are unique login identifiers. Email verification and password-reset emails require a configured email provider and are not enabled in this local build.")
    st.caption("JUDGEAI · YOUR RUBRIC · YOUR SIGNAL · YOUR INTELLIGENCE")
