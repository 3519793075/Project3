class DownComment:

    def __init__(self):
        # 爬取数据cookie user—agent
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6"
                          ") AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
            "Cookie": 'fspop=test; _lxsdk_cuid=1741e6d406ec8-07a55a88376aea-31657305-13c680-1741e6d406ec8; _lxsdk=1741e6d406ec8-07a55a88376aea-31657305-13c680-1741e6d406ec8; _hc.v=686b52bb-73c6-234a-0599-c881b393882d.1598238311; Hm_lvt_602b80cf8079ae6591966cc70a3940e7=1598238354; cityid=838; default_ab=index%3AA%3A3; switchcityflashtoast=1; s_ViewType=10; ll=7fd06e815b796be3df069dec7836c3df; ua=dpuser_7474971098; ctu=4cc4b902d60a40f51447c2d6d386233260a8f2e43bf520fb73056aa472dfbb35; aburl=1; Hm_lvt_dbeeb675516927da776beeb1d9802bd4=1598270129; Hm_lpvt_dbeeb675516927da776beeb1d9802bd4=1598270129; cy=1; cye=shanghai; dper=627d6236bc87ce08b3d5c48661e5572f504bcf9938fee451ebd4566d8234bc5b1ad10791c702986d1398b6a838a4e550619d42c3d68d02b0f53cf4ed5c38702b47d41ef5f7e7d368892b8be8a46b2eb844582afbcc419e5e28df0a92c1df589e; uamo=17643530928; dplet=7731f44d071e7840935794d1a9ae35d4; Hm_lpvt_602b80cf8079ae6591966cc70a3940e7=1598342331; _lxsdk_s=1742497507a-072-c5-68e%7C%7C766'
        }
        # 爬取大众点评的url
        self.url = None
        # 页面返回的text
        self.text = None
        # css文件的内容
        self.css_content = None
        # css文件的url
        self.css_url = None
        # 取出的字体文件的内容
        self.svg_content = None
        # 用来存储每一个字的映射关系的列表
        self.font_d_l = list()
        # 用来存储坐标映射
        self.position_l = list()
        # 字体位置
        self.position_list = list()
        # 数据
        self.data = list()


    def down_css(self):
        """
        获取css文件
        :return:
        """
        # 请求返回的text
        self.text = requests.get(self.url, headers=self.headers).text
        # 使用xpath取出所有link中的链接
        x = etree.HTML(self.text)
        css_list = x.xpath('//link/@href')
        self.css_url = 'https:' + str(re.findall('//s3plus\.meituan\.net.+?\.css', ' '.join(css_list))[0])

    def down_svg(self):
        """
        下载字体文件
        :return:
        """
        # css请求返回的text
        self.css_content = requests.get(self.css_url, headers=self.headers).text
        # 使用正则取出
        svg_list = re.findall(r"background-image: url\((.+?)\);", self.css_content)
        svg_url = ["https:{}".format(svg) for svg in svg_list]

        # 下载最大的svg文件
        length_d_l = list()
        [length_d_l.append({"len": len(requests.get(svg).text), "content": requests.get(svg).text}) for svg in svg_url]
        self.svg_content = str([x["content"] for x in length_d_l if x["len"] == max([i["len"] for i in length_d_l])][0])

        with open("xx.html", "w")as f:
            f.write(self.text)
        with open('xx.css', "w") as f:
            f.write(self.css_content)
        with open("font.svg", "w") as f:
            f.write(self.svg_content)

    def font_mapping(self):
        """
        字体映射
        :return:
        """
        # 使用正则取出字
        font_list = re.findall(r'<text x=".*" y="(.*)">(.+?)</text>', self.svg_content)
        # 循环并将映射添加到列表中
        for num, i in enumerate(font_list):
            for x, v in enumerate(i[1]):
                self.font_d_l.append({
                    "value": v,
                    "x": x,
                    "y": (int(font_list[num - 1][0]) if font_list[num - 1][0] != '2495' else 0, int(i[0]))
                })
    def position_mapping(self):
        '''
        位置映射
        :return:
        '''
        all_ = re.findall("\.(.+?){background:-(.+?)\.0px -(.+?)\.0px;}", self.css_content)
        [self.position_l.append({
            "class": i[0],
            "x": i[1],
            "y": i[2],
        }) for i in all_]

    def all_font_position(self):
        """
        所有字体位置
        :return:
        """
        x = etree.HTML(self.text)
        self.position_list = x.xpath('//svgmtsi/@class')

    def find_font(self, x, y):
        '''
        查询具体字体
        :param x:
        :param y:
        :return:
        '''
        # 根据坐标返回对应的字体
        new_x = int(x) / 14
        for i in self.font_d_l:
            if int(i.get("x")) == int(new_x) and i.get('y')[0] < int(y) < i.get('y')[1]:
                return i.get('value')

  def get_data(self, str_text):
        x = etree.HTML(str_text)
        # 取出所以li标签
        li = x.xpath('//div[@class="reviews-items"]/ul/li')
        print(len(li))
        for l in li:
        	# 定义一个字典用来存储数据
            item = dict()
            # 口味评分
            flavor = l.xpath("./div/div/span/span[1]/text()")
            # 环境评分
            ambient = l.xpath("./div/div/span/span[2]/text()")
            # 服务评分
            service = l.xpath("./div/div/span/span[3]/text()")
            # 人均价格
            price = l.xpath("./div/div/span/span[4]/text()")
            # 发布时间
            times = l.xpath("./div[@class='main-review']/div/span[@class='time']/text()")
            # 短评论
            s_comment = l.xpath("div[@class='main-review']/div[@class='review-words']")
            # 长评论
            l_comment = l.xpath("div[@class='main-review']//div[@class='review-words Hide']")
            # 存储到字典中
            item["flavor"] = str(flavor[0]).replace('\n', '').replace(' ', '') if flavor else "暂无"
            item["ambient"] = str(ambient[0]).replace('\n', '').replace(' ', '') if ambient else "暂无"
            item["service"] = str(service[0]).replace('\n', '').replace(' ', '') if service else "暂无"
            item["price"] = str(price[0]).replace('\n', '').replace(' ', '') if price else "暂无"
            item["time"] = str(times[0]).replace('\n', '').replace(' ', '') if times else "暂无"
			# 判断此条评论为长评还是短评 然后存储到字典
            if l_comment:
                l_str = html.unescape((etree.tostring(l_comment[0]).decode()))
                l_com = re.findall('<div class="review-words Hide">(.+?)<div class="less-words">', l_str,
                                   re.DOTALL)[0]
                item["comment"] = l_com.replace('\n', '').replace(' ', '').replace('\t', '')
            elif s_comment:
                s_str = html.unescape((etree.tostring(s_comment[0]).decode()))
                s_com = re.findall('<div class="review-words">(.+?)</div>', s_str, re.DOTALL)[0]
                item["comment"] = s_com.replace('\n', '').replace(' ', '').replace('\t', '')
            else:
                item["comment"] = "该用户没有填写评论..."
            # 类中的列表 来存储保存后的字典
            self.data.append(item)

    def save(self):
        """
        保存数据为csv文件
        :return:
        """
        pandas.DataFrame(self.data,
                         columns=["flavor", "ambient", "service", "price", "time", "comment"]).to_csv(
            'reviews.csv')


    def run(self, url):
        self.url = url
        # 获取css
        self.down_css()
        # 获取字体文件
        self.down_svg()
        # 添加字体映射
        self.font_mapping()
        # 添加位置映射
        self.position_mapping()
        # 获取所有加密字体位置
        self.all_font_position()
        # 查询对应字体 并替换
        str_text = str(self.text)
        for position in self.position_list:
            for x in self.position_l:
                if x.get("class") == position:
                    str_text = str_text.replace('<svgmtsi class="{}"></svgmtsi>'.format(position),str(self.find_font(x.get('x'),x.get('y')))).replace("&#x0A;",'').replace("&#x20;", '')
        # 获取数据
        self.get_data(str_text)
        # 保存文件
        self.save()
        # 控制台打印数据
        pprint(self.data)

def main():
    # 创建爬虫对象
    down_spider = DownComment()
    # 爬取5页数据
    for i in range(1, 2):
        print('-----------当前为{}页---------------'.format(i))
        url = "http://www.dianping.com/shop/k9oYRvTyiMk4HEdQ/review_all/p{}".format(i)
        down_spider.run(url=url)
