from pathlib import Path
import budou
import budoux

ML_FONT_PATH = str(Path(__file__).parent/"fonts/Pretendard-Regular.otf")
JA_FONT_PATH = str(Path(__file__).parent/"fonts/PretendardJP-Regular.otf")
ZH_FONT_PATH = str(Path(__file__).parent/"fonts/Alibaba-PuHuiTi-Medium.otf")

LINE_SPACING = 1

ROT_LANG = ["en"]
LTR_LANG = ["ko", "zh-CN", "zh-TW"]

LANG_REGEX = {
    "en": r"[a-zA-Z]+",
    "ko": r"[ㄱ-ㅎㅏ-ㅣ가-힣]+",
    "ja": r"[ぁ-ゔァ-ヴー々〆〤ｧ-ﾝﾞﾟ]+",
    "zh": r"[\u4e00-\u9fff]+",
    "zh-CN": r"[\u4e00-\u9fff]+",
    "zh-TW": r"[\u4e00-\u9fff]+",
}
SPECIAL_REGEX = r"[︵︶]+"

SCRIPTIO_DISCRETA = ["ko", "en", "uz", "tl", "th", "hi", "vi", "id"]
SCRIPTIO_CONTINUA = ["ja", "zh", "zh-CN", "zh-TW", "zhsg", "zhhk", "yue", "th", "hi", "ne", "km"]

MUST_PARSED = "・"

# Closing brackets + Chiisai kana and special marks + Delimiters + Mid-sentence punctuation +
    # Sentence-ending punctuation + etc.
JA_NOT_PERMIT_START = """)\]｝〕〉》」』】〙〗〟'"｠""" +\
    "ヽヾーァィゥェォッャュョヮヵヶぁぃぅぇぉっゃゅょゎゕゖㇰㇱㇲㇳㇴㇵㇶㇷㇸㇹㇺㇻㇼㇽㇾㇿ々〻‐゠–〜" +\
    "？!‼⁇⁈⁉" +\
    "・、:;," +\
    "。." +\
    "}】）?！`"
JA_NOT_PERMIT_END = """(\[｛〔〈《「『【〘〖〝'"｟«""" + "{【（`" # Opening brackets + etc.

ZHCN_NOT_PERMIT_START = """!%),，.:;?]}¢°·'"†‡›℃∶、。〃〆〕〗〞﹚﹜！＂％＇）．：；？！］｝～・"""
ZHCN_NOT_PERMIT_END = """$(£¥·'"〈《「『【〔〖〝﹙﹛＄（．［｛￡￥"""

ZHTW_NOT_PERMIT_START = """!),，.:;?]}¢·–— '"• 、。〆〞〕〉》」︰︱︲︳﹐﹑﹒､・"""
ZHTW_NOT_PERMIT_END = """([{£¥'"‵〈《「『〔〝︴﹙﹛（｛︵︷︹︻︽︿﹁﹃﹏"""

JA_PARSER = budou.get_parser("mecab")
ZHCN_PARSER = budoux.load_default_simplified_chinese_parser()
ZHTW_PARSER = budoux.load_default_traditional_chinese_parser()
