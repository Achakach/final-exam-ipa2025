import subprocess
import json
# sudo apt install ansible
# ansible-galaxy collection install cisco.ios


# --- ★★★[แก้ไข]★★★: เพิ่ม ip_address เป็นพารามิเตอร์
def showrun(student_id, ip_address, router_name="CSR1000v"):
    # read https://www.datacamp.com/tutorial/python-subprocess to learn more about subprocess
    command = [
        "ansible-playbook",
        "-i",
        "hosts",
        "showrun.yml",
        "--limit",
        ip_address,  # <-- ★★★[แก้ไข]★★★: เพิ่ม flag --limit
        "--extra-vars",
        f"MY_STUDENT_ID={student_id}",
        "--extra-vars",
        f"ROUTER_NAME={router_name}",
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    output_log = f"{result.stdout}\n{result.stderr}"
    print("--- ANSIBLE OUTPUT ---")
    print(output_log)
    print("----------------------")
    if "ok=2" in output_log and "failed=0" in output_log:
        return f"Success!!! {output_log}"
    else:
        return f"Failure {output_log}"


def set_motd(student_id, ip_address, motd_message):
    """
    Calls the Ansible playbook to set the MOTD banner.
    Uses JSON for extra-vars to safely handle spaces.
    """

    # --- ★★★[แก้ไข]★★★: สร้าง JSON string สำหรับ --extra-vars
    extra_vars = json.dumps({"MOTD_MESSAGE": motd_message, "MY_STUDENT_ID": student_id})

    command = [
        "ansible-playbook",
        "-i",
        "hosts",
        "set_motd.yml",
        "--limit",
        ip_address,
        "--extra-vars",
        extra_vars,  # <-- ★★★[แก้ไข]★★★: ส่ง JSON string ที่สร้างไว้
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    output_log = f"{result.stdout}\n{result.stderr}"
    print("--- ANSIBLE (set_motd) OUTPUT ---")
    print(output_log)
    print("---------------------------------")

    # สำหรับ task เดียว (set_motd) เราจะเช็ค "ok=1" (หรือ changed=1)
    if ("ok=1" in output_log or "changed=1" in output_log) and "failed=0" in output_log:
        return "Ok: success"
    else:
        return f"Failure {output_log}"
