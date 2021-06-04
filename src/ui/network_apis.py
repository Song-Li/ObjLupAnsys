# start a server and accept requests
import flask 
import uuid
import os
import json
from werkzeug.utils import secure_filename
from shutil import unpack_archive
from src.core.options import options
from src.core.opgen import OPGen
from src.core.logger import loggers, create_logger
from tinydb import TinyDB, Query

app = flask.Flask(__name__)
options.net_env_dir = None
#db = TinyDB('./net_env_dir/tinydb.json')

def update_env():
    options.net_env_dir = os.path.join('./net_env_dir/', str(uuid.uuid4()))
    env_dir = options.net_env_dir
    if not os.path.exists(env_dir):
        os.makedirs(env_dir, exist_ok=True)
    # update the tmp logger location
    loggers.update_loggers(options.net_env_dir)
    return env_dir

@app.route('/')
@app.route('/imgs/<path:imgname>')
@app.route('/js/<path:jsname>')
@app.route('/css/<path:cssname>')
def index(jsname=None, cssname=None, imgname=None):
    if not jsname and not cssname and not imgname:
        return flask.send_from_directory(app.static_folder, 'index.html')
    elif jsname:
        return flask.send_from_directory(os.path.join(app.static_folder, 'js'), jsname)
    elif cssname:
        return flask.send_from_directory(os.path.join(app.static_folder, 'css'), cssname)
    elif imgname:
        return flask.send_from_directory(os.path.join(app.static_folder, 'imgs'), imgname)

@app.route('/getFile', methods=['POST'])
def get_file():
    data = flask.request.get_json()
    file_name = os.path.abspath(os.path.join(options.run_env, data['name']))
    #TODO: vulnerable to path traversal
    return flask.send_file(file_name)


def generate_graph_json(render=True):
    """
    read the results form tmp results
    generate the json based graph
    Args:
        render (boolean): render as a js file or return nodes and edges
    Returns:
        str: the rendered template
    """
    env_dir = options.run_env

    with open(os.path.join(options.net_env_dir, "results_tmp.log"), 'r') as fp:
        res = fp.read()

    # handle the result
    if 'FilePath' not in res:
        return "Not detected"
    pathes = res.split("|checker|")[1:]

    # generate json for graph
    edges = []
    file_map = {}
    node_map = {}
    nodes = []
    node_blocks = []
    height = 0
    idx = 0
    for path in pathes:
        blocks = path.split("$FilePath$")
        cur_color = blocks[0].split("$color:")[1].split('$')[0]
        blocks = blocks[1:]
        pre_block = None
        for block in blocks:
            lines = block.split('\n')
            # if lines[0] is None, measn it's builtin
            if lines[0] == 'None':
                lines[0] = "Built-in Objects"
            else:
                lines[0] = os.path.relpath(lines[0], env_dir)
            max_len = max(len(line) for line in lines)

            title = lines[0]
            if title not in file_map:
                file_map[title] = idx
                node_map[title] = {"data": {"id": idx, "content": title}}
                idx += 1
            block = '\n'.join(block.split('\n')[1:])
            block = block.strip()
            block_height = len(lines) * 15

            if block not in node_map:
                node_map[block] = {
                    "data": {
                        "id": idx, 
                        "parent": file_map[title], 
                        "content": block,
                        "width": max_len * 8,
                        'height': block_height,
                        }}
                idx += 1

            if pre_block:
                source = node_map[pre_block]['data']['id']
                target = node_map[block]['data']['id'] 
                edges.append({
                    "data":{
                        "id": "{}-{}-{}".format(str(source),str(target),cur_color),
                        "source": source,
                        "target": target,
                        'color': cur_color
                        }
                    })

            pre_block = block

    nodes = json.dumps([v for k, v in node_map.items()])
    print(nodes)
    edges = json.dumps(edges)
    print(edges)
    if render:
        render_res = flask.render_template("graph.js", NODES=nodes, EDGES=edges)
        return render_res
    else:
        return nodes, edges

@app.route('/check', methods=['POST'])
def check():
    env_dir = options.net_env_dir
    form = flask.request.form
    options.vul_type = 'proto_pollution'
    if 'module' in form:
        options.module = True
    else:
        options.module = False

    if 'no_file_based' in form:
        options.no_file_based = True
    else:
        options.no_file_based = False
        
    if 'exit_when_found' in form:
        options.exit = True
    else:
        options.exit = False

    if 'run_all' in form:
        options.run_all = True
    else:
        options.run_all = False

    options.input_file = os.path.join(os.path.abspath(env_dir))

    if 'babel' in form:
        options.babel = os.path.abspath(env_dir)
        options.run_env = os.path.join('./net_env_dir/', str(uuid.uuid4()))
    else:
        options.babel = None
        options.run_env = options.net_env_dir

    # we need to clear the results tmp
    with open(os.path.join(options.net_env_dir, "results_tmp.log"), 'w') as fp:
        fp.write("")
    with open(os.path.join(options.net_env_dir, "progress.log"), 'w') as fp:
        fp.write("0\n")

    opg = OPGen()
    try:
        opg.run()
    except Exception as e:
        print(e)

    render_res = generate_graph_json()
    return render_res

@app.route('/progress', methods=['GET', 'POST'])
def get_progress():
    with open(os.path.join(options.net_env_dir, "progress.log"), 'r') as fp:
        lines = fp.readlines()
    if len(lines) != 0:
        return lines[-1]
    else:
        return 0

@app.route('/upload', methods=['POST'])
def upload():
    options.net_env_dir = update_env()
    env_dir = options.net_env_dir
    file_cnt = 0
    file_path = None
    try:
        uploaded = flask.request.files
        for file_values in uploaded.listvalues():
            # we only have one key here
            for f in file_values:
                file_path = os.path.join(env_dir, secure_filename(f.filename))
                f.save(file_path)
                file_cnt += 1
    except Exception as e:
        print(e)
        return "File uploading failed"

    try:
        # unzip the file
        unpack_archive(file_path, env_dir)
    except Exception as e:
        return "File unzipping failed"

    return f"Successfully uploaded and unzipped {file_cnt} Files"
