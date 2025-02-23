import json
import random
from pprint import pp
import re


# https://ecampusontario.pressbooks.pub/essentialsoflinguistics/chapter/2-5-ipa-symbols-and-speech-sounds/
# alphabet = set("pbtdkɡfvθðszʃʒhtʃdʒmnŋlɹjwɾiɪeɛæauʊoʌɔɑəɨɚɝaɪaʊɔɪju")
# https://www.ipachart.com/
alphabet = set(
        "iyɨʉɯuɪʏʊeøɘɵɤoəɛœɜɞʌɔæɐaɶɑɒpbtdʈɖcɟkgqɢʔmɱnɳɲŋɴʙrʀⱱɾɽɸβfvθðszʃʒʂʐçʝxɣχʁħʕhɦɬɮʋɹɻjɰlɭʎʟʘɓpǀɗtǃʄkǂɠsǁʛʍwɥʜʢʡɕʑɺɧʃxt͡st͡ʃt͡ɕʈ͡ʂd͡zd͡ʒd͡ʑɖ͡ʐ")

# https://ipa.typeit.org/
# ??: https://www.vocabulary.com/resources/ipa-pronunciation/
# ??
alphabet |= set("ʃθʊʊ̈ʌʒʔæɑðəɚɛɜɝɪɪ̈ɫŋɔɒɹɾpbtdkgmndfvszhwjrlieuoxɡ")


def simplify_ipa(w):
    w = w[1:-1] # remove the /

    acc = ""

    # this will ignore all the modifiers,
    # make optional sounds optional,
    # remove pauses, etc
    for c in w:
        # is this the tie mark?
        if c in alphabet and c != "\u0361":
            acc += c
    return acc

no_sound_count = 0
no_ipa_count = 0

def get_relevant_info(l):
    global no_ipa_count, no_sound_count
    d = json.loads(l)

    if d["word"][0].isupper() \
            or d["word"].startswith("-") \
            or d["word"].endswith("-"):
        return None

    if "sounds" not in d:
        no_sound_count += 1
        return None

    ipa = None
    for sound in d["sounds"]:
        if "ipa" not in sound:
            continue

        if ipa is None:
            ipa = sound["ipa"]

        if "tags" in sound and sound["ipa"].startswith("/") and "US" in sound["tags"]:
            break
    
    if ipa is None:
        no_ipa_count += 1
        return None

    gloss = []
    for sense in d["senses"]:
        if "glosses" not in sense:
            continue
        gloss += sense["glosses"]

    return (simplify_ipa(ipa), (d["word"], ipa, gloss))


acc = {}
counter = 0
with open("engl-dict.jsonl") as f:
    l = f.readline()
    while l and counter < 1000:
        if (t := get_relevant_info(l)) is not None and " " not in t[1][1]:
            simple, (word, true, senses) = t
            if simple not in acc:
                acc[simple] = (word, true, senses)
            else:
                acc[simple][2].extend(senses)
        l = f.readline()
        # counter += 1

buckets = {}

for a, b in acc.items():
    for l in a:
        if l not in buckets:
            buckets[l] = 0
        buckets[l] += 1

for a, b in buckets.items():
    print(a, b)

print(len(acc))

games = {}
for _ in range(15):
    while True:
        alph2 = list(buckets.keys())
        freqs = list(buckets.values())
        for i in range(len(freqs)):
            freqs[i] = int(freqs[i] ** 0.5)

        letters = set()
        for i in range(7):
            t = random.choices(alph2, weights=freqs)[0]
            letters.add(t)
            i2 = alph2.index(t)
            del alph2[i2]
            del freqs[i2]

        t = list(letters)
        random.shuffle(t)


        res = []
        word_sets = []
        for a, b in acc.items():
            if len(a) >= 4 and t[0] in a and set(a) <= letters:
                res.append((a, b))
                word_sets.append(set(a))

        # check for panagram as well
        if len(res) > 14 and set(letters) in word_sets:
            games["".join(t)] = dict(res)
            break



with open("games.json", "w") as f:
    f.write(json.dumps(games, indent=2))

