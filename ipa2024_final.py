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

from urllib3.util import response
import netconf_final
import restconf_final  # <-- ★★★[เพิ่มใหม่]★★★: Import ไฟล์ restconf

# --- แก้ไข: เพิ่ม import สำหรับโจทย์ส่วนที่ 2 ---
import netmiko_final
import ansible_final
from requests_toolbelt.multipart.encoder import MultipartEncoder
from dotenv import load_dotenv

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
current_method = None  # <-- ★★★[เพิ่มใหม่]★★★: ตัวแปรเก็บสถานะ (None, "netconf", "restconf")

print(f"Bot started. Waiting for commands for {MY_STUDENT_ID}...")
print(f"Current method: {current_method}")

while True:
    time.sleep(0.2)
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
        print(f"\nReceived message: {message}")

        if message.startswith(f"/{MY_STUDENT_ID} "):
            parts = message.split()
            ip_address = None
            command_to_run = None  # <-- ตัวแปรเก็บคำสั่งที่จะรัน
            responseMessage = ""  # <-- รีเซ็ตข้อความตอบกลับ

            # --- ★★★[แก้ไข]★★★: Logic การตรวจสอบคำสั่งใหม่ทั้งหมด ---

            # 1. ตรวจสอบคำสั่ง 'ตั้งค่า method' ก่อน (ทำงานได้เสมอ)
            if len(parts) == 1:
                responseMessage = "Error: Nothing specified"
            elif len(parts) == 2:
                if parts[1] == "netconf":
                    current_method = "netconf"
                    responseMessage = "OK: Netconf"
                    print(f"Method set to: {current_method}")
                elif parts[1] == "restconf":
                    current_method = "restconf"
                    responseMessage = "OK: Restconf"
                    print(f"Method set to: {current_method}")
                else:
                    # ถ้ามี 2 ส่วน แต่ไม่ใช่ netconf/restconf
                    # ให้สันนิษฐานว่าตั้งใจจะรันคำสั่ง แต่พิมพ์ผิด
                    if parts[1] in [
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
                        # อาจจะพิมพ์ IP แต่ไม่มีคำสั่ง
                        # เราจะปล่อยให้โลจิกข้างล่างจับ "Error: No command specified"
                        pass

            # --- ★★★[แก้ไข โลจิกใหม่ทั้งหมด]★★★ ---
            # 2. ถ้าไม่ใช่คำสั่งตั้งค่า method ให้ตรวจสอบคำสั่งอื่น
            if responseMessage == "":
                # 2a. ตรวจสอบรูปแบบคำสั่ง (IP + command) ก่อน
                if len(parts) < 2:
                    # กรณี: /66070244 (ถูกจับไปแล้วใน L85)
                    # แต่เผื่อไว้
                    responseMessage = "Error: Nothing specified"
                elif len(parts) < 3:
                    # กรณี: /66070244 10.0.15.61 (ไม่มีคำสั่ง)
                    responseMessage = "Error: No command specified"
                else:
                    # 2b. มี IP และ Command ครบถ้วน
                    ip_address = parts[1]
                    command_to_run = parts[2]

                    # 2c. ตรวจสอบว่า command นี้ต้องใช้ method (netconf/restconf) หรือไม่
                    netconf_restconf_commands = [
                        "create",
                        "delete",
                        "enable",
                        "disable",
                        "status",
                    ]

                    if command_to_run in netconf_restconf_commands:
                        # --- ถ้าใช่คำสั่งกลุ่มนี้ ค่อยเช็ค method ---
                        if current_method is None:
                            responseMessage = "Error: No method specified"
                        else:
                            # Method ถูกตั้งค่าแล้ว (OK)
                            print(
                                f"Attempting command: {command_to_run} on {ip_address} using {current_method}"
                            )
                    else:
                        # --- ถ้าเป็น gigabit_status, showrun, หรือคำสั่งที่ไม่รู้จัก ---
                        # เราจะปล่อยให้บล็อก "5. ทำงานตามคำสั่ง" (L160) ทำงาน
                        # ซึ่งมันจะจับ 'gigabit_status', 'showrun', และ 'Error: Unknown command' เอง
                        print(
                            f"Attempting command: {command_to_run} on {ip_address} (Method check skipped)"
                        )
            # --- ★★★[สิ้นสุดการแก้ไขโลจิก]★★★ ---

            # 5. ทำงานตามคำสั่ง (ถ้ามี)
            if command_to_run:
                # --- ★★★[เพิ่มใหม่]★★★: แยกการทำงานตาม current_method ---

                # กลุ่มคำสั่ง Netconf/Restconf
                if command_to_run in [
                    "create",
                    "delete",
                    "enable",
                    "disable",
                    "status",
                ]:
                    # (โลจิกส่วนนี้ทำงานต่อได้เลย เพราะผ่านการตรวจสอบ method มาแล้ว)
                    if current_method == "netconf":
                        if command_to_run == "create":
                            responseMessage = netconf_final.create(
                                MY_STUDENT_ID, ip_address
                            )
                        elif command_to_run == "delete":
                            responseMessage = netconf_final.delete(
                                MY_STUDENT_ID, ip_address
                            )
                        elif command_to_run == "enable":
                            responseMessage = netconf_final.enable(
                                MY_STUDENT_ID, ip_address
                            )
                        elif command_to_run == "disable":
                            responseMessage = netconf_final.disable(
                                MY_STUDENT_ID, ip_address
                            )
                        elif command_to_run == "status":
                            responseMessage = netconf_final.status(
                                MY_STUDENT_ID, ip_address
                            )

                    elif current_method == "restconf":
                        if command_to_run == "create":
                            responseMessage = restconf_final.create(
                                MY_STUDENT_ID, ip_address
                            )
                        elif command_to_run == "delete":
                            responseMessage = restconf_final.delete(
                                MY_STUDENT_ID, ip_address
                            )
                        elif command_to_run == "enable":
                            responseMessage = restconf_final.enable(
                                MY_STUDENT_ID, ip_address
                            )
                        elif command_to_run == "disable":
                            responseMessage = restconf_final.disable(
                                MY_STUDENT_ID, ip_address
                            )
                        elif command_to_run == "status":
                            responseMessage = restconf_final.status(
                                MY_STUDENT_ID, ip_address
                            )

                # --- ★★★[แก้ไข]★★★: ลบคอมเมนต์ว่าต้องตั้งค่า method ก่อน ---
                # กลุ่มคำสั่ง Netmiko
                elif command_to_run == "gigabit_status":
                    responseMessage = netmiko_final.gigabit_status(ip_address)

                # กลุ่มคำสั่ง Ansible
                elif command_to_run == "showrun":
                    responseMessage = ansible_final.showrun(MY_STUDENT_ID, ip_address)

                # ไม่รู้จักคำสั่ง
                else:
                    responseMessage = "Error: Unknown command"

            # 6. Post the message to the Webex Teams room
            postHTTPHeaders = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

            # --- ★★★[แก้ไข]★★★: ตรวจสอบว่า responseMessage 'มี' ข้อความหรือไม่
            if responseMessage:
                if command_to_run == "showrun" and "ok=2" in responseMessage:
                    filename = f"show_run_{MY_STUDENT_ID}_CSR1000v.txt"
                    try:
                        with open(filename, "rb") as file_content:
                            multipart_data = MultipartEncoder(
                                fields={
                                    "roomId": WEBEX_ROOM_ID,
                                    "text": f"Show running-config for {MY_STUDENT_ID} on {ip_address}",
                                    "files": (filename, file_content, "text/plain"),
                                }
                            )
                            postHTTPHeaders["Content-Type"] = (
                                multipart_data.content_type
                            )
                            r_post = requests.post(
                                "https://webexapis.com/v1/messages",
                                data=multipart_data,
                                headers=postHTTPHeaders,
                            )
                    except FileNotFoundError:
                        responseMessage = (
                            f"Error: Ansible ran, but file '{filename}' was not found."
                        )
                        # --- ส่ง Error นี้เป็นข้อความปกติแทน ---
                        postData = {"roomId": WEBEX_ROOM_ID, "text": responseMessage}
                        postHTTPHeaders["Content-Type"] = "application/json"
                        r_post = requests.post(
                            "https://webexapis.com/v1/messages",
                            data=json.dumps(postData),
                            headers=postHTTPHeaders,
                        )

                # --- ★★★[แก้ไข]★★★: ส่งข้อความตอบกลับ (ที่ไม่ใช่ไฟล์)
                # ตรวจสอบว่า *ไม่ใช่* showrun ที่สำเร็จ (เพราะส่งเป็นไฟล์ไปแล้ว)
                if not (command_to_run == "showrun" and "ok=2" in responseMessage):
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
