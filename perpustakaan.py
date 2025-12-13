import streamlit as st
import pandas as pd
import datetime
from data_manager import init_data, save_data, get_new_id, pinjam_buku, kembalikan_buku

st.set_page_config(
    page_title="Sistem Manajemen Perpustakaan",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'buku_df' not in st.session_state:
    st.session_state.buku_df, st.session_state.anggota_df, st.session_state.pinjam_df = init_data()

def update_and_save(buku_df=None, anggota_df=None, pinjam_df=None):
    if buku_df is not None:
        st.session_state.buku_df = buku_df
    if anggota_df is not None:
        st.session_state.anggota_df = anggota_df
    if pinjam_df is not None:
        st.session_state.pinjam_df = pinjam_df
       
    save_data(st.session_state.buku_df, st.session_state.anggota_df, st.session_state.pinjam_df)
    st.rerun()

def show_dashboard():
    st.title("🏛️ Dashboard Perpustakaan")
    st.markdown("Selamat datang di Sistem Manajemen Perpustakaan. Kelola data Anda menggunakan menu di sebelah kiri.")

    buku_df = st.session_state.buku_df
    anggota_df = st.session_state.anggota_df
    pinjam_df = st.session_state.pinjam_df

    col1, col2, col3, col4 = st.columns(4)
   
    total_stok = buku_df['Jumlah_Stok'].sum() if not buku_df.empty else 0
    total_anggota = len(anggota_df)
    buku_dipinjam = len(pinjam_df[pinjam_df['Status'] == 'Dipinjam'])

    col1.metric("Total Judul Buku", len(buku_df))
    col2.metric("Total Stok Buku", total_stok)
    col3.metric("Anggota Terdaftar", total_anggota)
    col4.metric("Buku Sedang Dipinjam", buku_dipinjam)

    st.divider()

    col_pinjam, col_stok = st.columns(2)