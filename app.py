import streamlit as st
import random
import uuid

# --- 1. SET UP GLOBAL SHARED STORAGE ---
# On Streamlit Cloud, this 'st.session_state' is local to a user.
# To make it global across ALL users, we use st.cache_resource for the "Database"
@st.cache_resource
def get_global_db():
    # This acts as our shared "Cloud" memory
    return {"users": {}, "video_feed": []}

db = get_global_db()

# Sync local session with global database
if "active_dare" not in st.session_state:
    st.session_state.active_dare = None
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# --- 2. LEVEL CALCULATION LOGIC ---
def get_user_stats(username):
    user_videos = [p for p in db["video_feed"] if p['user'] == username]
    total_likes = sum(len(p['liked_by']) for p in user_videos)
    total_xp = total_likes * 10
    level = total_xp // 100
    xp_in_level = total_xp % 100
    return level, total_xp, xp_in_level

# --- 3. SIDEBAR (Login & Levels) ---
st.sidebar.title("👤 Player Profile")
if st.session_state.current_user:
    lvl, xp, progress = get_user_stats(st.session_state.current_user)
    st.sidebar.subheader(f"Level {lvl}")
    st.sidebar.metric("Total XP", f"{xp} ⭐")
    st.sidebar.write(f"Progress to Level {lvl + 1}:")
    st.sidebar.progress(progress / 100)
    
    if st.sidebar.button("Logout"):
        st.session_state.current_user = None
        st.rerun()
else:
    menu = st.sidebar.selectbox("Menu", ["Login", "Register"])
    user_in = st.sidebar.text_input("Username")
    pass_in = st.sidebar.text_input("Password", type="password")
    if menu == "Register" and st.sidebar.button("Create Account"):
        if user_in and user_in not in db["users"]:
            db["users"][user_in] = pass_in
            st.sidebar.success("Account Created! Now Login.")
    elif menu == "Login" and st.sidebar.button("Login"):
        if user_in in db["users"] and db["users"][user_in] == pass_in:
            st.session_state.current_user = user_in
            st.rerun()
        else:
            st.sidebar.error("Wrong username or password")

# --- 4. MAIN APP ---
st.title("🏆 DareDash Global")

if st.session_state.current_user:
    # --- STEP 1: GET DARE ---
    st.header("🎲 Step 1: Get Your Dare")
    dares = [
        "Do 10 pushups", "Sing ABCs backwards", "Balance a spoon on your nose", 
        "Read a book for 1 min", "Do a 20 second plank", "Draw a cat in 10 seconds",
        "Say a tongue twister 5 times fast", "Balance on one leg for 30 seconds"
    ]
    
    if st.button("✨ CLICK FOR A DARE ✨"):
        st.session_state.active_dare = random.choice(dares)
    
    if st.session_state.active_dare:
        st.info(f"**YOUR CHALLENGE:** {st.session_state.active_dare}")

        # --- STEP 2: UPLOAD ---
        st.header("📤 Step 2: Upload Proof")
        uploaded_file = st.file_uploader("Upload Video", type=["mp4", "mov"])
        
        if st.button("Post to Global Feed"):
            if uploaded_file:
                new_post = {
                    "id": str(uuid.uuid4()),
                    "user": st.session_state.current_user,
                    "video": uploaded_file.read(), # Read bytes for global sharing
                    "dare_name": st.session_state.active_dare,
                    "liked_by": set()
                }
                db["video_feed"].append(new_post)
                st.session_state.active_dare = None
                st.success("Posted! Everyone can see it now!")
                st.rerun()

    # --- 5. GLOBAL FEED & LEADERBOARD ---
    st.divider()
    st.header("🌎 Global Feed")
    
    # Sort by likes
    sorted_feed = sorted(db["video_feed"], key=lambda x: len(x['liked_by']), reverse=True)
    
    if not sorted_feed:
        st.write("No videos yet. Be the first!")
    
    for post in sorted_feed:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                p_lvl, _, _ = get_user_stats(post['user'])
                st.write(f"**{post['user']}** (Lvl {p_lvl}) — *{post['dare_name']}*")
                st.video(post['video'])
            with col2:
                # Anti-Spam Check
                has_liked = st.session_state.current_user in post['liked_by']
                if st.button(f"❤️ {len(post['liked_by'])}", key=f"lk_{post['id']}", disabled=has_liked):
                    post['liked_by'].add(st.session_state.current_user)
                    st.rerun()
                if has_liked: st.caption("Liked!")
else:
    st.warning("Welcome! Register or Login to start doing dares and earning XP!")
