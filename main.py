import asyncio
import ipaddress
import socket
from flask import Flask, jsonify, request
from pywizlight import wizlight, PilotBuilder, discovery 
from list_scene import SCENES
from flask_cors import CORS 

app = Flask(__name__)
CORS(app)

def run_async(coro):
    return asyncio.run(coro)

# fungsi dapetin ip broadcast
def get_broadcast():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    finally:
        s.close()
    ip_obj = ipaddress.IPv4Interface(f"{local_ip}/24")
    return str(ip_obj.network.broadcast_address)

from flask import render_template

@app.route('/')
def main():
    server_url = request.host_url.strip('/')
    print(server_url)
    return render_template('coba.html', server_url=server_url)

@app.route('/api', methods=['GET'])
def api_root():
    return jsonify({"pesan": "Hello, World!"})

# UNTUK DISCOVER
@app.route('/api/lights/discover', methods=['GET'])
def discover_lights():
    try:
        ip_broadcast = get_broadcast()
        print(ip_broadcast)
        devices = asyncio.run(discovery.discover_lights(broadcast_space=ip_broadcast))
    
        result = [
            {
                "ip": str(device.ip),
                "port": device.port,
                "mac": device.mac if hasattr(device, 'mac') else None
            }
            for device in devices
        ]

        return jsonify({"status": True, "pesan": "Berhasil menemukan lampu", "data": result})
    except Exception as e:
        return jsonify({"status": False, "pesan": f"Gagal menemukan lampu: {e}" }), 500

# DAPETKAN STATE LAMPU 
@app.route('/api/lights/<ip>/state', methods=['GET'])
async def get_light_state(ip):
    try:
        light = wizlight(ip)
        state = await light.updateState()
        
        data = {
            "device": {
                "ip": ip,
                "mac": state.get_mac(),
            },
            "power": {
                "is_on": state.get_state(),
                "power_level": state.get_power(),
                "source": state.get_source(),
            },
            "light": {
                "brightness": state.get_brightness(),
                "colortemp": state.get_colortemp(),
                "warm_white": state.get_warm_white(),
                "cold_white": state.get_cold_white(),
                "rgb": {
                    "red": state.get_rgb()[0],
                    "green": state.get_rgb()[1],
                    "blue": state.get_rgb()[2],
                }
            },
            "scene": {
                "id": state.get_scene_id(),
                "name": state.get_scene(),
                "speed": state.get_speed()
            }
        }

        return jsonify({"status": True, "pesan": "Berhasil mengambil state lampu", "data": data})
    except Exception as e:
        app.logger.error(f"Gagal mengambil state lampu di IP {ip}: {e}")
        return jsonify({"status": False, "pesan": f"Gagal mengambil state lampu di IP {ip}" }), 500
    
# Matiakan lampu
@app.route('/api/lights/<ip>/off', methods=['GET'])
async def turn_off_light(ip):
    try:
        light = wizlight(ip)
        await light.turn_off()
        return jsonify({"status": True, "pesan": "Berhasil mematikan lampu"})
    except Exception as e:
      
        return jsonify({"status": False, "pesan": f"Gagal mematikan lampu di IP {ip}" }), 500
    
# Hidupkan lampu
@app.route('/api/lights/<ip>/on', methods=['GET'])
async def turn_on_light(ip):
    try:
        light = wizlight(ip)
        await light.turn_on()
        return jsonify({"status": True, "pesan": "Berhasil menghidupkan lampu"})
    except Exception as e:
   
        return jsonify({"status": False, "pesan": f"Gagal menghidupkan lampu di IP {ip}" }), 500

# set kecerahan
@app.route('/api/lights/<ip>/brightness/<int:brightness>', methods=['GET'])
async def set_brightness(ip, brightness):
    try:

        if brightness < 0 or brightness > 255:
            return jsonify({"status": False, "pesan": "Nilai kecerahan tidak valid (0-255)" }), 400

        app.logger.info(f"Memperbarui kecerahan lampu di IP {ip} menjadi {brightness}")
        light = wizlight(ip)
        await light.turn_on(PilotBuilder(brightness=brightness))
        return jsonify({"status": True, "pesan": "Berhasil mengatur kecerahan lampu"})
    except Exception as e:
        app.logger.error(f"Gagal mengatur kecerahan lampu di IP {ip}: {e}")
        return jsonify({"status": False, "pesan": f"Gagal mengatur kecerahan lampu di IP {ip}" }), 500

