import subprocess

# sudo apt install ansible
# ansible-galaxy collection install cisco.ios


def showrun(student_id, router_name="CSR1000v"):
    # read https://www.datacamp.com/tutorial/python-subprocess to learn more about subprocess
    command = [
        "ansible-playbook",
        "-i",
        "hosts",
        "showrun.yml",
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
