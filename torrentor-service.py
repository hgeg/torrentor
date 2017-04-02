from flask import Flask, request, jsonify, make_response, render_template
from werkzeug.debug import DebuggedApplication
from flup.server.fcgi import WSGIServer
from dot import Dot
from pathlib import Path
from tools import *

import core as torrentor
import time, json, sys, os, random, db, hashlib

app = Flask("torrentor",static_folder="static")
#debug settings
#remove on production
app.debug = True
app.wsgi_app = DebuggedApplication(app.wsgi_app, True)
DB = db.DB('torrentor')
namespace = "/torrentor"
config = Dot(json.loads(open('config.json').read()))

def sResponse(f):
    def response(*args,**kwargs):
        raw = f(*args, **kwargs)
        if(raw[0]=="file"):
            filename = raw[1]
            with open("./data/%s"%filename, 'rb') as fr:
                body = fr.read()
                size = fr.tell()
            headers = {"Content-Disposition": "attachment; filename=%s"%filename,"Content-Length":size, "Content-Type": "application/octet-stream", "Cache-Control": "no-cache", "Content-Description": "File Transfer"}
            return make_response((body, 200, headers)) 
        else:
            return jsonify(error=raw[0],data=raw[1])
    response.__name__ = f.__name__
    return response


@app.route(namespace + '/', methods=['POST','GET'])
def main(): 
    return render_template('index.html')

@app.route(namespace + '/list/', methods=['POST'])
@sResponse
def list(): 
    try:
        form = Dot(request.form)
        path = form.current_path
    except Exception as e:
        return True, "InvalidForm"
    current_path = Path(config.basePath) / path
    if current_path.exists() and current_path.is_dir():
        response = Dot()
        response.current_path = path
        response.files = []
        for f in current_path.iterdir():
            fd = Dot()
            fd.name = f.name
            if f.is_dir():
                fd.type = 'dir'
            elif is_mov(f.name):
                fd.type = 'mov'
            else:
                fd.type = 'reg'
            response.files += [fd.dump()]
        return False, response.dump()

@app.route(namespace + '/download/', methods=['POST'])
@sResponse
def download():
    try:
        form = Dot(request.form)
        url  = form.download_url
    except Exception as e:
        return True, "InvalidForm"
    current_path = Path(config.basePath).resolve()
    if current_path.exists() and current_path.is_dir():
        response = Dot()
        response.tid = torrentor.download(url, current_path.name)
        return False, response.dump()

@app.route(namespace + '/run/', methods=['POST'])
@sResponse
def run():
    try:
        form = Dot(request.form)
        key = form.key
        path = form.current_path
        action  = form.action
        print form.dump()
    except Exception as e:
        return True, "InvalidForm"
    try:
        target_path = Path(config.basePath) / path / key
        new_path = Path(path) / key
        response = Dot()
        if action == 'cd':
            assert(target_path.is_dir())
            response.current_path = str(new_path)
        if action == 'play':
            assert(is_mov(target_path.name))
            torrentor.play(path)
        return False, response.dump()
    except Exception as e:
        return True, "InvalidAction"

if __name__ == "__main__":
    #cache the players database
    if "--debug" in sys.argv:
        app.run('0.0.0.0',11389,debug=True)
    else:
        WSGIServer(app).run()
