import streamlit as st
import asyncio
import time
from mcstatus import JavaServer
from dotenv import load_dotenv
import os

# ---- Load environment variables ----
load_dotenv()
SERVER_IP = os.getenv("SERVER_IP")
SERVER_PORT = int(os.getenv("SERVER_PORT"))
REFRESH_INTERVAL = 30  # seconds
PASSWORD = os.getenv("DASHBOARD_PASSWORD")

# ---- Basic password protection ----
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        pwd = st.text_input("Enter password to access dashboard:", type="password")
        if pwd == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.stop()

check_password()

# ---- Async function to check server ----
async def get_server_status(ip, port):
    try:
        server = JavaServer.lookup(f"{ip}:{port}")
        status = await server.async_status()
        return {
            "online": True,
            "motd": status.description.get("text", str(status.description)),
            "players_online": status.players.online,
            "players_max": status.players.max,
            "latency": status.latency
        }
    except Exception as e:
        return {
            "online": False,
            "error": str(e)
        }

def get_status_sync(ip, port):
    return asyncio.run(get_server_status(ip, port))

# ---- Streamlit Dashboard ----
st.set_page_config(page_title="Minecraft Server Status", page_icon="🟢", layout="centered")
st.title("🟢 Minecraft Server Dashboard")

# Manual refresh
if st.button("🔁 Refresh Now"):
    st.rerun()

status_placeholder = st.empty()
status = get_status_sync(SERVER_IP, SERVER_PORT)

with status_placeholder.container():
    if status["online"]:
        st.success("✅ Server is ONLINE!")
        st.markdown(f"**MOTD:** {status['motd']}")
        st.markdown(f"**Players:** {status['players_online']} / {status['players_max']}")
        st.markdown(f"**Latency:** {status['latency']} ms")
    else:
        st.error("❌ Server is OFFLINE or unreachable.")
        st.markdown(f"**Error:** {status['error']}")

# Countdown
countdown_placeholder = st.empty()
for remaining in range(REFRESH_INTERVAL, 0, -1):
    countdown_placeholder.markdown(f"⏳ Refreshing in **{remaining}** seconds...")
    time.sleep(1)

st.rerun()
