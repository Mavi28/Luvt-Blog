"""
luvt/pages/Admin.py  —  Password-protected admin panel
Credentials live ONLY in .streamlit/secrets.toml (never in code)
"""
import streamlit as st
import json
from datetime import datetime
from db import (
    admin_get_all_posts, admin_get_post,
    admin_create_post, admin_update_post, admin_delete_post,
    CATEGORIES, fmt_date,
)

st.set_page_config(
    page_title="Luvt Admin",
    page_icon="⚙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Admin CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;1,400&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #111 !important;
    color: #ccc !important;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stSidebar"] {
    background: #141414 !important;
    border-right: 1px solid #222 !important;
}
[data-testid="stSidebar"] * { color: #888 !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding-top: 2rem !important; }

/* Login box */
.login-wrap {
    max-width: 400px;
    margin: 80px auto;
    padding: 52px;
    border: 1px solid #222;
    background: #141414;
}
.login-logo {
    font-family: 'Playfair Display', serif;
    font-size: 30px;
    letter-spacing: 5px;
    color: #e8e8e8;
    text-align: center;
    margin-bottom: 4px;
}
.login-sub {
    font-size: 10px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #444;
    text-align: center;
    margin-bottom: 36px;
}

/* Stats */
.stat-card {
    background: #1e1e1e;
    border: 1px solid #2a2a2a;
    padding: 24px;
    text-align: left;
}
.stat-num {
    font-family: 'Playfair Display', serif;
    font-size: 40px;
    font-style: italic;
    color: #e8e8e8;
    line-height: 1;
    margin-bottom: 6px;
}
.stat-label {
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #555;
}

/* Status badges */
.badge-pub {
    background: #1a3326; color: #5dcca0;
    font-size: 9px; letter-spacing: 2px;
    text-transform: uppercase; padding: 3px 9px;
    display: inline-block;
}
.badge-dft {
    background: #2a2616; color: #c4a040;
    font-size: 9px; letter-spacing: 2px;
    text-transform: uppercase; padding: 3px 9px;
    display: inline-block;
}

/* Streamlit overrides for dark admin */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    background: #1e1e1e !important;
    border: 1px solid #2a2a2a !important;
    color: #e8e8e8 !important;
    border-radius: 0 !important;
}
.stButton > button {
    border-radius: 0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}
