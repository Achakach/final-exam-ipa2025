from netmiko import ConnectHandler
from pprint import pprint

# --- แก้ไข: ลบข้อมูลการเชื่อมต่อที่ Hardcode ออก ---
# device_ip = "10.0.15.61"  <-- ลบออก
username = "admin"
password = "cisco"
# device_params = { ... } <-- ลบออก


# --- ★★★[แก้ไข]★★★: รับ ip_address เป็นพารามิเตอร์ ---
def gigabit_status(ip_address):
    # --- ★★★[แก้ไข]★★★: ย้าย device_params มาสร้างข้างในนี้ ---
    device_params = {
        "device_type": "cisco_xe",
        "ip": ip_address,  # <-- ★★★[แก้ไข]★★★
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


# --- ★★★[เพิ่มใหม่]★★★: ฟังก์ชันสำหรับอ่าน MOTD โดยใช้ TextFSM ---
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
            # เราใช้ show running-config เพราะ ntc_templates มี
            # template สำหรับคำสั่งนี้ที่สามารถดึง 'banner_motd' ได้
            command = "show running-config"

            # use_textfsm=True จะใช้ ntc_templates เพื่อแยกส่วน
            result = ssh.send_command(command, use_textfsm=True)

            if isinstance(result, dict):
                # TextFSM จะคืนค่า dict และเราดึงคีย์ 'banner_motd'
                motd_message = result.get("banner_motd")

                if motd_message:
                    # คืนค่าเฉพาะข้อความ MOTD
                    return motd_message
                else:
                    return "Error: No MOTD Configured"
            else:
                # กรณี TextFSM ไม่สามารถ parse ได้ (ไม่น่าเกิด)
                return f"Error: Could not parse running-config from {ip_address}."

    except Exception as e:
        error_message = f"An unexpected error occurred in get_motd on {ip_address}: {e}"
        pprint(error_message)
        return error_message


# --- ★★★[สิ้นสุดการเพิ่มใหม่]★★★
