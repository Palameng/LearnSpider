# -*- coding: utf-8 -*-
import scrapy
import re

from scrapy.http import Request
from urllib import parse

from ArticleSpider.items import JobBoleArticleItem
from ArticleSpider.utils.common import get_md5


class JobboleSpider(scrapy.Spider):
    """
    scrapy是一个异步框架， 所有的url都会直接交给异步的downloader， 然后之前parse的逻辑继续执行，进入下一页的爬取逻辑的意思就是说之前
    的20个url已经提交给异步downloader下载了， 但并不表示20个url全部返回了， 而且这20个url下载是并行的， 哪个先回来哪个后回来都不一定
    """
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    # start_urls = ['http://blog.jobbole.com/']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1. 获取文章列表页中的文章url交给scrapy下载并进行具体字段的解析
        2. 获取下一页的url并交给scrapy进行下载，完成后交给parse
        :param response:
        :return:
        """

        # 获取所有url
        post_nodes = response.css("#archive div.floated-thumb .post-thumb a")
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            # urljoin会根据post_url的情况 来拼接url 如果有url就不会强加response.url 如果没有就会加上 后期学习python
            # 的过程中建议随时打开一个终端 直接测试就行了 python一个好处就是测试很方便
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url}, callback=self.parse_detail)

        # 提取下一页并交给scrapy下载分析
        next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        # 返回的是一个SelectorList，因为向下可能还有其他标签，便于操作
        # chrome    //*[@id="post-113119"]/div[1]/h1
        # firefox   /html/body/div[3]/div[3]/div[1]/div[1]/h1
        # another   //*[@class="entry-header"]/h1/text()

        # 通过xpath得到的选择器例子
        # re1_selector = response.xpath("/html/body/div[1]/div[3]/div[1]/div[1]/h1")
        # re2_selector = response.xpath('//*[@id="post-113119"]/div[1]/h1/text()')
        # re3_selector = response.xpath('//div[@class="entry-header"]/h1/text()')

        article_item = JobBoleArticleItem()

        front_image_url = response.meta.get("front_image_url", "")  # 文章封面图

        # 获取到页面各个信息的选择器

        title_selector = response.xpath('//div[@class="entry-header"]/h1/text()')    # 标题
        title_css = response.css(".entry-header h1::text")  # 增加::伪类选择器去掉<h1>
        createtime_selector = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()')  # 时间
        info_selector = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()')  # 标签
        comment_selector = response.xpath('//span[@class="btn-bluet-bigger href-style hide-on-480"]/text()')    # 评论数
        vote_selector = response.xpath('//span[contains(@class, "vote-post-up")]/h10/text()')   # 点赞数
        bookmark_selector = response.xpath('//span[contains(@class, "bookmark")]/text()')   # 收藏数
        entry_selector = response.xpath('//div[(@class="entry")]')  # 正文

        # 对选择器进行extract()得到相应的列表
        title = title_selector.extract()[0]
        titlecss = title_css.extract_first('')    # 防止异常
        create_time = createtime_selector.extract()[0].strip().replace('·', '').strip()
        info = info_selector.extract()
        comment_num = comment_selector.extract()[0]
        vote_num = vote_selector.extract()[0]
        bookmark_num = bookmark_selector.extract()[0]
        entry = entry_selector.extract()[0]

        re_for_comment_num = re.match(r".*(\d+).*", comment_num)
        re_for_bookmark_num = re.match(r".*(\d+).*", bookmark_num)

        if re_for_comment_num:
            comment_num = int(re_for_comment_num.group(1))
        else:
            comment_num = 0

        if comment_num:
            bookmark_num = int(re_for_bookmark_num.group(1))
        else:
            bookmark_num = 0

        info = [element for element in info if not element.strip().endswith('评论')]
        str_info = ",".join(info)

        # title = scrapy.Field()
        # create_date = scrapy.Field()
        # url = scrapy.Field()
        # url_object_id = scrapy.Field()
        # front_image_url = scrapy.Field()
        # front_image_path = scrapy.Field()
        # vote_num = scrapy.Field()
        # bookmark_num = scrapy.Field()
        # comment_num = scrapy.Field()
        # info = scrapy.Field()
        # entry = scrapy.Field()

        article_item["title"] = title
        article_item["create_date"] = create_time
        article_item["url"] = response.url
        article_item["url_object_id"] = get_md5(response.url)
        article_item["front_image_url"] = [front_image_url]
        # article_item[front_image_path] =
        article_item["vote_num"] = vote_num
        article_item["bookmark_num"] = bookmark_num
        article_item["comment_num"] = comment_num
        article_item["info"] = info
        article_item["entry"] = entry

        # print(r'标题: %s' % title)
        # print(r'创建时间: %s' % create_time)
        # print(r'创建时间: %s' % info)
        # print(r'评论数: %d' % comment_num)
        # print(r'点赞数: %s' % vote_num)
        # print(r'收藏数: %d' % bookmark_num)
        # print(str_info)
        # print(entry)
        yield article_item
