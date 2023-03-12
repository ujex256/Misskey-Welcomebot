# NGワードのひらがな用ファイルの生成
from pykakasi import kakasi


def toKakashi(text):
    k = kakasi()
    return k.convert(text)


def toHira(text):
    k = toKakashi(text)
    if isinstance(k, list):
        result = [i["hira"] for i in k]
    else:
        result = k["hira"]
    return "".join(result)

def toKana(text):
    k = toKakashi(text)
    if isinstance(k, list):
        result = [i["kana"] for i in k]
    else:
        result = k["kana"]
    return "".join(result)

def toRomaji(text) -> list:
    k = toKakashi(text)
    if isinstance(k, list):
        result = [i["hepburn"] for i in k]
        result2 = [i["kunrei"] for i in k]
        if "".join(result) == "".join(result2):
            return ["".join(result)]
    else:
        if k["hepburn"] == k["kunrei"]:
            return [k["hepburn"]]
        else:
            result = k["hepburn"]
            result2 = k["kunrei"]
    return ["".join(result), "".join(result2)]

if __name__ == "__main__":
    try:
        f = open("../ngwords.txt", "r", encoding="utf8")
    except FileNotFoundError:
        f = open("./ngwords.txt", "r", encoding="utf8")
    _words = f.read()
    f.close()

    words = [i for i in _words.split("\n") if i[0] != "#"]

    a = ["Hira", "Kana"]
    functions = {"Hira": toHira, "Kana": toKana, "Romaji": toRomaji}

    # なんかかっこいい(?)
    for mode in a:
        data = map(lambda x: x + "\n", [functions[mode](word) for word in words])
        data = list(filter(lambda x: not (x.isascii() or x[:-1] in words), data))
        data[-1] = data[-1][:-1]
        with open(f"ngWords_{mode}.txt", "w", encoding="utf8") as f:
            f.writelines(data)

    with open("ngWords_Romaji.txt", "w", encoding="utf8") as f:
        data = map(lambda x: x + "\n", ["\n".join(toRomaji(word)) for word in words])
        romaji = []
        for i in data:
            if (i not in romaji) and (i != "") and (not i in words):
                romaji.append(i)
        romaji[-1] = romaji[-1][:-1]
        f.writelines(romaji)
