[
  // Test a message without a value
  [
    {
      "message": "<<2018-06-11 13:45:39,127+0300>> Everything is awesome!"
    },
    {
      "date": "2018-06-11 13:45:39,127+0300",
      "@timestamp": "2018-06-11T10:45:39.127Z",
      "msg_text": "Everything is awesome!",
      "metric": null,
    }
  ],

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