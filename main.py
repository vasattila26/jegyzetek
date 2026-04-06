import js
import json
from pyodide.ffi import create_proxy

STORAGE_KEY = "sajat_jegyzetek_adat"
PASS_KEY = "sajat_app_jelszo"

# --- BIZTONSÁG ---
def ellenorzes(event):
    bevitt_kod = js.document.getElementById("pass-input").value
    mentett_kod = js.localStorage.getItem(PASS_KEY)
    
    if not mentett_kod:
        if len(bevitt_kod) < 4:
            js.alert("A kód legyen legalább 4 számjegy!")
            return
        js.localStorage.setItem(PASS_KEY, bevitt_kod)
        js.alert("Kód beállítva!")
        feloldas()
    elif bevitt_kod == mentett_kod:
        feloldas()
    else:
        js.alert("Hibás kód!")
        js.document.getElementById("pass-input").value = ""

def feloldas():
    js.document.getElementById("login-screen").style.display = "none"
    megjelenites()

# --- ADATKEZELÉS ---
def mentes(event):
    textarea = js.document.getElementById("uj-jegyzet")
    szoveg = textarea.value.strip()
    if szoveg:
        jegyzetek = betoltes_adat()
        jegyzetek.append(szoveg)
        js.localStorage.setItem(STORAGE_KEY, json.dumps(jegyzetek))
        textarea.value = ""
        megjelenites()

def betoltes_adat():
    adat = js.localStorage.getItem(STORAGE_KEY)
    return json.loads(adat) if adat else []

def torles(index):
    jegyzetek = betoltes_adat()
    jegyzetek.pop(index)
    js.localStorage.setItem(STORAGE_KEY, json.dumps(jegyzetek))
    megjelenites()

def megjelenites():
    lista_div = js.document.getElementById("jegyzet-lista")
    lista_div.innerHTML = ""
    jegyzetek = betoltes_adat()
    
    for i, jegyzet in enumerate(reversed(jegyzetek)):
        real_index = len(jegyzetek) - 1 - i
        kartya = js.document.createElement("div")
        kartya.className = "jegyzet-kartya"
        kartya.innerHTML = f"<div style='white-space: pre-wrap;'>{jegyzet}</div>"
        
        torlo = js.document.createElement("div")
        torlo.className = "torles-btn"
        torlo.innerText = "TÖRLÉS"
        
        def torles_wrapper(e, idx=real_index):
            if js.confirm("Biztosan törlöd?"):
                torles(idx)
        
        torlo.onclick = create_proxy(torles_wrapper)
        kartya.appendChild(torlo)
        lista_div.appendChild(kartya)

# --- EXPORT / IMPORT ---
def export_adat(event):
    jegyzetek = betoltes_adat()
    kod = js.localStorage.getItem(PASS_KEY)
    mentes_csomag = {"kod": kod, "jegyzetek": jegyzetek}
    
    fajl_tartalom = json.dumps(mentes_csomag, ensure_ascii=False, indent=4)
    blob = js.Blob.new([fajl_tartalom], { "type": "application/json" })
    url = js.URL.createObjectURL(blob)
    
    link = js.document.createElement("a")
    link.href = url
    link.download = "vedett_jegyzetek.json"
    link.click()

async def import_adat(event):
    file = event.target.files.item(0)
    if not file: return
    szoveg = await file.text()
    try:
        beolvasott = json.loads(szoveg)
        aktualis_kod = js.localStorage.getItem(PASS_KEY)
        if beolvasott.get("kod") == aktualis_kod:
            js.localStorage.setItem(STORAGE_KEY, json.dumps(beolvasott.get("jegyzetek", [])))
            megjelenites()
            js.alert("Sikeres import!")
        else:
            js.alert("❌ Hiba: A fájl kódja nem egyezik!")
    except:
        js.alert("Sérült fájl!")

# --- START ---
file_input = js.document.getElementById("file-input")
file_input.onchange = create_proxy(import_adat)

if not js.localStorage.getItem(PASS_KEY):
    js.document.getElementById("login-title").innerText = "🆕 Új Kód"
    js.document.getElementById("login-msg").innerText = "Állíts be egy biztonsági kódot:"
