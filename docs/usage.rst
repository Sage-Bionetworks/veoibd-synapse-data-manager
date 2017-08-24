=====
Usage
=====


-----------------------------
Setup Your Site's Information
-----------------------------
1. Coming Soon.


-----------------
Register New Data
-----------------
#. This demo assumes that you have already gone through the demo: `Setup Your Site's Information <#setup-your-site-s-information>`_

#. Generate a new "push" configuration file. Here we will give it the "demo" identifier. The command and its output are shown below.

    .. code-block:: bash

        $ veoibd_synapse configs --generate-configs --kind push --prefix demo
        [I 170824 12:15:18 main:41] Setup logging configurations.
        [D 170824 12:15:18 main:118] kind = ('push',)
        [I 170824 12:15:18 config:32] Generated new config: configs/demo.push.yaml

    This gives you a blank config file to describe the data that you want to add to the system including:

    #. the project name
    #. annotation keywords to help filter the files on Synapse
    #. the location of the files you want to add to Synapse
    #. the location in Synapse where you want the files listed.

#. Amend the values in ``configs/demo.push.yaml`` to reflect the data files that you will add.

#. I have already created and configured a user named "GUSDUNN" (see how to do this `here <#setup-your-site-s-information>`_).

#. An example command to register the data described in ``demo.push.yaml`` with Synapse is shown below.

    .. code-block:: bash

        $ veoibd_synapse push -user GUSDUNN --push-config configs/demo.push.yaml

----------------------------
Sync Local Metadata Database
----------------------------
1. Coming Soon.

-----------------------
Query Metadata Database
-----------------------
1. `Sync Local Metadata Database <#sync-local-metadata-database>`_


-------------------
Download Data Files
-------------------
1. Coming Soon.
