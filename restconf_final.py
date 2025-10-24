import json
import requests

requests.packages.urllib3.disable_warnings()


# --- ★★★[เพิ่มใหม่]★★★: import ฟังก์ชัน get_ip_details จาก netconf_final ---
# (หรือคัดลอกฟังก์ชัน get_ip_details มาไว้ที่นี่เลยก็ได้)
# ในที่นี้ ผมจะคัดลอกมาไว้เลยเพื่อความสมบูรณ์ในไฟล์เดียว
def get_ip_details(student_id):
    """Generates IP address details from student ID."""
    last_three = student_id[-3:]
    x = int(last_three[0])
    y = int(last_three[1:])
    ip_address = f"172.{x}.{y}.1"
    netmask = "255.255.255.0"
    return ip_address, netmask


# --- ★★★[สิ้นสุดการเพิ่มใหม่]★★★


# Router IP Address จะถูกส่งมาจากพารามิเตอร์ ip_address
# api_url = "<!!!REPLACEME with URL of RESTCONF Configuration API!!!>" # <-- ไม่ใช้ตัวแปร global นี้

# the RESTCONF HTTP headers, including the Accept and Content-Type
# Two YANG data formats (JSON and XML) work with RESTCONF
# --- ★★★[แก้ไข]★★★: ระบุ Headers ที่ถูกต้อง ---
headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json",
}
basicauth = ("admin", "cisco")


# --- ★★★[แก้ไข]★★★: เพิ่มพารามิเตอร์ student_id และ ip_address ---
def create(student_id, ip_address):
    # --- ★★★[เพิ่มใหม่]★★★: สร้าง URL สำหรับการสร้าง interface ---
    api_url_create = f"https://{ip_address}/restconf/data/ietf-interfaces:interfaces"

    # --- ★★★[เพิ่มใหม่]★★★: ดึง IP และ Netmask ---
    loopback_ip, netmask = get_ip_details(student_id)

    # --- ★★★[แก้ไข]★★★: ระบุ YANG data สำหรับสร้าง Loopback ---
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": f"Loopback{student_id}",
            "type": "iana-if-type:softwareLoopback",
            "enabled": True,
            "ietf-ip:ipv4": {"address": [{"ip": loopback_ip, "netmask": netmask}]},
        }
    }

    # --- ★★★[แก้ไข]★★★: ใช้ HTTP POST เพื่อสร้าง ---
    resp = requests.post(
        api_url_create,  # <-- URL
        data=json.dumps(yangConfig),  # <-- data
        auth=basicauth,
        headers=headers,  # <-- headers
        verify=False,
    )

    if resp.status_code >= 200 and resp.status_code <= 299:
        print("STATUS OK: {}".format(resp.status_code))
        # --- ★★★[แก้ไข]★★★: ข้อความตอบกลับ ---
        return f"Interface loopback {student_id} is created successfully"
    else:
        print("Error. Status Code: {}".format(resp.status_code))
        # --- ★★★[เพิ่มใหม่]★★★: จัดการ Error กรณี Interface มีอยู่แล้ว (409 Conflict) ---
        if resp.status_code == 409:
            return f"Cannot create: Interface loopback {student_id}"
        return f"Error during create: {resp.text}"


# --- ★★★[แก้ไข]★★★: เพิ่มพารามิเตอร์ student_id และ ip_address ---
def delete(student_id, ip_address):
    # --- ★★★[เพิ่มใหม่]★★★: สร้าง URL สำหรับการลบ interface (ระบุชื่อ) ---
    api_url_delete = f"https://{ip_address}/restconf/data/ietf-interfaces:interfaces/interface=Loopback{student_id}"

    # --- ★★★[แก้ไข]★★★: ใช้ HTTP DELETE เพื่อลบ ---
    resp = requests.delete(
        api_url_delete,  # <-- URL
        auth=basicauth,
        headers=headers,  # <-- headers
        verify=False,
    )

    if resp.status_code >= 200 and resp.status_code <= 299:
        print("STATUS OK: {}".format(resp.status_code))
        # --- ★★★[แก้ไข]★★★: ข้อความตอบกลับ ---
        return f"Interface loopback {student_id} is deleted successfully"
    else:
        print("Error. Status Code: {}".format(resp.status_code))
        # --- ★★★[เพิ่มใหม่]★★★: จัดการ Error กรณี Interface ไม่มีอยู่ (404 Not Found) ---
        if resp.status_code == 404:
            return f"Cannot delete: Interface loopback {student_id}"
        return f"Error during delete: {resp.text}"


