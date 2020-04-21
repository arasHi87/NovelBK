import os
import json
from ebooklib import epub
from pprint import pprint
from random import randint

loc = os.path.dirname(__file__)

def txt2epub(data, base_store_path):
    base_name = list(data['index'].keys())[0]
    data = data['index'][base_name]
    
    for volume in data['index']:
        v_name = volume[0]
        b_name = base_name + v_name
        book = epub.EpubBook()
        chapter_list = []
        toc_list = []
        path = os.path.join(base_store_path, base_name, 'epub')

        if not os.path.isdir(path):
            os.makedirs(path)

        book.set_identifier('{}{}'.format(b_name, randint(0, 100000000)))
        book.set_title(b_name)
        book.add_author(data['author'])
        book.set_language('en')

        for c_name in volume[1:]:
            c_id = str(randint(0, 100000000))
            chapter = epub.EpubHtml(title = c_name, file_name = c_id + '.xhtml')

            with open(os.path.join(base_store_path, base_name, 'txt', v_name, c_name + '.txt'), 'r') as fp:
                chapter.content = '<h1>{}</h1><br>{}'.format(c_name, fp.read().replace('\n', '<br>'))
            
            book.add_item(chapter)
            chapter_list.append(chapter)
            toc_list.append(epub.Link(c_id + '.xhtml', c_name, c_id))
        
        book.toc = tuple(toc_list)
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        book.spine = ['nav'] + chapter_list
        epub.write_epub(os.path.join(path, b_name + '.epub'), book, {})

if __name__ == '__main__':
    test_data = {'index': {'战斗司书': [['第一卷 战斗司书与恋爱爆弹',
                     '主要登场人物',
                     '第一章 爆弹与『书』与灰色小镇',
                     '第二章 爆弹与公主与形形色色的人',
                     '第三章 爆弹与人类与风的轨迹',
                     '第四章 爆弹与司书与常笑之魔女',
                     '第五章 空壳与敌人与死神之病',
                     '第六章 暴风雨与魔刀与小花猫',
                     '终章 夕阳与丝柔与克里欧',
                     '断章 苹果与花与逝去石剑',
                     '后记'],
                    ['第二卷 战斗司书与雷之愚者',
                     '序章 黄金的怪物',
                     '第一章 透明的男人、揍人的少女',
                     '第二章 第一个的过去——船底',
                     '第三章 自我了断的男人、无法杀人的拳头',
                     '第四章 第二个的过去——雪击',
                     '第五章 自责的灵魂、圣洁的眼睛',
                     '第六章 终结的过去——虐杀',
                     '第七章 少女的愚蠢行为、不曾死亡的怪物',
                     '断章 真正的怪物',
                     '后记'],
                    ['第三卷 战斗司书与黑蚁迷宫',
                     '序章 没有暖炉的房间',
                     '第一章 红色的警讯灯',
                     '第二章 黑蚁的巢穴',
                     '第三章 潜行战士的踌躇',
                     '第四章 残暴的蜘蛛',
                     '第五章 控制皇后棋的棋手',
                     '第六章 善良男人的结局',
                     '断章 打瞌睡的病房',
                     '后记'],
                    ['第四卷 战斗司书与神之石剑',
                     '序章 雨夜的死尸',
                     '第一章 寻找虚幻的『书』商',
                     '第二章 铁锈色的女人',
                     '第三章 天国的回忆',
                     '第四章 某个家畜的一生',
                     '第五章 弱者们的决战',
                     '第六章 潜藏暗中主使者的幕后舞台',
                     '断章 等待幸福的天神沉眠处',
                     '后记'],
                    ['第五卷 战斗司书与追想魔女',
                     '序章 海边的哭喊',
                     '第一章 夜晚的邂逅',
                     '第二章 正义的传承',
                     '第三章 铅之心',
                     '第四章 追想的魔女',
                     '第五章 绝望的反叛',
                     '第六章 最后的誓言',
                     '断章 紫罗兰的余香',
                     '后记'],
                    ['第六卷 战斗司书与草绳公主',
                     '序章 公主的希望与热情',
                     '第一章 空之鲸与钟响中的怪物',
                     '第二章 少年与放弃',
                     '第三章 毫无理由的助人与杀人',
                     '第四章 老人的梦想与牺牲',
                     '第五章 郁黑蜥蜴与袋中穷鼠',
                     '第六章 光之花与洛萝缇的世界',
                     '断 章 乐园与继承者',
                     '后  记'],
                    ['第七卷 战斗司书与虚言者的宴会',
                     '序章 天国的骚动',
                     '第一章 虚伪的和平',
                     '第二章 叛乱的起始',
                     '第三章 暗中潜入里幕后黑影',
                     '第四章 魔刀之乱舞',
                     '第五章 虚言者的笑容',
                     '第六章 在屋顶上的畅所欲言',
                     '断章 男人里的名字叫露鲁塔',
                     '后记'],
                    ['第八卷 战斗司书与终章猛兽',
                     '序章 悲壮终结的开始',
                     '第一章 战败者的孤独苦斗',
                     '第二章 众多常识的崩坏',
                     '第三章 高傲奴隶的使命',
                     '第四章 欺骗者的末路',
                     '第五章 太阳下的绝望',
                     '断章 谜样的她的欲望',
                     '后记'],
                    ['第九卷 战斗司书与绝望魔王',
                     '序 章 魔王与昔日回忆',
                     '第一章 残兵败将与绝望魔王',
                     '第二章 战士与光之救世主',
                     '第三章 阴谋者与忧郁暴君',
                     '第四章 歌唱之人与某位少年',
                     '第五章 堇之少女与心爱的露鲁塔',
                     '断章 魔王与最终来访者',
                     '后记'],
                    ['第十卷 战斗司书与世界之力',
                     '序章 道具们的诀别',
                     '第一章 暗色的猛毒',
                     '第二章 无情魔王的报应',
                     '第三章 某观众的惋叹',
                     '第四章 美好的世界之光',
                     '第五章 武装司书的最终战役',
                     '第六章 爱的尽头',
                     '断章 于图书馆消失后的遗址',
                     '后记',
                     '祝完结'],
                    ['BD特典短篇', '摩卡尼亚与冷掉的牛奶咖啡']]}}
    txt2epub(test_data, '../data/wenku8')