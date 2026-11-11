from flask import Flask, request, jsonify, send_file, send_from_directory
from pathlib import Path
import io, threading, urllib.request, wave

ROOT = Path(__file__).resolve().parent
MODELS = ROOT / "models"
MODEL_NAME = "UVR-MDX-NET-Voc_FT.onnx"
MODEL_URL = "https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/" + MODEL_NAME

app = Flask(__name__, static_folder=str(ROOT), static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = 300 * 1024 * 1024


@app.after_request
def add_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return resp


@app.route("/api/<path:_any>", methods=["OPTIONS"])
def preflight(_any):
    return ("", 204)


@app.errorhandler(413)
def too_big(_e):
    return jsonify(error="El archivo es demasiado grande (máximo 300 MB)."), 413


@app.get("/")
def home():
    return send_from_directory(ROOT, "index.html")


@app.get("/api/health")
def health():
    return jsonify(ok=True)


@app.post("/api/export/flac")
def export_flac():
    """Convierte WAV PCM a FLAC PCM_24 sin pérdida."""
    if "audio" not in request.files:
        return jsonify(error="No se recibió el audio para convertir."), 400
    try:
        import soundfile as sf
        raw = request.files["audio"].read()
        data, rate = sf.read(io.BytesIO(raw), dtype="float32", always_2d=True)
        if data.shape[1] not in (1, 2):
            return jsonify(error="Solo se admite audio mono o estéreo."), 400
        out = io.BytesIO()
        sf.write(out, data, rate, format="FLAC", subtype="PCM_24")
        out.seek(0)
        return send_file(out, mimetype="audio/flac", as_attachment=True,
                         download_name="DJ_THE_OFFSPRIN_FLAC_24bit.flac", max_age=0)
    except ImportError:
        return jsonify(error="soundfile no está instalado. Ejecuta la instalación de requirements.txt."), 500
    except Exception as exc:
        return jsonify(error="No se pudo codificar FLAC: " + str(exc)), 500


@app.post("/api/export/mp3")
def export_mp3():
    """Convierte WAV (PCM 16 bits) a MP3 CBR 320 kbps con lameenc."""
    if "audio" not in request.files:
        return jsonify(error="No se recibió el audio para convertir."), 400
    try:
        import lameenc
        raw = request.files["audio"].read()
        with wave.open(io.BytesIO(raw), "rb") as wav:
            channels, rate, width = wav.getnchannels(), wav.getframerate(), wav.getsampwidth()
            frames = wav.readframes(wav.getnframes())
        if width != 2 or channels not in (1, 2):
            return jsonify(error="Formato WAV no admitido para MP3."), 400
        enc = lameenc.Encoder()
        enc.set_bit_rate(320)
        enc.set_in_sample_rate(rate)
        enc.set_channels(channels)
        enc.set_quality(2)
        mp3 = enc.encode(frames) + enc.flush()
        return send_file(io.BytesIO(mp3), mimetype="audio/mpeg", as_attachment=True,
                         download_name="DJ_THE_OFFSPRIN_320kbps.mp3", max_age=0)
    except ImportError:
        return jsonify(error="lameenc no instalado"), 500
    except Exception as exc:
        return jsonify(error="No se pudo codificar MP3: " + str(exc)), 500


def prefetch_model():
    """Descarga el modelo de IA una sola vez a ./models para que cualquier dispositivo
    de la red lo reciba directo de esta PC (más rápido y sin depender de Internet)."""
    try:
        MODELS.mkdir(exist_ok=True)
        dest = MODELS / MODEL_NAME
        if dest.exists() and dest.stat().st_size > 20_000_000:
            return
        print("Descargando el modelo de IA (~67 MB, solo esta vez)...")
        tmp = dest.with_suffix(".part")
        urllib.request.urlretrieve(MODEL_URL, tmp)
        if tmp.stat().st_size > 20_000_000:
            tmp.replace(dest)
            print("Modelo de IA listo.")
        else:
            tmp.unlink(missing_ok=True)
    except Exception as exc:  # el navegador lo descargará por su cuenta si esto falla
        print("(Aviso) No se pudo pre-descargar el modelo; el navegador lo bajará solo:", exc)


ORT_BASE = "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.17.3/dist/"
ORT_FILES = ["ort.min.js", "ort-wasm.wasm", "ort-wasm-simd.wasm", "ort-wasm-threaded.wasm",
             "ort-wasm-simd-threaded.wasm", "ort-wasm-threaded.worker.js"]


def prefetch_ort():
    """Guarda el motor de IA en ./ort para que se sirva desde esta misma PC (necesario para usar varios hilos)."""
    d = ROOT / "ort"
    d.mkdir(exist_ok=True)
    for f in ORT_FILES:
        try:
            if (d / f).exists() and (d / f).stat().st_size > 1000:
                continue
            urllib.request.urlretrieve(ORT_BASE + f, d / (f + ".part"))
            (d / (f + ".part")).replace(d / f)
        except Exception:
            (d / (f + ".part")).unlink(missing_ok=True)


if __name__ == "__main__":
    threading.Thread(target=prefetch_ort, daemon=True).start()
    threading.Thread(target=prefetch_model, daemon=True).start()
    print("\nDJ THE OFFSPRIN STUDIOS")
    print("Abre: http://127.0.0.1:5000")
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(("8.8.8.8", 80))
        print("Desde otro dispositivo de tu red: http://%s:5000" % s.getsockname()[0]); s.close()
    except Exception:
        pass
    print("No cierres esta ventana mientras uses el programa.\n")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
