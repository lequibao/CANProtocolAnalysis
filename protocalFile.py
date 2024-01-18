"""
data: 2018-09-06
author： Xiaoyamei
project: 1. the file is served for protocaoAnalysis.py.
         2. this file main contains a class named Protocal, it contains numbers of analysis methods for protocals
         between electric vehicle and charging pile.
"""

import math

# 定义把高位与地位进行交换的处理函数
def changePosition(data):
    li_data = list(data)  # 把字符串转换为列表，以便后面处理，处理完了再转换为字符串。
    temp = li_data[0:2]
    li_data[0:2] = data[2:4]
    li_data[2:4] = temp[:]
    data = ''.join(li_data)  # 处理完成后，把列表转换为字符串。
    return data


# 处理电压值的函数(适合：分辨率0.1、偏移量为0的电压.分辨率不为0.1或偏移量不为0的电压请选择proceeHex函数)
def processVoltage(data):   # data参数为报文中的原值
    voltageExchange = changePosition(data)   # 高低位交换
    try:
        voltage = str(round(int(voltageExchange, 16) * 0.1, 1)) + 'V'   # 把16进制转换为10进制，乘以分辨率（0.1）并保留1位小数，再加上单位V
        return voltage
    except:
        return data     # 如果出现异常，电压就显示原值


# 处理电流值的函数（适合：分辨率0.1、 偏移量-400的电流。分辨率不为0.1或偏移量不为-400的电流请选择proceeHex函数）
def processCurrent(data):    # data参数为报文中的原值
    currentExchange = changePosition(data)  # 高低位交换
    try:
        # 把16进制转换为10进制，再乘以分辨率（0.1），然后偏移量处理（-400），保留1位小数并加上单位
        current = str(round(400 - int(currentExchange, 16) * 0.1, 1)) + 'A'
        return current
    except:
        return data      # 如果出现异常，电流就显示为原值


# 处理二进制字符串中字符的提取和处理
def processBit(dataBin, dict, startBit, endBit):    # dataBin为单字节的二进制字符串、dict为字典、startBit为开始位、endBit为结束位
    if startBit == 1:
        dataStr = dataBin[-endBit:]
    else:
        dataStr = dataBin[-endBit:(-startBit + 1)]  # 取二进制字符串的bit：startBit-endBit（如bit1-2，就是bit[-2:0]）
    try:
        result = dict[dataStr]      # 获取字典中对应的value
        return result
    except:
        result = dataStr    # 如果字典中无该项，则等于提取的原字符串
        return result


# 没有字典的二进制处理（dataBin:二进制字符串， startBit/endBit:开始位/结束位， resolution:分辨率， offset:偏移量）
def processBitWithoutDict(dataBin, startBit, endBit, resolution, offset):
    # 在二进制字符串中提取对应的位
    if startBit == 1:
        dataStr = dataBin[-endBit:]     # 取二进制字符串的bit：startBit-endBit（如bit1-2，就是bit[-2:]）
    else:
        dataStr = dataBin[-endBit:(-startBit + 1)]  # 取二进制字符串的bit：startBit-endBit（如bit3-4，就是bit[-4:-2]）
    # 结合提取的二进制位、分辨率、偏移量计算输出值
    try:
        result = round(int(dataStr, 2) * resolution + offset, 2)    # 转成10进制，乘以分辨率， 加上偏移量
        return result
    except:
        result = dataStr    # 如果异常（如传进来的二进制字符串错误），则结果等于提取的原字符串
        return result


# 从16进制字符串提取字节，结合分辨率和偏移量计算结果（适合：两个字节的计算）
# (dataStr:去掉空格和序号后的字符串，startByte:开始字节,endByte:结束字节,resolution:分辨率, offset:偏移量, unit:单位)
def processHex(dataStr, startByte, endByte, resolution, offset, unit):
    dataStr = dataStr[(startByte - 1) * 2: endByte * 2]     # 根据开始和结束字节提取字符串（如byte1-byte2，就是data[0:4]）
    if len(dataStr) == (endByte - startByte + 1) * 2:   # 如果提取的字符串长度是期望的位数（如2个字节对应的字符串长度为4）
        dataChange = changePosition(dataStr)    # 高低位交换（只适合两字节的字符串）
        try:
            resultWithoutOffset = int(dataChange, 16) * resolution  # 16进制转成10进制，乘以分辨率
            decimalDigitsDict = {'0.01': 2, '0.1': 1, '1': 0}   # 分辨率0.01保留小数2位，0.1保留小数1位，1保留小数0位
            if offset == -400:
                # 适合计算电流，因为电流的偏移量为-400
               result = str(round(400 - resultWithoutOffset, decimalDigitsDict[str(resolution)])) + unit
            else:
                # 适合非-400的偏移量
                result = str(round(resultWithoutOffset + offset, decimalDigitsDict[str(resolution)])) + unit
        except:
            result = dataStr  # 如果出现异常（如出现非16进制外的字符），则返回原字符串
    else:
        result = 'null'     # 如果提取的字符串不是预期长度，则返回null
    return result


# 去掉多包报文中的序号(参数中的data为去掉空格和回车后的多包报文)
def delMulPackSerialNum(data):
    data = list(data)   # 把字符串转成列表
    length = len(data)  # 列表长度
    packetsNum = math.ceil(length / 16)  # 长度除16并向上取整,为报文含包的数量
    # 把每包开头的两个字符替换成空格
    for i in range(packetsNum):
        data[i * 16] = ' '
        data[i * 16 + 1] = ' '
        i += 1
    data = ''.join(data)    # 把data由列表转成字符串
    data = data.replace(' ', '')   # 去掉空格
    return data     # 返回去掉序号后的data


# 版本号处理(3字节,参数data为去掉空格和回车的三字节字符串)
def processVersion(data):
    # 计算整数部分
    iteger_part_str = data[0:2]     # 获取data的第一字节
    if len(iteger_part_str) == 2:
        try:
            iteger_part = str(int(iteger_part_str, 16))
        except:
            iteger_part = iteger_part_str
    else:
        iteger_part = 'null'
    # 计算小数部分
    decimal_part_str = data[2:6]    # 获取data的第2、3字节
    if len(decimal_part_str) == 4:
        decimal_part_exchange = changePosition(decimal_part_str)     # 进行高低位交换
        try:
            decimal_part = str(int(decimal_part_exchange, 16))
        except:
            decimal_part = decimal_part_str
    else:
        decimal_part = 'null'
    # 组装整数和小数部分
    result = 'V{}.{}'.format(iteger_part, decimal_part)
    return result


