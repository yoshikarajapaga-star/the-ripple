import html
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="The Ripple | Timetable Impact Analyzer",
    page_icon="🌊",
    layout="wide"
)

# ----------------------- DESIGN -----------------------

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
[data-testid="stSidebar"] [data-baseweb="select"]>div{background:#fff!important;border:1px solid #b7c8d8!important}
[data-testid="stSidebar"] [data-baseweb="select"] input,
[data-testid="stSidebar"] [data-baseweb="select"] [role="combobox"],
[data-testid="stSidebar"] [data-baseweb="select"] [role="combobox"] *,
[data-testid="stSidebar"] [data-baseweb="select"] span{color:#142235!important;-webkit-text-fill-color:#142235!important;opacity:1!important}
[data-testid="stSidebar"] [data-baseweb="select"] svg{fill:#142235!important}
[data-baseweb="popover"],[data-baseweb="popover"] [role="listbox"]{background:#fff!important}
[data-baseweb="popover"] [role="option"],[data-baseweb="popover"] [role="option"] *{color:#142235!important;-webkit-text-fill-color:#142235!important}
[data-baseweb="popover"] [role="option"]:hover{background:#d9f7f0!important}
.hero{border:1px solid #294963;border-radius:24px;padding:30px 32px;background:linear-gradient(115deg,#10243a,#0b1a2b);box-shadow:0 18px 50px #0003}
.hero h1{margin:0;font-size:clamp(2rem,4vw,3.2rem);font-weight:800}
.hero p{color:#c0d0e0;max-width:780px}
.eyebrow{color:var(--teal);text-transform:uppercase;letter-spacing:2px;font-size:.72rem;font-weight:800;margin-bottom:.45rem}
.pill{display:inline-block;border:1px solid #2e5a6b;color:var(--teal);background:#45e0c111;border-radius:100px;padding:6px 11px;font-size:.73rem;font-weight:800;margin-bottom:14px}
.metric{background:linear-gradient(150deg,#10243a,#0b1929);border:1px solid var(--line);border-radius:16px;padding:17px;min-height:100px}
.metric-label{color:var(--muted);font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:1px}
.metric-value{color:#f1f7ff;font-size:1.8rem;font-weight:800;margin-top:5px}
.metric-sub{color:var(--muted);font-size:.75rem}
.section-head{margin:1.3rem 0 .7rem}
.section-head h3{font-size:1.15rem;margin:0}
.section-head p{color:var(--muted);font-size:.83rem;margin:.25rem 0 0}
.panel{background:#0d1b2cee;border:1px solid var(--line);border-radius:18px;padding:18px 20px;margin:7px 0 12px}
.node{border:1px solid #294761;background:linear-gradient(145deg,#11263b,#0d1b2c);padding:15px;border-radius:14px;margin:7px 0}
.node-kicker{color:#b0c4d8;font-size:.7rem;letter-spacing:1.4px;text-transform:uppercase;font-weight:800}
.node-title{color:#edf6ff;font-weight:800;margin-top:5px}
.node-detail{color:#c0d0e0;font-size:.84rem;margin-top:4px}
.bad{border-left:4px solid #ff6b7c}
.good{border-left:4px solid var(--teal)}
.blue{border-left:4px solid var(--blue)}
.status{padding:12px 15px;border-radius:12px;margin:8px 0;border:1px solid #2a5265;background:#45e0c111;color:#eaf4ff}
.caption{color:var(--muted);font-size:.78rem}
.footer{color:#9bb0c8;border-top:1px solid var(--line);padding-top:16px;margin-top:30px;font-size:.75rem}
div[data-testid="stButton"]>button{border-radius:12px;border:1px solid #4ce2c4;color:#041720;background:linear-gradient(100deg,#45e0c1,#73caff);font-weight:800;min-height:42px}
div[data-testid="stDownloadButton"]>button{border-radius:10px;border:1px solid #31536e;background:#10243a;color:#eaf4ff}
</style>
""", unsafe_allow_html=True)

# ---------------- ACTUAL TIMETABLE DATA ----------------

DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT"]

PERIODS = [
    "09:30–10:30",
    "10:30–11:30",
    "11:30–12:20",
    "13:20–14:30",
    "14:30–15:30",
    "15:30–16:30",
]

SECTIONS = ["CSD-A", "CSD-B", "CSD-C"]

ROOMS = {
    "CSD-A": "1101",
    "CSD-B": "1108",
    "CSD-C": "1117",
}

# Subjects in period order: periods 1, 2, 3, 4, 5, 6.
# These schedules are transcribed from the supplied college timetable.

SCHEDULES = {
    "CSD-A": {
        "MON": ["M&C", "ED&CAD", "ED&CAD", "PPS", "APT", "APT"],
        "TUE": ["PPS", "PPS", "M&C", "BEE", "AEP LAB", "AEP LAB"],
        "WED": ["PPS LAB", "PPS LAB", "PPS LAB", "AEP", "BEE", "M&C"],
        "THU": ["AEP", "PPS", "PPS", "M&C", "BEE LAB", "BEE LAB"],
        "FRI": ["M&C", "PPS", "LYS", "BEE", "ED&CAD LAB", "ED&CAD LAB"],
        "SAT": ["BEE", "ITWS", "ITWS", "AEP", "Project", "Project"],
    },
    "CSD-B": {
        "MON": ["PPS", "AEP LAB", "AEP LAB", "M&C", "APT", "APT"],
        "TUE": ["M&C", "ED&CAD", "ED&CAD", "PPS", "BEE LAB", "BEE LAB"],
        "WED": ["PPS", "PPS", "M&C", "BEE", "ED&CAD LAB", "ED&CAD LAB"],
        "THU": ["PPS LAB", "PPS LAB", "PPS LAB", "AEP", "BEE", "M&C"],
        "FRI": ["AEP", "BEE", "M&C", "PPS", "ITWS", "ITWS"],
        "SAT": ["PPS", "BEE", "LYS", "AEP", "Project", "Project"],
    },
    "CSD-C": {
        "MON": ["PPS LAB", "PPS LAB", "PPS LAB", "BEE", "AEP", "M&C"],
        "TUE": ["M&C", "AEP", "BEE", "PPS", "ED&CAD LAB", "ED&CAD LAB"],
        "WED": ["PPS", "APT", "APT", "M&C", "BEE LAB", "BEE LAB"],
        "THU": ["BEE", "ITWS", "ITWS", "PPS", "PPS", "M&C"],
        "FRI": ["BEE", "PPS", "PPS", "AEP", "ED&CAD", "ED&CAD"],
        "SAT": ["LYS", "AEP LAB", "AEP LAB", "M&C", "Project", "Project"],
    },
}

# Primary faculty assigned from the faculty lists in the screenshots.
# Lab sessions use a listed faculty member as the primary instructor.
FACULTY = {
    "CSD-A": {
        "M&C": "Dr. Jayanti Sravani",
        "AEP": "Mrs. Rajani Rai",
        "PPS": "Mrs. T. Swathi",
        "BEE": "Mr. Harikrath Budida",
        "ED&CAD": "Mr. C. Venkatesh",
        "AEP LAB": "Mrs. Rajani Rai",
        "PPS LAB": "Mrs. T. Swathi",
        "BEE LAB": "Mr. Harikrath Budida",
        "ED&CAD LAB": "Mr. C. Venkatesh",
        "ITWS": "Mrs. Vagolu Vanaja",
        "Project": "Mrs. T. Swathi",
        "APT": "Mrs. Sumedha S. Gawande",
        "LYS": "Library / Yoga / Sports",
    },
    "CSD-B": {
        "M&C": "Dr. Jayanti Sravani",
        "AEP": "Mrs. K. Priyanka",
        "PPS": "Mrs. K. Sukeerthi",
        "BEE": "Dr. S. Mani Kuchibhatla",
        "ED&CAD": "Mr. C. Venkatesh",
        "AEP LAB": "Mrs. K. Priyanka",
        "PPS LAB": "Mrs. K. Sukeerthi",
        "BEE LAB": "Dr. S. Mani Kuchibhatla",
        "ED&CAD LAB": "Mr. C. Venkatesh",
        "ITWS": "Mrs. Vagolu Vanaja",
        "Project": "Mrs. K. Sukeerthi",
        "APT": "Mrs. Sumedha S. Gawande",
        "LYS": "Library / Yoga / Sports",
    },
    "CSD-C": {
        "M&C": "Mrs. P. Swapna",
        "AEP": "Dr. V. Venkatesh",
        "PPS": "Mrs. P. Niharika",
        "BEE": "Dr. P. Srinmanarayana",
        "ED&CAD": "Mr. C. H. Raju",
        "AEP LAB": "Dr. V. Venkatesh",
        "PPS LAB": "Mrs. P. Niharika",
        "BEE LAB": "Dr. P. Srinmanarayana",
        "ED&CAD LAB": "Mr. C. H. Raju",
        "ITWS": "Mrs. Vagolu Vanaja",
        "Project": "Mrs. P. Niharika",
        "APT": "Mr. M. Hari Krishna",
        "LYS": "Library / Yoga / Sports",
    },
}

rows = []
for sec in SECTIONS:
    for day in DAYS:
        for i, period in enumerate(PERIODS):
            subject = SCHEDULES[sec][day][i]
            rows.append({
                "Day": day,
                "Time": period,
                "Period": i + 1,
                "Section": sec,
                "Subject": subject,
                "Room": ROOMS[sec],
                "Teacher": FACULTY[sec].get(subject, "Not specified"),
            })

BASE = pd.DataFrame(rows)

# ----------------------- HELPERS -----------------------

def get_row(df, sec, day, slot):
    match = df[
        (df["Section"] == sec)
        & (df["Day"] == day)
        & (df["Time"] == slot)
    ]
    return match.iloc[0]

def room_options(df, day, slot, sec, unavailable):
    same = df[(df["Day"] == day) & (df["Time"] == slot)]
    occupied = set(same[same["Section"] != sec]["Room"])
    return [
        room for room in sorted(set(ROOMS.values()))
        if room not in unavailable and room not in occupied
    ]

def teacher_options(df, day, slot, sec, unavailable):
    same = df[(df["Day"] == day) & (df["Time"] == slot)]
    busy = set(same[same["Section"] != sec]["Teacher"])
    all_teachers = sorted({
        t for t in df["Teacher"]
        if t not in ("Not specified", "Library / Yoga / Sports")
    })
    return [
        t for t in all_teachers
        if t != unavailable and t not in busy
    ]

def metric(label, value, sub):
    st.markdown(
        f'<div class="metric"><div class="metric-label">{html.escape(label)}</div>'
        f'<div class="metric-value">{html.escape(value)}</div>'
        f'<div class="metric-sub">{html.escape(sub)}</div></div>',
        unsafe_allow_html=True
    )

def node(kicker, title, detail, tone="blue"):
    st.markdown(
        f'<div class="node {tone}"><div class="node-kicker">{html.escape(kicker)}</div>'
        f'<div class="node-title">{html.escape(title)}</div>'
        f'<div class="node-detail">{html.escape(detail)}</div></div>',
        unsafe_allow_html=True
    )

# ----------------------- SESSION STATE -----------------------

if "current_timetable" not in st.session_state:
    st.session_state.current_timetable = BASE.copy()

if "history" not in st.session_state:
    st.session_state.history = []

if "result" not in st.session_state:
    st.session_state.result = None

if "notice" not in st.session_state:
    st.session_state.notice = ""

# ----------------------- HERO -----------------------

st.markdown("""
<div class="hero">
 <div class="pill">● SCHEDULING RESILIENCE · COLLEGE DATA</div>
 <h1>The Ripple <span style="color:#45e0c1">🌊</span></h1>
 <p>One disruption. Many possible consequences. Analyse timetable
 impact, compare alternatives, and approve a practical change.</p>
 <div style="margin-top:16px;color:#a8bfd5;font-size:.76rem">
 ACE ENGINEERING COLLEGE / CSD / SECTIONS A, B & C
 </div>
</div>
""", unsafe_allow_html=True)

cols = st.columns(4)
for col, args in zip(cols, [
    ("Sections", "03", "CSD-A · CSD-B · CSD-C"),
    ("Teaching slots", "06", "Per day · Monday–Saturday"),
    ("College hours", "7 hrs", "09:30 AM – 04:30 PM"),
    ("Lunch break", "1 hr", "12:20 PM – 01:20 PM"),
]):
    with col:
        metric(*args)

# ----------------------- SIDEBAR -----------------------

with st.sidebar:
    st.markdown('<div class="eyebrow">CONTROL CENTRE</div>',
                unsafe_allow_html=True)
    st.markdown("## Configure a disruption")
    st.caption("Uses the supplied CSD-A, CSD-B and CSD-C timetables.")

    event = st.radio(
        "What changed?",
        ["A room becomes unavailable", "A teacher becomes unavailable"],
        key="event_type"
    )

    section = st.selectbox("Affected section", SECTIONS, key="affected_section")
    day = st.selectbox("Day", DAYS, key="affected_day")
    slot = st.selectbox("Time slot", PERIODS, key="time_slot")

    current_df = st.session_state.current_timetable
    scheduled = get_row(current_df, section, day, slot)

    unavailable_rooms = []
    unavailable_teacher = None

    if event == "A room becomes unavailable":
        unavailable_rooms = st.multiselect(
            "Mark rooms unavailable",
            sorted(set(ROOMS.values())),
            default=[scheduled["Room"]],
            key="unavailable_rooms"
        )
    else:
        available_teacher_names = sorted(set(current_df["Teacher"]))
        teacher_index = (
            available_teacher_names.index(scheduled["Teacher"])
            if scheduled["Teacher"] in available_teacher_names else 0
        )
        unavailable_teacher = st.selectbox(
            "Unavailable teacher",
            available_teacher_names,
            index=teacher_index,
            key="unavailable_teacher"
        )

    run = st.button("Generate Ripple Map →", use_container_width=True)
    reset = st.button("Reset demo", use_container_width=True)

    if reset:
        st.session_state.current_timetable = BASE.copy()
        st.session_state.history = []
        st.session_state.result = None
        st.session_state.notice = "Timetables reset to the original college schedules."
        for key in [
            "event_type", "affected_section", "affected_day",
            "time_slot", "unavailable_rooms", "unavailable_teacher"
        ]:
            st.session_state.pop(key, None)
        st.rerun()

    if st.session_state.history:
        if st.button("↶ Undo last approved change", use_container_width=True):
            st.session_state.current_timetable = st.session_state.history.pop()
            st.session_state.result = None
            st.session_state.notice = "Last approved change undone."
            st.rerun()

    st.markdown(
        '<p class="caption">Based on supplied timetable images. '
        'Confirm faculty and room availability before real-world use.</p>',
        unsafe_allow_html=True
    )

if st.session_state.notice:
    st.info(st.session_state.notice)
    st.session_state.notice = ""

# ----------------------- TIMETABLE -----------------------

df = st.session_state.current_timetable.copy()

st.markdown(
    '<div class="section-head"><h3>01 / Actual timetable overview</h3>'
    '<p>Browse the college schedule by day and section.</p></div>',
    unsafe_allow_html=True
)

v1, v2 = st.columns(2)
with v1:
    view_day = st.selectbox("Show day", ["All days"] + DAYS, key="view_day")
with v2:
    view_section = st.selectbox(
        "Show section", ["All sections"] + SECTIONS, key="view_section"
    )

shown = df.copy()
if view_day != "All days":
    shown = shown[shown["Day"] == view_day]
if view_section != "All sections":
    shown = shown[shown["Section"] == view_section]

st.dataframe(shown, use_container_width=True, hide_index=True)

c1, c2 = st.columns([1, 1])
with c1:
    st.download_button(
        "⬇ Download timetable CSV",
        df.to_csv(index=False).encode("utf-8"),
        "the_ripple_ace_csd_timetables.csv",
        "text/csv",
        use_container_width=True
    )
with c2:
    st.markdown(
        '<p class="caption">Export all three sections, all six days, '
        'faculty assignments and approved changes.</p>',
        unsafe_allow_html=True
    )

# ----------------------- RIPPLE ANALYSIS -----------------------

st.markdown(
    '<div class="section-head"><h3>02 / Ripple analysis</h3>'
    '<p>Identify immediate conflicts, compare alternatives and approve a change.</p></div>',
    unsafe_allow_html=True
)

if run:
    st.session_state.result = {
        "event": event,
        "section": section,
        "day": day,
        "slot": slot,
        "rooms": list(unavailable_rooms),
        "teacher": unavailable_teacher,
        "scheduled": get_row(df, section, day, slot).to_dict()
    }

result = st.session_state.result

if result is None:
    st.markdown(
        '<div class="panel"><div class="eyebrow">READY TO ANALYSE</div>'
        '<h3>Choose a disruption</h3>'
        '<p class="caption">Choose the day, section and time in the Control Centre, '
        'then generate the Ripple Map.</p></div>',
        unsafe_allow_html=True
    )

else:
    ev = result["event"]
    sec = result["section"]
    day = result["day"]
    period = result["slot"]
    original = result["scheduled"]

    left, right = st.columns([1.05, 1])

    with left:
        st.markdown('<div class="eyebrow">RIPPLE PATH</div>',
                    unsafe_allow_html=True)

        node(
            "01 · TRIGGER",
            "Disruption detected",
            f'{day} · {period} · {ev}',
            "bad"
        )

        if ev == "A room becomes unavailable":
            bad_rooms = result["rooms"]

            if original["Room"] not in bad_rooms:
                node(
                    "02 · DIRECT IMPACT",
                    "No direct room impact",
                    f'Room {original["Room"]} is not marked unavailable.',
                    "good"
                )
            else:
                node(
                    "02 · DIRECT IMPACT",
                    f"{sec} needs a replacement room",
                    f'{original["Subject"]} · original room {original["Room"]}',
                    "bad"
                )

                options = room_options(
                    st.session_state.current_timetable,
                    day, period, sec, bad_rooms
                )

                node(
                    "03 · AVAILABILITY CHECK",
                    f"{len(options)} room(s) available",
                    "Rooms assigned to other sections during this time are excluded.",
                    "blue" if options else "bad"
                )

                if options:
                    chosen = st.radio(
                        "Choose a replacement room",
                        options,
                        key=f"room_{sec}_{day}_{period}",
                        horizontal=True
                    )

                    for i, room in enumerate(options):
                        st.markdown(
                            f'<div class="status"><b>Room {html.escape(room)}</b><br>'
                            f'<span class="caption">'
                            f'{"Suggested option" if i == 0 else "Alternative option"}'
                            ' · no other section is assigned this room in this slot'
                            '</span></div>',
                            unsafe_allow_html=True
                        )

                    if st.button(
                        "✓ Approve room change",
                        key=f"approve_room_{sec}_{day}_{period}",
                        use_container_width=True
                    ):
                        latest = st.session_state.current_timetable
                        valid = room_options(
                            latest, day, period, sec, bad_rooms
                        )

                        if chosen in valid:
                            idx = latest.index[
                                (latest["Section"] == sec)
                                & (latest["Day"] == day)
                                & (latest["Time"] == period)
                            ][0]

                            st.session_state.history.append(latest.copy())
                            st.session_state.current_timetable.loc[idx, "Room"] = chosen
                            st.session_state.result = None
                            st.session_state.notice = (
                                f"Approved: {sec} moved to Room {chosen} "
                                f"on {day}, {period}."
                            )
                            st.rerun()
                        else:
                            st.error("Room availability changed. Generate the map again.")

                else:
                    node(
                        "04 · NO VALID ROOM",
                        "No replacement room found",
                        "Try another time slot or mark fewer rooms unavailable.",
                        "bad"
                    )

        else:
            bad_teacher = result["teacher"]

            if original["Teacher"] != bad_teacher:
                node(
                    "02 · DIRECT IMPACT",
                    "No direct teacher conflict",
                    f'{sec} has {original["Teacher"]}, not {bad_teacher}, in this slot.',
                    "good"
                )
            else:
                node(
                    "02 · DIRECT IMPACT",
                    f"{sec} needs a teacher replacement",
                    f'{original["Subject"]} · {bad_teacher} is unavailable.',
                    "bad"
                )

                options = teacher_options(
                    st.session_state.current_timetable,
                    day, period, sec, bad_teacher
                )

                node(
                    "03 · AVAILABILITY CHECK",
                    f"{len(options)} free listed faculty member(s)",
                    "Faculty assigned to other sections in this slot are excluded. "
                    "Subject qualifications must be verified.",
                    "blue" if options else "bad"
                )

                if options:
                    chosen = st.radio(
                        "Choose replacement faculty",
                        options,
                        key=f"teacher_{sec}_{day}_{period}",
                    )

                    for i, teacher in enumerate(options):
                        st.markdown(
                            f'<div class="status"><b>{html.escape(teacher)}</b><br>'
                            f'<span class="caption">'
                            f'{"Suggested option" if i == 0 else "Alternative option"}'
                            ' · listed as unassigned in this sample slot'
                            '</span></div>',
                            unsafe_allow_html=True
                        )

                    if st.button(
                        "✓ Approve teacher change",
                        key=f"approve_teacher_{sec}_{day}_{period}",
                        use_container_width=True
                    ):
                        latest = st.session_state.current_timetable
                        valid = teacher_options(
                            latest, day, period, sec, bad_teacher
                        )

                        if chosen in valid:
                            idx = latest.index[
                                (latest["Section"] == sec)
                                & (latest["Day"] == day)
                                & (latest["Time"] == period)
                            ][0]

                            st.session_state.history.append(latest.copy())
                            st.session_state.current_timetable.loc[idx, "Teacher"] = chosen
                            st.session_state.result = None
                            st.session_state.notice = (
                                f"Approved demo change: {sec} assigned to "
                                f"{chosen} on {day}, {period}. "
                                "Verify subject qualifications before real use."
                            )
                            st.rerun()
                        else:
                            st.error("Faculty availability changed. Generate the map again.")

                else:
                    node(
                        "04 · NO VALID FACULTY",
                        "No free listed faculty found",
                        "Try another day or time slot.",
                        "bad"
                    )

    with right:
        st.markdown('<div class="eyebrow">DECISION SUMMARY</div>',
                    unsafe_allow_html=True)

        current = get_row(
            st.session_state.current_timetable, sec, day, period
        )

        st.markdown(
            f'<div class="panel">'
            f'<p><b>Section:</b> {html.escape(sec)}</p>'
            f'<p><b>Day:</b> {html.escape(day)}</p>'
            f'<p><b>Period:</b> {html.escape(period)}</p>'
            f'<p><b>Subject:</b> {html.escape(original["Subject"])}</p>'
            f'<p><b>Current room:</b> {html.escape(str(current["Room"]))}</p>'
            f'<p><b>Current faculty:</b> {html.escape(current["Teacher"])}</p>'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown("""
        <div class="panel">
        <div class="eyebrow">ANALYSIS SCOPE</div>
        <p class="caption">This prototype checks immediate room or faculty
        conflicts for the selected day and period. It does not yet model room
        capacity, faculty qualifications, live availability or automatic
        cascading rescheduling.</p>
        </div>
        """, unsafe_allow_html=True)

# ----------------------- HOW IT WORKS -----------------------

st.markdown(
    '<div class="section-head"><h3>03 / How The Ripple works</h3>'
    '<p>Understand the consequences before approving a change.</p></div>',
    unsafe_allow_html=True
)

a, b, c = st.columns(3)
with a:
    node("STEP 1", "Detect", "Select a disruption, section, day and period.")
with b:
    node("STEP 2", "Compare", "Check available rooms or unassigned listed faculty.")
with c:
    node("STEP 3", "Approve", "Apply a demo change, inspect the timetable or undo it.")

with st.expander("What is included — and what is not?"):
    st.markdown("""
**Included**
- Three actual CSD section schedules from the supplied images.
- Monday–Saturday timetables and six daily teaching periods.
- Listed faculty assignments and section room numbers.
- Room/faculty disruption scenarios and immediate conflict checks.
- Alternative suggestions, approval, undo and CSV export.

**Not included yet**
- Live college database integration.
- Automatic changes across multiple periods.
- Room capacity or equipment checks.
- Verification of faculty expertise and availability outside the timetable.
""")

st.markdown(
    '<div class="footer"><b style="color:#45e0c1">THE RIPPLE</b> · '
    'Timetable Impact Analyzer · ACE CSD hackathon prototype · '
    'Verify source data before operational use</div>',
    unsafe_allow_html=True
)
