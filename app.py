import html
import pandas as pd
import streamlit as st

st.set_page_config(page_title="The Ripple | Timetable Impact Analyzer", page_icon="🌊", layout="wide")

# All CSS stays inside this style block. Dropdown controls use dark text on white.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');
:root{--bg:#07111f;--panel:#0d1b2c;--line:#29445e;--text:#eaf4ff;--muted:#b3c5d8;--teal:#45e0c1;--blue:#64a9ff}
.stApp{background:radial-gradient(ellipse at 10% 0%,rgba(27,103,145,.22),transparent 34%),linear-gradient(145deg,#07111f,#091727 55%,#07111f);color:var(--text);font-family:Manrope,sans-serif}
[data-testid="stHeader"]{background:rgba(7,17,31,.85)}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0c1b2c,#091522);border-right:1px solid var(--line)}
[data-testid="stSidebar"] label,[data-testid="stSidebar"] [data-testid="stWidgetLabel"] *{color:#eaf4ff!important}
.block-container{padding-top:1.5rem;padding-bottom:2.5rem;max-width:1450px}
h1,h2,h3,h4,p{color:var(--text)}
/* Selected dropdown values: dark text on a white background */
[data-testid="stSidebar"] [data-baseweb="select"]>div{background:#fff!important;border:1px solid #b7c8d8!important}
[data-testid="stSidebar"] [data-baseweb="select"] input,
[data-testid="stSidebar"] [data-baseweb="select"] [role="combobox"],
[data-testid="stSidebar"] [data-baseweb="select"] [role="combobox"] *,
[data-testid="stSidebar"] [data-baseweb="select"] span{color:#142235!important;-webkit-text-fill-color:#142235!important;opacity:1!important}
[data-testid="stSidebar"] [data-baseweb="select"] svg{fill:#142235!important;color:#142235!important}
[data-testid="stSidebar"] [data-baseweb="tag"]{background:#d9f7f0!important;border:1px solid #82d9c8!important}
[data-testid="stSidebar"] [data-baseweb="tag"] *{color:#142235!important;-webkit-text-fill-color:#142235!important}
[data-baseweb="popover"],[data-baseweb="popover"] [role="listbox"]{background:#fff!important}
[data-baseweb="popover"] [role="option"],[data-baseweb="popover"] [role="option"] *{color:#142235!important;-webkit-text-fill-color:#142235!important;opacity:1!important}
[data-baseweb="popover"] [role="option"]:hover{background:#d9f7f0!important}
.hero{border:1px solid #294963;border-radius:24px;padding:30px 32px;background:linear-gradient(115deg,#10243a,#0b1a2b);box-shadow:0 18px 50px #0003}
.hero h1{margin:0;font-size:clamp(2rem,4vw,3.2rem);font-weight:800}.hero p{color:#c0d0e0;max-width:780px}
.eyebrow{color:var(--teal);text-transform:uppercase;letter-spacing:2px;font-size:.72rem;font-weight:800;margin-bottom:.45rem}
.pill{display:inline-block;border:1px solid #2e5a6b;color:var(--teal);background:#45e0c111;border-radius:100px;padding:6px 11px;font-size:.73rem;font-weight:800;margin-bottom:14px}
.metric{background:linear-gradient(150deg,#10243a,#0b1929);border:1px solid var(--line);border-radius:16px;padding:17px;min-height:100px}
.metric-label{color:var(--muted);font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:1px}.metric-value{color:#f1f7ff;font-size:1.8rem;font-weight:800;margin-top:5px}.metric-sub{color:var(--muted);font-size:.75rem}
.section-head{margin:1.3rem 0 .7rem}.section-head h3{font-size:1.15rem;margin:0}.section-head p{color:var(--muted);font-size:.83rem;margin:.25rem 0 0}
.panel{background:#0d1b2cee;border:1px solid var(--line);border-radius:18px;padding:18px 20px;margin:7px 0 12px}
.node{border:1px solid #294761;background:linear-gradient(145deg,#11263b,#0d1b2c);padding:15px;border-radius:14px;margin:7px 0}
.node-kicker{color:#b0c4d8;font-size:.7rem;letter-spacing:1.4px;text-transform:uppercase;font-weight:800}.node-title{color:#edf6ff;font-weight:800;margin-top:5px}.node-detail{color:#c0d0e0;font-size:.84rem;margin-top:4px}
.bad{border-left:4px solid #ff6b7c}.good{border-left:4px solid var(--teal)}.blue{border-left:4px solid var(--blue)}
.status{padding:12px 15px;border-radius:12px;margin:8px 0;border:1px solid #2a5265;background:#45e0c111;color:#eaf4ff}
.caption{color:var(--muted);font-size:.78rem}.footer{color:#9bb0c8;border-top:1px solid var(--line);padding-top:16px;margin-top:30px;font-size:.75rem}
div[data-testid="stButton"]>button{border-radius:12px;border:1px solid #4ce2c4;color:#041720;background:linear-gradient(100deg,#45e0c1,#73caff);font-weight:800;min-height:42px}
div[data-testid="stDownloadButton"]>button{border-radius:10px;border:1px solid #31536e;background:#10243a;color:#eaf4ff}
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:12px;overflow:hidden}
</style>
""", unsafe_allow_html=True)

PERIODS = ["09:30–10:30", "10:30–11:30", "11:30–12:30", "13:30–14:30", "14:30–15:30", "15:30–16:30"]
SECTIONS = ["CSD-A", "CSD-B", "CSD-C"]
ROOMS = ["Room 101", "Room 102", "Room 103", "Room 104"]
TEACHERS = ["Teacher A", "Teacher B", "Teacher C", "Teacher D", "Teacher E", "Teacher F"]
SUBJECTS = {
    "CSD-A": ["PPS", "BEE", "AEP", "IT Workshop", "ED&CAD", "PPS Lab"],
    "CSD-B": ["BEE", "AEP", "PPS", "ED&CAD", "IT Workshop", "IT Workshop Lab"],
    "CSD-C": ["AEP", "PPS", "BEE", "IT Workshop", "ED&CAD", "ED&CAD Lab"],
}
TEACHER_PLAN = [
    ["Teacher A", "Teacher B", "Teacher C"], ["Teacher D", "Teacher E", "Teacher F"],
    ["Teacher A", "Teacher B", "Teacher C"], ["Teacher D", "Teacher E", "Teacher F"],
    ["Teacher A", "Teacher B", "Teacher C"], ["Teacher D", "Teacher E", "Teacher F"],
]
base_rows = []
for i, period in enumerate(PERIODS):
    for j, sec in enumerate(SECTIONS):
        base_rows.append({"Time": period, "Section": sec, "Subject": SUBJECTS[sec][i],
                          "Room": ROOMS[j], "Teacher": TEACHER_PLAN[i][j]})
BASE = pd.DataFrame(base_rows)

if "current_timetable" not in st.session_state: st.session_state.current_timetable = BASE.copy()
if "history" not in st.session_state: st.session_state.history = []
if "result" not in st.session_state: st.session_state.result = None
if "notice" not in st.session_state: st.session_state.notice = ""

def get_row(df, sec, slot):
    return df[(df["Section"] == sec) & (df["Time"] == slot)].iloc[0]

def room_options(df, slot, unavailable, sec):
    same = df[df.Time == slot]
    occupied = set(same[same.Section != sec].Room)
    return [r for r in ROOMS if r not in unavailable and r not in occupied]

def teacher_options(df, slot, unavailable, sec):
    same = df[df.Time == slot]
    busy = set(same[same.Section != sec].Teacher)
    return [t for t in TEACHERS if t != unavailable and t not in busy]

def metric(label, value, sub):
    st.markdown(f'<div class="metric"><div class="metric-label">{html.escape(label)}</div><div class="metric-value">{html.escape(value)}</div><div class="metric-sub">{html.escape(sub)}</div></div>', unsafe_allow_html=True)

def node(kicker, title, detail, tone="blue"):
    st.markdown(f'<div class="node {tone}"><div class="node-kicker">{html.escape(kicker)}</div><div class="node-title">{html.escape(title)}</div><div class="node-detail">{html.escape(detail)}</div></div>', unsafe_allow_html=True)

st.markdown("""
<div class="hero">
 <div class="pill">● SCHEDULING RESILIENCE · DEMO PROTOTYPE</div>
 <h1>The Ripple <span style="color:#45e0c1">🌊</span></h1>
 <p>One disruption. Many possible consequences. Explore timetable impact, compare alternatives, and approve a practical change before a small issue becomes a bigger scheduling problem.</p>
 <div style="margin-top:16px;color:#a8bfd5;font-size:.76rem">CSD DEPARTMENT &nbsp; / &nbsp; 3 SECTIONS &nbsp; / &nbsp; SAMPLE DATA</div>
</div>
""", unsafe_allow_html=True)

cols = st.columns(4)
for col, args in zip(cols, [
    ("Sections", "03", "CSD-A · CSD-B · CSD-C"),
    ("Teaching slots", "06", "Across the college day"),
    ("College hours", "7 hrs", "09:30 AM – 04:30 PM"),
    ("Lunch break", "1 hr", "12:30 PM – 01:30 PM"),
]):
    with col: metric(*args)

with st.sidebar:
    st.markdown('<div class="eyebrow">CONTROL CENTRE</div>', unsafe_allow_html=True)
    st.markdown("## Configure a disruption")
    st.caption("Choose a scenario using the sample timetable.")
    event = st.radio("What changed?", ["A room becomes unavailable", "A teacher becomes unavailable"], key="event_type")
    section = st.selectbox("Affected section", SECTIONS, key="affected_section")
    slot = st.selectbox("Time slot", PERIODS, key="time_slot")
    scheduled = get_row(st.session_state.current_timetable, section, slot)
    unavailable_rooms = []
    unavailable_teacher = None
    if event == "A room becomes unavailable":
        unavailable_rooms = st.multiselect("Mark rooms unavailable", ROOMS, default=[scheduled.Room], key="unavailable_rooms")
    else:
        unavailable_teacher = st.selectbox("Unavailable teacher", TEACHERS, index=TEACHERS.index(scheduled.Teacher), key="unavailable_teacher")
    run = st.button("Generate Ripple Map →", use_container_width=True)
    reset = st.button("Reset demo", use_container_width=True)
    if reset:
        st.session_state.current_timetable = BASE.copy()
        st.session_state.history = []
        st.session_state.result = None
        st.session_state.notice = "Demo timetable reset."
        for key in ["event_type", "affected_section", "time_slot", "unavailable_rooms", "unavailable_teacher"]:
            st.session_state.pop(key, None)
        st.rerun()
    if st.session_state.history and st.button("↶ Undo last approved change", use_container_width=True):
        st.session_state.current_timetable = st.session_state.history.pop()
        st.session_state.result = None
        st.session_state.notice = "Last approved change undone."
        st.rerun()
    st.markdown('<p class="caption">Demo uses sample data only. Changes affect this running app.</p>', unsafe_allow_html=True)

if st.session_state.notice:
    st.info(st.session_state.notice)
    st.session_state.notice = ""

df = st.session_state.current_timetable.copy()
st.markdown('<div class="section-head"><h3>01 / Timetable overview</h3><p>Approved demo changes appear here.</p></div>', unsafe_allow_html=True)
view = st.selectbox("Show timetable for", ["All sections"] + SECTIONS)
shown = df if view == "All sections" else df[df.Section == view]
st.dataframe(shown, use_container_width=True, hide_index=True)
c1, c2 = st.columns([1, 1])
with c1:
    st.download_button("⬇ Download timetable CSV", df.to_csv(index=False).encode("utf-8"),
                       "the_ripple_demo_timetable.csv", "text/csv", use_container_width=True)
with c2:
    st.markdown('<p class="caption">Export the current timetable, including approved demo changes.</p>', unsafe_allow_html=True)

st.markdown('<div class="section-head"><h3>02 / Ripple analysis</h3><p>Find conflicts, compare alternatives, and approve a change.</p></div>', unsafe_allow_html=True)
if run:
    st.session_state.result = {
        "event": event, "section": section, "slot": slot,
        "rooms": list(unavailable_rooms), "teacher": unavailable_teacher,
        "scheduled": get_row(df, section, slot).to_dict()
    }
result = st.session_state.result

if result is None:
    st.markdown('<div class="panel"><div class="eyebrow">READY TO ANALYSE</div><h3>Choose a disruption</h3><p class="caption">Use the Control Centre, choose a section and time, then click Generate Ripple Map.</p></div>', unsafe_allow_html=True)
else:
    ev, sec, period, original = result["event"], result["section"], result["slot"], result["scheduled"]
    left, right = st.columns([1.05, 1])
    with left:
        st.markdown('<div class="eyebrow">RIPPLE PATH</div>', unsafe_allow_html=True)
        node("01 · TRIGGER", "Disruption detected", f"{ev} · {period}", "bad")
        if ev == "A room becomes unavailable":
            bad_rooms = result["rooms"]
            if original["Room"] not in bad_rooms:
                node("02 · DIRECT IMPACT", "No direct room impact", f'{original["Room"]} is not marked unavailable for {sec}.', "good")
            else:
                node("02 · DIRECT IMPACT", f"{sec} needs a replacement room", f'{original["Subject"]} · originally {original["Room"]}', "bad")
                options = room_options(st.session_state.current_timetable, period, bad_rooms, sec)
                node("03 · AVAILABILITY CHECK", f"{len(options)} room(s) available", "Rooms assigned to other sections are excluded.", "blue")
                if options:
                    chosen = st.radio("Choose a replacement room", options, key=f"room_{sec}_{period}", horizontal=True)
                    for i, room in enumerate(options):
                        st.markdown(f'<div class="status"><b>{html.escape(room)}</b><br><span class="caption">{"Suggested option" if i == 0 else "Alternative option"} · free in this sample time slot</span></div>', unsafe_allow_html=True)
                    if st.button("✓ Approve room change", key=f"approve_room_{sec}_{period}", use_container_width=True):
                        latest = st.session_state.current_timetable
                        if chosen in room_options(latest, period, bad_rooms, sec):
                            idx = latest.index[(latest.Section == sec) & (latest.Time == period)][0]
                            st.session_state.history.append(latest.copy())
                            st.session_state.current_timetable.loc[idx, "Room"] = chosen
                            st.session_state.result = None
                            st.session_state.notice = f"Approved: {sec} moved to {chosen} at {period}."
                            st.rerun()
                        else: st.error("That room is no longer available. Generate the map again.")
                else:
                    node("04 · NO VALID ROOM", "No replacement room found", "Try another time slot or mark fewer rooms unavailable.", "bad")
        else:
            bad_teacher = result["teacher"]
            if original["Teacher"] != bad_teacher:
                node("02 · DIRECT IMPACT", "No direct teacher conflict", f'{sec} has {original["Teacher"]}, not {bad_teacher}, in this slot.', "good")
            else:
                node("02 · DIRECT IMPACT", f"{sec} needs a teacher replacement", f'{original["Subject"]} · {bad_teacher} is unavailable.', "bad")
                options = teacher_options(st.session_state.current_timetable, period, bad_teacher, sec)
                node("03 · AVAILABILITY CHECK", f"{len(options)} free demo teacher(s)", "Teachers assigned to other sections are excluded. Subject expertise is not modelled.", "blue")
                if options:
                    chosen = st.radio("Choose a replacement teacher", options, key=f"teacher_{sec}_{period}", horizontal=True)
                    for i, teacher in enumerate(options):
                        st.markdown(f'<div class="status"><b>{html.escape(teacher)}</b><br><span class="caption">{"Suggested option" if i == 0 else "Alternative option"} · free in this sample slot</span></div>', unsafe_allow_html=True)
                    if st.button("✓ Approve teacher change", key=f"approve_teacher_{sec}_{period}", use_container_width=True):
                        latest = st.session_state.current_timetable
                        if chosen in teacher_options(latest, period, bad_teacher, sec):
                            idx = latest.index[(latest.Section == sec) & (latest.Time == period)][0]
                            st.session_state.history.append(latest.copy())
                            st.session_state.current_timetable.loc[idx, "Teacher"] = chosen
                            st.session_state.result = None
                            st.session_state.notice = f"Approved: {sec} assigned to {chosen} at {period}. Verify qualifications before real use."
                            st.rerun()
                        else: st.error("That teacher is no longer available. Generate the map again.")
                else:
                    node("04 · NO VALID TEACHER", "No free demo teacher found", "All other listed teachers are assigned in this time slot.", "bad")
    with right:
        st.markdown('<div class="eyebrow">DECISION SUMMARY</div>', unsafe_allow_html=True)
        current = get_row(st.session_state.current_timetable, sec, period)
        st.markdown(f"""
        <div class="panel">
        <p><b>Affected section:</b> {html.escape(sec)}</p>
        <p><b>Time slot:</b> {html.escape(period)}</p>
        <p><b>Subject:</b> {html.escape(original["Subject"])}</p>
        <p><b>Current room:</b> {html.escape(current["Room"])}</p>
        <p><b>Current teacher:</b> {html.escape(current["Teacher"])}</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="panel"><div class="eyebrow">PROTOTYPE LIMITS</div><p class="caption">This demo checks immediate room or teacher clashes. It does not yet model live college data, room capacity, teacher qualifications, or cascading changes across multiple periods.</p></div>', unsafe_allow_html=True)

st.markdown('<div class="section-head"><h3>03 / How The Ripple works</h3><p>A simple explanation for your presentation.</p></div>', unsafe_allow_html=True)
a, b, c = st.columns(3)
with a: node("STEP 1", "Detect", "Choose a room or teacher disruption, section, and time.")
with b: node("STEP 2", "Compare", "Check available alternatives against sample data.")
with c: node("STEP 3", "Approve", "Apply a change, view the updated timetable, or undo it.")
with st.expander("What is included — and what is not?"):
    st.markdown("""
**Included:** three sample sections, six teaching slots, room and teacher disruption scenarios, immediate conflict checks, alternatives, approval, undo, and CSV export.

**Not included yet:** live college timetable integration, database, room capacity/equipment checks, teacher qualification rules, or automatic multi-period cascading rescheduling.
""")
st.markdown('<div class="footer"><b style="color:#45e0c1">THE RIPPLE</b> · Timetable Impact Analyzer · Student hackathon prototype · Sample data only</div>', unsafe_allow_html=True)