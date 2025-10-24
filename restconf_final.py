import json
import requests
requests.packages.urllib3.disable_warnings()

# Router IP Address is 10.0.15.181-184
api_url = "<!!!REPLACEME with URL of RESTCONF Configuration API!!!>"

# the RESTCONF HTTP headers, including the Accept and Content-Type
# Two YANG data formats (JSON and XML) work with RESTCONF
headers = <!!!REPLACEME with Accept and Content-Type information headers!!!>
basicauth = ("admin", "cisco")


def create():
    yangConfig = <!!!REPLACEME with YANG data!!!>

    resp = requests.<!!!REPLACEME with the proper HTTP Method!!!>(
        <!!!REPLACEME with URL!!!>,
        data=json.dumps(<!!!REPLACEME with yangConfig!!!>),
        auth=basicauth,
        headers=<!!!REPLACEME with HTTP Header!!!>,
        verify=False
        )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return "<!!!REPLACEME with proper message!!!>"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))


def delete():
    resp = requests.<!!!REPLACEME with the proper HTTP Method!!!>(
        <!!!REPLACEME with URL!!!>,
        auth=basicauth,
        headers=<!!!REPLACEME with HTTP Header!!!>,
        verify=False
        )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return "<!!!REPLACEME with proper message!!!>"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))


def enable():
    yangConfig = <!!!REPLACEME with YANG data!!!>

    resp = requests.<!!!REPLACEME with the proper HTTP Method!!!>(
        <!!!REPLACEME with URL!!!>,
        data=json.dumps(<!!!REPLACEME with yangConfig!!!>),
        auth=basicauth,
        headers=<!!!REPLACEME with HTTP Header!!!>,
        verify=False
        )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return "<!!!REPLACEME with proper message!!!>"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))


def disable():
    yangConfig = <!!!REPLACEME with YANG data!!!>

    resp = requests.<!!!REPLACEME with the proper HTTP Method!!!>(
        <!!!REPLACEME with URL!!!>,
        data=json.dumps(<!!!REPLACEME with yangConfig!!!>),
        auth=basicauth,
        headers=<!!!REPLACEME with HTTP Header!!!>,
        verify=False
        )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return "<!!!REPLACEME with proper message!!!>"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))


def status():
    api_url_status = "<!!!REPLACEME with URL of RESTCONF Operational API!!!>"

    resp = requests.<!!!REPLACEME with the proper HTTP Method!!!>(
        <!!!REPLACEME with URL!!!>,
        auth=basicauth,
        headers=<!!!REPLACEME with HTTP Header!!!>,
        verify=False
        )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        response_json = resp.json()
        admin_status = <!!!REPLACEME!!!>
        oper_status = <!!!REPLACEME!!!>
        if admin_status == 'up' and oper_status == 'up':
            return "<!!!REPLACEME with proper message!!!>"
        elif admin_status == 'down' and oper_status == 'down':
            return "<!!!REPLACEME with proper message!!!>"
    elif(resp.status_code == 404):
        print("STATUS NOT FOUND: {}".format(resp.status_code))
        return "<!!!REPLACEME with proper message!!!>"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
