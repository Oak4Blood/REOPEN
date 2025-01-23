import os
import subprocess
import time
import requests
import sys

config_path = "/sdcard/Download"
if config_path not in sys.path:
    sys.path.append(config_path)

try:
    import config
    url = config.url
    webhook_url = config.webhook_url
except ImportError as e:
    print(f"ไม่สามารถนำเข้า config.py ได้: {e}")
    url = None
    webhook_url = None

def is_process_running(package_name):
    """ตรวจสอบว่า process ของแอปกำลังทำงานและไม่ค้างหรือไม่"""
    try:
        output = subprocess.check_output(['su', '-c', 'ps -A'], stderr=subprocess.DEVNULL)
        if package_name.encode() in output:
            zombie_check = subprocess.check_output(['su', '-c', f'ps -o stat= -p $(pgrep -f {package_name})'], stderr=subprocess.DEVNULL)
            if b'Z' in zombie_check:
                print(f"{package_name} อยู่ในสถานะ zombie! กำลัง force stop...")
                subprocess.call(['su', '-c', f'am force-stop {package_name}'])
                return False
            return True
        return False
    except subprocess.CalledProcessError:
        return False

def open_chrome_with_url(url):
    """เปิด Google Chrome พร้อมวางลิงก์"""
    chrome_command = f"su -c 'am start -a android.intent.action.VIEW -d {url}'"
    os.system(chrome_command)

    data = {
        "content": "ผู้ช่วยได้เปิด Roblox ให้คุณแล้ว",
        "username": "ผู้ช่วยส่วนตัวของคุณ"
    }
    try:
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
        print("ส่งข้อความ เปิด Roblox สำเร็จ!")
    except requests.RequestException as e:
        print(f"ไม่สามารถส่งข้อความได้: {e}")

def kill_browsers():
    """ปิด Google Chrome และ Android Browser"""
    print("กำลังปิด Google Chrome และ Android Browser...")
    subprocess.call(['su', '-c', 'am force-stop com.android.chrome'])
    subprocess.call(['su', '-c', 'am force-stop com.android.browser'])

def kill_roblox_hourly(last_kill_time):
    """Force stop Roblox ทุกๆ 1 ชั่วโมงครึ่ง"""
    current_time = time.time()
    if current_time - last_kill_time >= 4680:
        print("ทำการ force stop com.roblox.client หลังจาก 1 ชั่วโมงครึ่ง")
        subprocess.call(['su', '-c', 'am force-stop com.roblox.client'])

        data = {
            "content": "ผู้ช่วยได้ปิด Roblox ให้คุณแล้วและกำลังจะเปิดให้ทันทีหลังจากนี้",
            "username": "ผู้ช่วย ส่วนตัวของคุณ"
        }
        try:
            response = requests.post(webhook_url, json=data)
            response.raise_for_status()
            print("ส่งข้อความปิด Roblox สำเร็จ!")
        except requests.RequestException as e:
            print(f"ไม่สามารถส่งข้อความได้: {e}")

        return current_time
    return last_kill_time

last_kill_time = time.time()

while True:
    try:
        if not is_process_running("com.roblox.client"):
            print("ไม่พบ Roblox กำลังทำงาน, เปิด Google Chrome...")
            open_chrome_with_url(url)
            time.sleep(10)
            kill_browsers() 
        else:
            print("Roblox กำลังทำงาน")
        
        last_kill_time = kill_roblox_hourly(last_kill_time)
        
        time.sleep(15)
        
    except KeyboardInterrupt:
        print("โปรแกรมหยุดทำงาน")
        break
