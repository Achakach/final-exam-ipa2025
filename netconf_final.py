from ncclient import manager
import xmltodict
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
from xml.etree.ElementTree import ParseError

# --- แก้ไข: ลบ ROUTER_IP ที่ Hardcode ออก ---
# ROUTER_IP = "10.0.15.61"  <-- ลบออก
NETCONF_PORT = 830
USERNAME = "admin"
PASSWORD = "cisco"


# --- ★★★[แก้ไข]★★★: รับ ip_address เป็นพารามิเตอร์ ---
def connect_to_router(ip_address):
    """Establishes a NETCONF connection to the router."""
    try:
        return manager.connect(
            host=ip_address,  # <-- ★★★[แก้ไข]★★★
            port=NETCONF_PORT,
            username=USERNAME,
            password=PASSWORD,
            hostkey_verify=False,
            timeout=10,
            device_params={"name": "csr"},
        )
    except (TimeoutExpiredError, SessionCloseError) as e:
        print(f"Error connecting to router ({ip_address}): {e}")  # <-- เพิ่ม IP ใน log
        return None


# --- (ฟังก์ชัน get_ip_details ไม่ต้องแก้ไข) ---
def get_ip_details(student_id):
    """Generates IP address details from student ID."""
    last_three = student_id[-3:]
    x = int(last_three[0])
    y = int(last_three[1:])
    ip_address = f"172.{x}.{y}.1"
    netmask = "255.255.255.0"
    return ip_address, netmask


# --- ★★★[แก้ไข]★★★: รับ ip_address ในทุกฟังก์ชัน ---


def create(student_id, ip_address):
    """Creates a Loopback interface."""
    loopback_ip, netmask = get_ip_details(student_id)
    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>Loopback{student_id}</name>
          <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
          <enabled>true</enabled>
          <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
            <address>
              <ip>{loopback_ip}</ip>
              <netmask>{netmask}</netmask>
            </address>
          </ipv4>
        </interface>
      </interfaces>
    </config>
    """
    try:
        with connect_to_router(ip_address) as m:  # <-- ★★★[แก้ไข]★★★
            if m is None:
                return f"Error: Could not connect to the router at {ip_address}."
            m.edit_config(target="running", config=netconf_config)
            return (
                f"Interface loopback {student_id} is created successfully using netconf"
            )
    except Exception as e:
        if "data-exists" in str(e):
            return (
                f"Cannot create: Interface loopback {student_id} (checked by netconf)"
            )
        return f"Error during create: {e}"


def delete(student_id, ip_address):
    """Deletes a Loopback interface."""
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
        with connect_to_router(ip_address) as m:  # <-- ★★★[แก้ไข]★★★
            if m is None:
                return f"Error: Could not connect to the router at {ip_address}."
            m.edit_config(target="running", config=netconf_config)
            return (
                f"Interface loopback {student_id} is deleted successfully using netconf"
            )
    except Exception as e:
        if "data-missing" in str(e):
            return (
                f"Cannot delete: Interface loopback {student_id} (checked by netconf)"
            )
        return f"Error during delete: {e}"


def enable(student_id, ip_address):
    """Enables a Loopback interface."""
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
    # ★★★[แก้ไข]★★★: ส่ง ip_address ไปให้ฟังก์ชัน status
    if "No Interface" in status(student_id, ip_address):
        return f"Cannot enable: Interface loopback {student_id} (checked by netconf)"
    try:
        with connect_to_router(ip_address) as m:  # <-- ★★★[แก้ไข]★★★
            if m is None:
                return f"Error: Could not connect to the router at {ip_address}."
            m.edit_config(target="running", config=netconf_config)
            return (
                f"Interface loopback {student_id} is enabled successfully using netconf"
            )
    except Exception as e:
        return f"Error during enable: {e}"


def disable(student_id, ip_address):
    """Disables a Loopback interface."""
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
    # ★★★[แก้ไข]★★★: ส่ง ip_address ไปให้ฟังก์ชัน status
    if "No Interface" in status(student_id, ip_address):
        return f"Cannot shutdown: Interface loopback {student_id} (checked by netconf)"
    try:
        with connect_to_router(ip_address) as m:  # <-- ★★★[แก้ไข]★★★
            if m is None:
                return f"Error: Could not connect to the router at {ip_address}."
            m.edit_config(target="running", config=netconf_config)
            return f"Interface loopback {student_id} is shutdowned successfully using netconf"
    except Exception as e:
        return f"Error during disable: {e}"


def status(student_id, ip_address):
    """Retrieves the status of a Loopback interface."""
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
        with connect_to_router(ip_address) as m:  # <-- ★★★[แก้ไข]★★★
            if m is None:
                return f"Error: Could not connect to the router at {ip_address}."
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
                    return f"Interface loopback {student_id} is enabled (checked by netconf)"
                elif admin_status == "down" and oper_status == "down":
                    return f"Interface loopback {student_id} is disabled (checked by netconf)"
            else:
                return f"No Interface loopback {student_id} (checked by netconf)"
    except (ParseError, AttributeError):
        return f"No Interface loopback {student_id} (checked by netconf)"
    except Exception as e:
        return f"Error during status check: {e}"
