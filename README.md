
# 💡 WizLight Controller API - Pakai Flask, Bisa Atur Lampu Pintar!

Halo! Ini adalah project Python kecil-kecilan yang bisa kamu pakai buat **kontrol lampu WiZ** (smart bulb) lewat **API berbasis Flask**. Mulai dari nyalain, matiin, ubah warna, ubah kecerahan, sampai ubah scene, semua bisa lewat endpoint HTTP. Cocok buat ngoprek IoT-an di rumah 😎

---

## 🔧 Teknologi yang Dipakai
- Python 3.x
- Flask (buat REST API-nya)
- pywizlight (library buat ngatur lampu WiZ)
- Socket & IPAddress (buat cari alamat broadcast lokal)

---

## 🚀 Cara Jalanin

1. **Install dulu semua kebutuhan**

   ```bash
   pip install flask pywizlight
   ```

2. **Jalankan aplikasinya**

   ```bash
   python main.py
   ```

   App-nya bakal jalan di `http://localhost:5000`

---

## 🔌 Endpoint API

### 🔍 Cek API nyala
`GET /api`  
Respons:
```json
{ "message": "Hello, World!" }
```

---

### 💡 Cari lampu yang tersedia
`GET /api/lights/discover`  
Mendeteksi lampu WiZ yang ada di jaringan lokal.

---

### 🔦 Cek status lampu (on/off, warna, brightness, scene, dll)
`GET /api/lights/<ip>/state`  
Contoh:  
```
GET /api/lights/192.168.1.50/state
```

---

### 📴 Matikan lampu
`GET /api/lights/<ip>/off`

---

### 💡 Hidupkan lampu
`GET /api/lights/<ip>/on`

---

### 🌞 Atur tingkat kecerahan (brightness)
`GET /api/lights/<ip>/brightness/<brightness>`  
`brightness`: nilai dari 10 - 255

---

### 🌡️ Atur suhu warna (color temperature)
`GET /api/lights/<ip>/colortemp/<colortemp>`  
Contoh:  
```
GET /api/lights/192.168.1.50/colortemp/4000
```

---

### 🌈 Atur warna RGB dan kecerahan
`GET /api/lights/<ip>/color/<red>/<green>/<blue>/<brightness>`  
Contoh:  
```
GET /api/lights/192.168.1.50/color/255/0/0/150
```

---

### 🎭 Atur scene
`GET /api/lights/<ip>/scene/<scene_id>/<speed>/<brightness>`  
Contoh:  
```
GET /api/lights/192.168.1.50/scene/4/50/200
```

### 🎞 List scene
`GET /api/lights/scenes`  
Contoh:  
```
GET /api/lights/scenes
```

---

## ⚠️ Catatan
- Lampu harus **terhubung ke jaringan yang sama** dengan server ini.
- Beberapa fitur bisa beda-beda tergantung model lampu WiZ yang kamu pakai.
- Kalau ada error, biasanya karena IP salah atau lampunya nggak merespons.

---

## 👨‍💻 Cocok Buat Apa?
- Automasi rumah
- Proyek IoT
- Kontrol lampu dari web/app buatan sendiri
- Kontrol lambu lewat bot
- Ngerjain tugas kuliah 😅

---

Selamat ngoprek! 🚀
