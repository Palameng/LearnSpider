# -*- coding: utf-8 -*-
import scrapy
import re


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    # start_urls = ['http://blog.jobbole.com/']
    start_urls = ['http://blog.jobbole.com/113119/']

    def parse(self, response):
        # 返回的是一个SelectorList，因为向下可能还有其他标签，便于操作
        # chrome    //*[@id="post-113119"]/div[1]/h1
        # firefox   /html/body/div[3]/div[3]/div[1]/div[1]/h1
        # another   //*[@class="entry-header"]/h1/text()

        re1_selector = response.xpath("/html/body/div[1]/div[3]/div[1]/div[1]/h1")
        re2_selector = response.xpath('//*[@id="post-113119"]/div[1]/h1/text()')
        re3_selector = response.xpath('//div[@class="entry-header"]/h1/text()')

        title_selector = response.xpath('//div[@id="post-113119"]/div[1]/h1/text()')                            # 标题
        createtime_selector = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()')                  # 时间
        info_selector = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()')                       # 标签
        comment_selector = response.xpath('//span[@class="btn-bluet-bigger href-style hide-on-480"]/text()')    # 评论数
        vote_selector = response.xpath('//span[contains(@class, "vote-post-up")]/h10/text()')                   # 点赞数
        bookmark_selector = response.xpath('//span[contains(@class, "bookmark")]/text()')                       # 收藏数
        entry_selector = response.xpath('//div[(@class="entry")]')                                              # 正文

        title = title_selector.extract()[0]
        create_time = createtime_selector.extract()[0].strip().replace('·', '').strip()
        info = info_selector.extract()
        comment_num = comment_selector.extract()[0]
        vote_num = vote_selector.extract()[0]
        bookmark_num = bookmark_selector.extract()[0]
        entry = entry_selector.extract()[0]

        re_for_comment_num = re.match(r".*(\d+).*", comment_num)
        re_for_bookmark_num = re.match(r".*(\d+).*", bookmark_num)

        if re_for_comment_num:
            comment_num = re_for_comment_num.group(1)
        else:
            comment_num = 0

        if comment_num:
            bookmark_num = re_for_bookmark_num.group(1)
        else:
            bookmark_num = 0

        info = [element for element in info if not element.strip().endswith('评论')]
        str_info = ",".join(info)

        print(r'标题: %s' % title)
        print(r'创建时间: %s' % create_time)
        print(r'创建时间: %s' % info)
        print(r'评论数: %d' % comment_num)
        print(r'点赞数: %s' % vote_num)
        print(r'收藏数: %d' % bookmark_num)
        print(str_info)
        print(entry)
        pass
