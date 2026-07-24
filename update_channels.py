import requests
import json
import re
import os

# ============================================
# CONFIGURACIÓN
# ============================================
JSONBIN_BIN_ID = "6a29a41ff5f4af5e29d9bfb1"
NO_LIVE_URL = "NO_LIVE"

CANALES_FIJOS = [
    {
        "nombre": "GUKA TV",
        "categoria": "Euskal Herria",
        "logo": "https://ekinsl.com/maratb/guka.png",
        "url": "https://streaming.ukt.eus/hls/test.m3u8",
        "tipo": "live"
    },
    {
        "nombre": "Hamaika TV",
        "categoria": "Euskal Herria",
        "logo": "https://graph.facebook.com/HamaikaTb/picture?width=200&height=200",
        "url": "https://cdn3.wowza.com/1/RERMR282dnU5eE5Z/OHY0dVFs/hls/live/playlist.m3u8",
        "tipo": "live"
    },
    {
        "nombre": "Urola TV",
        "categoria": "Euskal Herria",
        "logo": "https://graph.facebook.com/urolatelebista/picture?width=200&height=200",
        "url": "https://5940924978228.streamlock.net/j_Directo2/mp4:j_Directo2/playlist.m3u8",
        "tipo": "live"
    },
    {
        "nombre": "Goiena Eus",
        "categoria": "Euskal Herria",
        "logo": "https://graph.facebook.com/goiena.eus/picture?width=200&height=200",
        "url": "https://zuzenean.goienamedia.eus/goiena-telebista.m3u8",
        "tipo": "live"
    },
]

CANALES_YOUTUBE = [
    {
        "nombre": "Pulpo Eskubaloia",
        "categoria": "Kirola",
        "channel_id": "UCs4ba5SylAVo-D5Lo0vx3KQ",
        "logo": "https://yt3.googleusercontent.com/ytc/AIdro_mCKsWDcFUWBOaHMFkJRLgFRBBqr7jFGY8IhNaOcA=s176-c-k-c0x00ffffff-no-rj",
    },
    {
        "nombre": "San Pedro Parrokia",
        "categoria": "Komunitatea",
        "channel_id": "UCsanpedrozumaia",
        "logo": "https://yt3.googleusercontent.com/sanpedro=s176-c-k-c0x00ffffff-no-rj",
    },
    {
        "nombre": "7-Emanaldiak/Eventos",
        "categoria": "Gertakariak",
        "channel_id": "",
        "logo": "https://ekinsl.com/maratb/eventos.png",
        "url_manual": "",
    },
]

def get_youtube_live_url(channel_id):
    try:
        watch_url = f"https://www.youtube.com/channel/{channel_id}/live"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        r = requests.get(watch_url, headers=headers, timeout=10)
        hls_match = re.search(r'"hlsManifestUrl":"(https://[^"]+\.m3u8[^"]*)"', r.text)
        if hls_match:
            url = hls_match.group(1).replace("\\u0026", "&")
            print(f"  URL HLS encontrada")
            return url
        print(f"  Sin directo activo")
        return NO_LIVE_URL
    except Exception as e:
        print(f"  Error: {e}")
        return NO_LIVE_URL

def update_jsonbin(canales):
    api_key = os.environ.get("JSONBIN_API_KEY", "")
    headers = {
        "Content-Type": "application/json",
        "X-Master-Key": api_key,
        "X-Bin-Meta": "false"
    }
    data = {"canales": canales}
    r = requests.put(
        f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}",
        headers=headers,
        json=data,
        timeout=10
    )
    if r.status_code == 200:
        print("✅ JSONBin actualizado correctamente")
    else:
        print(f"❌ Error: {r.status_code} - {r.text}")
        exit(1)

def main():
    print("🔄 Actualizando canales YouTube...\n")
    canales = CANALES_FIJOS.copy()

    for ch in CANALES_YOUTUBE:
        print(f"📺 Comprobando {ch['nombre']}...")
        if ch["channel_id"] == "":
            url = ch.get("url_manual", "")
            tipo = "live" if url else "no_live"
            canales.append({
                "nombre": ch["nombre"],
                "categoria": ch["categoria"],
                "logo": ch["logo"],
                "url": url if url else NO_LIVE_URL,
                "tipo": tipo
            })
        else:
            url = get_youtube_live_url(ch["channel_id"])
            tipo = "live" if url != NO_LIVE_URL else "no_live"
            canales.append({
                "nombre": ch["nombre"],
                "categoria": ch["categoria"],
                "logo": ch["logo"],
                "url": url,
                "tipo": tipo
            })

    print(f"\n📋 Total canales: {len(canales)}")
    update_jsonbin(canales)

if __name__ == "__main__":
    main()