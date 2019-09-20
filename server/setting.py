import datetime
from os.path import abspath, dirname

project_dir = dirname(abspath(__file__))

# 学期开始时间
term_start_date = datetime.date(2019, 9, 2)

# 七牛对象存储配置
qiniu_access_key = ''
qiniu_secret_key = ''
qiniu_bucket_name = ''
