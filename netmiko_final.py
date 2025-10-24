from netmiko import ConnectHandler
from pprint import pprint
# --- (ลบ import re) ---

username = "admin"
password = "cisco"


# --- (ฟังก์ชัน gigabit_status เหมือนเดิม) ---
def gigabit_status(ip_address):
    # (โค้ดส่วนนี้เหมือนเดิม)
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
            command = "show banner motd"
            result = ssh.send_command(command, use_textfsm=True)

            print("--- MOTD DEBUG (TextFSM + show banner motd) ---")
            pprint(result)
            print("----------------------------------------------")

            # [ 1. กรณีที่ TextFSM ทำงานสำเร็จ (ได้ List[Dict]) ]
            if (
                isinstance(result, list)
                and len(result) > 0
                and isinstance(result[0], dict)
            ):
                banner_dict = result[0]
                if "message" in banner_dict:
                    motd_message = banner_dict.get("message")
                    return motd_message.strip()
                else:
                    return "Error: No MOTD Configured"

            # [ 2. กรณีที่ TextFSM ทำงานสำเร็จ แต่ไม่พบ MOTD (ได้ List ว่าง) ]
            elif isinstance(result, list) and len(result) == 0:
                return "Error: No MOTD Configured"

            # [ 3. ★★★ เพิ่มใหม่: กรณี TextFSM ล้มเหลว แต่ส่ง Raw String กลับมา (มีข้อความ) ★★★ ]
            elif isinstance(result, str) and result.strip():
                # ถ้าผลลัพธ์เป็น String ที่มีเนื้อหา ให้ใช้ String นั้นเลย
                return result.strip()

            # [ 4. กรณี TextFSM ล้มเหลว และส่ง String ว่างกลับมา ]
            elif isinstance(result, str) and not result.strip():
                return "Error: No MOTD Configured"

            # [ 5. กรณีอื่นๆ ที่ไม่คาดคิด ]
            else:
                return f"Error: Could not parse output from {ip_address} (Unexpected TextFSM output)."

    except Exception as e:
        error_message = f"An unexpected error occurred in get_motd on {ip_address}: {e}"
        pprint(error_message)
        return error_message
