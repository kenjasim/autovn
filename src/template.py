import os 
import shutil
import json
import yaml
from pathlib import Path
import requests
from restapi.client import RESTClient
from urllib.parse import urlparse

class Template(object):
    template_dir = Path.home() / ".avn" / "templates"

    def copy_template(self, path): 
        """Copy yaml topology config file to AVN config dir"""
        # Verify template 
        if not (os.path.isfile(path) and (path.endswith("yaml") or path.endswith("yml"))):
            raise Exception("Invalid template path") 
        # Copy template to avn config dir
        shutil.copy(path, str(self.template_dir))

    def send_template(self, path):
        """Forward template to api server via client"""
        # Verify template 
        if not (os.path.isfile(path) and (path.endswith("yaml") or path.endswith("yml"))):
            raise Exception("Invalid template path") 
        # Parse to json and forward to avn client
        with open(path, 'r') as yaml_file:
            json = yaml.load(yaml_file, Loader=yaml.FullLoader) 
            filename = os.path.basename(path)
            RESTClient.post_template(json, filename)
            
    def pull_template(self, url, remote):
        """Pull template from raw.githubusercontent"""
        r = requests.get(url)
        json = yaml.load(r.text, Loader=yaml.FullLoader) 
        filename = os.path.basename(urlparse(url).path)
        if remote:
            RESTClient.post_template(json, filename)
        else: 
            dst_path = self.template_dir / filename
            with open(str(dst_path), 'w') as f:
                yaml.dump(json, f)
