import streamlit as st
import pandas as pd

# ── Config ──────────────────────────────────────────────────────────────────
TEAMS = [
    "Team Bison", "Bulldogs", "Data Analytics", "404:NameNotFound",
    "Numpy Ninjas", "Brons", "Moving Averagers", "KSK",
    "Group 3", "Team Syntax", "Back Row", "Precision Portfolios",
    "Seth and Friends", "Annabal and Alison",
]

JUDGES = ["Dr Jaffri", "Dr Fariz", "Dr Stumphf"]

MEDAL = {1: "🥇", 2: "🥈", 3: "🥉"}

# ── Page setup ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Data Analytics Competition",
    page_icon="📊",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3 { font-family: 'Space Mono', monospace; }

.main { background-color: #0e1117; }

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: #1a1d27;
    border-radius: 12px;
    padding: 6px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #aaa;
    font-family: 'Space Mono', monospace;
    font-size: 13px;
}
.stTabs [aria-selected="true"] {
    background: #4f8ef7 !important;
    color: #fff !important;
}

div[data-testid="metric-container"] {
    background: #1a1d27;
    border: 1px solid #2e3348;
    border-radius: 12px;
    padding: 16px 20px;
}

.podium-card {
    background: linear-gradient(135deg, #1a1d27 0%, #242840 100%);
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    border: 1px solid #2e3348;
    margin-bottom: 16px;
}

.team-tag {
    display: inline-block;
    background: #1e2235;
    border: 1px solid #3a3f5c;
    border-radius: 6px;
    padding: 2px 10px;
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    color: #aab;
    margin: 2px;
}

.section-header {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    letter-spacing: 3px;
    color: #4f8ef7;
    text-transform: uppercase;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
if "scores" not in st.session_state:
    # scores[judge][team] = float or None
    st.session_state.scores = {j: {t: None for t in TEAMS} for j in JUDGES}

if "finalized" not in st.session_state:
    st.session_state.finalized = False

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 📊 Data Analytics Competition")
st.markdown("##### Judge Scoring Portal  •  14 Teams  •  3 Judges")
st.divider()

# ── Tabs: one per judge + Results ────────────────────────────────────────────
tab_labels = JUDGES + ["📋 Consolidate & Results"]
tabs = st.tabs(tab_labels)

for i, judge in enumerate(JUDGES):
    with tabs[i]:
        st.markdown(f"<div class='section-header'>Scoring as — {judge}</div>", unsafe_allow_html=True)
        st.markdown(f"### {judge}'s Scoreboard")
        st.caption("Enter a score (0–100) for each team. Leave blank to score later.")

        col1, col2 = st.columns(2)
        for j, team in enumerate(TEAMS):
            col = col1 if j % 2 == 0 else col2
            with col:
                current = st.session_state.scores[judge][team]
                val = st.number_input(
                    label=team,
                    min_value=0.0,
                    max_value=100.0,
                    value=float(current) if current is not None else 0.0,
                    step=0.5,
                    key=f"{judge}_{team}",
                    format="%.1f",
                )
                st.session_state.scores[judge][team] = val

        # Progress indicator
        filled = sum(1 for v in st.session_state.scores[judge].values() if v is not None and v > 0)
        st.divider()
        st.progress(filled / len(TEAMS), text=f"{filled}/{len(TEAMS)} teams scored")

# ── Results tab ───────────────────────────────────────────────────────────────
with tabs[-1]:
    st.markdown("### 📋 Consolidated Results")

    # Build dataframe
    rows = []
    for team in TEAMS:
        row = {"Team": team}
        total = 0.0
        for judge in JUDGES:
            s = st.session_state.scores[judge][team]
            score = s if s is not None else 0.0
            row[judge] = score
            total += score
        row["Total"] = round(total, 1)
        rows.append(row)

    df = pd.DataFrame(rows).sort_values("Total", ascending=False).reset_index(drop=True)
    df.insert(0, "Rank", range(1, len(df) + 1))

    # ── Summary metrics ──
    c1, c2, c3 = st.columns(3)
    for idx, judge in enumerate(JUDGES):
        scored = sum(1 for t in TEAMS if st.session_state.scores[judge][t] and st.session_state.scores[judge][t] > 0)
        [c1, c2, c3][idx].metric(judge, f"{scored}/{len(TEAMS)} scored")

    st.divider()

    # ── Full scores table ──
    st.markdown("<div class='section-header'>All Team Scores</div>", unsafe_allow_html=True)

    def highlight_top3(row):
        rank = row["Rank"]
        if rank == 1:
            return ["background-color: #2a3a1a; color: #7ed857"] * len(row)
        elif rank == 2:
            return ["background-color: #2a2a1a; color: #d4b83a"] * len(row)
        elif rank == 3:
            return ["background-color: #1a2a2a; color: #5ab8c8"] * len(row)
        return [""] * len(row)

    styled = df.style.apply(highlight_top3, axis=1).format(
        {j: "{:.1f}" for j in JUDGES} | {"Total": "{:.1f}"}
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.divider()

    # ── Announce button ──
    if st.button("🏆 Announce Winners", type="primary", use_container_width=True):
        st.session_state.finalized = True

    if st.session_state.finalized:
        st.balloons()
        st.markdown("## 🏆 Winners Announced!")
        st.divider()

        top3 = df.head(3)
        cols = st.columns(3)
        order = [1, 0, 2]  # display order: 2nd, 1st, 3rd (podium style)

        for display_pos, rank_idx in enumerate(order):
            if rank_idx < len(top3):
                row = top3.iloc[rank_idx]
                rank = int(row["Rank"])
                emoji = MEDAL.get(rank, "")
                height = ["180px", "220px", "160px"][display_pos]
                with cols[display_pos]:
                    st.markdown(f"""
                    <div class='podium-card' style='min-height:{height}'>
                        <div style='font-size:48px'>{emoji}</div>
                        <div style='font-size:22px; font-family:Space Mono,monospace; font-weight:700; margin:8px 0'>{rank}{"st" if rank==1 else "nd" if rank==2 else "rd"} Place</div>
                        <div style='font-size:18px; color:#dde; margin-bottom:8px'>{row["Team"]}</div>
                        <div style='font-size:28px; color:#4f8ef7; font-family:Space Mono,monospace; font-weight:700'>{row["Total"]}</div>
                        <div style='font-size:11px; color:#666; margin-top:4px'>TOTAL SCORE</div>
                    </div>
                    """, unsafe_allow_html=True)

        st.divider()
        st.markdown("#### Full Ranking")
        for _, row in df.iterrows():
            rank = int(row["Rank"])
            medal = MEDAL.get(rank, f"#{rank}")
            st.markdown(
                f"**{medal} {row['Team']}** — "
                f"Total: `{row['Total']}` &nbsp;|&nbsp; "
                + " &nbsp;|&nbsp; ".join([f"{j}: `{row[j]:.1f}`" for j in JUDGES]),
                unsafe_allow_html=True,
            )

        if st.button("🔄 Reset & Start Over", type="secondary"):
            st.session_state.scores = {j: {t: None for t in TEAMS} for j in JUDGES}
            st.session_state.finalized = False
            st.rerun()
