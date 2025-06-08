from enum import Enum

class Priorities(str, Enum):
    NEUTRAL = "neutral"
    IMPORTANT = "important"
    VITAL = "vital"

class GeneralType(str, Enum):
    SOCIAL = "Social"
    EDUCATION = "Education"
    GAMES = "Games"
    NEUTRAL = "Neutral"

class AppType(str, Enum):
    PRODUCTIVITY = "Productivity"
    SHOPPING = "Shopping"
    FOOD_DRINKS = "Food_Drinks"
    BOOKS_REFERENCES = "Books_References"
    LIFESTYLE = "Lifestyle"
    ENTERTAINMENT = "Entertainment"
    TOOLS = "Tools"
    BUSINESS = "Business"
    MUSIC_AUDIO = "Music_Audio"
    EDUCATION = "Education"
    SOCIAL = "Social"
    GAMES = "Games"
    NEWS_MAGAZINES = "News_Magazines"
    TRAVEL_LOCAL = "Travel_Local"

class AppRequestStatuses(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ERROR = "error"

class Genders(str, Enum):
    FEMALE = "female"
    MALE = "male"

class Shifts(str, Enum):
    MORNING = "morning"
    EVENING = "evening"

class OsTypes(str, Enum):
    IOS = "ios"
    ANDROID = "android"
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    CHROMEOS = "chromeos"

class AndroidUI(str, Enum):
    STOCK = "Stock"
    ONEUI = "OneUI"
    MIUI = "MIUI"
    MAGICOS = "MagicOS"
    HARMONYOS = "HarmonyOS"
    COLOROS = "ColorOS"
    OXYGENOS = "OxygenOS"
    HYPEROS = "HyperOS"
    REALMEUI = "RealmeUI"

class PhoneBrands(str, Enum):
    SAMSUNG = "samsung"
    APPLE = "apple"
    XIAOMI = "xiaomi"
    VIVO = "vivo"
    OPPO = "oppo"
    REALME = "realme"
    ASUS = "asus"
    NOKIA = "nokia"
    ARTEL = "artel"
    GOOGLE = "google"
    ONEPLUS = "oneplus"
    NOTHING = "nothing"
    MOTOROLA = "motorola"
    REDMI = "redmi"
    POCO = "poco"
    HUAWEI = "huawei"
    HONOR = "honor"
    TECNO = "tecno"

class ActionDegrees(str, Enum):
    NEUTRAL = "neutral"
    SUSPICIOUS = "suspicious"
    TERRIBLE = "terrible"

class Languages(str, Enum):
    UZB_LAT = "uzb_lat"
    UZB_CYR = "uzb_cyr"
    RUSSIAN = "russian"
    ENGLISH = "english"

class Themes(str, Enum):
    DARK = "dark"
    LIGHT = "light"
    W_LIGHT = "w_light"
    W_DARK = "w_dark"
