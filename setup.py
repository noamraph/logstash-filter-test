from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
    author='Noam Yorav-Raphael',
    author_email='noamraph@gmail.com',
    description='Easily test logstash filter',
    long_description=long_description,
    long_description_content_type='text/markdown',
    name='logstash-filter-test',
    url='https://github.com/noamraph/logstash-filter-test',
    version='0.1.1',
    license='MIT',
    py_modules=['logstash_filter_run', 'logstash_filter_test'],
    scripts=['logstash_filter_test.py'],

)
