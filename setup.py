import os
from setuptools import setup

# With help from https://stackoverflow.com/questions/26900328/install-dependencies-from-setup-py

# Find the root folder
root_folder = os.path.dirname(os.path.realpath(__file__))

# Find the requirements.txt
requirementPath = root_folder + '/requirements.txt'
install_requires = [] 

# Add all requirements to be installed https://stackoverflow.com/questions/3277503/how-to-read-a-file-line-by-line-into-a-list
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()

with open("README.md", 'r') as f:
    long_description = f.read()


# Run the setup
setup(name="avn", 
      version='0.1', 
      description='Pythonic application for automatically launching virtual networks using VirtualBox.',
      install_requires=install_requires,
      author = "Daniel Crouch & Kenan Jasim")