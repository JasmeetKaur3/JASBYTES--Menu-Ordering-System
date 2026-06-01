import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import os
import pywhatkit
import qrcode
from io import BytesIO
import time

CSV_FILE = "orders.csv"

# =============================
# CREATE CSV IF NOT EXISTS
# =============================
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=[
        "Order ID","Customer Name","Date","Time",
        "Item","Size","Qty","Price","Total",
        "Subtotal","GST","Delivery","Tip",
        "Final Bill","Payment Method",
        "JasCoins","Phone","Rating","Feedback"
    ])
    df.to_csv(CSV_FILE, index=False)

# =============================
# QR TO OPEN APP ON PHONE
# =============================
st.sidebar.title("📱 Run App on Phone")

APP_URL = st.sidebar.text_input(
    "Enter your Streamlit App URL",
    value="http://10.31.138.118:8501"
)

qr_app = qrcode.make(APP_URL)
buf_app = BytesIO()
qr_app.save(buf_app, format="PNG")

st.sidebar.image(buf_app.getvalue(), width=200)
st.sidebar.caption("Scan to open this app on your mobile")

# =============================
# LOGO + TITLE
# =============================
st.image("logo_red.png")
st.title(":red[𝓦𝓮𝓵𝓬𝓸𝓶𝓮 𝓽𝓸 𝓙𝓪𝓼𝓑𝔂𝓽𝓮𝓼!...🙏🏻]")

# =============================
# START ORDER BUTTON
# =============================
if "started" not in st.session_state:
    st.session_state.started = False

if st.button("Start Ordering"):
    st.session_state.started = True

start = st.session_state.started

# =============================
# PAYMENT STATE
# =============================
if "payment_success" not in st.session_state:
    st.session_state.payment_success = False

