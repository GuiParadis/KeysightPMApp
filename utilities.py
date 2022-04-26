import time
# utility functions and common commands


def try_parse_int(s, base=10, val=None):
    try:
        return int(s, base)
    except ValueError:
        return val


def try_parse_float(s, val=None):
    try:
        return float(s)
    except ValueError:
        return val


def WaitOperationComplete(device, log=None):
    status = 4
    while status > 0:
        try:
            time.sleep(0.05)
            device.write("STAT:OPER:COND?")
            status = int(device.read_raw())
            time.sleep(0.05)
        except Exception as e:
            if log is not None:
                log.error(e)
            return False
    return True


def local(device, setLocal):
    loc = "0"
    if setLocal: loc = "1"
    device.write("LCL "+loc)
    return device.query("LCL?")
