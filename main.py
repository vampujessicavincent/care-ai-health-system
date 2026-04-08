import streamlit as st
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
import requests
from sklearn.ensemble import RandomForestRegressor

st.set_page_config(page_title="Care-AI Pro", layout="wide")

# ================= SENSOR =================
def get_sensor_data():
    try:
        data = requests.get("https://care-ai-health-system.vercel.app/api/sensor").json()
        return data["hr"], data["bp"], data["spo2"], data["sugar"]
    except:
        return (
            np.random.randint(70,120),
            np.random.randint(110,160),
            np.random.randint(90,99),
            np.random.randint(80,180)
        )

# ================= ALERT =================
def alert_system(msg):
    st.error("🚨 DOCTOR ALERT")
    st.warning("📞 Emergency Contact Notified")
    st.write(msg)

# ================= NAV =================
page = st.sidebar.radio("Menu", [
    "Patient Input",
    "Live Monitoring",
    "Report",
    "AI Lifestyle & Diet"
])

# ================= PATIENT =================
if page == "Patient Input":

    name = st.text_input("Name")
    surgery = st.text_input("Surgery Type")
    doctor = st.text_input("Doctor Email")
    emergency = st.text_input("Emergency Contact")

    age = st.number_input("Age", 1, 100, 50)
    sex = st.selectbox("Sex", ["Male", "Female"])
    chol = st.number_input("Cholesterol", 100, 400, 200)

    if st.button("Save"):
        st.session_state.patient = {
            "name": name,
            "surgery": surgery,
            "doctor": doctor,
            "emergency": emergency,
            "age": age,
            "sex": sex,
            "chol": chol
        }
        st.success("Saved")

# ================= MONITOR =================
elif page == "Live Monitoring":

    if "patient" not in st.session_state:
        st.warning("Enter patient first")
        st.stop()

    if st.button("Start Monitoring"):

        st.session_state.records = []

        for i in range(7):

            hr, bp, spo2, sugar = get_sensor_data()
            chol = st.session_state.patient["chol"]

            insulin = sugar / 10
            stress = (hr + bp/2 + sugar/2)/3

            rsi = 100 - (0.25*bp + 0.2*chol + 0.2*hr + 0.2*sugar + 0.15*(100-spo2))/5
            rsi = max(0, min(100, rsi))

            data = {
                "Day": i+1,
                "HR": hr,
                "BP": bp,
                "SpO2": spo2,
                "Sugar": sugar,
                "Insulin": round(insulin,2),
                "Stress": round(stress,2),
                "RSI": rsi
            }

            st.session_state.records.append(data)

            st.write(data)
            st.progress(int(rsi))

            if rsi < 40 or bp > 160 or spo2 < 90:
                alert_system(f"Critical condition Day {i+1}")

            time.sleep(1)

# ================= REPORT =================
elif page == "Report":

    if "records" not in st.session_state:
        st.warning("Run monitoring first")
        st.stop()

    df = pd.DataFrame(st.session_state.records)
    avg = df.mean()

    st.dataframe(df)

    st.line_chart(df.set_index("Day")[["RSI","HR","SpO2","Sugar"]])

    # ===== FORECAST =====
    st.subheader("🔮 3-Day Forecast")

    model = RandomForestRegressor()
    model.fit(df["Day"].values.reshape(-1,1), df["RSI"].values)

    preds = model.predict(np.array([8,9,10]).reshape(-1,1))

    for i,p in enumerate(preds):
        st.write(f"Day {8+i}: {round(p,2)}")

    fig, ax = plt.subplots()
    ax.plot(df["Day"], df["RSI"])
    ax.plot([8,9,10], preds, '--')
    st.pyplot(fig)

    avg_pred = np.mean(preds)

    if avg_pred < 50:
        st.error("Forecast Risk: HIGH")
    elif avg_pred < 70:
        st.warning("Forecast Risk: MODERATE")
    else:
        st.success("Forecast Risk: LOW")

    # ===== RISK =====
    risk = (
        0.2*(avg["BP"]/160) +
        0.15*(st.session_state.patient["chol"]/300) +
        0.2*(avg["Sugar"]/200) +
        0.15*(avg["HR"]/150) +
        0.15*(avg["Stress"]/150) +
        0.15*(1 - avg["SpO2"]/100)
    ) * 100

    st.subheader(f"Risk Score: {round(risk,2)}")

    # ===== READMISSION =====
    slope = np.polyfit(range(len(df)), df["RSI"], 1)[0]
    readmit = min(100, (100-avg["RSI"])*0.7 + max(0,-slope)*10)

    st.subheader(f"Readmission: {round(readmit,2)}%")

    if readmit > 70:
        st.error("High Readmission Risk")
    elif readmit > 40:
        st.warning("Moderate Readmission Risk")
    else:
        st.success("Low Readmission Risk")

# ================= AI DIET + LIFESTYLE =================
elif page == "AI Lifestyle & Diet":

    if "records" not in st.session_state:
        st.warning("Run monitoring first")
        st.stop()

    df = pd.DataFrame(st.session_state.records)
    avg = df.mean()
    p = st.session_state.patient
    surgery = p["surgery"].lower()

    risk = (
        0.2*(avg["BP"]/160) +
        0.15*(p["chol"]/300) +
        0.2*(avg["Sugar"]/200) +
        0.15*(avg["HR"]/150) +
        0.15*(avg["Stress"]/150) +
        0.15*(1 - avg["SpO2"]/100)
    ) * 100

    st.title("🤖 AI Recovery Plan")

    # ================= SOUTH INDIAN DIET =================
    st.header("🍛 South Indian Diet Plan")

    if avg["Sugar"] > 150:
        st.write("Breakfast: Ragi dosa + chutney")
        st.write("Lunch: Brown rice + sambar + vegetables")
        st.write("Dinner: Vegetable soup + ragi roti")
        st.write("Avoid sweets and white rice")

    elif avg["Sugar"] < 80:
        st.write("Breakfast: Idli + banana")
        st.write("Lunch: Rice + dal + curd")
        st.write("Dinner: Chapati + vegetables")

    else:
        st.write("Breakfast: Idli / Upma")
        st.write("Lunch: Rice + sambar")
        st.write("Dinner: Chapati + curry")

    # ================= LIFESTYLE =================
    st.header("🧬 Lifestyle")

    if risk > 70:
        st.write("Strict monitoring, bed rest")
    elif risk > 50:
        st.write("Moderate activity")
    else:
        st.write("Normal routine")

    if avg["Stress"] > 120:
        st.write("Stress reduction required")

    if avg["SpO2"] < 95:
        st.write("Breathing exercises")

    if avg["HR"] > 110:
        st.write("Avoid intense activity")

    if "heart" in surgery:
        st.write("Cardiac rehab required")

    if "brain" in surgery:
        st.write("Mental rest required")
