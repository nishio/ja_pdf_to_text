# -*- encoding: utf-8 -*-
import re
import os
import subprocess
import argparse
import neologdn

PAGE_SEPARATOR = "\x0c"


def clean(data, ignore_newlines=True, ignore_cid=True,
          split_ligature=True, replace_punctuation=True):
    """
    >>> clean("ウェ~∼∾〜〰～イ")
    'ウェイ'
    >>> clean("aaa................1")
    'aaa 1'
    >>> clean("oﬃce")
    'office'
    """
    if isinstance(data, bytes):
        # UTF-8以外の文字を無視する
        data = data.decode('utf-8', 'ignore')

    data = neologdn.normalize(data)

    if ignore_newlines:
        # ハイフネーションを潰す
        data = re.sub('-[\r\n]+', '', data)
        # 改行を無視する
        data = re.sub('[\r\n]+', '', data)
    if ignore_cid:
        # CIDタグを無視する
        data = re.sub(r'\(cid:\d+\)', '', data)
    if split_ligature:
        # 合字を元に戻す
        data = data.replace(u'ﬃ', u'ffi')
        data = data.replace(u'ﬂ', u'fl')
        data = data.replace(u'ﬁ', u'fi')
        data = data.replace(u'ﬀ', u'ff')
    if replace_punctuation:
        # 約物などを空白に置き換える
        data = re.sub(r'\.\.\.+', ' ', data)
        data = re.sub('[•・、（）()「 」『 』｛ ｝［ ］〔 〕〈 〉《 》【 】〖 〗‥…゠]', ' ', data)

    return data


def get_pages(infile, outdir, to_output):
    _indir, filename = os.path.split(infile)
    outfile = os.path.join(outdir, filename).replace('.pdf', '.txt')
    if os.path.isfile(outfile):
        print('already exists')
        # continue
    subprocess.check_call(['pdf2txt.py', '-V', '-o', outfile, infile])
    data = open(outfile).read()
    pages = clean(data).split(PAGE_SEPARATOR)
    if to_output:
        lppfile = os.path.join(outdir, filename).replace('.pdf', '_lpp.txt')
        open(lppfile, "w").write("\n".join(pages))
    return pages


def _test():
    import doctest
    doctest.testmod()
    g = globals()
    for k in sorted(g):
        if k.startswith("TEST_"):
            doctest.run_docstring_examples(g[k], g, name=k)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--infile", help="input pdf file path",
        type=str)
    parser.add_argument(
        "--outdir", default=".", type=str)
    parser.add_argument(
        "--output-line-per-page", action="store_true",
        help="output line per page file (*.lpp)")
    parser.add_argument(
        "-t", "--test", help="test", action="store_true")
    args = parser.parse_args()
    print(args)
    if args.test:
        _test()

    if args.infile:
        pages = get_pages(args.infile, args.outdir, args.output_line_per_page)
