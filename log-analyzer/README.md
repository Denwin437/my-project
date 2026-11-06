# Log Analyzer


Summarizes web server access logs in Common Log Format (Apache and Nginx default): request counts, status code classes, server error rate, bytes served, and the busiest IPs and paths.

## Usage
```bash
python loganalyzer.py sample.log --top 3
cat /var/log/nginx/access.log | python loganalyzer.py
```

Example output:
```
Requests:     7 (1 malformed lines skipped)
Data sent:    4800 bytes
5xx rate:     14.3%
Status codes: 2xx=3, 3xx=1, 4xx=2, 5xx=1
```

## Run the tests
```bash
pip install pytest
pytest
```

## What I practiced
Parsing with named regex groups, streaming over large files line by line, tolerating bad input, and summarizing with `collections.Counter`.
