# Legacy vulnerable packages
In this section, we will analyze the 52 legacy vulnerable packages with our tool. The 52 vulnerable packages are listed in [lists/fse\_2021\_52.list](../../lists/fse_2021_52.list) 

## Package downloading
To download the listed packages, we prepared a script and embedded the script to the main **ObjLupAnsys.py** tool. You can download the list of packages by:

```shell
$ python3 ObjLupAnsys.py --install --list ./lists/fse_2021_52.list /PATH/TO/TARGET/LOCATION
```
You will see the packages will be downloaded to the **/PATH/TO/TARGET/LOCATION/packages/**. 

Note that due to the special format, the packages with sub-folders(e.g., @eivifj/dot@1.0.1, @sailshq/lodash@3.10.2) can not be downloaded by the script. To analyze those packages, you need to download them manually by:

```shell
$ npm install PACKAGE@VERSION
```

And then, you need to copy the installed package itself to the target packages folder by:

```shell
$ cp -rf node_modules/PACKAGE /PATH/TO/TARGET/LOCATION/packages/
```

To make it easier to run, you should flatten the sub-folders of the manually downloaded packages by copy the sub-folder to the /PATH/TO/TARGET/LOCATION/packages/ folder then re-name it to a special name, and remove the origin folder. for example:

```shell
$ cp -rf /path/to/packages/@eivifj/dot@1.0.1 /path/to/packages/eivifj_dot;
$ rm -rf /path/to/packages/@eivifj;
```

## Preparing the list file

To generate the list file of the packages, we prepared a script to do that. You can go to the **tools** folder and run the **generate_list.py** by:

```shell
$ python3 generate_list.py /PATH/TO/TARGET/LOCATION/packages/
```

Then a list file named **result.list** will be generated in the **tools** folder. This is the list file that can be used by **ObjLupAnsys.py**

## Run a list of packages
As described in the main [README.md](../../README.md), ObjLupAnsys supports running a list of packages. We will run the list by:

```shell
$ python3 ObjLupAnsys.py --nodejs -a --timeout 300 -q --list ./lists/result.list
```

If your device has multiple CPU cores, we will recommend the *--parallel PARALLEL* parameter to analyze the packages parallelly. The command will be like:

```shell
$ python3 ObjLupAnsys.py --nodejs -a --timeout 300 -q --list ./lists/result.list --parallel 16
```

Here, for normal modern computers, we recommend setting the timeout to be 300 seconds. You should adjust the number based on your computer. The detection result will be output to **succ.log** and **results.log**. The **succ.log** file includes a list of packages that detected prototype pollution vulnerabilities. The **results.log** file includes a list of timeout or not-detected packages. 

Normally, based on the performance of the computer, you should be able to find 35 to 38 packages in the **succ.log** file, which means ObjLupAnsys successfully detects 30 to 38 packages. You can compare your **succ.log** file with the **lists/succ.res** and see which package is not detected. You can run the not detected packages independently by:

```shell
$ python3 ./ObjLupAnsys.py --nodejs -a --timeout 300 -q /PATH/TO/PACKAGE
```

Note that there are two packages, **casperjs@1.1.4** and **dojo@1.12.0**, the vulnerable function can not be directly reached by the main entrance file. You need to analyze the package by input the target file directly like:

```shell
$ python3 ./ObjLupAnsys.py --nodejs -a --timeout 300 -q /PATH/TO/dojo@1.12.0/request/util.js
```

and

```shell
$ python3 ./ObjLupAnsys.py --nodejs -a --timeout 300 -q /PATH/TO/casperjs@1.1.4/modules/utils.js
```

Finally you should be able to see the packages can be detected.