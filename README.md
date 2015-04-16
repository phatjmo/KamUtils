# KamUtils

Scripts for facilitating and automating Kamailio management.

## LCR Import Utility

   **Script Name:** lcrstuffer.py
   **Command:** ./lcrstuffer.py <NUMBERFILE> <ACTION>
   **Requires:** Python 2.6+
   **Modules:** sys, MySQLdb (MySQL-python via pip), ast, json, sys.argv, os.path, os.stat
   **Dependencies:** python-dev, libmysqlclient-dev (Debian)
   **Additional Files:** cfgDict.json - see docs below

**Step 1:** Install MySQL and python dev dependencies:

```
sudo apt-get install python-dev libmysqlclient-dev 
```

**Step 2:** Install MySQL-python module:

```
sudo pip install MySQL-python
```

**Step 3:** Prepare cfgDict.json configuration file:

The file “cfgDict.json” belongs in the same folder as the script. The file is a json formatted plain text file with the following parameters, with description:

```javascript
{
"host": "lva1bkam00",		//MySQL Host (string)
"db": "kamailio",		    //Database name (string)
"user": "kamailio"		  //Database user (with R/W access) (string)
"passwd": "kmosr521",	  //Database password (string)
"gwList": [99, 100],		//List of gateway IDs from lcr_gw for distribution (array)
}
```


If you run the script without this file it will prompt you to manually enter these values and will create the file while using the entered parameters for the current job.

**Step 4:** Prepare the Number File:

The number file is a plain text file with one phone number match per line, without quotes or other characters. Number must be at least 1 character but is a Request-URI User match and is considered a “prefix match” so if less than 10 digits are used for a standard North American telephone number, then any number matching the specified digits will be routed according to the imported rule. So, if you accidentally import a line with only “888”, then all 888 toll free numbers will be routed to the specified gateways. This would be less than desirable for most applications.



Action Descriptions:

**Import -** Create new *lcr_rule entries* for each number listed and then create a matching *lcr_rule_target* entry for each number to each gateway listed in *cfgDict.gwList*. Default import behavior leaves *lcr_rule.enabled* = **True**.

**Remove -** Delete all *lcr_rule_target* entries and all *lcr_rule* entries that match the numbers in the provided list file.

**Enable -** Set *lcr_rule.enabled* = **True** for all numbers in the provided list file.

**Disable -** Set *lcr_rule.enabled* = **False** for all numbers in the provided list file.




**Note:** 

None of the above actions will impact the running Kamailio instance until *lcr.reload* has been run via kamcmd:

```
sudo kamcmd lcr.reload
```
