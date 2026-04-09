import streamlit as st
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor

st.set_page_config(page_title="Care-AI Pro", layout="wide")

# ================= SESSION =================
if "role" not in st.session_state:
    st.session_state.role = None
if "patients" not in st.session_state:
    st.session_state.patients = {}

# ================= LOGIN =================
def login():
    st.title("🔐 Care-AI Login")

    role = st.selectbox("Login As", ["Patient", "Doctor"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if password == "1234":
            st.session_state.role = role.lower()
            st.success(f"Welcome {username}")
        else:
            st.error("Invalid credentials")

if st.session_state.role is None:
    login()
    st.stop()

# ================= MENU =================
menu = ["Patient Input", "Live Monitoring", "Report", "AI Lifestyle & Diet"]
if st.session_state.role == "doctor":
    menu.append("Doctor Dashboard")

page = st.sidebar.radio("Menu", menu)

# ================= ALERT =================
def alert_system(msg):
    st.error("🚨 EMERGENCY ALERT")
    st.write(msg)
    st.info(f"📲 WhatsApp Message:\n{msg}")

# ================= PATIENT INPUT =================
if page == "Patient Input":

    st.title("🧑 Patient Details")

    name = st.text_input("Name")
    surgery = st.text_input("Surgery Type")
    doctor = st.text_input("Doctor Email")
    emergency = st.text_input("Emergency Contact")

    age = st.number_input("Age", 1, 100, 50)
    sex = st.selectbox("Sex", ["Male", "Female"])
    chol = st.number_input("Cholesterol", 100, 400, 200)

    st.subheader("🩺 Initial Health Values")

    hr = st.number_input("Heart Rate", 40, 180, 80)
    bp = st.number_input("Blood Pressure", 80, 200, 120)
    spo2 = st.number_input("SpO2", 70, 100, 98)
    sugar = st.number_input("Sugar", 60, 300, 110)

    if st.button("Save"):
        st.session_state.patients["user"] = {
            "name": name,
            "surgery": surgery,
            "doctor": doctor,
            "emergency": emergency,
            "age": age,
            "sex": sex,
            "chol": chol,
            "records": [{
                "Day": 0,
                "HR": hr,
                "BP": bp,
                "SpO2": spo2,
                "Sugar": sugar,
                "Stress": (hr + bp/2 + sugar/2)/3,
                "RSI": 100
            }]
        }
        st.success("Saved successfully")

# ================= LIVE =================
elif page == "Live Monitoring":

    if "user" not in st.session_state.patients:
        st.warning("Enter patient data first")
        st.stop()

    patient = st.session_state.patients["user"]

    if st.button("Start Monitoring"):

        for i in range(1, 8):

            hr = np.random.randint(70, 120)
            bp = np.random.randint(110, 170)
            spo2 = np.random.randint(90, 99)
            sugar = np.random.randint(80, 180)

            stress = (hr + bp/2 + sugar/2)/3
            rsi = 100 - (0.25*bp + 0.2*hr + 0.2*sugar + 0.15*(100-spo2))/5
            rsi = max(0, min(100, rsi))

            data = {
                "Day": i,
                "HR": hr,
                "BP": bp,
                "SpO2": spo2,
                "Sugar": sugar,
                "Stress": stress,
                "RSI": rsi
            }

            patient["records"].append(data)

            st.write(data)
            st.progress(int(rsi))
            st.write(f"RSI: {round(rsi,2)}%")

            if rsi < 25 or bp > 180 or spo2 < 85:
                alert_system(f"🚨 Patient {patient['name']} critical on Day {i}")

            time.sleep(1)

# ================= REPORT =================
elif page == "Report":

    patient = st.session_state.patients["user"]
    df = pd.DataFrame(patient["records"])
    avg = df.mean()

    st.dataframe(df)
    st.line_chart(df.set_index("Day")[["RSI","HR","SpO2","Sugar"]])

    # 🔮 Forecast
    st.subheader("🔮 3-Day RSI Forecast")

    model = RandomForestRegressor()
    model.fit(df["Day"].values.reshape(-1,1), df["RSI"])

    future_days = [8,9,10]
    preds = model.predict(np.array(future_days).reshape(-1,1))

    for i,p in zip(future_days, preds):
        st.write(f"Day {i} → RSI: {round(p,2)}%")

    # 📈 Graph with forecast
    fig, ax = plt.subplots()
    ax.plot(df["Day"], df["RSI"], label="Actual RSI")
    ax.plot(future_days, preds, '--', label="Forecast RSI")
    ax.legend()
    st.pyplot(fig)

    # 📊 Readmission
    slope = np.polyfit(range(len(df)), df["RSI"],1)[0]
    readmit = min(100,(100-avg["RSI"])*0.7+abs(slope)*10)

    st.subheader(f"📊 Readmission Risk: {round(readmit,2)}%")

# ================= AI =================
elif page == "AI Lifestyle & Diet":

    patient = st.session_state.patients["user"]
    df = pd.DataFrame(patient["records"])
    avg = df.mean()

    sugar, bp, stress, spo2 = avg["Sugar"], avg["BP"], avg["Stress"], avg["SpO2"]

    st.title("🤖 AI Recovery Plan")

    # 🔥 Risk Meter
    risk = (0.3*(bp/180)+0.3*(sugar/200)+0.2*(stress/150)+0.2*(1-spo2/100))*100

    if risk < 40:
        st.success(f"🟢 LOW RISK: {round(risk,2)}%")
    elif risk < 70:
        st.warning(f"🟡 MODERATE RISK: {round(risk,2)}%")
    else:
        st.error(f"🔴 HIGH RISK: {round(risk,2)}%")

    # 🍛 FULL MEAL PLAN
    st.header("🍛 Full South Indian Meal Plan")

    if sugar > 150:
        st.write("Breakfast: Ragi dosa + chutney")
        st.write("Lunch: Brown rice + sambar + greens")
        st.write("Dinner: Vegetable soup + ragi roti")
        st.write("Snacks: Sprouts / peanuts")
    elif sugar < 80:
        st.write("Breakfast: Idli + banana")
        st.write("Lunch: Rice + dal + curd")
        st.write("Dinner: Chapati + vegetables")
        st.write("Snacks: Fruits")
    else:
        st.write("Breakfast: Idli / dosa / upma")
        st.write("Lunch: Rice + sambar + vegetables + curd")
        st.write("Dinner: Chapati + curry")
        st.write("Snacks: Fruits + nuts")

    # 🏃 FULL EXERCISE PLAN
    st.header("🏃 Detailed Exercise Plan")

    if bp > 170 or spo2 < 90:
        st.write("Bed rest")
        st.write("Breathing exercises (5–10 mins)")
    elif stress > 120:
        st.write("Slow walking (10–15 mins)")
        st.write("Stretching")
    else:
        st.write("Walking (20–30 mins)")
        st.write("Yoga (15 mins)")
        st.write("Light strength exercises")

# ================= DOCTOR =================
elif page == "Doctor Dashboard":

    df = pd.DataFrame(st.session_state.patients["user"]["records"])
    st.dataframe(df)