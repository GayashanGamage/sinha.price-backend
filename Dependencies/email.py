import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

import os
from dotenv import load_dotenv

load_dotenv()


configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.getenv('bravo')
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))


def passwordReset(to_name, to_email, params):
    sender = {"name":"gayashan gamage","email":"gayashan.randimagamage@gmail.com"}
    to = [{"name": to_name,"email": to_email}]
    subject = 'SIGIRI Price - secreate code for change password'
    headers = {"Some-Custom-Name":"unique-id-1234"}
    param = {'code' : params}
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, headers=headers, sender=sender, subject=subject, template_id=8, params=param)
    output = api_instance.send_transac_email(send_smtp_email)
    return output