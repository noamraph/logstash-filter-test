import json
import os
from genericpath import exists
from os.path import join
from shutil import rmtree
from subprocess import Popen, PIPE
from tempfile import mkdtemp

LOGSTASH_BIN_ALTERNATIVES = [
    '/opt/logstash/bin/logstash',
    '/usr/share/logstash/bin/logstash',
    ]

PIPELINES_YML = """\
- pipeline.id: my-pipeline
  path.config: "{}"
  pipeline.workers: 1
"""

INPUT_OUTPUT_CONF = """\
input {
  stdin {
    codec => "json_lines"
  }
}
output {
  file {
    path => "%s"
  }
}
"""


def logstash_filter_run(inputs, filter_def, logstash_bin=None, remove_tempdir=True):
    """
    Run a bunch of json through logstash given the filter definition
    :param inputs: a list of dicts
    :param filter_def: logstash filter definition as a string
    :param logstash_bin: logstash executable path. By default will try
        LOGSTASH_BIN_ALTERNATIVES
    :param remove_tempdir: remove temporary working directory after done
    :return: a list of dicts, the results
    """
    input_jsons = [json.dumps(d) for d in inputs]
    assert all(s[0] == '{' for s in input_jsons), "inputs must be a list of dicts"
    if logstash_bin is None:
        for fn in LOGSTASH_BIN_ALTERNATIVES:
            if exists(fn):
                logstash_bin = fn
                break
        else:
            raise RuntimeError("Couldn't find logstash executable")

    workdir = mkdtemp(prefix='logstash-test-')
    data_dir = join(workdir, 'data')
    config_dir = join(workdir, 'config')
    pipeline_dir = join(workdir, 'pipeline.d')
    os.mkdir(data_dir)
    os.mkdir(config_dir)
    os.mkdir(pipeline_dir)
    open(join(config_dir, 'logstash.yml'), 'w').close()
    with open(join(config_dir, 'pipelines.yml'), 'w') as f:
        f.write(PIPELINES_YML.format(pipeline_dir))
    output_fn = join(workdir, 'output')
    with open(join(pipeline_dir, 'io.conf'), 'w') as f:
        f.write(INPUT_OUTPUT_CONF % output_fn)
    with open(join(pipeline_dir, 'filter.conf'), 'w') as f:
        f.write(filter_def)
    inputs_s = ''.join(s+'\n' for s in input_jsons)
    args = [logstash_bin, '--log.level=warn',
            '--path.settings', config_dir, '--path.data', data_dir]
    print(' '.join(args))
    popen = Popen(args, stdin=PIPE)
    popen.communicate(inputs_s.encode('utf8'))
    rc = popen.wait()
    if rc != 0:
        raise RuntimeError("logstash returned non-zero return code {}"
                           .format(rc))
    output_lines = list(open(output_fn))
    if len(output_lines) != len(inputs):
        raise RuntimeError("Received {} outputs, expecting {}"
                           .format(len(output_lines), len(inputs)))
    outputs = [json.loads(line) for line in output_lines]
    if remove_tempdir:
        rmtree(workdir)
    return outputs
