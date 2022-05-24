import utilities as util


def setunit(device, pnum, unit):
    if unit == 'dBm':
        u = 0
    else:
        u = 1
    device.write(':SENSe' + str(pnum+1) + ':POWer:REFerence:STATe 0')
    device.write(':SENSe' + str(pnum+1) + ':POWer:UNIT ' + str(u))


def setrange(device, pnum, powrange):
    if powrange == 'Auto':
        device.write(':SENSe' + str(pnum+1) + ':POWer:RANGe:AUTO 1')
    else:
        device.write(':SENSe' + str(pnum+1) + ':POWer:RANGe:AUTO 0')
        device.write(':SENSe' + str(pnum+1) + ':POWer:RANGe ' + str(powrange))


def setwav(device, pnum, wav):
    minwav = float(device.query(':SENSe' + str(pnum+1) + ':POWer:WAVelength? min'))
    maxwav = float(device.query(':SENSe' + str(pnum+1) + ':POWer:WAVelength? max'))
    if float(wav) * 1e-9 < minwav:
        wav = minwav/1e-9
    elif float(wav) * 1e-9 > maxwav:
        wav = maxwav/1e-9
    device.write(':SENSe' + str(pnum+1) + ':POWer:WAVelength ' + str(wav) + 'nm')


def setatime(device, pnum, atime):
    device.write(':SENSe' + str(pnum+1) + ':POWer:ATIMe ' + str(atime))


def dark(device, pnum):
    if pnum != 'All':
        device.timeout = 20000
        device.write(':SENSe' + str(pnum+1) + ':CORRection:COLLect:ZERO')
        if util.WaitOperationComplete(device):
            device.timeout = 10000
            pass
    else:
        device.timeout = 70000
        device.write(':SENSe:CORRection:COLLect:ZERO:ALL')
        if util.WaitOperationComplete(device):
            device.timeout = 10000
            pass


def readpow(device):
    read = [i for i in device.query_binary_values(':FETCh:POWer:ALL?') if i != 0]
    return read


def conttrig(device, pnum, stat):
    device.write(':INITiate' + str(pnum+1) + ':CONTinuous ' + str(stat))


def getip(device):
    try:
        ip = device.query(':SYSTem:COMMunicate:ETHernet:IPADdress:CURRent?')
        ip = ip.lstrip('"').rstrip('"')
        return ip
    except Exception as e:
        return 'No IP address available'


def setmode(device, pnum, mode):
    device.write(':SENSe' + str(pnum+1) + ':POWer:REFerence:STATe ' + str(mode))


def reference(device, pnum, init=False):
    if init:
        device.write(':SENSe' + str(pnum+1) + ':POWer:REFerence TOREF,0DBM')
    else:
        setmode(device, pnum, '0')
        read = readpow(device)
        device.write(':SENSe' + str(pnum+1) + ':POWer:REFerence TOREF,' + str(read[pnum]) + 'DBM')
        setmode(device, pnum, '1')

