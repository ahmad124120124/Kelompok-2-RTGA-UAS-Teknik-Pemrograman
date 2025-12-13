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

    with col_pinjam:
        st.subheader("📊 Transaksi Peminjaman Terbaru")
        if not pinjam_df.empty:
            display_df = pinjam_df.tail(10).sort_values(by='Tanggal_Pinjam', ascending=False)
           
            display_df = display_df.merge(buku_df[['ID_Buku', 'Judul']], on='ID_Buku', how='left')
            display_df = display_df.merge(anggota_df[['ID_Anggota', 'Nama']], on='ID_Anggota', how='left')

            st.dataframe(display_df[[
                'ID_Pinjam', 'Judul', 'Nama', 'Tanggal_Pinjam', 'Status'
            ]], use_container_width=True)
        else:
            st.info("Belum ada data peminjaman.")

def show_buku():
    st.title("📚 Manajemen Buku")
    buku_df = st.session_state.buku_df
   
    tab1, tab2, tab3 = st.tabs(["Lihat & Cari", "Tambah Buku", "Edit & Hapus"])
   
    with tab1:
        st.subheader("Daftar Semua Buku")
        st.dataframe(buku_df, use_container_width=True)

    with tab2:
        st.subheader("Form Tambah Buku Baru")
        with st.form("tambah_buku"):
            judul = st.text_input("Judul", key="t_judul")
            penulis = st.text_input("Penulis", key="t_penulis")
            tahun = st.number_input("Tahun Terbit", min_value=1500, max_value=2050, step=1, value=datetime.date.today().year, key="t_tahun")
            stok = st.number_input("Jumlah Stok", min_value=1, step=1, key="t_stok")
            submitted = st.form_submit_button("Tambah Buku", type="primary")

            if submitted:
                new_id = get_new_id(buku_df, 'ID_Buku')
                new_row = pd.DataFrame([{
                    'ID_Buku': new_id, 'Judul': judul, 'Penulis': penulis,
                    'Tahun_Terbit': int(tahun), 'Jumlah_Stok': int(stok)
                }])
                st.success(f"Buku '{judul}' berhasil ditambahkan dengan ID {new_id}!")
                update_and_save(buku_df=pd.concat([buku_df, new_row], ignore_index=True))

    with tab3:
        st.subheader("Edit/Hapus Buku")
       
        book_options = buku_df['ID_Buku'].astype(str) + ' - ' + buku_df['Judul']
        selected_book = st.selectbox("Pilih Buku yang Akan Diedit/Dihapus", book_options.tolist(), index=None)
       
        if selected_book:
            selected_id = int(selected_book.split(' - ')[0])
            book_data = buku_df[buku_df['ID_Buku'] == selected_id].iloc[0]
           
            st.markdown("---")
            st.text(f"Mengedit Buku ID: {selected_id}")

            with st.form("edit_buku"):
                e_judul = st.text_input("Judul", value=book_data['Judul'])
                e_penulis = st.text_input("Penulis", value=book_data['Penulis'])
                e_tahun = st.number_input("Tahun Terbit", min_value=1500, max_value=2050, step=1, value=book_data['Tahun_Terbit'])
                e_stok = st.number_input("Jumlah Stok", min_value=0, step=1, value=book_data['Jumlah_Stok'])

                col_edit, col_delete = st.columns(2)
               
                with col_edit:
                    edited = st.form_submit_button("Simpan Perubahan", type="primary")
                with col_delete:
                    deleted = st.form_submit_button("Hapus Buku", type="secondary")

                if edited:
                    idx = buku_df[buku_df['ID_Buku'] == selected_id].index[0]
                    buku_df.loc[idx, 'Judul'] = e_judul
                    buku_df.loc[idx, 'Penulis'] = e_penulis
                    buku_df.loc[idx, 'Tahun_Terbit'] = int(e_tahun)
                    buku_df.loc[idx, 'Jumlah_Stok'] = int(e_stok)
                    st.success(f"Buku '{e_judul}' (ID {selected_id}) berhasil diperbarui!")
                    update_and_save(buku_df=buku_df)

                if deleted:
                    buku_df = buku_df[buku_df['ID_Buku'] != selected_id].reset_index(drop=True)
                    st.warning(f"Buku (ID {selected_id}) berhasil dihapus!")
                    update_and_save(buku_df=buku_df)

def show_anggota():
    st.title("👤 Manajemen Anggota")
    anggota_df = st.session_state.anggota_df
   
    tab1, tab2, tab3 = st.tabs(["Lihat & Cari", "Tambah Anggota", "Edit & Hapus"])

    with tab1:
        st.subheader("Daftar Semua Anggota")
        st.dataframe(anggota_df, use_container_width=True)

    with tab2:
        st.subheader("Form Tambah Anggota Baru")
        with st.form("tambah_anggota"):
            nama = st.text_input("Nama", key="t_nama_a")
            alamat = st.text_area("Alamat", key="t_alamat_a")
            telp = st.text_input("Nomor Telepon", key="t_telp_a")
            submitted = st.form_submit_button("Tambah Anggota", type="primary")

            if submitted:
                new_id = get_new_id(anggota_df, 'ID_Anggota')
                new_row = pd.DataFrame([{
                    'ID_Anggota': new_id, 'Nama': nama, 'Alamat': alamat, 'No_Telp': telp
                }])
                st.success(f"Anggota '{nama}' berhasil ditambahkan dengan ID {new_id}!")
                update_and_save(anggota_df=pd.concat([anggota_df, new_row], ignore_index=True))

    with tab3:
        st.subheader("Edit/Hapus Anggota")
       
        member_options = anggota_df['ID_Anggota'].astype(str) + ' - ' + anggota_df['Nama']
        selected_member = st.selectbox("Pilih Anggota yang Akan Diedit/Dihapus", member_options.tolist(), index=None)
       
        if selected_member:
            selected_id = int(selected_member.split(' - ')[0])
            member_data = anggota_df[anggota_df['ID_Anggota'] == selected_id].iloc[0]
           
            st.markdown("---")
            st.text(f"Mengedit Anggota ID: {selected_id}")
  
            with st.form("edit_anggota"):
                e_nama = st.text_input("Nama", value=member_data['Nama'])
                e_alamat = st.text_area("Alamat", value=member_data['Alamat'])
                e_telp = st.text_input("Nomor Telepon", value=member_data['No_Telp'])

                col_edit, col_delete = st.columns(2)
               
                with col_edit:
                    edited = st.form_submit_button("Simpan Perubahan", type="primary")
                with col_delete:
                    deleted = st.form_submit_button("Hapus Anggota", type="secondary")

                if edited:
                    idx = anggota_df[anggota_df['ID_Anggota'] == selected_id].index[0]
                    anggota_df.loc[idx, 'Nama'] = e_nama
                    anggota_df.loc[idx, 'Alamat'] = e_alamat
                    anggota_df.loc[idx, 'No_Telp'] = e_telp
                    st.success(f"Anggota '{e_nama}' (ID {selected_id}) berhasil diperbarui!")
                    update_and_save(anggota_df=anggota_df)

                if deleted:
                    anggota_df = anggota_df[anggota_df['ID_Anggota'] != selected_id].reset_index(drop=True)
                    st.warning(f"Anggota (ID {selected_id}) berhasil dihapus!")
                    update_and_save(anggota_df=anggota_df)