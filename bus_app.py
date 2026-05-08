import streamlit as st
import pandas as pd
from datetime import datetime
import os
import time
import pytz

# ১. কনফিগারেশন
RECORD_FILE = "daily_customer_list.csv"
ADMIN_PASSWORD = "SOHEL502" 
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/11LAiSvWu3I_bKRGUg26uBIuGlob4cdRB6SOs7no3QiM/edit?gid=0#gid=0"

# ২. সময় ও ডাটা সেভ ফাংশন
def get_bd_time():
    bd_timezone = pytz.timezone('Asia/Dhaka')
    return datetime.now(bd_timezone)

def save_booking_data(data):
    df = pd.DataFrame([data])
    if not os.path.isfile(RECORD_FILE):
        df.to_csv(RECORD_FILE, index=False, encoding='utf-8-sig')
    else:
        df.to_csv(RECORD_FILE, mode='a', index=False, header=False, encoding='utf-8-sig')

# ৩. পেজ সেটআপ
st.set_page_config(page_title="২৮ সিট স্মার্ট বাস", layout="wide")
st.title("🚌 মীরপুর টু নাজিরপুর - স্মার্ট বাস সার্ভিস")

# ৪. ২৮টি সিটের তালিকা
rows = ["A", "B", "C", "D", "E", "F", "G"]
seat_list = [f"{r}{c}" for r in rows for c in range(1, 5)]

# ৫. সেশন স্টেট (বুকড সিট ও লগইন চেক)
if 'booked_seats' not in st.session_state:
    st.session_state.booked_seats = []
    if os.path.isfile(RECORD_FILE):
        df_existing = pd.read_csv(RECORD_FILE)
        today = get_bd_time().strftime("%Y-%m-%d")
        if 'তারিখ ও সময়' in df_existing.columns:
            df_today = df_existing[df_existing['তারিখ ও সময়'].astype(str).str.contains(today)]
            st.session_state.booked_seats = df_today['সিট নম্বর'].tolist()

if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

if 'last_ticket' not in st.session_state:
    st.session_state.last_ticket = None

col1, col2 = st.columns([2, 1])

# ৬. সিট ম্যাপ (বাম পাশ)
with col1:
    st.subheader("সিট নির্বাচন করুন (২৮ সিট)")
    for i in range(0, len(seat_list), 4):
        r_seats = seat_list[i:i+4]
        cols = st.columns([1, 1, 0.5, 1, 1])
        for idx, seat in enumerate(r_seats):
            d_idx = idx if idx < 2 else idx + 1
            if seat in st.session_state.booked_seats:
                cols[d_idx].button(f"🔴 {seat}", key=f"btn_{seat}", disabled=True)
            else:
                cols[d_idx].button(f"🟢 {seat}", key=f"btn_{seat}")

