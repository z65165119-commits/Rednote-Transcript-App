import streamlit as st
import yt_dlp
import google.generativeai as genai
import os

st.set_page_config(page_title="Rednote Transcript App", page_icon="📝", layout="centered")

st.title("📌 Rednote Video Transcript Generator")
st.write("Rednote ဗီဒီယိုလင့်ခ်ကို ထည့်သွင်းပြီး စာသား (Transcript) ထုတ်ယူနိုင်ပါပြီ။")

# API Key ထည့်သွင်းရန် (Gemini API)
api_key = st.text_input("Gemini API Key ထည့်ပါ", type="password")

# Rednote လင့်ခ်ထည့်ရန်
rednote_url = st.text_input("Rednote Video URL ကို ထည့်ပါ (ဥပမာ - https://www.xiaohongshu.com/...)")

if st.button("Transcript ထုတ်မည်"):
    if not api_key:
        st.error("ကျေးဇူးပြု၍ Gemini API Key ထည့်ပါ။")
    elif not rednote_url:
        st.error("ကျေးဇူးပြု၍ Rednote ဗီဒီယိုလင့်ခ် ထည့်ပါ။")
    else:
        with st.spinner("ဗီဒီယိုကို ဒေါင်းလုဒ်လုပ်နေပါပြီ..."):
            try:
                # yt-dlp ဖြင့် ဗီဒီယို သို့မဟုတ် အသံဖိုင်ကို ဒေါင်းလုဒ်ဆွဲရန်
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': 'downloads/temp_audio.%(ext)s',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
                
                os.makedirs("downloads", exist_ok=True)
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(rednote_url, download=True)
                    audio_filename = ydl.prepare_filename(info)
                    audio_filename = os.path.splitext(audio_filename)[0] + ".mp3"

                st.success("အသံဖိုင် ရယူပြီးပါပြီ။ Gemini ဖြင့် စာသားပြောင်းနေပါပြီ...")

                # Gemini API ဖြင့် အသံဖိုင်ကို စာသားပြောင်းခြင်း (Transcription)
                genai.configure(api_key=api_key)
                
                # ဖိုင်ကို Gemini သို့ Upload တင်ခြင်း
                audio_file = genai.upload_file(audio_filename)
                
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content([
                    audio_file, 
                    "ഈ ဗီဒီယိုထဲမှာ ပြောထားတဲ့ စာသားတွေကို အစအဆုံး မြန်မာဘာသာဖြင့် သို့မဟုတ် မူရင်းဘာသာဖြင့် တိကျစွာ Transcript ထုတ်ပေးပါ။"
                ])

                st.subheader("📝 ရရှိလာသော Transcript:")
                st.write(response.text)

                # ဖိုင်များကို ရှင်းလင်းခြင်း
                if os.path.exists(audio_filename):
                    os.remove(audio_filename)

            except Exception as e:
                st.error(f"အမှားအယွင်း ဖြစ်ပေါ်သွားပါသည်: {e}")
      
