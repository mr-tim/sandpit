import re
import subprocess
import json

def untable(output):
    result = []
    headings = None
    for line in output.strip().split('\n'):
        if headings is None:
            headings = [x.lower() for x in re.split('   +', line)]
        else:
            result.append(dict(zip(headings, re.split('   +', line))))
    return result

def images():
    return untable(docker(['images']))

def ps():
    return untable(docker(['ps']))

def inspect(object_id):
    j = docker(['inspect', object_id])
    return json.loads(j)

def run(image, params, ports=[]):
    args = ['run', '-d', '-t']
    for p in ports:
        args.extend(['-p', str(p)])
    args.append(image)
    args.extend(params)
    return docker(args)

def wait(container_id):
    return docker(['wait', container_id])

def commit(container_id, repository):
    return docker(['commit', container_id, repository])

def stop(container_id):
    return docker(['stop', container_id])

def docker(args):
    args = ['docker'] + list(args)
    print "Running docker: %r" % args
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out.strip()