#协议类型定义
class Protocal(object):
    # cml充电桩最大输出能力报文解析
    def cmlPileMaximumOutputCapability(self, data):
        maxPressure = 'null'    # 最大输出电压
        minPressure = 'null'    # 最小输出电压
        maxCurrent = 'null'     # 最大输出电流
        minCurrent = 'null'     # 最小输出电流
        data = data.replace(' ', '')  # 去掉报文中的空格
        data = data.replace('\n', '')
        try:
            #计算最大输出电压
            maxPressureStr = data[0:4]
            if len(maxPressureStr) == 4:
                maxPressure = processVoltage(maxPressureStr)
            #计算最低输出电压
            minPressureStr = data[4:8]
            if len(minPressureStr) == 4:
                minPressure = processVoltage(minPressureStr)
            #计算最大输出电流
            maxCurrentStr = data[8:12]
            if len(maxCurrentStr) == 4:
                maxCurrent = processCurrent(maxCurrentStr)
            #计算最低输出电流
            minCurrentStr = data[12:16]
            if len(minCurrentStr) == 4:
                minCurrent = processCurrent(minCurrentStr)
        except:
            pass
        finally:
            resultStr = "***CML Charging Pile Maximum Output Capability Message***\nHighest Output Voltage: %s\nLowest Output Voltage: %s\nMaximum Output Current: %s\n" \
            "Minimum Output Current: %s" % (maxPressure, minPressure, maxCurrent, minCurrent)

            return resultStr

    # bcl电池充电需求报文解析
    def bclBatteryChargingDemand(self, data):
        pressureDemand = 'null'     # 电压需求
        currentDemand = 'null'      # 电流需求
        chargePattern = 'null'  # 充电模式
        data = data.replace(' ', '')  # 去空格
        data = data.replace('\n', '')
        try:
            # 计算电压需求
            pressureDemandStr = data[0:4]
            if len(pressureDemandStr) == 4:
                pressureDemand = processVoltage(pressureDemandStr)   # 获取高低位互换后的字符串
            # 计算电流需求
            currentDemandStr = data[4:8]
            if len(currentDemandStr) == 4:
                currentDemand = processCurrent(currentDemandStr)
            # 判断充电模式，0x01:恒压充电， 0x02:恒流充电
            chargePatternStr = data[8:10]
            if len(chargePatternStr) == 2:
                chargePatternDict = {'01': 'Constant Voltage Charging', '02': 'Constant Current Charging'}
                try:
                    chargePattern = chargePatternDict[chargePatternStr]
                except KeyError:
                    chargePattern = chargePatternStr
        except:
            pass
        finally:
            resultStr = "***BCL Battery Charging Demand Message***\nVoltage Demand: %s\nCurrent Demand: %s\nCharging Mode: %s"\
                        % (pressureDemand, currentDemand, chargePattern)
            return resultStr

    # chm充电机握手报文
    def chmHandshake(self, data):
        data = data.replace(' ', '')
        data = data.replace('\n', '')
        versionInfo = processVersion(data)
        resultStr = "***CHM Charger Handshake Message***\nCharger Communication Protocol Version Number: {}".format(versionInfo)
        return resultStr

    # BHM车辆握手报文
    def bhmHandshake(self, data):
        max_voltage = 'null'    # 最高允许充电总电压变量
        data = data.replace(' ', '')
        data = data.replace('\n', '')
        try:
            # 计算最高允许充电总电压变量
            max_voltagea_str = data[0:4]    # 获取data的前两个字节
            if len(max_voltagea_str) == 4:
                max_voltage = processVoltage(max_voltagea_str)
        except:
            pass
        finally:
            resultStr = "***BHM Vehicle Handshake Message***\nHighest Allowable Total Charging Voltage: %s" % max_voltage
            return resultStr

    # CRM充电机辨识报文
    def crm_identify(self, data):
        identify_result = 'null'    # 辨识结果变量
        data = data.replace(' ', '')
        data = data.replace('\n', '')
        # 计算辨识结果
        identify_result_dict = {'00': 'BMS cannot identify', 'AA': 'BMS can identify'}
        identify_result_str = data[0:2]
        if len(identify_result_str) == 2:
            try:
                identify_result = identify_result_dict[identify_result_str.upper()]
            except:
                identify_result = identify_result_str
        resultStr = "***CRM Charger Identification Message***\nIdentification result: %s" % identify_result
        return resultStr

    # BRO车辆准备就绪报文
    def broCarReadyOk(self, data):
        isReady = 'null'    # BMS是否充电准备就绪变量
        data = data.replace(' ', '')
        data = data.replace('\n', '')
        # 计算 BMS是否充电准备就绪
        isReadyDict = {'00': 'No', 'AA': 'Yes'}
        isReadyStr = data[0:2]
        if len(isReadyStr) == 2:
            try:
                isReady = isReadyDict[isReadyStr.upper()]
            except:
                isReady = isReadyStr
        resultStr = "***CRO Charger Ready Message***\nIs charger ready to charge: %s" % isReady
        return resultStr

    # CRO充电机准备就绪报文
    def croChargerReadyOk(self, data):
        isReady = 'null'    # 充电机是否充电准备就绪 变量
        data = data.replace(' ', '')
        data = data.replace('\n', '')
        # 计算 充电机是否充电准备就绪
        isReadyDict = {'00': '否', 'AA': '是'}
        isReadyStr = data[0:2]
        if len(isReadyStr) == 2:
            try:
                isReady = isReadyDict[isReadyStr.upper()]
            except:
                isReady = isReadyStr
        resultStr = "***CRO充电机准备就绪报文***\n充电机是否充电准备就绪：%s" % isReady
        return resultStr

    # CCS充电机充电状态报文
    def ccsChargerState(self, data):
        voltageOutput = 'null'  # 电压输出 变量
        currentOutput = 'null'  # 电流输出
        times = 'null'          # 累计充电时间
        status = 'null'         # 充电允许状态
        data = data.replace(' ', '')
        data = data.replace('\n', '')
        try:
            # 计算电压输出
            voltageOutputStr = data[0:4]   # 获取报文前两个字节
            if len(voltageOutputStr) == 4:
                voltageOutput = processVoltage(voltageOutputStr)
            # 计算电流输出
            currentOutputStr = data[4:8]   # 获取报文第3～4字节
            if len(currentOutputStr) == 4:
                currentOutput = processCurrent(currentOutputStr)
            # 计算累计充电时间
            timesStr = data[8:12]
            if len(timesStr) == 4:
                timesExchange = changePosition(timesStr)
                try:
                    times = str(int(timesExchange, 16)) + 'min'
                except:
                    times = timesStr
            # 计算是否允许充电
            statusStr = data[12:14]    # 获取第7字节（原字符）
            statusDict = {'00': 'Paused', '01': 'Allowed'}
            if len(statusStr) == 2:
                try:
                    statusBin = bin(int(statusStr, 16))[2:].zfill(8)  # 把第7字节转成2进制
                except:
                    status = statusStr  # 如果出现异常（如出现16进制外的字符）则取原字符
                else:
                    status = processBit(statusBin, statusDict, 1, 2)
        except:
            pass
        finally:
            resultStr = "***CCS Charger Charging State Message***\nVoltage output value: %s\nCurrent output value: %s\nTotal charging time: %s\nCharging allow status: %s" % (
        voltageOutput, currentOutput, times, status)
            return resultStr

    # BSM动力蓄电池状态信息报文
    def bsmBatteryStatus(self, data):
        highVoltageNum = 'null'         # 最高动力蓄电池电压所在编号 变量
        highBatteryTem = 'null'         # 最高动力蓄电池温度
        highTemNum = 'null'             # 最高温度检测点编号
        lowBatterTem = 'null'           # 最低动力蓄电池温度
        lowTemNum = 'null'              # 最低温度检测点编号
        voltageStatus = 'null'          # 单体动力蓄电池电压状态
        batterySOCStatus = 'null'       # 整车动力蓄电池SOC状态
        batteryCurrentStatus = 'null'   # 动力蓄电池充电电流状态
        batteryTemStatus = 'null'       # 动力蓄电池温度状态
        batteryInsulationState = 'null'      # 动力蓄电池绝缘状态
        batteryConnectStatus = 'null'   # 动力蓄电池输出连接器连接状态
        chargeAllowState = 'null'       # 充电允许状态

        data = data.replace(' ', '')
        data = data.replace('\n', '')
        try:
            # 计算最高动力蓄电池电压所在编号
            highVoltageNumStr = data[0:2]   # 获取报文byte1
            if len(highVoltageNumStr) == 2:
                try:
                    highVoltageNum = str(int(highVoltageNumStr, 16) + 1)     # 把byte1的16进制转成10进制，再加上偏移量1
                except:
                    highVoltageNum = highVoltageNumStr
            # 计算最高动力蓄电池温度
            highBatteryTemStr = data[2:4]   # 获取报文byte2
            if len(highBatteryTemStr) == 2:
                try:
                    highBatteryTem = str(int(highBatteryTemStr, 16) - 50) + '˚C'    # 把byte2的16进制转成10进制，再加上偏移量-50
                except:
                    highBatteryTem = highBatteryTemStr
            # 计算最高温度检测点编号
            highTemNumStr = data[4:6]       # 获取报文byte3
            if len(highTemNumStr) == 2:
                try:
                    highTemNum = str(int(highTemNumStr, 16) + 1)             # 把byte3的16进制转成10进制，再加上偏移量1
                except:
                    highTemNum = highTemNumStr
            # 计算最低动力蓄电池温度
            lowBatterTemStr = data[6:8]     # 获取报文byte4
            if len(lowBatterTemStr) == 2:
                try:
                    lowBatterTem = str(int(lowBatterTemStr, 16) - 50) + '˚C'        # 把byte4的16进制转成10进制，再加上偏移量-50
                except:
                    lowBatterTem = lowBatterTemStr
            # 计算最低温度检测点编号
            lowTemNumStr = data[8:10]       # 获取报文byte5
            if len(lowTemNumStr) == 2:
                try:
                    lowTemNum = str(int(lowTemNumStr, 16) + 1)               # 把byte5的16进制转成10进制，再加上偏移量1
                except:
                    lowTemNum = lowTemNumStr

            byte6Str = data[10:12]   # 获取报文byte6，为后续4个状态的计算提供数据
            if len(byte6Str) == 2:
                try:
                    byte6Bin = bin(int(byte6Str, 16))   # 把byte6转成2进制
                    byte6Bin = byte6Bin[2:].zfill(8)    # 去掉二进制开头的0b, 把二进制字符串右对齐，左边不够则用0填充至8位
                except:
                    voltageStatus = byte6Str
                    batterySOCStatus = byte6Str
                    batteryCurrentStatus = byte6Str
                    batteryTemStatus = byte6Str
                else:
                    # Calculate the status of individual power battery voltage
                    voltageStatusDict = {'00': 'Normal', '01': 'Too High', '10': 'Too Low'}
                    voltageStatus = processBit(byte6Bin, voltageStatusDict, 1, 2)
                    # Calculate the SOC status of the entire power battery
                    batterySOCStatusDict = {'00': 'Normal', '01': 'Too High', '10': 'Too Low'}
                    batterySOCStatus = processBit(byte6Bin, batterySOCStatusDict, 3, 4)
                    # Calculate the charging current status of the power battery
                    batteryCurrentStatusDict = {'00': 'Normal', '01': 'Overcurrent', '10': 'Untrusted'}
                    batteryCurrentStatus = processBit(byte6Bin, batteryCurrentStatusDict, 5, 6)
                    # Calculate the temperature status of the power battery
                    batteryTemStatusDict = {'00': 'Normal', '01': 'Too High', '10': 'Untrusted'}
                    batteryTemStatus = processBit(byte6Bin, batteryTemStatusDict, 7, 8)


            byte7Str = data[12:14]  # 获取报文byte7，为后续3个状态的计算提供数据
            if len(byte7Str) == 2:
                try:
                    byte7Bin = bin(int(byte7Str, 16))[2:].zfill(8)       # 把byte6转成2进制,去掉0b标记，并转成标准的8位二进制形式
                except:
                    batteryInsulationState = byte7Str
                    batteryConnectStatus = byte7Str
                    chargeAllowState = byte7Str
                else:
                    # Calculate the insulation status of the power battery
                    batteryInsulationStateDict = {'00': 'Normal', '01': 'Not Normal', '10': 'Untrusted'}
                    batteryInsulationState = processBit(byte7Bin, batteryInsulationStateDict, 1, 2)
                    # Calculate the connection status of the power battery output connector
                    batteryConnectStatusDict = {'00': 'Normal', '01': 'Not Normal', '10': 'Untrusted'}
                    batteryConnectStatus = processBit(byte7Bin, batteryConnectStatusDict, 3, 4)
                    # Calculate the charge allow status
                    chargeAllowStateDict = {'00': 'Forbidden', '01': 'Allowed'}
                    chargeAllowState = processBit(byte7Bin, chargeAllowStateDict, 5, 6)
        except:
            pass
        finally:
            resultStr = "***BSM Power Battery Status Information Message***\nHighest power battery voltage number: %s\nHighest power battery temperature: %s\n" \
                "Highest temperature detection point number: %s\nLowest power battery temperature: %s\nLowest temperature detection point number: %s\nIndividual power battery voltage status: %s\n" \
                "Entire power battery SOC status: %s\nPower battery charging current status: %s\nPower battery temperature status: %s\nPower battery insulation status: %s\n" \
                "Power battery output connector connection status: %s\nCharge allow status: %s" % (highVoltageNum, highBatteryTem, highTemNum, lowBatterTem, lowTemNum, voltageStatus, batterySOCStatus,
        batteryCurrentStatus, batteryTemStatus, batteryInsulationState, batteryConnectStatus, chargeAllowState)
            return resultStr


    # BCS多包数据（2包）
    def bcsMulPackets(self, data):
        voltage = 'null'    # 充电电压测量值
        current = 'null'    # 充电电流测量值
        highVoltage = 'null'    # 最高单体动力蓄电池电压及其组号-电压
        groupNum = 'null'   # 最高单体动力蓄电池电压及其组号-组号
        soc = 'null'    # 当前荷电状态SOC
        remainderTime = 'null'   # 估算剩余充电时间

        data = data.replace(' ', '')
        data = data.replace('\n', '')

        try:
            # 计算充电电压测量值
            voltageStr = data[2:6]  # 取data的byte2～3（去掉byte1的分包序号01）
            if len(voltageStr) == 4:
                voltage = processVoltage(voltageStr)    # 计算电压值

            # 计算充电电流测量值
            currentStr = data[6:10]    # 取data的byte4～5（去掉byte1的分包序号01）
            if len(currentStr) == 4:
                current = processCurrent(currentStr)    # 计算电流值

            # 计算最高单体动力蓄电池电压及其组号
            highVoltageAndGroupNumStr = data[10:14]     # 取data的byte6～7（去掉byte1的分包序号01）
            if len(highVoltageAndGroupNumStr) == 4:
                highVoltageAndGroupNumExchange = changePosition(highVoltageAndGroupNumStr)      # 高低位交换处理
                try:
                    highVoltageAndGroupNumBin = bin(int(highVoltageAndGroupNumExchange, 16))[2:].zfill(16)   # 转换成二进制字符串
                    # 计算最高单体动力蓄电池电压
                    highVoltageStr = highVoltageAndGroupNumBin[-12:]    # 获取二进制字符串的bit1——bit12
                    highVoltage = str(round(int(highVoltageStr, 2) * 0.01, 2)) + 'V'   # 把二进制字符串转换为十进制，乘以偏移量（0.01）
                    # 计算所在组号
                    groupNumStr = highVoltageAndGroupNumBin[0:4]   # 获取二进制字符串的bit13——bit16
                    groupNum = int(groupNumStr, 2)  # 把二进制字符串转成十进制
                except:
                    highVoltage = highVoltageAndGroupNumStr    # 如果出现异常（如报文中出现了十六进制之外的字符），则取原值
                    groupNum = highVoltageAndGroupNumStr

            # 计算当前荷电状态SOC
            socStr = data[14:16]    # 获取data的byte8（去掉byte1的分包序号01）
            if len(socStr) == 2:
                try:
                    soc = str(int(socStr, 16)) + '%'    # 计算soc值
                except:
                    soc = socStr

            # 估算剩余充电时间
            remainderTimeStr = data[18:22]  # 取data的byte10～11（去掉byte1和tyte2的分包序号01、02）
            if len(remainderTimeStr) == 4:
                remainderTimeExchange = changePosition(remainderTimeStr)    # 高低位交换
                try:
                    remainderTime = str(int(remainderTimeExchange, 16)) + 'min'  # 计算剩余充电时间
                except:
                    remainderTime = remainderTimeStr    # 如果常出现异常，则取原值
        except:
            pass
        finally:
            resultStr = "***BCS Battery Charging Overall Status Message***\nCharging voltage measurement: {}\nCharging current measurement: {}\nHighest single power battery voltage: {}\n" \
            "Group number of the highest single power battery voltage: {}\nCurrent State of Charge (SOC): {}\nEstimated remaining charging time: {}".format(voltage, current,
                                                                               highVoltage, groupNum, soc, remainderTime)
        return resultStr

    # BST中止充电报文
    def bstEndCharge(self, data):
        endReason = 'null'             # BMS中止充电原因
        socTarget = 'null'             # BMS中止充电原因-达到所需要的soc目标值
        totalVoltageSettle = 'null'    # BMS中止充电原因-达到总电压的设定值
        singleVoltageSettle = 'null'   # BMS中止充电原因-达到单体电压的设定值
        chargerEnd = 'null'            # BMS中止充电原因-充电机主动中止

        faultReason = 'null'           # BMS中止充电故障原因
        insulationFault = 'null'       # BMS中止充电故障原因-绝缘故障
        outConnOverTempr = 'null'      # BMS中止充电故障原因-输出连接器过温故障
        bmsAndoutConnOverTempr = 'null'     # BMS中止充电故障原因-BMS元件、输出连接器过温
        chargeConnFault = 'null'       # BMS中止充电故障原因-充电连接器故障
        batteryOverTempr = 'null'      # BMS中止充电故障原因-电池组温度过高故障
        highVolRelayFault = 'null'     # BMS中止充电故障原因-高压继电器故障
        monitorPoint2 = 'null'         # BMS中止充电故障原因-监测点2电压检测故障
        otherFault = 'null'            # BMS中止充电故障原因-Other故障

        errorReason = 'null'    # BMS中止充电错误原因
        currentOver = 'null'    # BMS中止充电错误原因-电流过大
        voltageOver = 'null'    # BMS中止充电错误原因-电压过大

        data = data.replace(' ', '')    # 去空格
        data = data.replace('\n', '')

        # 计算BMS中止充电原因
        endReasonStr = data[0:2]    # 取byte1
        if len(endReasonStr) == 2:
            try:
                endReasonBin = bin(int(endReasonStr, 16))[2:].zfill(8)   # 16进制转成2进制
            except:
                socTarget = totalVoltageSettle = singleVoltageSettle = chargerEnd = endReasonStr
            else:
                # Calculate bits 1-2: Reached the SOC target value required
                socTargetDict = {'00': 'Did not reach the required SOC target value', '01': 'Reached the required SOC target value', '10': 'Untrusted'}
                socTarget = processBit(endReasonBin, socTargetDict, 1, 2)
                # Calculate bits 3-4: Reached the set total voltage
                totalVoltageSettleDict = {'00': 'Did not reach the set total voltage', '01': "Reached the set total voltage", '10': 'Untrusted'}
                totalVoltageSettle = processBit(endReasonBin, totalVoltageSettleDict, 3, 4)
                # Calculate bits 5-6: Reached the set single cell voltage
                singleVoltageSettleDict = {'00': 'Did not reach the set single cell voltage', '01': "Reached the set single cell voltage", '10': 'Untrusted'}
                singleVoltageSettle = processBit(endReasonBin, singleVoltageSettleDict, 5, 6)
                # Calculate bits 7-8: Charger actively stopped
                chargerEndDict = {'00': 'Normal', '01': "Charger stopped (received CST frame)", '10': 'Untrusted'}
                chargerEnd = processBit(endReasonBin, chargerEndDict, 7, 8)

        # 计算BMS中止充电故障原因
        faultReasonStr = data[2:6]  # 取byte2-3
        if len(faultReasonStr) == 4:
            faultReasonChange = changePosition(faultReasonStr)  # 把提取的两个字节互换位置
            try:
                faultReasonBin = bin(int(faultReasonChange, 16))[2:].zfill(16)  # 转成2进制
            except:
                insulationFault = outConnOverTempr = bmsAndoutConnOverTempr = chargeConnFault = batteryOverTempr = \
                    highVolRelayFault = monitorPoint2 = otherFault = faultReasonStr    # 如果出现异常，则取原字符串
            else:
                # bits 1-2: Insulation fault
                insulationFaultDict = {'00': 'Normal', '01': 'Fault', '10': 'Untrusted'}
                insulationFault = processBit(faultReasonBin, insulationFaultDict, 1, 2)
                # bits 3-4: Over-temperature fault of output connector
                outConnOverTemprDict = {'00': 'Normal', '01': 'Fault', '10': 'Untrusted'}
                outConnOverTempr = processBit(faultReasonBin, outConnOverTemprDict, 3, 4)
                # bits 5-6: Over-temperature of BMS components, output connector
                bmsAndoutConnOverTemprDict = {'00': 'Normal', '01': 'Fault', '10': 'Untrusted'}
                bmsAndoutConnOverTempr = processBit(faultReasonBin, bmsAndoutConnOverTemprDict, 5, 6)
                # bits 7-8: Charging connector fault
                chargeConnFaultDict = {'00': 'Charging connector Normal', '01': 'Charging connector fault', '10': 'Untrusted'}
                chargeConnFault = processBit(faultReasonBin, chargeConnFaultDict, 7, 8)
                # bits 9-10: Battery pack over-temperature fault
                batteryOverTemprDict = {'00': 'Battery pack temperature Normal', '01': 'Battery pack temperature fault', '10': 'Untrusted'}
                batteryOverTempr = processBit(faultReasonBin, batteryOverTemprDict, 9, 10)
                # bits 11-12: High voltage relay fault
                highVolRelayFaultDict = {'00': 'Normal', '01': 'Fault', '10': 'Untrusted'}
                highVolRelayFault = processBit(faultReasonBin, highVolRelayFaultDict, 11, 12)
                # bits 13-14: Monitoring point 2 voltage detection fault
                monitorPoint2Dict = {'00': 'Normal', '01': 'Fault', '10': 'Untrusted'}
                monitorPoint2 = processBit(faultReasonBin, monitorPoint2Dict, 13, 14)
                # bits 15-16: Other faults
                otherFaultDict = {'00': 'Normal', '01': 'Fault', '10': 'Untrusted'}
                otherFault = processBit(faultReasonBin, otherFaultDict, 15, 16)

        # 计算BMS中止充电错误原因
        errorReasonStr = data[6:8]     # 取byte4
        if len(errorReasonStr) == 2:
            try:
                errorReasonBin = bin(int(errorReasonStr, 16))[2:].zfill(8)  # 转成2进制
            except:
                currentOver = voltageOver = errorReasonStr
            else:
                # Current too high
                currentOverDict = {'00': 'Current Normal', '01': 'Current exceeds demand value', '10': 'Untrusted'}
                currentOver = processBit(errorReasonBin, currentOverDict, 1, 2)
                # Voltage too high
                voltageOverDict = {'00': 'Normal', '01': 'Voltage anomaly', '10': 'Untrusted'}
                voltageOver = processBit(errorReasonBin, voltageOverDict, 3, 4)

        resultStr = "***BMS Stop Charging Message (BST)***\nI. BMS Stop Charging Reasons\nSOC: {}\nTotal voltage: {}\nSingle cell voltage: {}\nCharger: {}\n" \
                    "II. BMS Stop Charging Fault Reasons\nInsulation: {}\nOutput connector: {}\nBMS components, output connector: {}\nCharging connector: {}\nBattery pack temperature: " \
                    "{}\nHigh voltage relay: {}\nMonitoring point 2 voltage: {}\nOther: {}\nIII. BMS Stop Charging Error Reasons\nCurrent: {}\nVoltage: {}" \
                    "".format(socTarget, totalVoltageSettle, singleVoltageSettle, chargerEnd, insulationFault,
                              outConnOverTempr, bmsAndoutConnOverTempr, chargeConnFault, batteryOverTempr,
                              highVolRelayFault, monitorPoint2, otherFault, currentOver, voltageOver)

        return resultStr

    # CST报文：充电机中止充电报文
    def cstEndCharge(self, data):
        endChargeReason = 'null'    # 充电机中止充电原因
        reachCondition = 'null'     # 充电机中止充电原因-达到充电机设定的条件中止
        manualEnd = 'null'  # 充电机中止充电原因-人工中止
        faultEnd = 'null'   # 充电机中止充电原因-故障中止
        bmsEnd = 'null'     # 充电机中止充电原因-BMS主动中止

        endChargeFaultReason = 'null'   # 充电机中止充电故障原因
        overTempr = 'null'  # 充电机中止充电故障原因-充电机过温故障
        connFault = 'null'  # 充电机中止充电故障原因-充电机连接器故障
        innerOverTempr = 'null' # 充电机中止充电故障原因-充电机内部过温故障
        notDeliveryElec = 'null'    # 充电机中止充电故障原因-所需电量不能传送
        sharpStop = 'null'  # 充电机中止充电故障原因-充电机急停故障
        otherFault = 'null' # 充电机中止充电故障原因-Other故障

        endChargeErrorReason = 'null'   # 充电机中止充电错误原因
        currentNotMatch = 'null'    # 充电机中止充电错误原因-电流不匹配
        voltageError = 'null'   # 充电机中止充电错误原因-电压异常

        data = data.replace(' ', '')
        data = data.replace('\n', '')

        # 充电机中止充电原因
        endChargeReasonStr = data[0:2]  # 取byte1
        if len(endChargeReasonStr) == 2:
            try:
                endChargeReasonBin = bin(int(endChargeReasonStr, 16))[2:].zfill(8)  # 转2进制
            except:
                reachCondition = manualEnd = faultEnd = bmsEnd = endChargeReasonStr     # 取原值
            else:
                # bit1-2: 达到充电机设定的条件中止
                # bits 1-2: Stopped due to conditions set by the charger
                reachConditionDict = {'00': 'Normal', '01': 'Stopped due to charger set conditions', '10': 'Untrusted'}
                reachCondition = processBit(endChargeReasonBin, reachConditionDict, 1, 2)
                # bits 3-4: Manually stopped
                manualEndDict = {'00': 'Normal', '01': 'Manually stopped', '10': 'Untrusted'}
                manualEnd = processBit(endChargeReasonBin, manualEndDict, 3, 4)
                # bits 5-6: Stopped due to a fault
                faultEndDict = {'00': 'Normal', '01': 'Stopped due to a fault', '10': 'Untrusted'}
                faultEnd = processBit(endChargeReasonBin, faultEndDict, 5, 6)
                # bits 7-8: Actively stopped by BMS
                bmsEndDict = {'00': 'Normal', '01': 'Actively stopped by BMS (received BST frame)', '10': 'Untrusted'}
                bmsEnd = processBit(endChargeReasonBin, bmsEndDict, 7, 8)

        # 充电机中止充电故障原因
        endChargeFaultReasonStr = data[2:6]     # 取byte2-3
        if len(endChargeFaultReasonStr) == 4:
            endChargeFaultReasonChange = changePosition(endChargeFaultReasonStr)  # 高低位字节互换
            try:
                endChargeFaultReasonBin = bin(int(endChargeFaultReasonChange, 16))[2:].zfill(16)   # 转2进制
            except:
                overTempr = connFault = innerOverTempr = notDeliveryElec = sharpStop = otherFault = endChargeFaultReasonStr
            else:
                # bits 1-2: Charger over-temperature fault
                overTemprDict = {'00': 'Charger temperature Normal', '01': 'Charger over-temperature', '10': 'Untrusted'}
                overTempr = processBit(endChargeFaultReasonBin, overTemprDict, 1, 2)
                # bits 3-4: Charger connector fault
                connFaultDict = {'00': 'Charging connector Normal', '01': 'Charging connector fault', '10': 'Untrusted'}
                connFault = processBit(endChargeFaultReasonBin, connFaultDict, 3, 4)
                # bits 5-6: Internal over-temperature fault of the charger
                innerOverTemprDict = {'00': 'Charger internal temperature Normal', '01': 'Charger internal over-temperature', '10': 'Untrusted'}
                innerOverTempr = processBit(endChargeFaultReasonBin, innerOverTemprDict, 5, 6)
                # bits 7-8: Failure to transmit the required power
                notDeliveryElecDict = {'00': 'Power transmission Normal', '01': 'Failure to transmit power', '10': 'Untrusted'}
                notDeliveryElec = processBit(endChargeFaultReasonBin, notDeliveryElecDict, 7, 8)
                # bits 9-10: Charger emergency stop fault
                sharpStopDict = {'00': 'Normal', '01': 'Charger emergency stop', '10': 'Untrusted'}
                sharpStop = processBit(endChargeFaultReasonBin, sharpStopDict, 9, 10)
                # bits 11-12: Other faults
                otherFaultDict = {'00': 'Normal', '01': 'Fault', '10': 'Untrusted'}
                otherFault = processBit(endChargeFaultReasonBin, otherFaultDict, 11, 12)