# =============================
# MAIN APP
# =============================
if start:

    choice = st.selectbox(
        "Select Category",
        ["Veg","Non-Veg","Snacks","Beverages","Combos"]
    )

    if choice == "Veg":

        st.image("veg.jpg", width=600)

        menu = {
            "Paneer Butter Masala": {"Half":120,"Full":200},
            "Chole Bhature": {"Half":80,"Full":140},
            "Mix Veg": {"Half":90,"Full":150},
            "Dal Tadka": {"Half":70,"Full":120},
            "Veg Biryani": {"Half":100,"Full":180},
        }

        st.subheader("🥗 VEG MENU")

    elif choice == "Non-Veg":

        st.image("nonveg.jpg", width=600)

        menu = {
            "Butter Chicken": {"Half":140,"Full":220},
            "Chicken Soup": {"Half":180,"Full":300},
            "Egg Curry": {"Half":90,"Full":150},
            "Chicken Biryani": {"Half":130,"Full":210},
            "Fish Fry": {"Half":160,"Full":260},
        }

        st.subheader("🍗 NON-VEG MENU")

    elif choice == "Snacks":

        st.image("snacks.jpg", width=600)

        menu = {
            "Momos": {"Half":30,"Full":50},
            "Chowmein": {"Half":40,"Full":60},
            "Panipuri": {"Half":20,"Full":40},
            "White sauce pasta": {"Half":50,"Full":80},
            "Regular pasta": {"Half":40,"Full":80},
        }

        st.subheader("🍟 SNACKS")

    elif choice == "Beverages":

        st.image("drink.jpg", width=600)

        menu = {
            "Mojito":89,
            "Blue Lagoon":99,
            "Soft drinks":40,
            "Kitkat Shake":129,
            "Jasbytes Special Juice":179
        }

        st.subheader("🥤 BEVERAGES")

    else:

        st.image("combo.jpg", width=600)

        menu = {
            "Burger mania":200,
            "Fusion meal":160,
            "Veg combo":180,
            "Non veg combo":299,
            "Family combo":249
        }

        st.subheader("🍱 COMBOS")

    st.subheader("🛒 Add Items to Cart")

    if "cart" not in st.session_state:
        st.session_state.cart = []

    for item, val in menu.items():

        if isinstance(val, dict):

            size = st.selectbox(
                f"Select Size for {item}",
                ["Half","Full"],
                key=item
            )

            price = val[size]

        else:

            size = ""
            price = val

        if st.button(f"Add {item}"):

            st.session_state.cart.append(
                [item,size,price,1]
            )

            st.success(f"Added: {item} ({size})")

    st.subheader("🛍 YOUR CART")

    if st.session_state.cart:

        cart_df = pd.DataFrame(
            st.session_state.cart,
            columns=["Item","Size","Price","Qty"]
        )

        cart_df["Total"] = cart_df.Price * cart_df.Qty

        for i, row in cart_df.iterrows():

            col1, col2, col3, col4, col5, col6 = st.columns(6)

            col1.write(row["Item"])
            col2.write(row["Size"])
            col3.write(f"₹{row['Price']}")
            col4.write(row["Qty"])
            col5.write(f"₹{row['Total']}")

            if col6.button("❌ Remove", key=f"remove_{i}"):

                st.session_state.cart.pop(i)
                st.rerun()

        subtotal = cart_df["Total"].sum()

        gst = round(subtotal * 0.05,2)

        delivery = 100 if subtotal < 499 else 0

        tip = st.number_input(
            "Enter Tip ₹:",
            min_value=0.0,
            step=0.01
        )

        final_amount = subtotal + gst + delivery + tip

        st.write(f"Subtotal: ₹{subtotal}")
        st.write(f"GST (5%): ₹{gst}")
        st.write(f"Delivery: ₹{delivery}")
        st.write(f"Tip: ₹{tip}")
        st.write(f"### Final Amount: ₹{final_amount}")

        payment_method = st.radio(
            "Select Payment Method",
            ["Cash","UPI"]
        )

        if payment_method == "UPI":
            if st.button("I Have Paid"):
                st.session_state.payment_success = True

        if payment_method == "Cash":

            cash_given = st.number_input(
                "Enter Cash Amount ₹",
                min_value=0.0,
                step=0.01
            )

            if st.button("Confirm Cash Payment"):

                if abs(cash_given - final_amount) < 0.01:
                    st.session_state.payment_success = True
                else:
                    st.error("Insufficient Amount")

        customer_name = st.text_input(
            "Enter Customer Name:"
        )

        customer_phone = st.text_input(
            "Enter Customer WhatsApp Number:"
        )

        if st.button("Place Order"):

            st.balloons()

            if not st.session_state.payment_success:
                st.error("Please complete payment first!")
                st.stop()

            order_id = str(uuid.uuid4())[:8]

            now = datetime.now()

            jascoins = int((final_amount // 100) * 5)

            st.success("Order Placed Successfully!")

            # =============================
            # WHATSAPP
            # =============================
            try:

                phone = f"+91{customer_phone}"

                message = f"""
Welcome {customer_name}! 🥳

JasBytes Restaurant Bill

Order ID: {order_id}

Customer: {customer_name}

Total Amount: ₹{final_amount}

Payment: {payment_method}

You earned {jascoins} JasCoins

Thanks for choosing JasBytes

◆ ᴀ ʙʏᴛᴇ ᴏꜰ ᴛʀᴀᴅɪᴛɪᴏɴ ɪɴ ᴇᴠᴇʀʏ ʙɪᴛᴇ ◆

🌟 How it works:

* Earn JasCoins on every bill
* You earned {jascoins} JasCoins
* Redeem them anytime using your mobile number

🎁 Get rewarded on every purchase!
"""

                time.sleep(5)

                pywhatkit.sendwhats_image(
                    receiver=phone,
                    img_path="logo_red.png",
                    caption="JasBytes"
                )

                time.sleep(8)

                pywhatkit.sendwhatmsg_instantly(
                    phone_no=phone,
                    message=message,
                    wait_time=15,
                    tab_close=True,
                    close_time=5
                )

                st.success("WhatsApp message sent!")

            except Exception as e:

                st.warning(f"WhatsApp message failed: {e}")

else:

    st.title("Click the button to begin…")