from netmiko import ConnectHandler
from pprint import pprint

# --- ข้อมูลการเชื่อมต่อ (ควรอยู่นอกฟังก์ชัน) ---
device_ip = "10.0.15.61"  # กรุณาเปลี่ยนเป็น IP ของ Router ที่คุณได้รับ
username = "admin"
password = "cisco"

device_params = {
    "device_type": "cisco_xe",
    "ip": device_ip,
    "username": username,
    "password": password,
}


def gigabit_status():
    status_list = []
    try:
        with ConnectHandler(**device_params) as ssh:
            up = 0
            down = 0
            admin_down = 0

            command = "show ip interface brief"
            result = ssh.send_command(command, use_textfsm=True)
            # print("\n" + "="*20 + " DEBUGGING INFO " + "="*20)
            # print("Type of 'result':", type(result))
            # print("Content of 'result':")
            # pprint(result)
            # print("="*58 + "\n")

            # --- เพิ่มการตรวจสอบข้อมูล ---
            # 1. ตรวจสอบว่าผลลัพธ์ที่ได้เป็น list หรือไม่
            if not isinstance(result, list):
                error_msg = f"Error: TextFSM failed to parse the output from the router. Please check if ntc-templates are installed."
                print(error_msg)
                return error_msg

            for interface_data in result:
                if interface_data["interface"].startswith("GigabitEthernet"):
                    status_text = ""
                    # ตรวจสอบสถานะเพื่อความแม่นยำ
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
                return "No GigabitEthernet interfaces were found."

            status_summary = ", ".join(status_list)
            count_summary = f"{up} up, {down} down, {admin_down} administratively down"
            ans = f"{status_summary} -> {count_summary}"

            pprint(ans)
            return ans

    except Exception as e:
        error_message = f"An unexpected error occurred in gigabit_status: {e}"
        pprint(error_message)
        return error_message
