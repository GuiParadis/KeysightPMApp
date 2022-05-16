import utilities as util
import math


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
    device.write(':SENSe' + str(pnum+1) + ':CORRection:COLLect:ZERO')
    util.WaitOperationComplete(device)


def readpow(device):
    # readpow = {'mW': '', 'dBm': ''}
    # read = device.query_binary_values(':FETCh:POWer:ALL?')
    read = [i for i in device.query_binary_values(':FETCh:POWer:ALL?') if i != 0]
    # readpow['dBm'] = [10 * math.log10(1000 * i) for i in read]
    return read


def conttrig(device, pnum, stat):
    device.write(':INITiate' + str(pnum+1) + ':CONTinuous ' + str(stat))
