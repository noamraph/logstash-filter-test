# logstash-filter-test
[Logstash](https://www.elastic.co/products/logstash) is a program that collects
json documents from various inputs, transform them according to a configuration
file (a *filter*), and sends them to various outputs. This script helps you make
sure that your filter does what you expect by writing a test suite.

This is similar to
[logstash-filter-verifier](https://github.com/magnusbaeck/logstash-filter-verifier).
After being frustrated with it for a few days I decided to write my own. I find
it to be much simpler and easier. Try it and decide for yourself!

## Installation

You can install using pip:

```
pip install logstash-filter-test
```

or just copy `logstash_filter_run.py` and `logstash_filter_test.py`. There are
no dependencies. Python 3.5+ and 2.7 are supported.

## Example

Here is a simple test suite file:

testcases.js:
```javascript
[
  // Test a message with a value
  [
    {
      "message": "<<2018-06-11 13:45:39,127+0300>> TAU = 6.2831853"
    },
    {
      "date": "2018-06-11 13:45:39,127+0300",
      "@timestamp": "2018-06-11T10:45:39.127Z",
      "msg_text": "TAU = 6.2831853",
      "metric": "TAU",
      "value": 6.2831853,
    }
  ],
]
```

filter.conf:
```
filter {
  grok {
    match => {
      "message" => [
        "^<<%{TIMESTAMP_ISO8601:date}>> %{GREEDYDATA:msg_text}$"
      ]
    }
  }
  date {
    match => ["date", "ISO8601"]
  }
  grok {
    match => {
      "msg_text" => [
        "^%{WORD:metric} = %{NUMBER:value:float}"
      ]
    }
    tag_on_failure => []
  }
}
```

Put them in a directory, run `./logstash_filter_test.py` and it will inform you
if the testcases passed, and if not, why.

`testcases.js` can be a simple json file. It has the extension `.js` because
javascript comments and trailing commas are allowed, thanks to
[jstyleson](https://github.com/linjackson78/jstyleson). It is a list of
test cases. Each test case is a list of size 2. The first item is the input 
json document. The second item is compared to the output json document. All
fields that are defined must be equal to the fields in the output document.
The output document may include other fields. To test that an output field
doesn't exist, use `"field": null`.

## Testing `[@metadata]`

Logstash allows using a transient field called `[@metadata]`, which is not produced by any output plugins. This is useful if you want to influence the flow of the filter (and/or the output) section, but not by using a field that would be present in the output. The metadata field acts like a bucket for internal variables (it is a nested field on which you can set sub-fields. For example, in the filter section you could set `[@metadata][target_index]` to a desired value for an Elasticsearch index and then in the output section in the `elasticsearch` plugin you could use `%{[@metadata][target_index]}-%{+yyyy.MM.dd}` as your index name pattern.

However, since `[@metadata]` is by definition not produced by the output section, it is consequently not possible to write test cases that verify that the filter section set the correct data in the `[@metadata]` field (or that it correctly didn't set metadata). Once your filter and output sections start relying on metadata it becomes critical that you are also able to write test cases that cover metadata. But, rejoice, as with logstash-filter-test you can still test metadata! The whole `[@metadata]` field will be copied into another field called `[__@metadata]`, allowing you do to something like this:

```
    [
        {
            "message" : "my sample log line",
            "path" : "/path/to/source/file.log",
            "host" : "my-host-name"
        },
        {
            "__@metadata" : 
            {
                "target_index" : "kittycat"
            },
           "@timestamp" : "2019-02-10T00:19:02.106Z",
           "hostname" : "my-host-name",
           "level" : "INFO",
           "source.file.path.raw" : "/path/to/source/file.log",
           "tags" : null
        }
    ]
```

In addition, if you choose to not remove the temp directory that logstash-filter-test creates during execution (see corresponding command line argument), then you can have a look at the file `pipeline.d/output-ap`. Running your test cases through your filters will generate this output in the Ruby Awesome Print format, which is what Logstash's rubydebug codec uses. The AP format is just another format in addition to the JSON file `output-json` that logstash-filter-test also produces. The AP file is not actually used by logstash-filter-test, but it can be useful for debugging your test cases and filters, because the file contains the `[@metadata]` field exactly as set and modified by your filters (no renaming to `[__@metadata]`). It is also formatted in a more human-readable way than the JSON output file.


## Command line arguments

| Argument | Description | Default |
| -------- | ----------- | ------- |
| `--filters` | File with Logstash filter definition to test. | `filter.conf` |
| `--testcases` | File with test cases. | `testcases.js` |
| `--remove_tempdir` | Whether to remove the temp dir that is created during execution (yes/no). | `yes` (any other value will be equivalent to `no`) |
| `--logstash` | Path to the Logstash executable. | \[ `/opt/logstash/bin/logstash`, `/usr/share/logstash/bin/logstash` \] |

Example on Windows:

```
logstash_filter_test.py --remove_tempdir=yes --logstash C:\path\to\logstash-6.2.3\bin\logstash.bat --filters C:\path\to\logstash\indexer\config\filter.conf --testcases C:\path\to\logstash\indexer\test\testcases.js
```

## Testing from Python

If you don't like the testcase file format, it's easy to test by yourself:

```pydocstring
>>> from logstash_filter_run import logstash_filter_run
>>> logstash_filter_run([{"a": 3}], 'filter { mutate { copy => { "a" => "b" } } }')
[{'@timestamp': '2018-07-10T18:26:58.411Z',
  '@version': '1',
  'a': 3,
  'b': 3,
  'host': 'myhost'}]
```
