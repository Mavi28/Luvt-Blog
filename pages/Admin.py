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
    upload_cover_image, delete_cover_image,
    CATEGORIES, fmt_date,
)

st.set_page_config(
    page_title="Luvt Admin",
    page_icon="⚙",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;1,400&family=DM+Sans:wght@300;400;500&display=swap');

html { font-size: 14px !important; }
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] * { font-size: inherit; }
.stMarkdown p, .stMarkdown li, .stMarkdown span { font-size: 13px !important; }
.stButton > button { font-size: 10px !important; padding: 6px 14px !important; }

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
.stat-card {
    background: #1e1e1e;
    border: 1px solid #2a2a2a;
    padding: 24px;
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
.badge-pub { background:#1a3326;color:#5dcca0;font-size:9px;letter-spacing:2px;text-transform:uppercase;padding:3px 9px;display:inline-block; }
.badge-dft { background:#2a2616;color:#c4a040;font-size:9px;letter-spacing:2px;text-transform:uppercase;padding:3px 9px;display:inline-block; }

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

/* image upload area */
[data-testid="stFileUploader"] {
    background: #1e1e1e !important;
    border: 1px dashed #2a2a2a !important;
    border-radius: 0 !important;
    padding: 12px !important;
}
</style>
""", unsafe_allow_html=True)


# ── Auth ───────────────────────────────────────────────────────────────────────
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

if not st.session_state.admin_logged_in:
    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.markdown('<div style="background:#141414;border:1px solid #222;padding:48px;margin-top:60px">', unsafe_allow_html=True)
        st.markdown('<div class="login-logo">Luvt</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">Admin Panel</div>', unsafe_allow_html=True)
        username = st.text_input("Username", key="login_user", placeholder="your username")
        password = st.text_input("Password", type="password", key="login_pass", placeholder="••••••••••")
        if st.button("Sign in", use_container_width=True):
            if check_credentials(username, password):
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Incorrect username or password.")
        st.markdown('<div style="font-size:11px;color:#333;text-align:center;margin-top:16px">Credentials set in Streamlit secrets — not in this file.</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:Playfair Display,serif;font-size:22px;letter-spacing:4px;color:#e8e8e8 !important;padding:8px 0 24px;border-bottom:1px solid #222;margin-bottom:20px">Luvt</div>', unsafe_allow_html=True)
    panel = st.radio("Navigate", ["Dashboard", "All Posts", "Write Post", "Import / Export"], label_visibility="collapsed")
    st.markdown("---")
    if st.button("Log out", use_container_width=True):
        st.session_state.admin_logged_in = False
        for k in ["editing_post_id"]:
            st.session_state.pop(k, None)
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

    c1, c2, c3, c4 = st.columns(4)
    for col, num, label in [(c1,len(posts),"Total Posts"),(c2,len(published),"Published"),(c3,len(drafts),"Drafts"),(c4,len(cats),"Categories")]:
        with col:
            st.markdown(f'<div class="stat-card"><div class="stat-num">{num}</div><div class="stat-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="background:#1e1e1e;border:1px solid #2a2a2a;padding:28px">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#444;margin-bottom:18px">Recent posts</div>', unsafe_allow_html=True)

    if posts:
        for post in posts[:8]:
            c_t, c_cat, c_s, c_a = st.columns([4, 2, 1, 1])
            with c_t:
                st.markdown(f'<div style="font-size:13px;color:#e8e8e8">{post["title"]}</div><div style="font-size:10px;color:#555">{post["author"]} · {fmt_date(post["created_at"])}</div>', unsafe_allow_html=True)
            with c_cat:
                st.markdown(f'<div style="font-size:10px;color:#666;padding-top:6px">{post["category"]}</div>', unsafe_allow_html=True)
            with c_s:
                st.markdown(f'<div style="padding-top:4px"><span class="{"badge-pub" if post["status"]=="published" else "badge-dft"}">{post["status"]}</span></div>', unsafe_allow_html=True)
            with c_a:
                if st.button("Edit", key=f"dash_edit_{post['id']}"):
                    st.session_state.editing_post_id = post["id"]
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
        for post in posts:
            c1, c2, c3, c4, c5, c6 = st.columns([4, 2, 2, 1, 1, 1])
            with c1:
                st.markdown(f'<div style="font-size:13px;color:#e8e8e8">{post["title"]}</div><div style="font-size:11px;color:#555">{(post.get("deck") or "")[:55]}{"…" if len(post.get("deck","") or "") > 55 else ""}</div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div style="font-size:11px;color:#666;padding-top:6px">{post["category"]}</div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div style="font-size:11px;color:#666;padding-top:6px">{post["author"]}</div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<span class="{"badge-pub" if post["status"]=="published" else "badge-dft"}">{post["status"]}</span>', unsafe_allow_html=True)
            with c5:
                if st.button("Edit", key=f"tbl_edit_{post['id']}"):
                    st.session_state.editing_post_id = post["id"]
                    st.rerun()
            with c6:
                if st.button("Del", key=f"tbl_del_{post['id']}"):
                    st.session_state[f"confirm_del_{post['id']}"] = True

            if st.session_state.get(f"confirm_del_{post['id']}"):
                st.warning(f"Delete **{post['title']}**? Cannot be undone.")
                yes, no = st.columns(2)
                with yes:
                    if st.button("Yes, delete", key=f"yes_del_{post['id']}", type="primary"):
                        if post.get("cover_image_url"):
                            delete_cover_image(post["cover_image_url"])
                        admin_delete_post(post["id"])
                        del st.session_state[f"confirm_del_{post['id']}"]
                        st.success("Deleted.")
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
    editing_id = st.session_state.get("editing_post_id")
    existing = admin_get_post(editing_id) if editing_id else None

    title_label = f"Editing: {existing['title']}" if existing else "Write a new post"
    st.markdown(f'<h2 style="font-family:Playfair Display,serif;font-weight:400;font-style:italic;color:#e8e8e8;margin-bottom:28px">{title_label}</h2>', unsafe_allow_html=True)

    if editing_id and existing:
        if st.button("✕ Cancel — write new post instead"):
            del st.session_state["editing_post_id"]
            st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Title *", value=existing["title"] if existing else "", placeholder="Post title")
    with col2:
        author = st.text_input("Author *", value=existing["author"] if existing else "", placeholder="Your name")

    col3, col4 = st.columns(2)
    with col3:
        category = st.selectbox("Category", CATEGORIES,
            index=CATEGORIES.index(existing["category"]) if existing and existing["category"] in CATEGORIES else 0)
    with col4:
        read_time = st.text_input("Read time", value=existing.get("read_time","") if existing else "", placeholder="e.g. 8 min read")

    deck = st.text_input("Subtitle / Deck",
        value=existing.get("deck","") if existing else "",
        placeholder="One sentence shown on cards and post page")

    st.markdown('<div style="font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:#555;margin:4px 0">Body * — blank line = paragraph · ## Heading · > Pull quote</div>', unsafe_allow_html=True)
    body = st.text_area("Body", value=existing.get("body","") if existing else "", height=380,
        placeholder="Start writing here...\n\n## A subheading\n\n> A pull quote",
        label_visibility="collapsed")

    # ── IMAGE UPLOAD ──────────────────────────────────────────────────────────
    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:#555;margin-bottom:8px">Cover Image</div>', unsafe_allow_html=True)

    current_img = existing.get("cover_image_url") if existing else None

    # Show existing image if editing
    if current_img:
        img_col, remove_col = st.columns([3, 1])
        with img_col:
            st.image(current_img, caption="Current cover image", use_container_width=True)
        with remove_col:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if st.button("🗑 Remove image", key="remove_img"):
                delete_cover_image(current_img)
                admin_update_post(editing_id, {"cover_image_url": None})
                st.success("Image removed.")
                st.rerun()

    uploaded_img = st.file_uploader(
        "Upload cover image",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
        help="Recommended: 1200×800px or wider. JPG, PNG or WebP."
    )

    if uploaded_img:
        st.image(uploaded_img, caption="Preview — will be uploaded on save", use_container_width=True)

    # ── STATUS / FEATURED ─────────────────────────────────────────────────────
    col5, col6 = st.columns(2)
    with col5:
        status = st.selectbox("Status", ["published", "draft"],
            index=0 if not existing else (0 if existing["status"] == "published" else 1))
    with col6:
        featured = st.selectbox("Feature on homepage?",
            ["Yes — show in hero", "No — grid only"],
            index=0 if not existing else (0 if existing.get("featured") else 1))

    st.markdown("<br>", unsafe_allow_html=True)
    save_col, _ = st.columns([1, 4])
    with save_col:
        if st.button("💾 Save Post", type="primary", use_container_width=True):
            if not title.strip() or not author.strip() or not body.strip():
                st.error("Title, author and body are required.")
            else:
                # Upload image first if provided
                cover_url = current_img  # keep existing by default
                if uploaded_img:
                    with st.spinner("Uploading image..."):
                        try:
                            cover_url = upload_cover_image(
                                uploaded_img.getvalue(),
                                uploaded_img.name,
                                uploaded_img.type,
                            )
                            # Delete old image from storage if replacing
                            if current_img and current_img != cover_url:
                                delete_cover_image(current_img)
                        except Exception as e:
                            st.error(f"Image upload failed: {e}")
                            st.stop()

                data = {
                    "title":           title.strip(),
                    "author":          author.strip(),
                    "category":        category,
                    "deck":            deck.strip(),
                    "body":            body.strip(),
                    "read_time":       read_time.strip(),
                    "status":          status,
                    "featured":        featured.startswith("Yes"),
                    "cover_image_url": cover_url,
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
        st.markdown('<div style="background:#1e1e1e;border:1px solid #2a2a2a;padding:28px;margin-bottom:16px"><div style="font-family:Playfair Display,serif;font-size:18px;font-style:italic;color:#e8e8e8;margin-bottom:8px">Export all posts</div><div style="font-size:12px;color:#666;line-height:1.7">Download every post as a JSON backup file.</div></div>', unsafe_allow_html=True)
        posts = admin_get_all_posts()
        if posts:
            st.download_button(
                label=f"⬇ Download luvt-posts.json ({len(posts)} posts)",
                data=json.dumps({"version":1,"blog":"luvt","exported":datetime.utcnow().isoformat()+"Z","posts":posts}, indent=2, default=str),
                file_name="luvt-posts.json",
                mime="application/json",
                use_container_width=True,
            )
        else:
            st.info("No posts to export yet.")

    with col_imp:
        st.markdown('<div style="background:#1e1e1e;border:1px solid #2a2a2a;padding:28px;margin-bottom:16px"><div style="font-family:Playfair Display,serif;font-size:18px;font-style:italic;color:#e8e8e8;margin-bottom:8px">Import posts</div><div style="font-size:12px;color:#666;line-height:1.7">Upload a JSON file exported from Luvt. New posts are merged in — existing ones are never overwritten.</div></div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Choose a .json file", type=["json"], label_visibility="collapsed")
        if uploaded:
            try:
                raw = json.loads(uploaded.read())
                incoming = raw.get("posts", raw) if isinstance(raw, dict) else raw
                existing_posts = admin_get_all_posts()
                existing_titles = {p["title"].strip().lower() for p in existing_posts}
                to_insert = [
                    {k: v for k, v in p.items() if k not in ("id","created_at","updated_at")}
                    for p in incoming
                    if p.get("title","").strip().lower() not in existing_titles
                ]
                if st.button(f"Import {len(to_insert)} new posts", type="primary"):
                    for p in to_insert:
                        admin_create_post(p)
                    st.success(f"Imported {len(to_insert)} posts.")
                    st.rerun()
            except Exception as e:
                st.error(f"Could not read file: {e}")

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("⚠ Danger zone — delete all posts"):
        st.warning("Permanently deletes ALL posts. Export a backup first.")
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
