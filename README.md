# logstash-filter-test
[Logstash](https://www.elastic.co/products/logstash) is a program that collects
json documents from various inputs, transform them according to a configuration
file (a *filter*), and sends them to various outputs. This script helps you make
sure that your filter does what you expect by writing a test suite.

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
