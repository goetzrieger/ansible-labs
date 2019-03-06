#/bin/bash
# Script can be used to remove the tediousness of setting up the same stuff over and over again 
# in Tower while testing/developing the lab

# Just add the admin password, the SSH key for user ansible as prepared by the awk (thanks to some Github issue comment)
# command below and some water. Let come to the boil.

PASSWORD='redhat'

## Install & configure tower-cli on control

yum install python2-ansible-tower-cli -y
tower-cli config host tower2.example.com
tower-cli config username admin
tower-cli config password $PASSWORD

tower-cli inventory list

## Create inventories

tower-cli inventory create --name "Example Inventory" --organization "Default"
tower-cli host create --name "host1.example.com" --inventory "Example Inventory"
tower-cli host create --name "host2.example.com" --inventory "Example Inventory"

tower-cli inventory create --name "Imported Inventory" --organization "Default"
ssh tower1.example.com 'echo -e "host1.example.com\nhost2.example.com" > /root/example_inventory'
ssh tower1.example.com 'awx-manage inventory_import --source=/root/example_inventory --inventory-name="Imported Inventory"'

## Create machine and scm creds
# Use to create SSH key in correct format:
# awk '{printf "      %s\n", $0}' < /home/ansible/.ssh/id_rsa

machine_cred_inputs="username: ansible
ssh_key_data: |
      -----BEGIN RSA PRIVATE KEY-----
      
      -----END RSA PRIVATE KEY-----"

tower-cli credential create --name="Example Credentials" --credential-type=Machine --organization Default --inputs="$machine_cred_inputs" 
tower-cli credential create --credential-type="Source Control" --name="Gitea Credentials" --inputs="{username: git, password: $PASSWORD}" --organization="Default"

## Create project
tower-cli project create --name="Apache" --scm-type=git --scm-url="http://control.example.com/gitea/git/Apache.git" --scm-credential="Gitea Credentials" --organization "Default" --scm-clean=yes --scm-delete-on-update=yes --scm-update-on-launch=yes --wait

##Create template
tower-cli job_template create --name="Install Apache" --inventory="Example Inventory" --credential="Example Credentials" --project=Apache --playbook=apache_install.yml --become-enabled="yes"
