from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from collections import Counter
import streamlit as st
import pandas as pd

# API
API_KEY = st.secrets["API_KEY"]
youtube = build("youtube", "v3", developerKey=st.secrets["API_KEY"])

def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")

load_css("style.css")

# Header
st.markdown('<div class="header"><h1>YOUTUBE COMMENT SCRAPPER</h1></div>',unsafe_allow_html=True)
st.write(" ")

# Input Video ID
Video_ID = st.text_input("Masukkan Video ID:")

#Langkah memasukkan Video ID
step1, step2, step3 = st.columns(3, gap="large")

with step1:
    st.markdown('<div class="step">1. Ambil ID dari URL video Youtube</div>', unsafe_allow_html=True)
    st.image("1.png")

with step2:
    st.markdown('<div class="step">2. Letakkan ID kedalam text field</div>', unsafe_allow_html=True)
    st.image("2.png")

with step3:
    st.markdown('<div class="step">3. Klik tombol "Tampilkan Komentar"</div>', unsafe_allow_html=True)
    st.image("3.png")

# Input Kata yang Ingin Di-filter
st.write(" ")
filterchoose = st.text_input("(Opsional) Kata yang Ingin di-Filter:",placeholder="Contoh: jelek keren sulit").split()
st.write(" ")

# Fungsi menghitung 10 kata terbanyak
def top_10_words(komentar_list):
    text = " ".join(komentar_list).lower()
    words = text.split()

    stopwords = {
        # Bahasa Indonesia
        "dan", "yang", "di", "ke", "dari", "ini", "itu", "untuk", "dengan",
        "pada", "adalah", "saya", "kamu", "dia", "kami", "kita", "nya"

        # Bahasa Inggris
        "the", "a", "an", "is", "are", "to", "of", "in", "this", "and", "that", 
        "was", "but", "for", "just", "with", "when", "have", "the"
    }

    stopwords = stopwords.union(set(filterchoose))

    filtered_words = [w for w in words if w not in stopwords and len(w) > 2]
    return Counter(filtered_words).most_common(10)

# Tombol ambil komentar
if st.button("Tampilkan Komentar", key="black"):
    comments = []

    if Video_ID.strip() == "":
        st.error("Video ID tidak boleh kosong!")

    else:
        try:
            # Request awal
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=Video_ID.strip(),
                maxResults=100,
                textFormat="plainText"
            )

            # Loop pagination
            while request:
                response = request.execute()

                for komentar in response["items"]:
                    snippet = komentar["snippet"]["topLevelComment"]["snippet"]
                    comments.append({
                        "Username": snippet["authorDisplayName"],
                        "Tanggal": snippet["publishedAt"],
                        "Komentar": snippet["textDisplay"]
                    })

                request = youtube.commentThreads().list_next(request, response)

            # Tampilkan hasil komentar
            if comments:
                df = pd.DataFrame(comments)
                komentar_list = df["Komentar"].tolist()
                top_words = top_10_words(komentar_list)

                st.success(f"Berhasil mengambil {len(df)} komentar")
                st.subheader("10 Kata yang Paling Sering Muncul")
                top_df = pd.DataFrame(top_words, columns=["Kata", "Frekuensi"])

                col_table, col_chart = st.columns(2, gap="small")

                with col_table:
                    st.table(top_df)

                with col_chart:
                    st.bar_chart(
                        data=top_df.set_index("Kata"),
                        use_container_width=True
    )
                st.subheader("List Semua Komentar")
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("Tidak ada komentar yang ditemukan.")

        except HttpError as e:
            st.error(f"Terjadi error API: {e}")