# --- ★★★[แก้ไข]★★★: เพิ่มพารามิเตอร์ student_id และ ip_address ---
def enable(student_id, ip_address):
    # --- ★★★[เพิ่มใหม่]★★★: ตรวจสอบว่ามี Interface ก่อนหรือไม่ ---
    if "No Interface" in status(student_id, ip_address):
        return f"Cannot enable: Interface loopback {student_id}"

    # --- ★★★[เพิ่มใหม่]★★★: สร้าง URL สำหรับการแก้ไข interface (ระบุชื่อ) ---
    api_url_enable = f"https://{ip_address}/restconf/data/ietf-interfaces:interfaces/interface=Loopback{student_id}"

    # --- ★★★[แก้ไข]★★★: ระบุ YANG data สำหรับ enable (enabled: true) ---
    # เราจะส่งแค่ field ที่ต้องการเปลี่ยน
    yangConfig = {
        "ietf-interfaces:interface": {"name": f"Loopback{student_id}", "enabled": True}
    }

    # --- ★★★[แก้ไข]★★★: ใช้ HTTP PATCH เพื่ออัปเดตบางส่วน ---
    resp = requests.patch(
        api_url_enable,  # <-- URL
        data=json.dumps(yangConfig),  # <-- data
        auth=basicauth,
        headers=headers,  # <-- headers
        verify=False,
    )

    if resp.status_code >= 200 and resp.status_code <= 299:
        print("STATUS OK: {}".format(resp.status_code))
        # --- ★★★[แก้ไข]★★★: ข้อความตอบกลับ ---
        return f"Interface loopback {student_id} is enabled successfully"
    else:
        print("Error. Status Code: {}".format(resp.status_code))
        return f"Error during enable: {resp.text}"


# --- ★★★[แก้ไข]★★★: เพิ่มพารามิเตอร์ student_id และ ip_address ---
def disable(student_id, ip_address):
    # --- ★★★[เพิ่มใหม่]★★★: ตรวจสอบว่ามี Interface ก่อนหรือไม่ ---
    if "No Interface" in status(student_id, ip_address):
        return f"Cannot shutdown: Interface loopback {student_id}"

    # --- ★★★[เพิ่มใหม่]★★★: สร้าง URL สำหรับการแก้ไข interface (ระบุชื่อ) ---
    api_url_disable = f"https://{ip_address}/restconf/data/ietf-interfaces:interfaces/interface=Loopback{student_id}"

    # --- ★★★[แก้ไข]★★★: ระบุ YANG data สำหรับ disable (enabled: false) ---
    yangConfig = {
        "ietf-interfaces:interface": {"name": f"Loopback{student_id}", "enabled": False}
    }

    # --- ★★★[แก้ไข]★★★: ใช้ HTTP PATCH เพื่ออัปเดตบางส่วน ---
    resp = requests.patch(
        api_url_disable,  # <-- URL
        data=json.dumps(yangConfig),  # <-- data
        auth=basicauth,
        headers=headers,  # <-- headers
        verify=False,
    )

    if resp.status_code >= 200 and resp.status_code <= 299:
        print("STATUS OK: {}".format(resp.status_code))
        # --- ★★★[แก้ไข]★★★: ข้อความตอบกลับ ---
        return f"Interface loopback {student_id} is shutdowned successfully"
    else:
        print("Error. Status Code: {}".format(resp.status_code))
        return f"Error during disable: {resp.text}"


# --- ★★★[แก้ไข]★★★: เพิ่มพารามิเตอร์ student_id และ ip_address ---
def status(student_id, ip_address):
    # --- ★★★[แก้ไข]★★★: URL สำหรับดู Operational Data (interfaces-state) ---
    api_url_status = f"https://{ip_address}/restconf/data/ietf-interfaces:interfaces-state/interface=Loopback{student_id}"

    # --- ★★★[แก้ไข]★★★: ใช้ HTTP GET เพื่อดึงข้อมูล ---
    resp = requests.get(
        api_url_status,  # <-- URL
        auth=basicauth,
        headers=headers,  # <-- headers
        verify=False,
    )

    if resp.status_code >= 200 and resp.status_code <= 299:
        print("STATUS OK: {}".format(resp.status_code))

        try:
            response_json = resp.json()
            # --- ★★★[แก้ไข]★★★: ดึงค่าจาก JSON response ---
            # เนื่องจากเรา GET ไปที่ interface โดยตรง ข้อมูลจะอยู่ใน key นี้
            interface_data = response_json.get("ietf-interfaces:interface")
            if not interface_data:
                return f"No Interface loopback {student_id}"

            admin_status = interface_data.get("admin-status")
            oper_status = interface_data.get("oper-status")

            # --- ★★★[แก้ไข]★★★: ข้อความตอบกลับตามสถานะ ---
            if admin_status == "up" and oper_status == "up":
                return f"Interface loopback {student_id} is enabled"
            elif admin_status == "down" and oper_status == "down":
                return f"Interface loopback {student_id} is disabled"
            else:
                # กรณีสถานะไม่ตรงกัน (เช่น admin up แต่ oper down)
                return f"Interface loopback {student_id} status is: admin {admin_status}, oper {oper_status}"
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON response for status check.")
            return f"Error during status check: Invalid JSON response."

    elif resp.status_code == 404:
        print("STATUS NOT FOUND: {}".format(resp.status_code))
        # --- ★★★[แก้ไข]★★★: ข้อความตอบกลับ (ไม่พบ Interface) ---
        return f"No Interface loopback {student_id}"
    else:
        print("Error. Status Code: {}".format(resp.status_code))
        return f"Error during status check: {resp.text}"