# set suhu
@app.route('/api/lights/<ip>/colortemp/<int:colortemp>', methods=['GET'])
async def set_colortemp(ip, colortemp):
    try:

        if colortemp < 2200 or colortemp > 6500:
            return jsonify({"status": False, "pesan": "Nilai suhu tidak valid (2200-9000)" }), 400

        app.logger.info(f"Memperbarui suhu lampu di IP {ip} menjadi {colortemp}")
        light = wizlight(ip)
        await light.turn_on(PilotBuilder(colortemp=colortemp))
        return jsonify({"status": True, "pesan": "Berhasil mengatur suhu lampu"})
    except Exception as e:
        app.logger.error(f"Gagal mengatur suhu lampu di IP {ip}: {e}")
        return jsonify({"status": False, "pesan": f"Gagal mengatur suhu lampu di IP {ip}" }), 500
    
# set color and brightness
@app.route('/api/lights/<ip>/color', methods=['GET'])
async def set_color(ip):

    red = request.args.get('red', type=int)
    green = request.args.get('green', type=int)
    blue = request.args.get('blue', type=int)
    brightness = request.args.get('brightness', type=int)

    if not all([ip, red is not None, green is not None, blue is not None]):
        return jsonify({"status": False, "pesan": "Parameter ip, red, green, dan blue wajib"}), 400

    if not all([0 <= red <= 255, 0 <= green <= 255, 0 <= blue <= 255]):
        return jsonify({"status": False, "pesan": "Nilai warna tidak valid (0-255)" }), 400

    try:
        app.logger.info(f"Memperbarui lampu di IP {ip}")
        light = wizlight(ip)

        if brightness is None:
            state = await light.updateState()
            brightness = state.get_brightness()
        
        if brightness < 0 or brightness > 255:
            return jsonify({"status": False, "pesan": "Nilai kecerahan tidak valid (0-255)" }), 400

        await light.turn_on(PilotBuilder(rgb=(red, green, blue), brightness=brightness))
        return jsonify({"status": True, "pesan": "Berhasil mengatur warna dan kecerahan lampu"})
    except Exception as e:
        app.logger.error(f"Gagal mengatur warna dan kecerahan lampu di IP {ip}: {e}")
        return jsonify({"status": False, "pesan": f"Gagal mengatur warna dan kecerahan lampu di IP {ip}" }), 500
    
# set scene
@app.route('/api/lights/<ip>/scene/<int:scene_id>', methods=['GET'])
async def set_scene(ip, scene_id):

    speed = request.args.get('speed', type=int)
    brightness = request.args.get('brightness', type=int)

    try:
        if scene_id not in SCENES:
            return jsonify({"status": False, "pesan": f"Scene {scene_id} tidak tersedia"}), 400

        app.logger.info(f"Memperbarui scene lampu di IP {ip}")
        light = wizlight(ip)

        if brightness or speed is  None:
            state = await light.updateState()
            brightness = state.get_brightness()
            speed = state.get_speed()

        await light.turn_on(PilotBuilder(scene=scene_id, speed=speed, brightness=brightness))
        return jsonify({"status": True, "pesan": "Berhasil mengatur scene lampu"})
    except Exception as e:
        app.logger.error(f"Gagal mengatur scene lampu di IP {ip}: {e}")
        return jsonify({"status": False, "pesan": f"Gagal mengatur scene lampu di IP {ip}" }), 500

# list scene
@app.route('/api/lights/scenes', methods=['GET'])
def list_scenes():
    try:
        scenes_list = [{"id": id, "name": name} for id, name in SCENES.items()]
        return jsonify({
            "status": True,
            "pesan": "Daftar scene tersedia",
            "data": {
                "scenes": scenes_list,
                "total_scenes": len(scenes_list)
            }
        })
    except Exception as e:
        app.logger.error(f"Gagal mengambil daftar scene: {e}")
        return jsonify({
            "status": False,
            "pesan": "Gagal mengambil daftar scene"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)