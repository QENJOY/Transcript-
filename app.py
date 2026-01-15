import streamlit as st
import yt_dlp
import requests
import json

# Pagina instellingen
st.set_page_config(page_title="YouTube Data Extractor", layout="wide")
st.title("🎥 YouTube Data & Transcript Inlezer")
st.write("Kopieer titel, datum, URL en transcript in één gestructureerd blok.")

# Input veld
url = st.text_input("YouTube Video URL:", placeholder="Plak hier de link...")

def fetch_and_clean_transcript(info):
    """Haalt de tekst op uit de JSON-data van YouTube."""
    for lang in ['nl', 'en']:
        subs = info.get('subtitles', {}).get(lang) or info.get('automatic_captions', {}).get(lang)
        if subs:
            sub_url = next((s['url'] for s in subs if 'json' in s['url']), subs[0]['url'])
            response = requests.get(sub_url)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    volledige_tekst = ""
                    for event in data.get('events', []):
                        if 'segs' in event:
                            for seg in event['segs']:
                                volledige_tekst += seg.get('utf8', '')
                    return " ".join(volledige_tekst.split())
                except:
                    return None
    return None

if url:
    try:
        with st.spinner('Gegevens ophalen...'):
            ydl_opts = {'skip_download': True, 'writesubtitles': True, 'writeautomaticsubs': True, 'quiet': True}
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Metadata ophalen
                titel = info.get('title', 'Onbekende Titel')
                video_url = info.get('webpage_url', url)
                
                # Datum JJJJ-MM-DD
                raw_date = info.get('upload_date', 'Onbekende Datum')
                if raw_date != 'Onbekende Datum':
                    formatted_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
                else:
                    formatted_date = raw_date
                
                schone_tekst = fetch_and_clean_transcript(info)

                if schone_tekst:
                    st.success(f"Gereed: {titel}")
                    
                    # SAMENSTELLEN OUTPUT:
                    # Titel - datum - url
                    # -Transcript: tekst
                    gecombineerde_output = (
                        f"{titel} - {formatted_date} - {video_url}\n\n"
                        f"-Transcript: {schone_tekst}"
                    )
                    
                    st.subheader("📋 Gecombineerde Output")
                    st.info("Klik op het kopieer-icoontje rechtsboven om alles te kopiëren.")
                    
                    st.code(gecombineerde_output, language=None)
                else:
                    st.error("Kon geen ondertitels vinden voor deze video.")
                    
    except Exception as e:
        st.error(f"Fout: {e}")