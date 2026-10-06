import streamlit as st
import plotly.express as px
from datetime import datetime
from utils.ui import setup_page, header, BADGE
from utils import database as db
from ml.predict import predict, ModelMissingError

setup_page("AI Prediction", "🤖")
header("AI Prediction", "Predict CNG availability and waiting time for a chosen situation")

try:
    stations = db.get_stations_with_status()
except db.DatabaseError as e:
    st.error(str(e)); st.stop()
if not stations:
    st.warning("No stations available."); st.stop()

now = datetime.now()
names = {f"{s['name']} (#{s['station_id']})": s for s in stations}
with st.form("predict_form"):
    choice = st.selectbox("Station", list(names))
    c1, c2, c3 = st.columns(3)
    hour = c1.slider("Hour of day", 0, 23, now.hour)
    dow = c2.selectbox("Day of week", range(7), index=now.weekday(),
                       format_func=lambda i: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][i])
    traffic = c3.selectbox("Traffic level", ["Low", "Medium", "High"], index=1)
    c4, c5, c6, c7 = st.columns(4)
    queue = c4.number_input("Current queue (vehicles)", 0, 100, 5)
    vph = c5.number_input("Vehicles per hour", 0, 200, 25)
    pw = c6.number_input("Previous waiting time (min)", 0, 240, 10)
    pa = c7.selectbox("Previous availability", ["High", "Medium", "Low"])
    go = st.form_submit_button("Predict")

if go:
    s = names[choice]
    try:
        r = predict(s["station_id"], hour, dow, queue, traffic, vph, pw, pa)
    except ModelMissingError as e:
        st.error(f"{e}"); st.stop()
    except ValueError as e:
        st.error(f"Invalid input: {e}"); st.stop()
    st.subheader("Result")
    a, b, c = st.columns(3)
    a.metric("AI Predicted Availability", f"{BADGE[r['availability']]} {r['availability']}")
    b.metric("Predicted waiting time", f"{r['waiting_time']} min")
    c.metric("Model confidence", f"{r['confidence']:.0%}")
    fig = px.bar(x=list(r["probabilities"]), y=list(r["probabilities"].values()),
                 labels={"x": "Availability", "y": "Probability"}, title="Class probabilities")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("This is an ML estimate from sample/historical data, not confirmed real-time availability.")
    try:
        db.log_prediction(s["station_id"], r["availability"], r["waiting_time"])
    except db.DatabaseError as e:
        st.warning(f"Prediction shown, but could not be saved to history: {e}")
