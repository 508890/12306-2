#send SMS ， 100 per month
from qcloudsms_py import QcloudSms
from qcloudsms_py.httpclient import HTTPError

appid = 1400066168
appkey = "c0c77fe0d613c96d76505f59ccc980bb"
phone_numbers = ["14781275573","18783976036"]
template_id = 205694
sms_sign = "hsxsix"
qcloudsms = QcloudSms(appid, appkey)  

def sendTemplateSMS(notice="你的短信已发送。"):
    ssender = qcloudsms.SmsSingleSender()
    params = [notice]  
    try:
        result = ssender.send_with_param(86, phone_numbers[0],
            template_id, params, sign=sms_sign, extend="", ext="")
    except HTTPError as e:
        print(e)
    except Exception as e:
        print(e)
    print(result)

def sendGroupTemplateSMS(notice="你的短信已发送。"):
    msender = qcloudsms.SmsMultiSender()
    params = [notice]
    try:
        result = msender.send_with_param(86, phone_numbers,
            template_id, params, sign=sms_sign, extend="", ext="")   
    except HTTPError as e:
        print(e)
    except Exception as e:
        print(e)

    print(result)
    pass

if __name__ == "__main__":
    pass
    # sendTemplateSMS("你好！")
    sendGroupTemplateSMS("这是一条消息！")