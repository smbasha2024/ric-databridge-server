from typing import Dict, Any
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema
from app.services.email_providers.base import BaseEmailProvider
from app.schema.email_dto import Email as EmailDTO
from app.configs.settings import settings

import json

from app.infra.email.email_render import EmailTemplateRender

class GmailProvider(BaseEmailProvider):
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.mail.mail_username,
            MAIL_PASSWORD=settings.mail.mail_password,
            MAIL_FROM=settings.mail.mail_from,
            MAIL_PORT=settings.mail.mail_port,
            MAIL_SERVER=settings.mail.mail_server,
            MAIL_STARTTLS=settings.mail.mail_starttls,
            MAIL_SSL_TLS=settings.mail.mail_ssl_tls,
            USE_CREDENTIALS=settings.mail.use_credentials,
            VALIDATE_CERTS=settings.mail.validate_certs
        )

    async def send_email_non_template(self, email: EmailDTO, extras: str = "") -> Dict[str, Any]:
        try:
            print(f"📧 [GmailProvider] Preparing to send email...", flush=True)
            print(f"📥 ################## send_email without template ##################", flush=True)
            email_body = f"""
            {email.message}<br/><br/>
            --------<br/>
            Customer Name: {email.name}<br/>
            Customer Email: {email.customer_email}<br/>
            {extras}<br/>
            --------
            """

            message = MessageSchema(
                subject=email.subject,
                recipients=email.email,  # List of recipients
                body=email_body,
                subtype="html"
            )

            fm = FastMail(self.conf)
            await fm.send_message(message)
            
            print(f"✅ [GmailProvider] Email sent successfully", flush=True)
            print(f"Email Message:", message)
            return {"message": "Email sent successfully"}

        except Exception as e:
            print(f"❌ [GmailProvider] FAILED to send email: {str(e)}", flush=True)
            raise e
    
    async def send_email(self, email: EmailDTO, extras: str = "") -> Dict[str, Any]:
        print(f"📥 ################## send_email with template ################## {extras}", flush=True)
        print(f"📥 ################## send_email extras ##################", extras)
        email_templ_render = EmailTemplateRender()

        email_vars = {
                        "subscriber_name": email.name, 
                        "sender_name": "RICA", 
                        "company_name": email.subject, 
                        "email_id": email.customer_email #, 
                        #"mobile_number": email.message
                    }
        
        if email.purpose is not None and email.purpose != "" and email.purpose != False:
            email_vars["purpose"] = email.purpose
        if email.category is not None and email.category != "" and email.category != False:
            email_vars["category"] = email.category
        if email.prod_serv_name is not None and email.prod_serv_name != "" and email.prod_serv_name != False:
            email_vars["prod_serv_name"] = email.prod_serv_name

        
        if extras is not None and extras != "" and extras != False :
            extra_params = extras
            for key, value in extra_params.items():
                email_vars[key] = value

        print(f"############### Email Vars : ############", email_vars)
        template_name = email_templ_render.get_template_by_purpose(email.purpose)
        #print(f"############### Email Template Name: ############", template_name)
        email_subject, email_content = email_templ_render.render_email_template(template_name, email_vars)
        #print(f"############### Email Content: ############", template_name, email_subject, email_content)

        try:
            print(f"📧 [GmailProvider] Preparing to send email...", flush=True)
            from datetime import datetime
            timestamp = datetime.now().strftime("%d-%b-%Y %H:%M:%S")

            message = MessageSchema(
                subject=f"{email_subject} | {timestamp}",
                recipients=email.email,  # List of recipients
                body=email_content,
                reply_to=[email.customer_email] if email.customer_email else None,
                subtype="html"
            )

            fm = FastMail(self.conf)
            await fm.send_message(message)
            
            print(f"✅ [GmailProvider] Email sent successfully", flush=True)
            #print(f"Email Message:", message)
            return {"message": "Email sent successfully"}

        except Exception as e:
            print(f"❌ [GmailProvider] FAILED to send email: {str(e)}", flush=True)
            raise e
