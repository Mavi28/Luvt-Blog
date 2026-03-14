"""
luvt/Home.py  —  Public blog (readers see this)
Run:  streamlit run Home.py
"""
import streamlit as st
from db import get_published_posts, get_post_by_id, CATEGORIES, fmt_date

# ── page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Luvt — Design & Architecture",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;1,400;1,500&family=DM+Sans:wght@300;400;500&display=swap');

/* reset & base */
html, body, [data-testid="stAppViewContainer"] {
    background: #f8f6f1 !important;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* topbar */
.luvt-topbar {
    background: #1e1e1e;
    color: #888;
    padding: 8px 48px;
    font-family: 'DM Sans', sans-serif;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    display: flex;
    justify-content: space-between;
}

/* nav */
.luvt-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 48px;
    height: 72px;
    border-bottom: 1px solid #e8e3d8;
    background: #f8f6f1;
    position: sticky;
    top: 0;
    z-index: 100;
}
.luvt-nav-links { display: flex; gap: 36px; }
.luvt-nav-links a {
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #888;
    text-decoration: none;
    transition: color .2s;
}
.luvt-nav-links a:hover { color: #1e1e1e; }
.luvt-logo { text-align: center; }
.luvt-logo-text {
    font-family: 'Playfair Display', serif;
    font-size: 32px;
    font-weight: 400;
    letter-spacing: 6px;
    color: #1e1e1e;
    line-height: 1;
}
.luvt-logo-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 8px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #888;
    margin-top: 3px;
}
.luvt-nav-right { display: flex; gap: 20px; align-items: center; }
.btn-nav {
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #1e1e1e;
    border: 1px solid #ddd7c8;
    padding: 7px 18px;
    background: transparent;
    cursor: pointer;
    text-decoration: none;
    transition: all .2s;
    display: inline-block;
}
.btn-nav:hover { background: #1e1e1e; color: #f8f6f1; border-color: #1e1e1e; }

/* hero post */
.hero-wrap {
    display: grid;
    grid-template-columns: 1fr 1fr;
    min-height: 500px;
    border-bottom: 1px solid #e8e3d8;
}
.hero-img {
    background: #f0ede5;
    border-right: 1px solid #e8e3d8;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 500px;
}
.hero-content {
    padding: 64px 56px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.hero-cat {
    font-family: 'DM Sans', sans-serif;
    font-size: 10px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #5c7a6a;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.hero-cat::before { content: ''; width: 24px; height: 1px; background: #5c7a6a; display: inline-block; }
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 42px;
    line-height: 1.1;
    font-weight: 400;
    color: #1e1e1e;
    margin-bottom: 18px;
    letter-spacing: -.5px;
}
.hero-deck { font-size: 15px; line-height: 1.85; color: #555; margin-bottom: auto; }
.hero-footer {
    border-top: 1px solid #e8e3d8;
    padding-top: 20px;
    margin-top: 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.post-meta { font-family: 'DM Sans', sans-serif; font-size: 12px; color: #888; }
.post-meta strong { color: #333; font-weight: 500; }

/* card grid */
.card-grid { display: grid; grid-template-columns: repeat(3,1fr); border-bottom: 1px solid #e8e3d8; }
.post-card {
    padding: 32px 28px;
    border-right: 1px solid #e8e3d8;
    border-bottom: 1px solid #e8e3d8;
    cursor: pointer;
    transition: background .2s;
}
.post-card:hover { background: #f0ede5; }
.post-card:nth-child(3n) { border-right: none; }
.card-thumb {
    height: 160px;
    background: #f0ede5;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.card-cat {
    font-family: 'DM Sans', sans-serif;
    font-size: 9px;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #5c7a6a;
    margin-bottom: 8px;
}
.card-title {
    font-family: 'Playfair Display', serif;
    font-size: 19px;
    line-height: 1.35;
    font-weight: 400;
    color: #1e1e1e;
    margin-bottom: 10px;
}
.card-excerpt { font-size: 13px; line-height: 1.8; color: #666; }
.card-footer {
    display: flex;
    justify-content: space-between;
    margin-top: 16px;
    padding-top: 12px;
    border-top: 1px solid #e8e3d8;
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    color: #999;
}

/* single post */
.post-header { padding: 64px 48px 40px; border-bottom: 1px solid #e8e3d8; max-width: 820px; }
.post-cat {
    font-family: 'DM Sans', sans-serif;
    font-size: 10px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #5c7a6a;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.post-cat::before { content: ''; width: 24px; height: 1px; background: #5c7a6a; display: inline-block; }
.post-title {
    font-family: 'Playfair Display', serif;
    font-size: 52px;
    line-height: 1.06;
    font-weight: 400;
    letter-spacing: -1px;
    color: #1e1e1e;
    margin-bottom: 22px;
}
.post-deck { font-size: 19px; line-height: 1.75; color: #555; font-weight: 300; margin-bottom: 28px; }
.post-byline {
    display: flex;
    align-items: center;
    gap: 14px;
    padding-top: 22px;
    border-top: 1px solid #e8e3d8;
}
.byline-av {
    width: 40px; height: 40px; border-radius: 50%;
    background: #e8e3d8;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Playfair Display', serif;
    font-size: 14px; font-style: italic; color: #777;
    flex-shrink: 0;
}
.byline-name { font-size: 14px; font-weight: 500; color: #2e2e2e; }
.byline-date { font-size: 12px; color: #999; margin-top: 2px; }
.post-body-wrap { display: grid; grid-template-columns: 1fr 280px; border-bottom: 1px solid #e8e3d8; }
.post-body {
    padding: 56px 60px 64px 48px;
    border-right: 1px solid #e8e3d8;
    font-family: 'Playfair Display', serif;
    font-size: 17px;
    line-height: 1.95;
    color: #2e2e2e;
    font-weight: 400;
}
.post-sidebar { padding: 56px 32px; display: flex; flex-direction: column; gap: 36px; }
.sidebar-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 9px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #999;
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 1px solid #e8e3d8;
}

/* cat filter bar */
.cat-bar {
    display: flex;
    border-bottom: 1px solid #e8e3d8;
    overflow-x: auto;
    padding: 0 48px;
}
.cat-btn {
    font-family: 'DM Sans', sans-serif;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #999;
    padding: 14px 18px;
    border: none;
    background: transparent;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    white-space: nowrap;
    transition: all .2s;
}
.cat-btn:hover { color: #1e1e1e; }
.cat-btn.active { color: #1e1e1e; border-bottom-color: #1e1e1e; }

/* archive list */
.archive-row {
    display: grid;
    grid-template-columns: 60px 1fr 160px 100px 40px;
    align-items: center;
    padding: 22px 48px;
    border-bottom: 1px solid #e8e3d8;
    cursor: pointer;
    gap: 24px;
    transition: background .2s;
}
.archive-row:hover { background: #f0ede5; }
.ar-num { font-family: 'Playfair Display', serif; font-size: 22px; font-style: italic; color: #ddd7c8; }
.ar-title { font-family: 'Playfair Display', serif; font-size: 20px; font-weight: 400; color: #1e1e1e; }
.ar-excerpt { font-size: 12px; color: #999; margin-top: 3px; }
.ar-cat {
    font-family: 'DM Sans', sans-serif;
    font-size: 9px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #5c7a6a;
    background: #e8f0eb;
    padding: 4px 10px;
    display: inline-block;
}
.ar-date { font-size: 12px; color: #999; text-align: right; }

/* about */
.about-split { display: grid; grid-template-columns: 1fr 1fr; border-bottom: 1px solid #e8e3d8; }
.about-left { padding: 64px 56px 56px 48px; border-right: 1px solid #e8e3d8; }
.about-right { padding: 64px 48px 56px; }
.about-heading {
    font-family: 'Playfair Display', serif;
    font-size: 48px;
    font-weight: 400;
    line-height: 1.08;
    letter-spacing: -1px;
    color: #1e1e1e;
    margin-bottom: 24px;
}
.about-heading em { font-style: italic; color: #555; }
.about-text { font-size: 16px; line-height: 1.95; color: #333; font-weight: 300; }
.about-text p { margin-bottom: 18px; }

/* newsletter */
.nl-bar {
    background: #1e1e1e;
    padding: 48px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 60px;
    align-items: center;
}
.nl-title { font-family: 'Playfair Display', serif; font-size: 28px; font-style: italic; color: #f8f6f1; margin-bottom: 8px; }
.nl-sub { font-size: 13px; color: #888; line-height: 1.7; }

/* footer */
.luvt-footer {
    padding: 36px 48px;
    border-top: 1px solid #e8e3d8;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.footer-copy { font-family: 'DM Sans', sans-serif; font-size: 11px; color: #999; }
.footer-logo { font-family: 'Playfair Display', serif; font-size: 22px; letter-spacing: 4px; color: #555; }

/* page section heading */
.page-heading {
    padding: 64px 48px 40px;
    border-bottom: 1px solid #e8e3d8;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
}
.ph-title { font-family: 'Playfair Display', serif; font-size: 64px; font-weight: 400; font-style: italic; letter-spacing: -2px; color: #1e1e1e; line-height: 1; }
.ph-count { font-family: 'Playfair Display', serif; font-size: 88px; font-weight: 400; color: #e8e3d8; line-height: 1; font-style: italic; }

/* read more btn */
.btn-read {
    font-family: 'DM Sans', sans-serif;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #1e1e1e;
    border: none;
    border-bottom: 1px solid #1e1e1e;
    padding: 0 0 2px;
    background: none;
    cursor: pointer;
    transition: color .2s;
}
.btn-read:hover { color: #5c7a6a; border-color: #5c7a6a; }

/* streamlit button overrides */
.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    border-radius: 0 !important;
}
</style>
""", unsafe_allow_html=True)

SVG_DECO = [
    '<svg width="100" height="100" viewBox="0 0 100 100"><rect x="10" y="10" width="80" height="80" fill="none" stroke="#ddd7c8" stroke-width=".8"/><rect x="24" y="24" width="52" height="52" fill="#f0ede5" stroke="#e8e3d8" stroke-width=".8"/><line x1="10" y1="50" x2="90" y2="50" stroke="#e8e3d8" stroke-width=".5"/><line x1="50" y1="10" x2="50" y2="90" stroke="#e8e3d8" stroke-width=".5"/></svg>',
    '<svg width="100" height="100" viewBox="0 0 100 100"><circle cx="50" cy="50" r="38" fill="none" stroke="#ddd7c8" stroke-width=".8"/><circle cx="50" cy="50" r="20" fill="#f0ede5" stroke="#e8e3d8" stroke-width=".8"/><circle cx="50" cy="50" r="5" fill="#ddd7c8"/></svg>',
    '<svg width="100" height="100" viewBox="0 0 100 100"><path d="M10 80 Q24 12 50 34 Q76 56 90 12" fill="none" stroke="#ddd7c8" stroke-width="1.2"/><circle cx="50" cy="34" r="7" fill="none" stroke="#e8e3d8" stroke-width=".8"/></svg>',
    '<svg width="100" height="100" viewBox="0 0 100 100"><polygon points="50,8 92,82 8,82" fill="none" stroke="#ddd7c8" stroke-width=".8"/><polygon points="50,28 74,72 26,72" fill="#f0ede5" stroke="#e8e3d8" stroke-width=".8"/></svg>',
]

def initials(name: str) -> str:
    return "".join(w[0] for w in name.split() if w)[:2].upper()

# ── session state ──────────────────────────────────────────────────────────────
if "view" not in st.session_state:
    st.session_state.view = "home"       # home | post | archive | about
if "current_post_id" not in st.session_state:
    st.session_state.current_post_id = None
if "home_filter" not in st.session_state:
    st.session_state.home_filter = "All"
if "archive_filter" not in st.session_state:
    st.session_state.archive_filter = "All"

def go(view, post_id=None):
    st.session_state.view = view
    if post_id:
        st.session_state.current_post_id = post_id
    st.rerun()

# ── topbar + nav ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="luvt-topbar">
  <span>Design &amp; Architecture — Est. 2026</span>
  <span style="font-family:'Playfair Display',serif;font-style:italic;font-size:12px;letter-spacing:1px">Slow looking, honest writing</span>
</div>
""", unsafe_allow_html=True)

n1, n2, n3 = st.columns([1, 1, 1])
with n1:
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Home", key="nav_home", use_container_width=True):
            go("home")
    with c2:
        if st.button("All Posts", key="nav_archive", use_container_width=True):
            go("archive")
    with c3:
        if st.button("About", key="nav_about", use_container_width=True):
            go("about")
with n2:
    st.markdown("""
    <div style="text-align:center;padding:12px 0">
      <div class="luvt-logo-text">Luvt</div>
      <div class="luvt-logo-sub">Design &amp; Architecture</div>
    </div>""", unsafe_allow_html=True)
with n3:
    pass  # intentionally empty — nav is left-weighted

st.markdown('<hr style="margin:0;border:none;border-top:1px solid #e8e3d8"/>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HOME VIEW
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.view == "home":
    posts = get_published_posts()
    feat = [p for p in posts if p.get("featured")]
    hero = feat[0] if feat else (posts[0] if posts else None)

    if hero:
        col_img, col_text = st.columns(2)
        with col_img:
            st.markdown(f"""
            <div style="background:#f0ede5;min-height:480px;border-right:1px solid #e8e3d8;
                        display:flex;align-items:center;justify-content:center">
              {SVG_DECO[0]}
            </div>""", unsafe_allow_html=True)
        with col_text:
            st.markdown(f"""
            <div style="padding:60px 52px">
              <div class="hero-cat">{hero['category']}</div>
              <div class="hero-title">{hero['title']}</div>
              <div class="hero-deck">{hero.get('deck','')}</div>
              <div style="border-top:1px solid #e8e3d8;padding-top:20px;margin-top:32px;
                          display:flex;justify-content:space-between;align-items:center">
                <div class="post-meta">
                  <strong>{hero['author']}</strong> · {fmt_date(hero['created_at'])}
                  {' · ' + hero['read_time'] if hero.get('read_time') else ''}
                </div>
              </div>
            </div>""", unsafe_allow_html=True)
            st.write("")
            if st.button("Read post →", key=f"hero_read_{hero['id']}"):
                go("post", hero["id"])
    else:
        st.info("No published posts yet. Add your first post from the Admin panel.")

    # Category filter
    st.markdown('<div class="cat-bar">', unsafe_allow_html=True)
    filter_cols = st.columns(len(CATEGORIES) + 1)
    with filter_cols[0]:
        if st.button("All", key="f_all"):
            st.session_state.home_filter = "All"; st.rerun()
    for i, cat in enumerate(CATEGORIES):
        with filter_cols[i + 1]:
            if st.button(cat, key=f"f_{cat}"):
                st.session_state.home_filter = cat; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Post cards
    used = {hero["id"]} if hero else set()
    filt = st.session_state.home_filter
    grid_posts = [p for p in posts if p["id"] not in used and (filt == "All" or p["category"] == filt)]

    if grid_posts:
        for row_start in range(0, min(len(grid_posts), 6), 3):
            row = grid_posts[row_start:row_start + 3]
            cols = st.columns(3)
            for i, post in enumerate(row):
                with cols[i]:
                    st.markdown(f"""
                    <div class="post-card">
                      <div class="card-thumb">{SVG_DECO[i % 4]}</div>
                      <div class="card-cat">{post['category']}</div>
                      <div class="card-title">{post['title']}</div>
                      <div class="card-excerpt">{post.get('deck','')}</div>
                      <div class="card-footer">
                        <span>{post['author']}</span>
                        <span>{post.get('read_time', fmt_date(post['created_at']))}</span>
                      </div>
                    </div>""", unsafe_allow_html=True)
                    if st.button("Read →", key=f"card_{post['id']}"):
                        go("post", post["id"])
    else:
        st.markdown('<div style="padding:40px 48px;color:#999;font-family:DM Sans,sans-serif">No posts in this category yet.</div>', unsafe_allow_html=True)

    # Newsletter
    st.markdown("""
    <div class="nl-bar">
      <div>
        <div class="nl-title">Stay in the loop</div>
        <p class="nl-sub">New posts on design and architecture, delivered when they're ready.</p>
      </div>
      <div style="color:#888;font-size:13px;font-style:italic;font-family:'Playfair Display',serif">
        Newsletter coming soon.
      </div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SINGLE POST VIEW
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.view == "post":
    post = get_post_by_id(st.session_state.current_post_id)
    if not post:
        st.error("Post not found.")
        if st.button("← Back to home"):
            go("home")
    else:
        # Breadcrumb
        bc1, bc2 = st.columns([6, 1])
        with bc1:
            st.markdown(f'<div style="padding:14px 48px;font-family:DM Sans,sans-serif;font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#999;border-bottom:1px solid #e8e3d8"><span style="cursor:pointer" onclick="">Home</span> › {post["category"]}</div>', unsafe_allow_html=True)
        with bc2:
            if st.button("← Back", key="post_back"):
                go("home")

        # Header
        st.markdown(f"""
        <div class="post-header">
          <div class="post-cat">{post['category']}</div>
          <h1 class="post-title">{post['title']}</h1>
          <p class="post-deck">{post.get('deck','')}</p>
          <div class="post-byline">
            <div class="byline-av">{initials(post['author'])}</div>
            <div>
              <div class="byline-name">{post['author']}</div>
              <div class="byline-date">{fmt_date(post['created_at'])}{' · ' + post['read_time'] if post.get('read_time') else ''}</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        # Hero image placeholder
        st.markdown(f"""
        <div style="height:400px;background:#f0ede5;border-bottom:1px solid #e8e3d8;
                    display:flex;align-items:center;justify-content:center">
          {SVG_DECO[0]}
        </div>""", unsafe_allow_html=True)

        # Body + sidebar
        body_col, side_col = st.columns([3, 1])
        with body_col:
            # Parse body text into HTML
            body_html = ""
            for line in post.get("body", "").split("\n"):
                l = line.strip()
                if not l:
                    body_html += "<br>"
                elif l.startswith("## "):
                    body_html += f'<h2 style="font-family:Playfair Display,serif;font-size:28px;font-weight:400;font-style:italic;color:#1e1e1e;margin:44px 0 18px;letter-spacing:-.3px">{l[3:]}</h2>'
                elif l.startswith("> "):
                    body_html += f'<blockquote style="border-left:2px solid #e8e3d8;margin:36px 0;padding:4px 0 4px 28px;font-size:22px;font-style:italic;color:#777;line-height:1.5">{l[2:]}</blockquote>'
                else:
                    body_html += f'<p style="font-size:17px;line-height:1.95;color:#2e2e2e;margin-bottom:26px;font-weight:300">{l}</p>'

            st.markdown(f"""
            <div style="padding:56px 56px 64px 48px;border-right:1px solid #e8e3d8;font-family:'DM Sans',sans-serif">
              {body_html}
            </div>""", unsafe_allow_html=True)

        with side_col:
            st.markdown('<div style="padding:56px 28px">', unsafe_allow_html=True)
            st.markdown('<div class="sidebar-label">About Luvt</div>', unsafe_allow_html=True)
            st.markdown("""
            <div style="background:#f0ede5;padding:20px;border:1px solid #e8e3d8;margin-bottom:32px">
              <div style="font-family:'Playfair Display',serif;font-size:18px;font-style:italic;color:#1e1e1e;margin-bottom:6px">Luvt</div>
              <p style="font-size:12px;color:#666;line-height:1.7">A blog about design and architecture. Written slowly, with attention.</p>
            </div>""", unsafe_allow_html=True)

            # More posts
            all_posts = get_published_posts()
            related = [p for p in all_posts if p["id"] != post["id"]][:3]
            if related:
                st.markdown('<div class="sidebar-label">More posts</div>', unsafe_allow_html=True)
                for rp in related:
                    st.markdown(f"""
                    <div style="margin-bottom:16px;padding-bottom:16px;border-bottom:1px solid #e8e3d8;cursor:pointer">
                      <div style="font-family:'DM Sans',sans-serif;font-size:9px;letter-spacing:2px;text-transform:uppercase;color:#5c7a6a;margin-bottom:4px">{rp['category']}</div>
                      <div style="font-family:'Playfair Display',serif;font-size:14px;color:#2e2e2e;line-height:1.4">{rp['title']}</div>
                    </div>""", unsafe_allow_html=True)
                    if st.button("Read", key=f"rel_{rp['id']}"):
                        go("post", rp["id"])
            st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ARCHIVE VIEW
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.view == "archive":
    filt = st.session_state.archive_filter
    posts = get_published_posts(None if filt == "All" else filt)

    st.markdown(f"""
    <div class="page-heading">
      <div>
        <div class="ph-title">All Posts</div>
        <div style="font-family:'DM Sans',sans-serif;font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#999;margin-top:8px">{filt if filt != 'All' else 'Every piece, in order'}</div>
      </div>
      <div class="ph-count">{len(posts)}</div>
    </div>""", unsafe_allow_html=True)

    # Filter buttons
    filter_cols = st.columns(len(CATEGORIES) + 1)
    with filter_cols[0]:
        if st.button("All", key="af_all"):
            st.session_state.archive_filter = "All"; st.rerun()
    for i, cat in enumerate(CATEGORIES):
        with filter_cols[i + 1]:
            if st.button(cat, key=f"af_{cat}"):
                st.session_state.archive_filter = cat; st.rerun()

    st.markdown('<div style="border-top:1px solid #e8e3d8"></div>', unsafe_allow_html=True)

    if posts:
        for i, post in enumerate(posts):
            col_num, col_text, col_cat, col_date, col_arrow = st.columns([1, 5, 2, 2, 1])
            with col_num:
                st.markdown(f'<div class="ar-num">{str(i+1).zfill(2)}</div>', unsafe_allow_html=True)
            with col_text:
                st.markdown(f"""
                <div>
                  <div class="ar-title">{post['title']}</div>
                  <div class="ar-excerpt">{(post.get('deck','') or '')[:80]}{'…' if len(post.get('deck','') or '') > 80 else ''}</div>
                </div>""", unsafe_allow_html=True)
            with col_cat:
                st.markdown(f'<div style="padding-top:8px"><span class="ar-cat">{post["category"]}</span></div>', unsafe_allow_html=True)
            with col_date:
                st.markdown(f'<div class="ar-date" style="padding-top:10px">{fmt_date(post["created_at"])}</div>', unsafe_allow_html=True)
            with col_arrow:
                if st.button("→", key=f"arc_{post['id']}"):
                    go("post", post["id"])
            st.markdown('<hr style="margin:0;border:none;border-top:1px solid #e8e3d8"/>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="padding:40px 48px;color:#999">No posts yet.</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ABOUT VIEW
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.view == "about":
    left, right = st.columns(2)
    with left:
        st.markdown("""
        <div class="about-left">
          <div style="font-family:'DM Sans',sans-serif;font-size:10px;letter-spacing:3px;text-transform:uppercase;color:#5c7a6a;margin-bottom:18px;display:flex;align-items:center;gap:10px"><span style="display:inline-block;width:24px;height:1px;background:#5c7a6a"></span>About Luvt</div>
          <h1 class="about-heading">Writing about design <em>honestly</em></h1>
          <div class="about-text">
            <p>Luvt is a blog about design and architecture — not the kind that gets photographed for Instagram, but the kind that shapes how we actually live, move through space, and understand the world.</p>
            <p>Every post is written slowly, with real attention to the subject. We are not interested in trends or rankings. We are interested in what things are actually like, and why.</p>
            <p>Started in 2026. Written independently. No advertising, no affiliates, no agenda beyond honest observation.</p>
          </div>
        </div>""", unsafe_allow_html=True)
    with right:
        st.markdown("""
        <div class="about-right">
          <div style="border:1px solid #e8e3d8;margin-bottom:32px">
            <div style="padding:24px 28px;border-bottom:1px solid #e8e3d8;display:flex;gap:16px">
              <div style="font-family:'Playfair Display',serif;font-size:26px;font-style:italic;color:#ddd7c8;width:28px">01</div>
              <div><div style="font-family:'Playfair Display',serif;font-size:17px;color:#1e1e1e;margin-bottom:4px">Slow writing</div><div style="font-size:12px;color:#888;line-height:1.7">Every post takes as long as it needs.</div></div>
            </div>
            <div style="padding:24px 28px;border-bottom:1px solid #e8e3d8;display:flex;gap:16px">
              <div style="font-family:'Playfair Display',serif;font-size:26px;font-style:italic;color:#ddd7c8;width:28px">02</div>
              <div><div style="font-family:'Playfair Display',serif;font-size:17px;color:#1e1e1e;margin-bottom:4px">First-hand attention</div><div style="font-size:12px;color:#888;line-height:1.7">We only write about things we've encountered directly.</div></div>
            </div>
            <div style="padding:24px 28px;display:flex;gap:16px">
              <div style="font-family:'Playfair Display',serif;font-size:26px;font-style:italic;color:#ddd7c8;width:28px">03</div>
              <div><div style="font-family:'Playfair Display',serif;font-size:17px;color:#1e1e1e;margin-bottom:4px">No advertising</div><div style="font-size:12px;color:#888;line-height:1.7">Luvt is independent. No brands, no affiliates.</div></div>
            </div>
          </div>
          <div style="background:#1e1e1e;padding:28px 32px">
            <div style="font-family:'DM Sans',sans-serif;font-size:9px;letter-spacing:3px;text-transform:uppercase;color:#555;margin-bottom:10px">Get in touch</div>
            <div style="font-family:'Playfair Display',serif;font-size:22px;font-style:italic;color:#f8f6f1">hello@luvt.co</div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="nl-bar">
      <div>
        <div class="nl-title">Get new posts by email</div>
        <p class="nl-sub">When there's something worth reading, you'll hear about it.</p>
      </div>
      <div style="color:#555;font-size:13px;font-style:italic;font-family:'Playfair Display',serif">Newsletter coming soon.</div>
    </div>""", unsafe_allow_html=True)


# ── footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="luvt-footer">
  <div class="footer-copy">© 2026 Luvt. All rights reserved.</div>
  <div class="footer-logo">Luvt</div>
  <div class="footer-copy">Design &amp; Architecture</div>
</div>""", unsafe_allow_html=True)
