from netmiko import ConnectHandler
from pprint import pprint
# --- ★★★[แก้ไข]★★★: ลบ re ออก เราจะใช้ TextFSM
# import re

username = "admin"
password = "cisco"


# --- (ฟังก์ชัน gigabit_status เหมือนเดิม ไม่ต้องแก้ไข) ---
def gigabit_status(ip_address):
    device_params = {
        "device_type": "cisco_xe",
        "ip": ip_address,
        "username": username,
        "password": password,
    }

    status_list = []
    try:
        with ConnectHandler(**device_params) as ssh:
            up = 0
            down = 0
            admin_down = 0

            command = "show ip interface brief"
            result = ssh.send_command(command, use_textfsm=True)

            if not isinstance(result, list):
                error_msg = f"Error: TextFSM failed to parse the output from the router ({ip_address})."
                print(error_msg)
                return error_msg

            for interface_data in result:
                if interface_data["interface"].startswith("GigabitEthernet"):
                    status_text = ""
                    if (
                        interface_data.get("status") == "up"
                        and interface_data.get("proto") == "up"
                    ):
                        status_text = "up"
                        up += 1
                    elif interface_data.get("status") == "administratively down":
                        status_text = "administratively down"
                        admin_down += 1
                    else:
                        status_text = "down"
                        down += 1

                    status_list.append(f"{interface_data['interface']} {status_text}")

            if not status_list:
                return f"No GigabitEthernet interfaces were found on {ip_address}."

            status_summary = ", ".join(status_list)
            count_summary = f"{up} up, {down} down, {admin_down} administratively down"
            ans = f"{status_summary} -> {count_summary}"

            pprint(ans)
            return ans

    except Exception as e:
        error_message = (
            f"An unexpected error occurred in gigabit_status on {ip_address}: {e}"
        )
        pprint(error_message)
        return error_message


# --- ★★★[แก้ไข]★★★: ฟังก์ชันสำหรับอ่าน MOTD (ใช้ TextFSM + show banner motd) ---
def get_motd(ip_address):
    """
    Retrieves the MOTD banner from the router using Netmiko and TextFSM.
    """
    device_params = {
        "device_type": "cisco_xe",
        "ip": ip_address,
        "username": username,
        "password": password,
    }

    try:
        with ConnectHandler(**device_params) as ssh:
            # --- ★★★[แก้ไข]★★★: ใช้คำสั่ง 'show banner motd'
            command = "show running-config"

            # --- ★★★[แก้ไข]★★★: เปิด 'use_textfsm=True' ตามโจทย์
            result = ssh.send_command(command, use_textfsm=True)

            print("--- MOTD DEBUG (TextFSM + show banner motd) ---")
            pprint(result)
            print("----------------------------------------------")

            # --- ★★★[แก้ไข]★★★: ตรวจสอบผลลัพธ์ที่ถูกต้อง (List[Dict])
            # TextFSM สำหรับ 'show banner motd' จะคืนค่าเป็น List ที่มี Dict 1 ตัว
            # เช่น: [{'banner': 'motd', 'message': 'Authorized users only!'}]
            if (
                isinstance(result, list)
                and len(result) > 0
                and isinstance(result[0], dict)
            ):
                banner_dict = result[0]

                # ตรวจสอบว่า key 'message' (จาก template) มีอยู่หรือไม่
                if "message" in banner_dict:
                    motd_message = banner_dict.get("message")
                    return motd_message.strip()  # .strip() เผื่อมี \n
                else:
                    # ถ้าได้ List[Dict] แต่ไม่มี key 'message' (อาจจะไม่มี MOTD)
                    return f"No MOTD banner is set on {ip_address}."

            # --- ถ้า TextFSM คืนค่าว่างเปล่า (กรณีไม่มี banner motd) ---
            elif isinstance(result, str) and not result:
                return f"No MOTD banner is set on {ip_address}."

            # --- ถ้าโครงสร้างไม่ตรง (เช่น ได้ raw text กลับมา) ---
            else:
                return f"Error: Could not parse output from {ip_address} (Unexpected TextFSM output)."

    except Exception as e:
        error_message = f"An unexpected error occurred in get_motd on {ip_address}: {e}"
        pprint(error_message)
        return error_message


# --- ★★★[สิ้นสุดการแก้ไข]★★★
