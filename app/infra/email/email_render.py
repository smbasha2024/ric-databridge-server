from typing import Dict
#import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

import json

from app.schema.email_dto import Email as EmailDTO

class EmailTemplateRender: 
    def __init__(self):
        TEMPLATE_DIR = Path(__file__).parent / "templates"

        #TEMPLATE_DIR = "/html"
        print(f"Template Dir: ", TEMPLATE_DIR)
        
        self.templ_env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            autoescape=select_autoescape(["html", "xml"])
        )
        
    # Load JSON file once (recommended)
    def load_templates(self):
        json_file = Path("app/infra/email/templates/email_template_configs.json")
        print(f"Template JSON file: ", json_file)
        with open(json_file, "r", encoding="utf-8") as f:
            return json.load(f)

    # Lookup function
    def get_template_details(self, templates, template_id=None,template_name=None):
        for template in templates:

            # handle typo safely
            tid = template.get("template_id") or template.get("tempplate_id")

            if template_id is not None and tid == template_id:
                return template["template_file"], template["email_subject"]

            if template_name is not None and template.get("template_name") == template_name:
                return template["template_file"], template["email_subject"]

        raise ValueError("Template not found")


    def render_email_template(self, template_name: str, variables: dict) -> str:
        templates = self.load_templates()

        template_file, email_subject = self.get_template_details(
            templates,
            template_name=template_name
        )
        template = self.templ_env.get_template(f"/{template_file}")
        email_content = template.render(**variables)
        return email_subject, email_content
    
    def get_template_by_purpose(self, purpose: str):
        """
        Returns template name based on purpose.
        """
        purpose = purpose.strip().lower()
        #print(f"################ Purpose Value: ###############", purpose)
        match purpose: 
            case "a":
                return ""
            
            case _:
                raise ValueError(f"Unsupported email purpose: {purpose}")
            
    