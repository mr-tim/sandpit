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
    obj = json.loads(j)
    if len(obj):
        return obj[0]
    else:
        return None

def run(image, params=[], ports=[]):
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

def start(container_id):
    return docker(['start', container_id])

def stop(container_id):
    return docker(['stop', container_id])

def rm(container_id):
    return docker(['rm', container_id])

def build(build_dir, tag):
    output = docker(['build', '-t', tag, build_dir])
    last_line = output.split('\n')[-1]
    image_id = last_line.split(' ')[-1]
    return image_id

def docker(args):
    args = ['docker'] + list(args)
    print "Running docker: %r" % args
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out.strip()

