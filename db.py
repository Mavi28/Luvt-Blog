"""
luvt/db.py
Shared Supabase helpers used by both the public app and the admin page.
"""
from __future__ import annotations
import streamlit as st
from supabase import create_client, Client
from typing import Optional


# ── client ────────────────────────────────────────────────────────────────────

@st.cache_resource
def get_public_client() -> Client:
    """Anon key — read-only, respects RLS (published posts only)."""
    return create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["anon_key"],
    )


@st.cache_resource
def get_admin_client() -> Client:
    """Service role key — full access, bypasses RLS."""
    return create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["service_key"],
    )


# ── public queries ─────────────────────────────────────────────────────────────

def get_published_posts(category: Optional[str] = None) -> list[dict]:
    client = get_public_client()
    q = (
        client.table("posts")
        .select("*")
        .eq("status", "published")
        .order("created_at", desc=True)
    )
    if category and category != "All":
        q = q.eq("category", category)
    return q.execute().data or []


def get_post_by_id(post_id: str) -> Optional[dict]:
    client = get_public_client()
    result = (
        client.table("posts")
        .select("*")
        .eq("id", post_id)
        .eq("status", "published")
        .single()
        .execute()
    )
    return result.data


# ── admin queries ──────────────────────────────────────────────────────────────

def admin_get_all_posts() -> list[dict]:
    client = get_admin_client()
    return (
        client.table("posts")
        .select("*")
        .order("created_at", desc=True)
        .execute()
        .data or []
    )


def admin_get_post(post_id: str) -> Optional[dict]:
    client = get_admin_client()
    result = (
        client.table("posts")
        .select("*")
        .eq("id", post_id)
        .single()
        .execute()
    )
    return result.data


def admin_create_post(data: dict) -> dict:
    client = get_admin_client()
    return client.table("posts").insert(data).execute().data[0]


def admin_update_post(post_id: str, data: dict) -> dict:
    client = get_admin_client()
    return (
        client.table("posts")
        .update(data)
        .eq("id", post_id)
        .execute()
        .data[0]
    )


def admin_delete_post(post_id: str) -> None:
    client = get_admin_client()
    client.table("posts").delete().eq("id", post_id).execute()


# ── helpers ────────────────────────────────────────────────────────────────────

CATEGORIES = ["Architecture", "Interiors", "Objects", "Cities", "Essays"]


def fmt_date(ts: str) -> str:
    """Format ISO timestamp to readable date."""
    if not ts:
        return ""
    from datetime import datetime, timezone
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%-d %B %Y")
    except Exception:
        return ts[:10]