# Reasons for Charger Stop Charging due to an error

        # 充电机中止充电错误原因
        endChargeErrorReasonStr = data[6:8]     # 取byte4
        if len(endChargeErrorReasonStr) == 2:
            try:
                endChargeErrorReasonBin = bin(int(endChargeErrorReasonStr, 16))[2:].zfill(8)    # 转2进制
            except:
                currentNotMatch = voltageError = endChargeErrorReasonStr
            else:
                # Current mismatch
                currentNotMatchDict = {'00': 'Current matches', '01': 'Current mismatch', '10': 'Untrusted'}
                currentNotMatch = processBit(endChargeErrorReasonBin, currentNotMatchDict, 1, 2)
                # Voltage anomaly
                voltageErrorDict = {'00': 'Normal', '01': 'Voltage anomaly', '10': 'Untrusted'}
                voltageError = processBit(endChargeErrorReasonBin, voltageErrorDict, 3, 4)
# This code snippet processes specific reasons for a charger stopping the 
        """
        resultStr = "***充电机中止充电报文（CST）***\n一、充电机中止充电原因\n达到充电机设定的条件中止：{}\n人工中止：{}\n故障中止：" \
                    "{}\nBMS主动中止：{}\n二、充电机中止充电故障原因\n充电机过温故障：{}\n充电机连接器故障：{}\n充电机内部过温故障：" \
                    "{}\n所需电量不能传送：{}\n充电机急停故障：{}\nOther故障：{}\n三、充电机中止充电错误原因\n电流不匹配：{}\n电压" \
                    "异常：{}".format(reachCondition, manualEnd, faultEnd, bmsEnd, overTempr, connFault, innerOverTempr,
                                   notDeliveryElec, sharpStop, otherFault, currentNotMatch, voltageError)
        """
        resultStr = "***Charger Stop Charging Message (CST)***\nI. Reasons for Charger Stop Charging\nStopped due to reaching the conditions set by the charger: {}\nManually stopped: {}\nStopped due to a fault: " \
                    "{}\nActively stopped by BMS: {}\nII. Fault Reasons for Charger Stop Charging\nCharger: {}\nCharger connector: {}\nInternal temperature of the charger: " \
                    "{}\nFailure to transmit the required power: {}\nCharger emergency stop fault: {}\nOther: {}\nIII. Error Reasons for Charger Stop Charging\nCurrent: {}\nVoltage: {}" \
                    "".format(reachCondition, manualEnd, faultEnd, bmsEnd, overTempr, connFault, innerOverTempr,
                                   notDeliveryElec, sharpStop, otherFault, currentNotMatch, voltageError)

        return resultStr

    # BMV多包(单体动力蓄电池电压报文)
    def bmvMulitiPackets(self, data):
        batteryVoltageGroups = []     # 蓄电池电压
        data = data.replace(' ', '')    # 去空格
        data = data.replace('\n', '')   # 去换行符

        #  去掉多包的序号, 便于后面计算各单体动力蓄电池电压
        data = delMulPackSerialNum(data)

        # 计算所有单体动力蓄电池电压
        i = 0
        batteryVoltageStr = data[4*i:4*i+4]      # byte1-2: 1单体动力蓄电池电压（原字符串）
        while batteryVoltageStr.upper() != 'FFFF' and batteryVoltageStr.upper() != 'FF':
            if len(batteryVoltageStr) == 4:
                batteryVoltageChange = changePosition(batteryVoltageStr)    # 高低位换位（换位后的字符串）
                try:
                    batteryVoltageBin = bin(int(batteryVoltageChange, 16))[2:].zfill(16)  # 转成2进制（2进制字符串）
                except:
                    batteryVoltage = batteryVoltageStr      # 如果出现异常（如出现非16进制字符）,则该电压和组号为提取的原字符串
                    batteryGroup = batteryVoltageStr
                    batteryVoltageGroups.append((batteryVoltage, batteryGroup))
                else:
                    batteryVoltage = processBitWithoutDict(batteryVoltageBin, 1, 12, 0.01, 0)   # 单体动力蓄电池电压
                    batteryGroup = processBitWithoutDict(batteryVoltageBin, 13, 16, 1, 0)       # 电池分组号
                    batteryVoltageGroups.append((batteryVoltage, batteryGroup))
            elif 0 < len(batteryVoltageStr) < 4:
                batteryVoltage = 'null'     # 如果提取的字符串不足2个字节，则输出该电池电压为null
                batteryGroup = 'null'       # 电池分组号
                batteryVoltageGroups.append((batteryVoltage, batteryGroup))
                break
            else:
                break
            i += 1
            batteryVoltageStr = data[4*i:4*i+4]     # 往后取两个字节

        # 组装返回的结果字符串
        batteryNums = len(batteryVoltageGroups)     # 单体动力蓄电池个数
        resultStr = '***Single Power Battery Cell Voltage Message (BMV)***\n'
        for i in range(batteryNums):
            batteryDescription = '# {} Single power battery cell--> \nBattery voltage: {}V\nBattery group number: {}\n'.format(
                i+1, batteryVoltageGroups[i][0], batteryVoltageGroups[i][1])
            resultStr = resultStr + batteryDescription

        return resultStr

    # BCP:动力蓄电池充电参数报文
    def bcpChargePamrameters(self, data):
        data = data.replace(' ', '')    # 去空格
        data = data.replace('\n', '')   # 去回车
        data = delMulPackSerialNum(data)    # 去多包序号

        # 单体动力蓄电池最高允许充电电压
        highVoltage  = processHex(data, 1, 2, 0.01, 0, 'V')
        # 最高允许充电电流
        highCurrent = processHex(data, 3, 4, 0.1, -400, 'A')
        # 动力蓄电池标称总能量
        totalEnerge = processHex(data, 5, 6, 0.1, 0, 'kW·h')
        # 最高允许充电总电压
        totalVoltage = processHex(data, 7, 8, 0.1, 0, 'V')
        # 最高允许温度
        highTemprature = processHex(data, 9, 9, 1, -50, '˚C')
        # 整车动力蓄电池荷电状态
        chargeState = processHex(data, 10, 11, 0.1, 0, '%')
        # 整车动力蓄电池当前电池电压
        currentVoltage = processHex(data, 12, 13, 0.1, 0, 'V')

        # 组装结果字符串
        resultStr = "***动力蓄电池充电参数报文(BCP)***\n单体动力蓄电池最高允许充电电压：{}\n最高允许充电电流：{}\n动力蓄电池标称总能量" \
                    "：{}\n最高允许充电总电压：{}\n最高允许温度：{}\n整车动力蓄电池荷电状态（SOC）：{}\n整车动力蓄电池当前电池电压：" \
                    "{}".format(highVoltage, highCurrent, totalEnerge, totalVoltage, highTemprature, chargeState,
                                currentVoltage)

        return resultStr

    # BRM多包（BMS和车辆辨识报文）
    def brmMuitiPackes(self, data):
        data = data.replace(' ', '')
        data = data.replace('\n', '')
        data = delMulPackSerialNum(data)    # 去多包序号
        # BMS通信协议版本号
        versionStr = data[0:6]      # byte1-3
        version = processVersion(versionStr)
        # 电池类型
        batteryTypeDict = {'01': 'Lead-acid battery', '02': 'Nickel-hydrogen battery', '03': 'Lithium iron phosphate battery', '04': 'Lithium manganese battery', '05': 'Lithium cobalt battery',
                       '06': 'Ternary material battery', '07': 'Lithium-ion polymer battery', '08': 'Lithium titanate battery', 'FF': 'Other types of batteries'}
        batteryTypeStr = data[6:8]  # byte4
        if len(batteryTypeStr) == 2:
            try:
                batteryType = batteryTypeDict[batteryTypeStr]
            except:
                batteryType = batteryTypeStr
        else:
            batteryType = 'null'
        # 整车动力蓄电池系统额定容量
        capacity = processHex(data, 5, 6, 0.1, 0, 'Ah')
        # 整车动力蓄电池系统额定总电压
        totalVoltage = processHex(data, 7, 8, 0.1, 0, 'V')

        # 后续为可选项，待需求明确后完善
        # 电池生产厂商名称
        factoryName = data[16:24]  # byte9-12
        # 电池组序号
        batteryGroupSerialNum = data[24:32]  # byte13-16
        # 电池组生产日期-年
        batteryGroupsProductionDate_year = data[32:34]   # byte17
        # 电池组生产日期-月
        batteryGroupsProductionDate_month = data[34:36]      # byte18
        # 电池组生产日期-日
        batteryGroupsProductionDate_day = data[36:38]    # byte19
        # 电池组充电次数
        batteryGroupsChargeTimes = data[38:44]   # byte20-22
        # 电池组产权标识
        batteryGroupsPropertyRightDict = {'0': 'Leased', '1': 'Owned by the vehicle'}
        batteryGroupsPropertyRightStr = data[44:46]     # byte23
        if len(batteryGroupsPropertyRightStr) == 2:
            try:
                batteryGroupsPropertyRight = batteryGroupsPropertyRightDict[int(batteryGroupsPropertyRightStr, 16)]
            except:
                batteryGroupsPropertyRight = batteryGroupsPropertyRightStr
        else:
            batteryGroupsPropertyRight = 'null'
        # 车辆识别码
        vehicleIdentify = data[48:82]    # byte25-41
        #  BMS版本信息
        bmsVersion = data[82:98]     # byte42-49

        # 组装输出字符串
        resultStr = "***BMS and Vehicle Identification Message (BRM)***\nBMS communication protocol version number: {}\nBattery type: {}\nRated capacity of the entire vehicle power battery system: {}\n" \
                "Rated total voltage of the entire vehicle power battery system: {}\nBattery manufacturer name: {}\nBattery pack serial number: {}\nBattery pack production date: {}/{}/{}\n" \
                "Number of times the battery pack has been charged: {}\nProperty rights identification of the battery pack: {}\nVehicle identification code: {}\nBMS version information: {}".format(version, batteryType,
                capacity, totalVoltage, factoryName, batteryGroupSerialNum, batteryGroupsProductionDate_year,
                batteryGroupsProductionDate_month, batteryGroupsProductionDate_day, batteryGroupsChargeTimes,
                batteryGroupsPropertyRight, vehicleIdentify, bmsVersion)
        return resultStr

    # BMT多包（动力蓄电池温度报文）
    def bmtMultiPackes(self, data):
        batteryTemprGroups = []  # 蓄电池温度
        data = data.replace(' ', '')  # 去空格
        data = data.replace('\n', '')  # 去换行符

        #  去掉多包的序号, 便于后面计算各动力蓄电池温度
        data = delMulPackSerialNum(data)

        # 计算所有动力蓄电池温度
        i = 1   # 表示取的是第几字节，1则表示取第1字节
        batteryTemprStr = data[(i - 1) * 2: i * 2]  # byte1: # 1动力蓄电池温度（原字符串）
        while batteryTemprStr.upper() != 'FF' and batteryTemprStr != '':      # FF代表是填充数，代表后面没有电池了
            if len(batteryTemprStr) == 2:
                try:
                    batteryTempr = str(int(batteryTemprStr, 16) - 50) + '˚C'
                    batteryTemprGroups.append(batteryTempr)
                except:
                    batteryTempr = batteryTemprStr      # 有非16进制的字符
                    batteryTemprGroups.append(batteryTempr)
            elif 0 < len(batteryTemprStr) < 2:          # 有该号电池但数据不全
                batteryTempr = 'null'
                batteryTemprGroups.append(batteryTempr)
                break
            i += 1  # 取下一个字节
            batteryTemprStr = data[(i - 1) * 2: i * 2]

        # 组装返回的结果字符串
        batteryNums = len(batteryTemprGroups)  # 动力蓄电池个数
        resultStr = '***Power Battery Temperature Message (BMT)***\n'
        for i in range(batteryNums):
            batteryDescription = 'Power battery temperature {}：{}\n'.format(i + 1, batteryTemprGroups[i])
            resultStr = resultStr + batteryDescription

        return resultStr

    # BMS统计数据报文(BSD)
    def bsd(self, data):
        data = data.replace(' ', '')
        data = data.replace('\n', '')

        # 中止荷电状态SOC
        socStr = data[0:2]     # tyte1:原字符串
        if len(socStr) == 2:
            try:
                soc = str(int(socStr, 16)) + '%'    # soc值：分辨率1%， 偏移量0%
            except:
                soc = socStr    # 如果出现异常，soc为原字符串
        else:
            soc = 'null'    # 如果长度不为2，则soc为null

        # 动力蓄电池单体最低电压
        lowVoltage = processHex(data, 2, 3, 0.01, 0, 'V')

        # 动力蓄电池单体最高电压
        highVoltage = processHex(data, 4, 5, 0.01, 0, 'V')

        # 动力蓄电池最低温度
        lowTempratureStr = data[10:12]      # byte6: 原字符串
        if len(lowTempratureStr) == 2:
            try:
                lowTemprature = str(int(lowTempratureStr, 16) - 50) + '˚C'  # 计算最低温度
            except:
                lowTemprature = lowTempratureStr    # 如果异常，则等于原字符串
        else:
            lowTemprature = 'null'

        # 动力蓄电池最高温度
        highTempratureStr = data[12:14]  # byte7: 原字符串
        if len(highTempratureStr) == 2:
            try:
                highTemprature = str(int(highTempratureStr, 16) - 50) + '˚C'  # 计算最低温度
            except:
                highTemprature = highTempratureStr  # 如果异常，则等于原字符串
        else:
            highTemprature = 'null'

        # 结果返回
        resultStr = "***BMS Statistical Data Message (BSD)***\nState of Charge (SOC) upon termination: {}\nLowest voltage of individual power battery cell: {}\nHighest voltage of individual power battery cell: {}\n" \
                    "Lowest temperature of power battery: {}\nHighest temperature of power battery: {}".format(soc, lowVoltage, highVoltage, lowTemprature, highTemprature)
        return resultStr

    # 充电机统计数据报文（CSD）
    def csd(self, data):
        data = data.replace(' ', '')
        data = data.replace('\n', '')
        # 累计充电时间
        time = processHex(data, 1, 2, 1, 0, 'min')
        # 输出能量
        power = processHex(data, 3, 4, 0.1, 0, 'kW·h')
        # 充电机编号(待标准弄清楚后完善，暂时取源码)
        numStr = data[8: 16]    # byte5-8:原字符串
        if len(numStr) == 8:
            num = numStr
        else:
            num = 'null'    # 如果长度错误则取null
        # 返回结果
        resultStr = "***Charger Statistical Data Message (CSD)***\nAccumulated charging time: {}\nOutput energy: {}\nCharger number: {}".format(time, power, num)
        return resultStr

    # BMS错误报文（BEM）
    def bem(self, data):
        data = data.replace(' ', '')
        data = data.replace('\n', '')

        # byte1:
        byte1Str = data[0: 2]   # byte1原字符串
        # 把byte1转为2进制字符串
        if len(byte1Str) == 2:
            try:
                byte1Bin = bin(int(byte1Str, 16))[2:].zfill(8)
                # 接收SPN2560=0x00的充电机辨识报文Timeout
                spn00_chargePileTimeOutStrDict = {'00': 'Normal', '01': 'Timeout', '10': 'Untrusted'}
                spn00_chargePileTimeOut = processBit(byte1Bin, spn00_chargePileTimeOutStrDict, 1, 2)
                # 接收SPN2560=0xAA的充电机辨识报文Timeout
                spnAA_chargePileTimeOutStrDict = {'00': 'Normal', '01': 'Timeout', '10': 'Untrusted'}
                spnAA_chargePileTimeOut = processBit(byte1Bin, spnAA_chargePileTimeOutStrDict, 3, 4)
            except:
                spn00_chargePileTimeOut = byte1Str
                spnAA_chargePileTimeOut = byte1Str
        else:
            spn00_chargePileTimeOut = 'null'    # 接收SPN2560=0x00的充电机辨识报文Timeout
            spnAA_chargePileTimeOut = 'null'    # 接收SPN2560=0xAA的充电机辨识报文Timeout

        # byte2
        byte2Str = data[2: 4]   # byte2原字符串
        # 把byte2转为2进制字符串
        if len(byte2Str) == 2:
            try:
                byte2Bin = bin(int(byte2Str, 16))[2:].zfill(8)
                # 接收充电机的时间同步和充电机最大输出能力报文Timeout
                recv_pile_timeSynAndMaxCapDict = {'00': 'Normal', '01': 'Timeout', '10': 'Untrusted'}
                recv_pile_timeSynAndMaxCap = processBit(byte2Bin, recv_pile_timeSynAndMaxCapDict, 1, 2)
                # 接收充电机完成充电准备报文Timeout
                recv_pile_readyOkDict = {'00': 'Normal', '01': 'Timeout', '10': 'Untrusted'}
                recv_pile_readyOk = processBit(byte2Bin, recv_pile_readyOkDict, 3, 4)
            except:
                recv_pile_timeSynAndMaxCap = byte2Str
                recv_pile_readyOk = byte2Str
        else:
            recv_pile_timeSynAndMaxCap = 'null'     # 接收充电机的时间同步和充电机最大输出能力报文Timeout
            recv_pile_readyOk = 'null'  # 接收充电机完成充电准备报文Timeout

        # byte3
        byte3Str = data[4: 6]   # byte3原字符串
        # 把byte3转为2进制字符串
        if len(byte3Str) == 2:
            try:
                byte3Bin = bin(int(byte3Str, 16))[2:].zfill(8)
                # 接收充电机充电状态报文Timeout
                recv_pile_chargeStateTimeOut_Dict = {'00': 'Normal', '01': 'Timeout', '10': 'Untrusted'}
                recv_pile_chargeStateTimeOut = processBit(byte3Bin, recv_pile_chargeStateTimeOut_Dict, 1, 2)
                # 接收充电机中止充电报文Timeout
                recv_pile_FinishChargeTimeOut_Dict = {'00': 'Normal', '01': 'Timeout', '10': 'Untrusted'}
                recv_pile_FinishChargeTimeOut = processBit(byte3Bin, recv_pile_FinishChargeTimeOut_Dict, 3, 4)
            except:
                recv_pile_chargeStateTimeOut = byte3Str
                recv_pile_FinishChargeTimeOut = byte3Str
        else:
            recv_pile_chargeStateTimeOut = 'null'      # 接收充电机充电状态报文Timeout
            recv_pile_FinishChargeTimeOut = 'null'      # 接收充电机中止充电报文Timeout

        # byte4
        byte4Str = data[6: 8]   # byte4原字符串
        # 把byte4转成二进制字符串
        if len(byte4Str) == 2:
            try:
                byte4Bin = bin(int(byte4Str, 16))[2:].zfill(8)
                # 接收充电机充电统计报文Timeout
                recv_pill_chargeStatistics_TimeOut_Dict = {'00': 'Normal', '01': 'Timeout', '10': 'Untrusted'}
                recv_pill_chargeStatistics_TimeOut = processBit(byte4Bin, recv_pill_chargeStatistics_TimeOut_Dict, 1, 2)
                # Other
                other = byte4Bin[:-2]
            except:
                recv_pill_chargeStatistics_TimeOut = byte4Str
                other = byte4Str
        else:
            recv_pill_chargeStatistics_TimeOut = 'null'     # 接收充电机充电统计报文Timeout
            other = 'null'  # Other

        # 结果返回
        resultStr = "***BMS Error Message (BEM)***\nTimeout for receiving the charger identification message with SPN2560：{}\nTimeout for receiving the charger identification message with SPN2560=0xAA:{}\n" \
                    "Timeout of receiving the time synchronization and maximum output capacity message of the charger:{}\nTimeout of receiving the message of charger completion of charging preparation:{}\n" \
                    "Timeout for receiving charger charging status message:{}\nTimeout for receiving charger abort charging message:{}\nTimeout for receiving charger charging statistics message:{}\nOthers:{}".format(
            spn00_chargePileTimeOut, spnAA_chargePileTimeOut, recv_pile_timeSynAndMaxCap, recv_pile_readyOk,
            recv_pile_chargeStateTimeOut, recv_pile_FinishChargeTimeOut, recv_pill_chargeStatistics_TimeOut, other)
        return resultStr

    # Charger error message（CEM）
    def cem(self, data):
        data = data.replace(' ', '')
        data = data.replace('\n', '')
        # byte1:
        byte1Str = data[0:2]  # byte1原字符串
        # 把byte1转为2进制字符串
        if len(byte1Str) == 2:
            try:
                byte1Bin = bin(int(byte1Str, 16))[2:].zfill(8)
                # Receive BMS and vehicle identification messages Timeout
                recv_vehicle_bmsAndIdenty_timeOutDict = {'00': 'Normal', '01': 'Timeout', '10': 'Untrusted'}
                recv_vehicle_bmsAndIdenty_timeOut = processBit(byte1Bin, recv_vehicle_bmsAndIdenty_timeOutDict, 1, 2)
            except:
                recv_vehicle_bmsAndIdenty_timeOut = byte1Str
        else:
            recv_vehicle_bmsAndIdenty_timeOut = 'null'  # Receive BMS and vehicle identification messages Timeout


        # byte2
        byte2Str = data[2:4]  # byte2原字符串
        # 把byte2转为2进制字符串
        if len(byte2Str) == 2:
            try:
                byte2Bin = bin(int(byte2Str, 16))[2:].zfill(8)
                # 
