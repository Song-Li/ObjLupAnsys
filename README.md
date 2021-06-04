# ObjLupAnsys
ObjLupAnsys is a tool to detect prototype pollution vulnerabilities in Node.js packages. This project is written in Python and JavaScript and the source code is included in the repository. 

## Installation
Please check out [INSTALL.md](https://github.com/Song-Li/ObjLupAnsys/blob/main/INSTALL.md) for the detailed instruction of the installation.

## How to use
ObjLupAnsys provides two interfaces--a command-line-based interface for experts and a Web-based interface for beginners or web users. 
### Command-line 
Use the following arugments to run the tool:

```bash
python3 ObjLupAnsys.py	[-h] [-p] [-m] [-q] [-s] [-a] [--timeout TIMEOUT] [-l LIST] [--install] 
						[--max-rep MAX_REP] [--no-prioritized-funcs] [--nodejs] 
						[--entrance-func ENTRANCE_FUNC] [--pre-timeout PRE_TIMEOUT]
						[--max-file-stack MAX_FILE_STACK] [--skip-func SKIP_FUNC] [--run-env RUN_ENV] 
						[--no-file-based] [--parallel PARALLEL] [input_file]
```

| Argument | Description |
| -------- | ----------- |
| `input_file` | See subsection Input. |
| `-p, --print` | Print logs to console, instead of files. |
| `-m, --module` | Module mode. Indicate the input is a module, instead of a script. |
| `-q, --exit` | Exit the analysis immediately when vulnerability is found. Do not use this if you need a complete graph. |
| `-s, --single-branch` | Single branch mode (or single execution). If set, ObjLupAnsys will disable the branch-sensitive mode. |
| `-a, --run-all` | Run all exported functions in module.exports of **all** analyzed files even if the file is not the entrance file.|
| `--timeout TIMEOUT`| The timeout(in seconds) of running a single module for one time. (Optimizations may run a module multiple times. This is the timeout for a single run.)|
| `-l, --list LIST`| Run a list of files/packages. Each line of the file contains the path to a file/package. |
| `--install`| Download the source code of a list of packages to the --run-env location. |
| `--max-rep MAX_REP`| If set, every function can only exsits in the call stack for at most MAX_REP times. (To prevent too many levels of recursive calls)| 
| `--no-prioritized-funcs`| If set, ObjLupAnsys will not start from the prioritized functions. |
| `--nodejs`| Node.js mode. Indicate the input is a Node.js package. |
| `--entrance-func ENTRANCE_FUNC`| If set, ObjLupAnsys will analyse the ENTRANCE_FUNC before analyzing the package. |
| `--pre-timeout PRE_TIMEOUT`| The timeout(in seconds) for preparing the environment before running the prioritized functions. Defaults to 30.|
| `--max-file-stack MAX_FILE_STACK`| The max depth of the required file stack. |
| `--skip-func SKIP_FUNC`| Skip a list of functions, separated by "," .|
| `--run-env ENV_DIR` | Set the running environment location.|
| `--no-file-based`| Only detect the vulnerabilities that can be directly accessed from the main entrance of the package. |
| `--parallel PARALLEL`| Run a list of packages parallelly in PARALLEL threads. Only works together with --list argument. |

Here is an example to show how to use our command-line based tool:

```shell
$ python3 ./ObjLupAnsys.py --nodejs -a ./tests/packages/set-value
```
Once finished, the tool will output the detecting result, and if any vulnerability is found, it will also output the location of the vulnerability and the attack path.
### Web-based GUI
The Web-based GUI includes a back-end server and a front-end client. To start the server, you can simply run:

```shell
$ ./start_server.py
```
Once the server is started, you can open your browser and visit the url [http://localhost:9870/](http://localhost:9870/) to access the Web-based GUI. The following steps show how to use our GUI:

1. Click "Choose zip file to upload" to pick the zip file of the package. Note that the package should be directly zipped without any sub-folders
2. Click Submit until a green icon appears, which means the zip file is successfully uploaded
3. Select the options. For large packages, we recommend checking "Module". For small packages, we recommend checking "Module" and "Run Exported Functions". For packages that use ES2015 and above features, we recommend checking "Use Babel"
4. Click "Submit" and wait for the progress bar to finish
5. Once the Results are ready, you can click the components of the graph. We will grep the related source code from the server for you to check.

# Artifacts Available
Our code is stored at GitHub. The link to the repository is [https://github.com/Song-Li/ObjLupAnsys](https://github.com/Song-Li/ObjLupAnsys). The source code is released with the [GPL 2.0](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html) license.

For example:
```console
$ python3 ObjLupAnsys.py --install --list ./lists/fse_2021_52.list --run-env ~/
$ python3 generate_list.py ~/packages/
$ python3 ./ObjLupAnsys.py --timeout 300 --nodejs -a --list ./tools/result.list --parallel 16
```

## Examples

```shell
$ ./generate_opg.py ./tests/test.js -m -a -t os_command
```

For the modified version of challenge example, you can simply run 
```shell
$ ./generate_opg.py -t os_command ./tests/chas/main.js
```

For the original version of challenge example, you can simply run 
```shell
$ ./generate_opg.py -t os_command ./tests/chas_class/main.js --babel ./tests/chas_class/
```
