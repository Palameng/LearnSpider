# -*- coding: utf-8 -*-

from scrapy.cmdline import execute

import sys
import os

print(os.path.dirname(os.path.abspath(__file__)))

# os.path.abspath(__file__) 获取到main文件的绝对路径, os.path.dirname获取到父目录
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy", "crawl", "jobbole"])