label { color: #555 !important; font-size: 11px !important; letter-spacing: 1.5px !important; text-transform: uppercase !important; }
</style>
""", unsafe_allow_html=True)


# ── Auth check ─────────────────────────────────────────────────────────────────
# Credentials come from Streamlit secrets — NEVER from the code
def check_credentials(username: str, password: str) -> bool:
    try:
        return (
            username == st.secrets["admin"]["username"]
            and password == st.secrets["admin"]["password"]
        )
    except Exception:
        st.error("Admin credentials not configured. Add [admin] to your secrets.toml.")
        return False

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ── Login screen ───────────────────────────────────────────────────────────────
if not st.session_state.admin_logged_in:
    st.markdown("""
    <div class="login-wrap">
      <div class="login-logo">Luvt</div>
      <div class="login-sub">Admin Panel</div>
    </div>""", unsafe_allow_html=True)

    # Center the login form
    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.markdown('<div style="background:#141414;border:1px solid #222;padding:48px;margin-top:-80px">', unsafe_allow_html=True)
        st.markdown('<div class="login-logo" style="margin-bottom:4px">Luvt</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">Admin Panel</div>', unsafe_allow_html=True)
        username = st.text_input("Username", key="login_user", placeholder="your username")
        password = st.text_input("Password", type="password", key="login_pass", placeholder="••••••••••")
        if st.button("Sign in", use_container_width=True):
            if check_credentials(username, password):
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Incorrect username or password.")
        st.markdown('<div style="font-size:11px;color:#333;text-align:center;margin-top:16px">Credentials are set in Streamlit secrets — not in this file.</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()  # Don't render anything else for unauthenticated users


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN SHELL — only reached if logged in
# ══════════════════════════════════════════════════════════════════════════════

# Sidebar navigation
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Playfair Display',serif;font-size:22px;letter-spacing:4px;
                color:#e8e8e8 !important;padding:8px 0 24px;border-bottom:1px solid #222;
                margin-bottom:20px">
      Luvt
    </div>""", unsafe_allow_html=True)

    panel = st.radio(
        "Navigate",
        ["Dashboard", "All Posts", "Write Post", "Import / Export"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    if st.button("← Back to blog", use_container_width=True):
        # Redirect to public app
        st.markdown('<meta http-equiv="refresh" content="0; url=/">', unsafe_allow_html=True)

    if st.button("Log out", use_container_width=True):
        st.session_state.admin_logged_in = False
        # Clear any edit state
        for k in ["editing_post_id", "edit_prefill"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if panel == "Dashboard":
    st.markdown('<h2 style="font-family:Playfair Display,serif;font-weight:400;font-style:italic;color:#e8e8e8;margin-bottom:28px">Dashboard</h2>', unsafe_allow_html=True)

    posts = admin_get_all_posts()
    published = [p for p in posts if p["status"] == "published"]
    drafts    = [p for p in posts if p["status"] == "draft"]
    cats      = set(p["category"] for p in posts)

    # Stats
    c1, c2, c3, c4 = st.columns(4)
    for col, num, label in [
        (c1, len(posts),     "Total Posts"),
        (c2, len(published), "Published"),
        (c3, len(drafts),    "Drafts"),
        (c4, len(cats),      "Categories"),
    ]:
        with col:
            st.markdown(f"""
            <div class="stat-card">
              <div class="stat-num">{num}</div>
              <div class="stat-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Recent posts table
    st.markdown('<div style="background:#1e1e1e;border:1px solid #2a2a2a;padding:28px">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#444;margin-bottom:18px">Recent posts</div>', unsafe_allow_html=True)

    if posts:
        for post in posts[:8]:
            col_title, col_cat, col_status, col_action = st.columns([4, 2, 1, 1])
            with col_title:
                st.markdown(f'<div style="font-size:13px;color:#e8e8e8">{post["title"]}</div><div style="font-size:10px;color:#555;margin-top:2px">{post["author"]} · {fmt_date(post["created_at"])}</div>', unsafe_allow_html=True)
            with col_cat:
                st.markdown(f'<div style="font-size:10px;color:#666;padding-top:6px">{post["category"]}</div>', unsafe_allow_html=True)
            with col_status:
                badge = "badge-pub" if post["status"] == "published" else "badge-dft"
                st.markdown(f'<div style="padding-top:4px"><span class="{badge}">{post["status"]}</span></div>', unsafe_allow_html=True)
            with col_action:
                if st.button("Edit", key=f"dash_edit_{post['id']}"):
                    st.session_state.editing_post_id = post["id"]
                    st.session_state.panel_override = "Write Post"
                    st.rerun()
            st.markdown('<hr style="margin:8px 0;border:none;border-top:1px solid #222"/>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#444;font-size:13px">No posts yet.</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ALL POSTS
# ══════════════════════════════════════════════════════════════════════════════
elif panel == "All Posts":
    st.markdown('<h2 style="font-family:Playfair Display,serif;font-weight:400;font-style:italic;color:#e8e8e8;margin-bottom:28px">All Posts</h2>', unsafe_allow_html=True)

    posts = admin_get_all_posts()

    if not posts:
        st.info("No posts yet. Use 'Write Post' to create your first one.")
    else:
        # Header row
        h1, h2, h3, h4, h5, h6 = st.columns([4, 2, 2, 1, 1, 1])
        for col, label in zip([h1, h2, h3, h4, h5, h6], ["Title", "Category", "Author", "Date", "Status", "Actions"]):
            with col:
                st.markdown(f'<div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;color:#444;padding-bottom:8px;border-bottom:1px solid #222">{label}</div>', unsafe_allow_html=True)

        for post in posts:
            c1, c2, c3, c4, c5, c6, c7 = st.columns([4, 2, 2, 1, 1, 1, 1])
            with c1:
                st.markdown(f'<div style="font-size:13px;color:#e8e8e8;padding-top:4px">{post["title"]}</div><div style="font-size:11px;color:#555">{(post.get("deck") or "")[:55]}{"…" if len(post.get("deck","") or "") > 55 else ""}</div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div style="font-size:11px;color:#666;padding-top:6px">{post["category"]}</div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div style="font-size:11px;color:#666;padding-top:6px">{post["author"]}</div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<div style="font-size:11px;color:#555;padding-top:6px;white-space:nowrap">{fmt_date(post["created_at"])}</div>', unsafe_allow_html=True)
            with c5:
                badge = "badge-pub" if post["status"] == "published" else "badge-dft"
                st.markdown(f'<div style="padding-top:4px"><span class="{badge}">{post["status"]}</span></div>', unsafe_allow_html=True)
            with c6:
                if st.button("Edit", key=f"tbl_edit_{post['id']}"):
                    st.session_state.editing_post_id = post["id"]
                    st.rerun()
            with c7:
                if st.button("Del", key=f"tbl_del_{post['id']}"):
                    st.session_state[f"confirm_del_{post['id']}"] = True
                    st.rerun()

            # Confirm delete
            if st.session_state.get(f"confirm_del_{post['id']}"):
                st.warning(f"Delete **{post['title']}**? This cannot be undone.")
                yes, no = st.columns(2)
                with yes:
                    if st.button("Yes, delete", key=f"yes_del_{post['id']}", type="primary"):
                        admin_delete_post(post["id"])
                        del st.session_state[f"confirm_del_{post['id']}"]
                        st.success("Post deleted.")
                        st.rerun()
                with no:
                    if st.button("Cancel", key=f"no_del_{post['id']}"):
                        del st.session_state[f"confirm_del_{post['id']}"]
                        st.rerun()

            st.markdown('<hr style="margin:6px 0;border:none;border-top:1px solid #1e1e1e"/>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# WRITE / EDIT POST
# ══════════════════════════════════════════════════════════════════════════════
elif panel == "Write Post":
    # Check if editing an existing post
    editing_id = st.session_state.get("editing_post_id")
    existing = None
    if editing_id:
        existing = admin_get_post(editing_id)

    title_label = f"Editing: {existing['title']}" if existing else "Write a new post"
    st.markdown(f'<h2 style="font-family:Playfair Display,serif;font-weight:400;font-style:italic;color:#e8e8e8;margin-bottom:28px">{title_label}</h2>', unsafe_allow_html=True)

    if editing_id and existing:
        if st.button("✕ Cancel edit — start fresh instead"):
            del st.session_state["editing_post_id"]
            st.rerun()

    # Form
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Title *", value=existing["title"] if existing else "", placeholder="Post title")
    with col2:
        author = st.text_input("Author *", value=existing["author"] if existing else "", placeholder="Your name")

    col3, col4 = st.columns(2)
    with col3:
        category = st.selectbox(
            "Category",
            CATEGORIES,
            index=CATEGORIES.index(existing["category"]) if existing and existing["category"] in CATEGORIES else 0,
        )
    with col4:
        read_time = st.text_input("Read time", value=existing.get("read_time","") if existing else "", placeholder="e.g. 8 min read")

    deck = st.text_input(
        "Subtitle / Deck",
        value=existing.get("deck","") if existing else "",
        placeholder="One sentence shown on cards and post page"
    )

    st.markdown('<div style="font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:#555;margin:4px 0">Body * &nbsp;—&nbsp; blank line = new paragraph &nbsp;·&nbsp; ## Heading &nbsp;·&nbsp; > Pull quote</div>', unsafe_allow_html=True)
    body = st.text_area(
        "Body",
        value=existing.get("body","") if existing else "",
        height=380,
        placeholder="Start writing here...\n\n## A subheading\n\n> A pull quote or key line",
        label_visibility="collapsed",
    )

    col5, col6 = st.columns(2)
    with col5:
        status = st.selectbox(
            "Status",
            ["published", "draft"],
            index=0 if not existing else (0 if existing["status"] == "published" else 1),
        )
    with col6:
        featured = st.selectbox(
            "Feature on homepage?",
            ["Yes — show in hero", "No — grid only"],
            index=0 if not existing else (0 if existing.get("featured") else 1),
        )

    st.markdown("<br>", unsafe_allow_html=True)
    save_col, clear_col = st.columns([1, 4])

    with save_col:
        if st.button("💾 Save Post", type="primary", use_container_width=True):
            if not title.strip() or not author.strip() or not body.strip():
                st.error("Title, author and body are required.")
            else:
                data = {
                    "title":     title.strip(),
                    "author":    author.strip(),
                    "category":  category,
                    "deck":      deck.strip(),
                    "body":      body.strip(),
                    "read_time": read_time.strip(),
                    "status":    status,
                    "featured":  featured.startswith("Yes"),
                }
                try:
                    if existing:
                        admin_update_post(editing_id, data)
                        st.success(f"Post updated: **{title}**")
                        del st.session_state["editing_post_id"]
                    else:
                        admin_create_post(data)
                        st.success(f"Post published: **{title}**")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving post: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# IMPORT / EXPORT
# ══════════════════════════════════════════════════════════════════════════════
elif panel == "Import / Export":
    st.markdown('<h2 style="font-family:Playfair Display,serif;font-weight:400;font-style:italic;color:#e8e8e8;margin-bottom:28px">Import / Export</h2>', unsafe_allow_html=True)

    col_exp, col_imp = st.columns(2)

    with col_exp:
        st.markdown("""
        <div style="background:#1e1e1e;border:1px solid #2a2a2a;padding:28px;margin-bottom:16px">
          <div style="font-family:'Playfair Display',serif;font-size:18px;font-style:italic;color:#e8e8e8;margin-bottom:8px">Export all posts</div>
          <div style="font-size:12px;color:#666;line-height:1.7">Download every post as a JSON file. Use this to back up your content or migrate it.</div>
        </div>""", unsafe_allow_html=True)

        posts = admin_get_all_posts()
        if posts:
            export_data = {
                "version": 1,
                "blog": "luvt",
                "exported": datetime.utcnow().isoformat() + "Z",
                "count": len(posts),
                "posts": posts,
            }
            st.download_button(
                label=f"⬇ Download luvt-posts.json ({len(posts)} posts)",
                data=json.dumps(export_data, indent=2, default=str),
                file_name="luvt-posts.json",
                mime="application/json",
                use_container_width=True,
            )
        else:
            st.info("No posts to export yet.")

    with col_imp:
        st.markdown("""
        <div style="background:#1e1e1e;border:1px solid #2a2a2a;padding:28px;margin-bottom:16px">
          <div style="font-family:'Playfair Display',serif;font-size:18px;font-style:italic;color:#e8e8e8;margin-bottom:8px">Import posts</div>
          <div style="font-size:12px;color:#666;line-height:1.7">Upload a JSON file exported from Luvt. Existing posts are never overwritten — only new ones are added.</div>
        </div>""", unsafe_allow_html=True)

        uploaded = st.file_uploader("Choose a .json file", type=["json"], label_visibility="collapsed")
        if uploaded:
            try:
                raw = json.loads(uploaded.read())
                incoming = raw.get("posts", raw) if isinstance(raw, dict) else raw
                if not isinstance(incoming, list):
                    st.error("Invalid format — expected a list of posts.")
                else:
                    existing_posts = admin_get_all_posts()
                    existing_ids = {p["id"] for p in existing_posts}

                    # Strip id so Supabase generates new UUIDs, avoid duplicates by title
                    existing_titles = {p["title"].strip().lower() for p in existing_posts}
                    to_insert = []
                    for p in incoming:
                        if p.get("title","").strip().lower() not in existing_titles:
                            new = {k: v for k, v in p.items() if k not in ("id","created_at","updated_at")}
                            to_insert.append(new)

                    if st.button(f"Import {len(to_insert)} new posts", type="primary"):
                        for p in to_insert:
                            admin_create_post(p)
                        st.success(f"Imported {len(to_insert)} posts. {len(incoming)-len(to_insert)} skipped (already existed).")
                        st.rerun()
            except Exception as e:
                st.error(f"Could not read file: {e}")

    # Storage info
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#1e1e1e;border:1px solid #2a2a2a;padding:28px">
      <div style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#444;margin-bottom:14px">About storage</div>
      <div style="font-size:13px;color:#888;line-height:2">
        Posts are stored in your <strong style="color:#ccc">Supabase</strong> database — not in the browser.
        They are accessible from any device, backed up by Supabase, and will not be lost if you clear your browser.
        The free Supabase tier includes 500 MB of database storage, which is enough for thousands of blog posts.
      </div>
    </div>""", unsafe_allow_html=True)

    # Danger zone
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("⚠ Danger zone"):
        st.warning("This will permanently delete ALL posts from your database. Export a backup first.")
        confirm_text = st.text_input("Type DELETE to confirm", placeholder="DELETE")
        if st.button("Delete all posts", type="primary"):
            if confirm_text.strip() == "DELETE":
                posts = admin_get_all_posts()
                for p in posts:
                    admin_delete_post(p["id"])
                st.success(f"Deleted {len(posts)} posts.")
                st.rerun()
            else:
                st.error("Type DELETE exactly to confirm.")
