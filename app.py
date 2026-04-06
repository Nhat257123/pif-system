import streamlit as st
import pandas as pd
import pif_backend
import io
import os
import zipfile
import hashlib
import logging
import html as html_lib
from datetime import datetime

# ─────────────────────────────────────────────
# 1. AUDIT LOGGING SETUP
# ─────────────────────────────────────────────
logging.basicConfig(
    filename="pif_audit.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)

def audit(message: str):
    user = st.session_state.get("username", "anonymous")
    logging.info(f"[USER:{user}] {message}")

# ─────────────────────────────────────────────
# 2. USER AUTHENTICATION
# ─────────────────────────────────────────────
# Để thêm / đổi mật khẩu: chạy lệnh Python sau rồi paste hash vào đây
#   import hashlib; print(hashlib.sha256("mat_khau_moi".encode()).hexdigest())
AUTHORIZED_USERS = {
    "admin":   "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9",  # admin123
    "rd_user": "87ebd596a167518f7e465df66b7fe23c2d04253ff1174903fe68247b57d450b0",  # rd2026 (Updated hash)
}

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def check_auth():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = ""

    if not st.session_state.authenticated:
        # Full-page login form
        st.set_page_config(page_title="Đăng nhập – PIF System", page_icon="🔐", layout="centered")
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');
            html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
            .stApp { background-color: #F9F7F3; }
            .login-box {
                background: white; border-radius: 16px; padding: 2rem;
                box-shadow: 0 4px 20px rgba(91,123,97,0.12);
                max-width: 380px; margin: 3rem auto;
                border-top: 4px solid #5B7B61;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="login-box">
                <div style='text-align:center; margin-bottom:1.5rem;'>
                    <span style='font-size:2.5rem;'>🌿</span>
                    <h2 style='color:#5B7B61; margin:0.3rem 0 0 0; font-size:1.3rem;'>HỆ THỐNG HỒ SƠ PIF</h2>
                    <p style='color:#94a3b8; font-size:0.8rem; margin:0;'>Vui lòng đăng nhập để tiếp tục</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("👤 Tên đăng nhập", placeholder="Nhập tên đăng nhập...")
            password = st.text_input("🔑 Mật khẩu", type="password", placeholder="Nhập mật khẩu...")
            submitted = st.form_submit_button("🚀 ĐĂNG NHẬP", use_container_width=True)

        if submitted:
            if AUTHORIZED_USERS.get(username.strip()) == hash_pw(password):
                st.session_state.authenticated = True
                st.session_state.username = username.strip()
                audit("Đăng nhập thành công")
                st.rerun()
            else:
                audit(f"Đăng nhập thất bại – username thử: '{username}'")
                st.error("❌ Sai tên đăng nhập hoặc mật khẩu.")
        st.stop()

# ─────────────────────────────────────────────
# 3. RUN AUTH CHECK FIRST
# ─────────────────────────────────────────────
check_auth()

# ─────────────────────────────────────────────
# 4. MAIN APP (chỉ chạy khi đã xác thực)
# ─────────────────────────────────────────────

# Initialize Session State
if 'processed_results' not in st.session_state:
    st.session_state.processed_results = []
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if 'ready_to_show_downloads' not in st.session_state:
    st.session_state.ready_to_show_downloads = False

st.set_page_config(page_title="Natural PIF System", layout="wide", page_icon="🌿")

# --- Custom CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
    .stApp { background-color: #F9F7F3; color: #2D3A30; }
    .main-header {
        background: linear-gradient(135deg, #5B7B61 0%, #74967A 100%);
        padding: 1.2rem; border-radius: 12px; color: white;
        text-align: center; margin-bottom: 1rem;
        box-shadow: 0 4px 10px rgba(91, 123, 97, 0.15);
    }
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #FFFFFF !important; border-radius: 12px !important;
        border: 1.5px solid #EAE2D6 !important; padding: 1.5rem !important;
        box-shadow: 0 2px 8px rgba(91, 123, 97, 0.05) !important;
    }
    /* Bo bot duong vien long nhau cua cac element con (file uploader, checkbox...) */
    [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"] > div {
        border: none !important; padding: 0 !important; background: transparent !important;
        box-shadow: none !important;
    }
    .section-title {
        color: #5B7B61; font-weight: 700;
        border-bottom: 2px solid #F0EEE9; padding-bottom: 0.5rem;
        margin-bottom: 1.2rem; margin-top: 0; font-size: 1.2rem;
    }
    .stButton>button {
        width: 100%; background-color: #5B7B61; color: white;
        border-radius: 12px; font-weight: 600; border: none; transition: all 0.3s;
        padding: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header Banner ---
safe_username = html_lib.escape(st.session_state.username)
st.markdown(f"""
    <div class="main-header">
        <h2 style='margin:0; font-size: 1.8rem;'>🌿 HỆ THỐNG HỒ SƠ DỮ LIỆU PIF</h2>
        <p style='font-size: 0.9rem; opacity: 0.9;'>Chuẩn hóa – Tự động – Bảo mật</p>
    </div>
    <div style='display: flex; justify-content: flex-end; align-items: center; margin-top: -0.5rem; margin-bottom: 1rem;'>
        <p style='color:#64748B; font-size:0.8rem; margin:0;'>👤 Dang nhap: <strong>{safe_username}</strong></p>
    </div>
""", unsafe_allow_html=True)

# --- Logout button ---
if st.sidebar.button("🚪 Đăng xuất"):
    audit("Đăng xuất")
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.sidebar.markdown(f"**👤 Người dùng:** {safe_username}")
st.sidebar.markdown("---")
st.sidebar.markdown("**📋 Hướng dẫn:**")
st.sidebar.markdown("1. Tải lên File tổng hợp NL (T01)\n2. Tải lên 1+ file ĐMVT\n3. Nhấn **Bắt đầu xử lý**\n4. Tải ZIP kết quả")

# --- Main Layout ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    with st.container(border=True):
        st.markdown('<h3 class="section-title">1. Cấu hình & Tải lên</h3>', unsafe_allow_html=True)
        db_file = st.file_uploader("📂 Bước 1: File tổng hợp thông tin NL", type=["xlsx"])
        formula_files = st.file_uploader("📂 Bước 2: Tệp ĐMVT", type=["xlsx"], accept_multiple_files=True)
        st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
        process_btn = st.button("🚀 BẮT ĐẦU XỬ LÝ HỒ SƠ")

with col2:
    with st.container(border=True):
        st.markdown('<h3 class="section-title">2. Trạng thái & Kết quả</h3>', unsafe_allow_html=True)

        if process_btn:
            if not db_file or not formula_files:
                st.warning("⚠️ Vui lòng tải lên đầy đủ file tổng hợp thông tin NL và ít nhất một file ĐMVT.")
            else:
                # Validate file sizes (max 50MB each)
                MAX_SIZE = 50 * 1024 * 1024
                size_ok = True
                for f in formula_files:
                    if f.size > MAX_SIZE:
                        st.error(f"❌ File '{html_lib.escape(f.name)}' vượt quá giới hạn 50MB.")
                        audit(f"Upload bị từ chối – file quá lớn: {f.name} ({f.size} bytes)")
                        size_ok = False
                        break
                if db_file.size > MAX_SIZE:
                    st.error("❌ File tổng hợp NL vượt quá giới hạn 50MB.")
                    size_ok = False

                if size_ok:
                    try:
                        # RESET previous results before starting new batch
                        st.session_state.processed_results = []
                        st.session_state.show_results = False
                        st.session_state.ready_to_show_downloads = False

                        audit(f"Bắt đầu xử lý – DB: {db_file.name}, Số ĐMVT: {len(formula_files)}")
                        db_df = pd.read_excel(db_file)
                        templates_dir = "."
                        progress_text = st.empty()
                        progress_bar = st.progress(0)

                        for i, f_file in enumerate(formula_files):
                            safe_fname = html_lib.escape(f_file.name)
                            progress_text.markdown(f"**🌿 Đang xử lý:** `{safe_fname}`")
                            audit(f"Xử lý ĐMVT: {f_file.name}")

                            # Trả về cả file_dict và metadata để không cần đọc file 2 lần
                            file_dict, f_info = pif_backend.process_single_formula(f_file, db_df, templates_dir)

                            p_name = pif_backend.sanitize_filename(f_info.get('ten_san_pham', f_file.name))[:30]
                            p_id = f_info.get('ma_so_pif', 'FILE')
                            zip_filename = pif_backend.sanitize_filename(f"PIF_{p_id}_{p_name}") + ".zip"

                            zip_buffer = io.BytesIO()
                            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                                for filename, content in file_dict.items():
                                    zip_file.writestr(filename, content)
                            zip_buffer.seek(0)

                            st.session_state.processed_results.append({
                                'display_name': f_info.get('ten_san_pham', f_file.name),
                                'original_filename': f_file.name,
                                'zip_data': zip_buffer.getvalue(),
                                'zip_filename': zip_filename,
                                'count': len(file_dict)
                            })
                            audit(f"Hoàn thành: {f_file.name} → {len(file_dict)} tài liệu")
                            progress_bar.progress((i + 1) / len(formula_files))

                        st.session_state.show_results = True
                        st.session_state.ready_to_show_downloads = False
                        progress_text.empty()
                        progress_bar.empty()
                        st.success("✅ Đã xử lý xong!")
                        st.rerun()

                    except Exception as e:
                        logging.exception("Lỗi xử lý PIF")
                        audit(f"LỖI xử lý: {type(e).__name__}")
                        st.error("❌ Đã xảy ra lỗi trong quá trình xử lý. Vui lòng kiểm tra lại file đầu vào hoặc liên hệ R&D Team.")

        # Display Area
        if not st.session_state.show_results:
            st.markdown("""
                <div style='text-align: center; padding-top: 1rem;'>
                    <img src="https://img.icons8.com/dotty/80/5B7B61/spa-flower.png" width="70">
                    <p style='color: #74967A; margin-top: 1rem;'>Kết quả sẽ hiển thị tại đây.</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            if not st.session_state.ready_to_show_downloads:
                st.info("Hồ sơ đã sẵn sàng.")
                if st.button("📂 XEM DANH SÁCH TẢI XUỐNG", type="primary"):
                    st.session_state.ready_to_show_downloads = True
                    st.rerun()
            else:
                for res in st.session_state.processed_results:
                    # FIX XSS: escape tên sản phẩm trước khi đưa vào HTML
                    safe_display = html_lib.escape(res['display_name'])
                    safe_orig = html_lib.escape(res.get('original_filename', 'N/A'))
                    st.markdown(f"""
                    <div style='background-color: #FFFFFF; padding: 0.6rem 1rem; border-radius: 8px;
                                border-left: 5px solid #5B7B61; margin-bottom: 8px; 
                                border-top: 1px solid #F0EEE9; border-right: 1px solid #F0EEE9; border-bottom: 1px solid #F0EEE9;'>
                        <div style='font-weight: 600; color: #2D3A30; font-size: 0.95rem;'>
                            🌿 {safe_display}
                        </div>
                        <div style='font-size: 0.75rem; color: #64748B; margin-top: 2px;'>
                            📂 File: {safe_orig}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.download_button(
                        label=f"📥 TẢI ZIP – {res['display_name'][:25]}...",
                        data=res['zip_data'],
                        file_name=res['zip_filename'],
                        mime="application/zip",
                        key=f"zip_{res['zip_filename']}",
                        use_container_width=True
                    )
                    st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)

                if st.button("🗑️ XÓA KẾT QUẢ", use_container_width=True):
                    audit("Xóa kết quả phiên làm việc")
                    st.session_state.processed_results = []
                    st.session_state.show_results = False
                    st.session_state.ready_to_show_downloads = False
                    st.rerun()

st.markdown(
    "<p style='text-align: center; color: #64748B; font-size: 0.8rem; margin-top: 2rem;'>"
    "© 2026 R&D Team</p>",
    unsafe_allow_html=True
)
