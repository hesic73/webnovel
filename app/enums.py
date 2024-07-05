from enum import Enum


class Genre(Enum):
    玄幻 = "玄幻"
    奇幻 = "奇幻"
    武侠 = "武侠"
    仙侠 = "仙侠"
    都市 = "都市"
    现实 = "现实"
    历史 = "历史"
    军事 = "军事"
    游戏 = "游戏"
    体育 = "体育"
    科幻 = "科幻"
    悬疑 = "悬疑"
    轻小说 = "轻小说"
    短篇 = "短篇"
    诸天无限 = "诸天无限"


class UserType(Enum):
    COMMON = "common"
    ADMIN = "admin"
    
