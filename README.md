
OpenStack Cinder Diagnostic tools 

This repository contains a collection of diagnostic tools geared toward helping OpenStack Cinder users configure and 
monitor their environment.

"cinderdiags" (diags/cli/diagsapp) is a CLI tool that validates a users cinder.conf configuration file.

Under diags/docs you will find a users manual for the CLI command. There is also a technical doc that details how to 
maintain and modify the CLI code base.

Under diags/monasca_agent is a plug-in that feeds Cinder related log errors into OpenStack Monasca. This is a work
in progress - see "monasca_agent_check_overview" doc to get background information about how this is supposed to work.


