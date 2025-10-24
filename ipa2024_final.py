#######################################################################################
# Yourname: Kacha Thanaphitak
# Your student ID: 66070244
# Your GitHub Repo: https://github.com/Achakach/IPA2024-Final
#######################################################################################
# 1. Import libraries
import requests
import json
import time
import os
import netconf_final

# --- แก้ไข: เพิ่ม import สำหรับโจทย์ส่วนที่ 2 ---
import netmiko_final
import ansible_final
from requests_toolbelt.multipart.encoder import MultipartEncoder  # <-- ต้อง import ตัวนี้
from dotenv import load_dotenv  # <-- เพิ่มเข้ามาเพื่อใช้ .env

# --- แก้ไข: โหลดค่าจากไฟล์ .env ---
load_dotenv()

# --- แก้ไข: ย้ายค่าคงที่มาไว้รวมกัน ---
MY_STUDENT_ID = "66070244"
WEBEX_ROOM_ID = "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vYmQwODczMTAtNmMyNi0xMWYwLWE1MWMtNzkzZDM2ZjZjM2Zm"

#######################################################################################
# 2. Assign the Webex access token
ACCESS_TOKEN = os.environ.get("WEBEX_ACCESS_TOKEN")
if not ACCESS_TOKEN:
    raise Exception("WEBEX_ACCESS_TOKEN not set. Check your .env file.")

#######################################################################################
# 3. Main loop
last_message_id = None  # <-- แก้ไข: สร้างตัวแปรเพื่อเก็บ ID ของข้อความล่าสุด

while True:
    time.sleep(1)
    getParameters = {"roomId": WEBEX_ROOM_ID, "max": 1}
    # --- แก้ไข: ต้องมี "Bearer " นำหน้า Token ---
    getHTTPHeader = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    # --- แก้ไข: เพิ่ม try...except block เพื่อให้โปรแกรมไม่ล่มเมื่อเกิด error ---
    try:
        r = requests.get(
            "https://webexapis.com/v1/messages",
            params=getParameters,
            headers=getHTTPHeader,
        )
        if not r.status_code == 200:
            print(
                f"Warning: Incorrect reply from Webex Teams API. Status code: {r.status_code}"
            )
            if r.status_code == 401:
                print(
                    ">>> Your WEBEX_ACCESS_TOKEN may have expired. Please update it. <<<"
                )
            continue

        json_data = r.json()
        if not json_data.get("items"):
            continue

        # --- แก้ไข: เพิ่ม Logic ป้องกันการทำงานซ้ำซ้อน ---
        current_message_id = json_data["items"][0].get("id")
        if current_message_id == last_message_id:
            continue  # ข้ามไปถ้าเป็นข้อความเดิม

        last_message_id = current_message_id  # อัปเดต ID ของข้อความล่าสุด
        message = json_data["items"][0]["text"]
        print(f"Received message: {message}")

        if message.startswith(f"/{MY_STUDENT_ID} "):
            parts = message.split()
            command = parts[1] if len(parts) > 1 else None
            print(f"Executing command: {command}")

            # 5. Complete the logic for each command
            responseMessage = ""
            if command == "create":
                responseMessage = netconf_final.create(MY_STUDENT_ID)
            elif command == "delete":
                responseMessage = netconf_final.delete(MY_STUDENT_ID)
            elif command == "enable":
                responseMessage = netconf_final.enable(MY_STUDENT_ID)
            elif command == "disable":
                responseMessage = netconf_final.disable(MY_STUDENT_ID)
            elif command == "status":
                responseMessage = netconf_final.status(MY_STUDENT_ID)
            # --- แก้ไข: เรียกฟังก์ชันจากไฟล์ที่ถูกต้องตามโจทย์ ---
            elif command == "gigabit_status":
                responseMessage = (
                    netmiko_final.gigabit_status()
                )  # <-- ต้องมาจาก netmiko_final
            elif command == "showrun":
                responseMessage = ansible_final.showrun(
                    MY_STUDENT_ID
                )  # <-- ต้องมาจาก ansible_final
            else:
                responseMessage = "Error: No command or unknown command"

            # 6. Post the message to the Webex Teams room
            postHTTPHeaders = {
                "Authorization": f"Bearer {ACCESS_TOKEN}"
            }  # <-- แก้ไข: ต้องมี "Bearer "

            if command == "showrun" and "ok=2" in responseMessage:
                filename = f"show_run_{MY_STUDENT_ID}_CSR1000v.txt"  # <-- แก้ไข: ทำให้ชื่อไฟล์เป็นแบบไดนามิก
                try:
                    with open(filename, "rb") as file_content:
                        multipart_data = MultipartEncoder(
                            fields={
                                "roomId": WEBEX_ROOM_ID,
                                "text": f"Show running-config for {MY_STUDENT_ID}",
                                "files": (filename, file_content, "text/plain"),
                            }
                        )
                        postHTTPHeaders["Content-Type"] = multipart_data.content_type
                        r_post = requests.post(
                            "https://webexapis.com/v1/messages",
                            data=multipart_data,
                            headers=postHTTPHeaders,
                        )
                except FileNotFoundError:
                    responseMessage = (
                        f"Error: Ansible ran, but file '{filename}' was not found."
                    )

            if not (command == "showrun" and "ok=2" in responseMessage):
                postData = {"roomId": WEBEX_ROOM_ID, "text": responseMessage}
                postHTTPHeaders["Content-Type"] = "application/json"
                r_post = requests.post(
                    "https://webexapis.com/v1/messages",
                    data=json.dumps(postData),
                    headers=postHTTPHeaders,
                )

            if not r_post.status_code == 200:
                print(
                    f"Error posting message to Webex. Status: {r_post.status_code}, Details: {r_post.text}"
                )

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
