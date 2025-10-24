from ncclient import manager
import xmltodict
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
from xml.etree.ElementTree import ParseError

# --- แก้ไข: กำหนดค่าคงที่สำหรับการเชื่อมต่อ ---
# แนะนำให้ใช้ IP ของ Router ที่คุณได้รับมอบหมาย
ROUTER_IP = "10.0.15.61"
NETCONF_PORT = 830
USERNAME = "admin"
PASSWORD = "cisco"


# --- แก้ไข: สร้างฟังก์ชันเชื่อมต่อเพื่อจัดการ Error ได้ดีขึ้น ---
def connect_to_router():
    """Establishes a NETCONF connection to the router."""
    try:
        return manager.connect(
            host=ROUTER_IP,
            port=NETCONF_PORT,
            username=USERNAME,
            password=PASSWORD,
            hostkey_verify=False,
            timeout=10,  # เพิ่ม timeout เพื่อป้องกันการค้าง
            device_params={"name": "csr"},
        )
    except (TimeoutExpiredError, SessionCloseError) as e:
        print(f"Error connecting to router: {e}")
        return None


# --- แก้ไข: สร้างฟังก์ชันสำหรับสร้าง IP Address ตามโจทย์ ---
def get_ip_details(student_id):
    """Generates IP address details from student ID."""
    last_three = student_id[-3:]
    x = int(last_three[0])
    y = int(last_three[1:])
    ip_address = f"172.{x}.{y}.1"
    netmask = "255.255.255.0"
    return ip_address, netmask


def create(student_id):
    """Creates a Loopback interface."""
    ip_address, netmask = get_ip_details(student_id)
    # --- แก้ไข: เติม XML Payload สำหรับสร้าง Interface ---
    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>Loopback{student_id}</name>
          <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
          <enabled>true</enabled>
          <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
            <address>
              <ip>{ip_address}</ip>
              <netmask>{netmask}</netmask>
            </address>
          </ipv4>
        </interface>
      </interfaces>
    </config>
    """
    try:
        with connect_to_router() as m:
            if m is None:
                return "Error: Could not connect to the router."
            m.edit_config(target="running", config=netconf_config)
            return f"Interface loopback {student_id} is created successfully"
    except Exception as e:
        # --- แก้ไข: จัดการ Error กรณี Interface มีอยู่แล้ว ---
        if "data-exists" in str(e):
            return f"Cannot create: Interface loopback {student_id}"
        return f"Error during create: {e}"


def delete(student_id):
    """Deletes a Loopback interface."""
    # --- แก้ไข: เติม XML Payload สำหรับลบ Interface ---
    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface operation="delete">
          <name>Loopback{student_id}</name>
        </interface>
      </interfaces>
    </config>
    """
    try:
        with connect_to_router() as m:
            if m is None:
                return "Error: Could not connect to the router."
            m.edit_config(target="running", config=netconf_config)
            return f"Interface loopback {student_id} is deleted successfully"
    except Exception as e:
        # --- แก้ไข: จัดการ Error กรณี Interface ไม่มีอยู่แล้ว ---
        if "data-missing" in str(e):
            return f"Cannot delete: Interface loopback {student_id}"
        return f"Error during delete: {e}"


def enable(student_id):
    """Enables a Loopback interface."""
    # --- แก้ไข: เติม XML Payload สำหรับ enable ---
    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>Loopback{student_id}</name>
          <enabled>true</enabled>
        </interface>
      </interfaces>
    </config>
    """
    # --- แก้ไข: ตรวจสอบก่อนว่ามี Interface หรือไม่ ---
    if "No Interface" in status(student_id):
        return f"Cannot enable: Interface loopback {student_id}"
    try:
        with connect_to_router() as m:
            if m is None:
                return "Error: Could not connect to the router."
            m.edit_config(target="running", config=netconf_config)
            return f"Interface loopback {student_id} is enabled successfully"
    except Exception as e:
        return f"Error during enable: {e}"


def disable(student_id):
    """Disables a Loopback interface."""
    # --- แก้ไข: เติม XML Payload สำหรับ disable ---
    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>Loopback{student_id}</name>
          <enabled>false</enabled>
        </interface>
      </interfaces>
    </config>
    """
    # --- แก้ไข: ตรวจสอบก่อนว่ามี Interface หรือไม่ ---
    if "No Interface" in status(student_id):
        return f"Cannot shutdown: Interface loopback {student_id}"
    try:
        with connect_to_router() as m:
            if m is None:
                return "Error: Could not connect to the router."
            m.edit_config(target="running", config=netconf_config)
            return f"Interface loopback {student_id} is shutdowned successfully"
    except Exception as e:
        return f"Error during disable: {e}"


def status(student_id):
    """Retrieves the status of a Loopback interface."""
    # --- แก้ไข: เติม XML Filter สำหรับดึงข้อมูลสถานะ ---
    netconf_filter = f"""
    <filter>
      <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>Loopback{student_id}</name>
        </interface>
      </interfaces-state>
    </filter>
    """
    try:
        with connect_to_router() as m:
            if m is None:
                return "Error: Could not connect to the router."
            reply = m.get(filter=netconf_filter)
            print("--- RAW XML REPLY FROM ROUTER ---")
            print(reply.xml)
            data_dict = xmltodict.parse(reply.xml)

            interface_data = (
                data_dict.get("rpc-reply", {})
                .get("data", {})
                .get("interfaces-state", {})
                .get("interface")
            )

            if interface_data:
                admin_status = interface_data.get("admin-status")
                oper_status = interface_data.get("oper-status")

                if admin_status == "up" and oper_status == "up":
                    return f"Interface loopback {student_id} is enabled"
                elif admin_status == "down" and oper_status == "down":
                    return f"Interface loopback {student_id} is disabled"
            else:
                return f"No Interface loopback {student_id}"
    except (ParseError, AttributeError):
        # กรณีที่ reply กลับมาไม่มีข้อมูล interface เลย
        return f"No Interface loopback {student_id}"
    except Exception as e:
        return f"Error during status check: {e}"