# Receive battery charging parameter message Timeout
                recv_vehicle_chargePam_timeout_Dict = {'00': 'Normal', '01': 'Timeout', '10': 'Untrusted'}
                recv_vehicle_chargePam_timeout = processBit(byte2Bin, recv_vehicle_chargePam_timeout_Dict, 1, 2)
                # 接收BMS完成充电准备报文Timeout
                recv_vehicle_readyOkDict = {'00': 'Normal', '01': 'Timeout', '10': 'Untrusted'}
                recv_vehicle_readyOk = processBit(byte2Bin, recv_vehicle_readyOkDict, 3, 4)
            except:
                recv_vehicle_chargePam_timeout = byte2Str
                recv_vehicle_readyOk = byte2Str
        else:
            recv_vehicle_chargePam_timeout = 'null'  # 
# Receive battery charging parameter message Timeout
            recv_vehicle_readyOk = 'null'  # 接收BMS完成充电准备报文Timeout

        # byte3
        byte3Str = data[4:6]  # byte3原字符串
        # 把byte3转为2进制字符串
        if len(byte3Str) == 2:
            try:
                byte3Bin = bin(int(byte3Str, 16))[2:].zfill(8)
                # 接收电池充电总状态报文Timeout
                recv_vehicle_chargeStateTimeOut_Dict = {'00': 'Normal', '01': 'Timeout', '10': 'Untrusted'}
                recv_vehicle_chargeStateTimeOut = processBit(byte3Bin, recv_vehicle_chargeStateTimeOut_Dict, 1, 2)
                # 接收电池充电要求报文Timeout
                recv_vehicle_chargeDemandTimeOut_Dict = {'00': 'Normal', '01': 'Timeout', '10': 'Untrusted'}
                recv_vehicle_chargeDemandTimeOut = processBit(byte3Bin, recv_vehicle_chargeDemandTimeOut_Dict, 3, 4)
                # 接收BMS中止充电报文Timeout
                recv_vehicle_FinishChargeTimeOut_Dict = {'00': 'Normal', '01': 'Timeout', '10': 'Untrusted'}
                recv_vehicle_FinishChargeTimeOut = processBit(byte3Bin, recv_vehicle_FinishChargeTimeOut_Dict, 5, 6)
            except:
                recv_vehicle_chargeStateTimeOut = byte3Str
                recv_vehicle_chargeDemandTimeOut = byte3Str
                recv_vehicle_FinishChargeTimeOut = byte3Str
        else:
            recv_vehicle_chargeStateTimeOut = 'null'  # 接收电池充电总状态报文Timeout
            recv_vehicle_chargeDemandTimeOut = 'null'  # 接收电池充电要求报文Timeout
            recv_vehicle_FinishChargeTimeOut = 'null'   # 接收BMS中止充电报文Timeout


        # byte4
        byte4Str = data[6:8]  # byte4原字符串
        # 把byte4转成二进制字符串
        if len(byte4Str) == 2:
            try:
                byte4Bin = bin(int(byte4Str, 16))[2:].zfill(8)
                # 接收BMS充电统计报文Timeout
                recv_vehicle_chargeStatistics_TimeOut_Dict = {'00': 'Normal', '01': 'Timeout', '10': 'Untrusted'}
                recv_vehicle_chargeStatistics_TimeOut = processBit(byte4Bin, recv_vehicle_chargeStatistics_TimeOut_Dict,
                                                                   1, 2)
                # Other
                other = byte4Bin[:-2]
            except:
                recv_vehicle_chargeStatistics_TimeOut = byte4Str    # 如果异常，则等于原字符串
                other = byte4Str
        else:
            recv_vehicle_chargeStatistics_TimeOut = 'null'  # 接收BMS充电统计报文Timeout
            other = 'null'  # Other

        # 结果返回
        resultStr = "***Charger error message（CEM）***\nReceive BMS and vehicle identification messages Timeout：{}\nReceive battery charging parameter message Timeout：{}\n" \
                    "Receive BMS complete charging preparation message Timeout：{}\nReceive battery charging status message Timeout：{}\nReceive battery charging request messageTimeout：{}\n" \
                    "Receive BMS charging termination message Timeout：{}\nReceive BMS charging statistics messages Timeout：{}\nOther：{}".format(
            recv_vehicle_bmsAndIdenty_timeOut, recv_vehicle_chargePam_timeout, recv_vehicle_readyOk,
            recv_vehicle_chargeStateTimeOut, recv_vehicle_chargeDemandTimeOut, recv_vehicle_FinishChargeTimeOut,
            recv_vehicle_chargeStatistics_TimeOut, other)
        return resultStr


