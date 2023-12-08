# Getting Started

## Create a kb-sdk dynamic service

Follow instructions in https://kbase.github.io/kb_sdk_docs/tutorial/2_install.html

or the slightly simpler and less intrusive:



docker run kbase/kb-sdk genscript > ./kb-sdk


chmod +x ./kb-sdk

export PATH=$PATH:${PWD}

create a project directory and cd into it

kb-sdk init --verbose --language python --user eapearson eapearsonFirst

cd eapearsonFirst

make


That is about it.

Then, one change to make it a dynamic service, adding this to kbase.yml:

service-config:
  dynamic-service: true


## Apply the DS Widget patches

now we are ready to run the ds widget tool to the repo to add the widget support.