# ৭. যাত্রী তথ্য ও টিকিট জেনারেশন (ডান পাশ)
with col2:
    # যদি টিকিট অলরেডি জেনারেট হয়ে থাকে তবে তা দেখাবে
    if st.session_state.last_ticket:
        st.success("✅ আপনার টিকিট জেনারেট হয়েছে!")
        ticket = st.session_state.last_ticket
        st.markdown(f"""
        <div style="border: 2px dashed #4CAF50; padding: 20px; border-radius: 10px; background-color: #f9f9f9; color: black;">
            <h2 style="text-align: center; color: #2E7D32;">🎫 স্মার্ট বাস টিকিট</h2>
            <hr>
            <p><b>যাত্রীর নাম:</b> {ticket['কাস্টমারের নাম']}</p>
            <p><b>সিট নম্বর:</b> <span style="font-size: 20px; color: red;">{ticket['সিট নম্বর']}</span></p>
            <p><b>মোবাইল:</b> {ticket['মোবাইল নম্বর']}</p>
            <p><b>TrxID:</b> {ticket['TrxID']}</p>
            <p><b>তারিখ ও সময়:</b> {ticket['তারিখ ও সময়']}</p>
            <hr>
            <p style="text-align: center; font-size: 12px;">শুভ যাত্রা - মীরপুর টু নাজিরপুর</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("নতুন বুকিং করুন"):
            st.session_state.last_ticket = None
            st.rerun()
    
    else:
        st.subheader("যাত্রী তথ্য ও পেমেন্ট")
        available_seats = [s for s in seat_list if s not in st.session_state.booked_seats]
        
        if not available_seats:
            st.warning("আজকের সব সিট বুক হয়ে গেছে!")
        else:
            s_seat = st.selectbox("সিট বেছে নিন", available_seats)
            name = st.text_input("যাত্রীর নাম")
            phone = st.text_input("মোবাইল নম্বর")
            bkash_no = st.text_input("বিকাশ নম্বর:01717840502 (টাকা যেখান থেকে এসেছে)")
            trx_id = st.text_input("TrxID (১০ অক্ষর)")
            screenshot = st.file_uploader("পেমেন্ট স্ক্রিনশট আপলোড করুন", type=["jpg", "png", "jpeg"])

            if st.button("বুকিং কনফার্ম করুন"):
                if name and phone and len(trx_id) >= 10:
                    current_time = get_bd_time().strftime("%Y-%m-%d %I:%M %p")
                    booking_info = {
                        "তারিখ ও সময়": current_time,
                        "কাস্টমারের নাম": name,
                        "সিট নম্বর": s_seat,
                        "মোবাইল নম্বর": phone,
                        "বিকাশ নম্বর": bkash_no,
                        "TrxID": trx_id,
                        "স্ক্রিনশট ফাইল": "সংযুক্ত" if screenshot else "নেই"
                    }
                    save_booking_data(booking_info)
                    st.session_state.booked_seats.append(s_seat)
                    st.session_state.last_ticket = booking_info # টিকিট ডাটা সেশনে রাখা
                    st.balloons()
                    st.rerun()
                else:
                    st.error("সঠিক তথ্য দিন (নাম, ফোন এবং অন্তত ১০ অক্ষরের TrxID)।")

st.markdown("---")

# ৮. অ্যাডমিন কন্ট্রোল
st.subheader("🔐 অ্যাডমিন কন্ট্রোল")

if not st.session_state.admin_logged_in:
    admin_pass = st.text_input("অ্যাডমিন পাসওয়ার্ড দিন", type="password")
    if st.button("লগইন"):
        if admin_pass == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.success("লগইন সফল হয়েছে!")
            st.rerun()
        else:
            st.error("ভুল পাসওয়ার্ড!")
else:
    st.info("অ্যাডমিন মোড অ্যাক্টিভ")
    
    if st.button("🚫 আজকের হিসাব ক্লোজ করুন"):
        if os.path.isfile(RECORD_FILE):
            df_all = pd.read_csv(RECORD_FILE)
            backup_name = f"backup_{get_bd_time().strftime('%Y-%m-%d')}.csv"
            df_all.to_csv(backup_name, index=False, encoding='utf-8-sig')
            os.remove(RECORD_FILE)
            st.session_state.booked_seats = []
            st.session_state.last_ticket = None
            st.success(f"হিসাব ক্লোজ হয়েছে। ব্যাকআপ সেভ হয়েছে: {backup_name}")
            time.sleep(2)
            st.rerun()
        else:
            st.warning("ক্লোজ করার মতো কোনো ডাটা নেই।")

    if st.button("লগআউট"):
        st.session_state.admin_logged_in = False
        st.rerun()
    
    if os.path.isfile(RECORD_FILE):
        df_show = pd.read_csv(RECORD_FILE)
        st.write("📊 আজকের বুকিং রেকর্ড:")
        st.dataframe(df_show, use_container_width=True)
        
        for index, row in df_show.iterrows():
            with st.expander(f"যাত্রী: {row['কাস্টমারের নাম']} (সিট: {row['সিট নম্বর']})"):
                st.write(f"📅 সময়: {row['তারিখ ও সময়']}")
                st.write(f"📞 মোবাইল: {row['মোবাইল নম্বর']}")
                st.write(f"💳 বিকাশ: {row['বিকাশ নম্বর']} | 🆔 TrxID: {row['TrxID']}")

        st.markdown("---")
        btn1, btn2 = st.columns(2)
        with btn1:
            st.download_button("📁 Excel ডাউনলোড", df_show.to_csv(index=False).encode('utf-8-sig'), "report.csv")
        with btn2:
            st.link_button("🌐 Google Sheet খুলুন", GOOGLE_SHEET_URL)