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
        device.write(':SENSe' + str(pnum+1) + ':POWer:RANGe: ' + str(powrange))


def setwav(device, pnum, wav):
    minwav = device.query(':SENSe' + str(pnum+1) + ':POWer:WAVelength? min')
    maxwav = device.query(':SENSe' + str(pnum+1) + ':POWer:WAVelength? max')
    if wav < minwav:
        wav = minwav
    elif wav > maxwav:
        wav = maxwav
    device.write(':SENSe' + str(pnum+1) + ':POWer:WAVelength ' + str(wav) + 'nm')


def setatime(device, pnum, atime):
    device.write(':SENSe' + str(pnum+1) + ':POWer:ATIMe ' + str(atime))


def dark(device, pnum):
    device.write(':SENSe' + str(pnum+1) + ':CORRection:COLLect:ZERO')
    util.WaitOperationComplete(device)


def readpow(device):
    # readpow = device.query(':READ' + str(pnum+1) + ':POW?')
    # util.WaitOperationComplete(device)
    readpow = device.query(':FETCh:POWer:ALL?')
    return readpow

# def reference(device, pnum):


def conttrig(device, pnum, stat):
    device.write(':INITiate' + str(pnum) + ':CONTinuous ' + str(stat))
