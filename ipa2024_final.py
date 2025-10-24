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
last_message_id = None

while True:
    time.sleep(1)
    getParameters = {"roomId": WEBEX_ROOM_ID, "max": 1}
    getHTTPHeader = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

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

        current_message_id = json_data["items"][0].get("id")
        if current_message_id == last_message_id:
            continue

        last_message_id = current_message_id
        message = json_data["items"][0]["text"]
        print(f"Received message: {message}")

        if message.startswith(f"/{MY_STUDENT_ID} "):
            parts = message.split()
            ip_address = None
            command = None
            responseMessage = ""  # <-- ★★★[แก้ไข]★★★: เริ่มต้นตัวแปรไว้ก่อน

            # --- ★★★[แก้ไข]★★★: Logic การตรวจสอบคำสั่งใหม่ ---
            if len(parts) < 2:
                # กรณี: /66070244 (มีแค่ 1 ส่วน)
                responseMessage = "Error: No IP specified"
            elif len(parts) < 3:
                # กรณี: /66070244 10.0.15.61 (มี 2 ส่วน)
                # หรือ /66070244 create (มี 2 ส่วน)

                # ตรวจสอบว่าส่วนที่ 2 เป็นคำสั่งหรือไม่
                potential_command = parts[1]
                if potential_command in [
                    "create",
                    "delete",
                    "enable",
                    "disable",
                    "status",
                    "gigabit_status",
                    "showrun",
                ]:
                    responseMessage = "Error: No IP specified"
                else:
                    # ถ้าไม่ใช่คำสั่ง ก็ถือว่าเป็น IP
                    responseMessage = "Error: No method specified"
            else:
                # กรณี: /66070244 10.0.15.61 create (มี 3 ส่วนขึ้นไป)
                ip_address = parts[1]
                command = parts[2]
                print(f"Executing command: {command} on IP: {ip_address}")

            # 5. Complete the logic for each command
            # --- ★★★[แก้ไข]★★★: ส่ง ip_address เข้าไปในฟังก์ชัน ---

            # ทำงานต่อเมื่อ command ถูกกำหนดค่า (ไม่มี Error จากด้านบน)
            if command == "create":
                responseMessage = netconf_final.create(MY_STUDENT_ID, ip_address)
            elif command == "delete":
                responseMessage = netconf_final.delete(MY_STUDENT_ID, ip_address)
            elif command == "enable":
                responseMessage = netconf_final.enable(MY_STUDENT_ID, ip_address)
            elif command == "disable":
                responseMessage = netconf_final.disable(MY_STUDENT_ID, ip_address)
            elif command == "status":
                responseMessage = netconf_final.status(MY_STUDENT_ID, ip_address)
            elif command == "gigabit_status":
                responseMessage = netmiko_final.gigabit_status(ip_address)
            elif command == "showrun":
                responseMessage = ansible_final.showrun(MY_STUDENT_ID, ip_address)
            elif command is not None:
                # ถ้ามี command แต่ไม่ตรงกับอันไหนเลย
                responseMessage = "Error: Unknown command"

            # 6. Post the message to the Webex Teams room
            postHTTPHeaders = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

            if command == "showrun" and "ok=2" in responseMessage:
                filename = f"show_run_{MY_STUDENT_ID}_CSR1000v.txt"
                try:
                    with open(filename, "rb") as file_content:
                        multipart_data = MultipartEncoder(
                            fields={
                                "roomId": WEBEX_ROOM_ID,
                                "text": f"Show running-config for {MY_STUDENT_ID} on {ip_address}",  # <-- เพิ่ม IP ในข้อความ
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

            # --- ★★★[แก้ไข]★★★: ปรับเงื่อนไขการส่งข้อความ
            # ถ้า responseMessage ไม่ว่าง (มี Error หรือมีผลลัพธ์)
            # และ (ไม่ใช่คำสั่ง showrun ที่สำเร็จ)
            if responseMessage and not (
                command == "showrun" and "ok=2" in responseMessage
            ):
                postData = {"roomId": WEBEX_ROOM_ID, "text": responseMessage}
                postHTTPHeaders["Content-Type"] = "application/json"
                r_post = requests.post(
                    "https://webexapis.com/v1/messages",
                    data=json.dumps(postData),
                    headers=postHTTPHeaders,
                )

            if "r_post" in locals() and not r_post.status_code == 200:
                print(
                    f"Error posting message to Webex. Status: {r_post.status_code}, Details: {r_post.text}"
                )

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
