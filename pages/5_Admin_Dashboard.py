import pandas as pd
import streamlit as st
from utils.ui import setup_page, header
from utils import auth, database as db
from utils import charts
from utils.distance import is_valid_coordinate

setup_page("Admin Dashboard", "🛠️")
header("Admin Dashboard", "Manage stations, status updates, history and analytics")
auth.require_admin()

try:
    stations = db.get_stations_with_status()
except db.DatabaseError as e:
    st.error(str(e)); st.stop()

tabs = st.tabs(["Stations", "Update status", "History", "Predictions", "Analytics"])

with tabs[0]:
    if stations:
        st.dataframe(pd.DataFrame(stations)[["station_id", "name", "address", "latitude", "longitude",
                     "phone", "operating_hours", "status"]], hide_index=True, use_container_width=True)
    else:
        st.info("No stations yet.")
    st.subheader("Add station")
    with st.form("add"):
        n = st.text_input("Name"); ad = st.text_input("Address")
        c1, c2 = st.columns(2)
        la = c1.number_input("Latitude", value=17.4, format="%.6f"); lo = c2.number_input("Longitude", value=78.5, format="%.6f")
        ph = st.text_input("Phone"); hr = st.text_input("Operating hours", "06:00-22:00")
        stt = st.selectbox("Status", ["open", "closed", "maintenance"])
        if st.form_submit_button("Add"):
            if not n.strip() or not ad.strip(): st.error("Name and address are required.")
            elif not is_valid_coordinate(la, lo): st.error("Invalid coordinates.")
            else:
                db.add_station(n.strip(), ad.strip(), la, lo, ph.strip(), hr.strip(), stt)
                st.success("Station added."); st.rerun()
    if stations:
        st.subheader("Update / delete station")
        pick = st.selectbox("Choose station", stations, format_func=lambda s: f"#{s['station_id']} {s['name']}")
        with st.form("upd"):
            n = st.text_input("Name", pick["name"]); ad = st.text_input("Address", pick["address"])
            c1, c2 = st.columns(2)
            la = c1.number_input("Latitude", value=float(pick["latitude"]), format="%.6f")
            lo = c2.number_input("Longitude", value=float(pick["longitude"]), format="%.6f")
            ph = st.text_input("Phone", pick["phone"] or ""); hr = st.text_input("Hours", pick["operating_hours"] or "")
            opts = ["open", "closed", "maintenance"]
            stt = st.selectbox("Status", opts, index=opts.index(pick["status"]))
            if st.form_submit_button("Save changes"):
                if not n.strip() or not ad.strip() or not is_valid_coordinate(la, lo):
                    st.error("Check name, address and coordinates.")
                else:
                    db.update_station(pick["station_id"], n.strip(), ad.strip(), la, lo, ph.strip(), hr.strip(), stt)
                    st.success("Updated."); st.rerun()
        confirm = st.checkbox(f"I confirm I want to delete '{pick['name']}' and all its history")
        if st.button("Delete station", disabled=not confirm):
            db.delete_station(pick["station_id"]); st.success("Deleted."); st.rerun()

with tabs[1]:
    if not stations:
        st.info("Add a station first.")
    else:
        pick = st.selectbox("Station", stations, format_func=lambda s: f"#{s['station_id']} {s['name']}", key="ps")
        with st.form("status"):
            av = st.selectbox("Availability", ["High", "Medium", "Low"])
            q = st.number_input("Queue length", 0, 200, 0)
            wt = st.number_input("Waiting time (min)", 0, 300, 0)
            tr = st.selectbox("Traffic level", ["Low", "Medium", "High"], index=1)
            if st.form_submit_button("Save update"):
                db.add_status(pick["station_id"], av, q, wt, tr)
                st.success("Status updated (recorded as an admin update, not a live sensor reading).")

with tabs[2]:
    hist = db.get_status_history()
    st.subheader("Station status updates")
    st.dataframe(pd.DataFrame(hist), hide_index=True, use_container_width=True) if hist else st.info("No updates yet.")
    st.subheader("Training dataset (synthetic sample)")
    if charts.DATA_PATH.exists():
        st.dataframe(charts.load_history().tail(200), hide_index=True, use_container_width=True)
    else:
        st.warning("Run generate_dataset.py first.")

with tabs[3]:
    preds = db.get_prediction_history()
    st.dataframe(pd.DataFrame(preds), hide_index=True, use_container_width=True) if preds else st.info("No predictions logged yet. Use the AI Prediction page.")

with tabs[4]:
    if not charts.DATA_PATH.exists():
        st.warning("Dataset not found. Run generate_dataset.py.")
    else:
        df = charts.load_history()
        c1, c2 = st.columns(2)
        c1.plotly_chart(charts.wait_by_hour(df), use_container_width=True)
        c2.plotly_chart(charts.queue_by_station(df), use_container_width=True)
        c3, c4 = st.columns(2)
        c3.plotly_chart(charts.availability_distribution(df), use_container_width=True)
        c4.plotly_chart(charts.traffic_vs_wait(df), use_container_width=True)
        st.plotly_chart(charts.daily_demand(df), use_container_width=True)
        perf = charts.model_performance()
        if perf: 
            st.plotly_chart(perf, use_container_width=True)
            m = charts.load_metrics()
            st.write("**Regression (waiting time):**", m["regression"])
            st.caption(m["data_note"])
        else:
            st.info("Train the model to see performance: python -m ml.train_model")
