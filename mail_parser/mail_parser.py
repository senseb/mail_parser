import os
import quopri
import re
import sys

from email import message_from_file
from email.utils import parseaddr
from email.header import decode_header, make_header
from lxml import etree
from six import StringIO
from pprint import pprint


def extract_mail(mail_file, key):
    mail_message = message_from_file(mail_file)
    header_decode = decode_mail_header(mail_message)
    message_decode = decode_mail_message(mail_message, key)
    # pprint(header_decode)
    # pprint(message_decode)
    return {**header_decode, **message_decode}


def decode_mail_message(mail_message, key):
    """
        Extracts content from an e-mail message.
        This works for multipart and nested multipart messages too.
        m -- email.Message() or mailbox.Message()
        key -- Initial message ID (some string)
        Returns {
            'text': _text, all text from all parts.
            'html': _html, all HTMLs from all parts
            'file': _files, dictionary mapping extracted file to message ID it belongs to.
            'part': _part, number of parts in original message.
        }
    """
    # Path to directory where attachments will be stored:
    # workdir = "./msgfiles"
    # abs_file_path = abs_file_path(work_dir, file_name)
    mail_content_total = {'text': '', 'html': '', 'file_list': {}, 'parts': 1}

    if not mail_message.is_multipart():
        if mail_message.get_filename():  # It's an attachment
            file_name = mail_message.get_filename()
            cfn = construct_name(key, file_name)
            mail_content_total['file_list'].update({file_name: (cfn, None)})
            if file_exists(cfn):
                return mail_content_total
            save_file(cfn, mail_message.get_payload(decode=True))
            return mail_content_total

        # Not an attachment!
        # See where this belongs. Text, Html or some other data:
        mail_message.set_charset('UTF-8')
        content_type = mail_message.get_content_type()
        if content_type == "text/plain":
            mail_content_total['text'] += mail_message.get_payload(decode=True)
        elif content_type == "text/html":
            # Html += m.get_payload(decode=True)
            # FIXME(SENSEB): fix the input encoding.
            mail_content_total['html'] += quopri.decodestring(mail_message.get_payload()).decode('utf-8')
        else:
            # Something else!
            # Extract a message ID and a file name if there is one:
            # This is some packed file and name is contained in content-type header
            # instead of content-disposition header explicitly
            content_type = mail_message.get("content-type")
            content_id = disgra(mail_message.get("content-id", ""))

            # FIXME(senseb): find file name, use regex to instead
            o = content_type.find("name=")
            if o == -1: 
                return mail_content_total
            ox = content_type.find(";", o)
            if ox == -1:
                ox = None
            o += 5
            file_name = content_type[o:ox]
            file_name = disqo(file_name)
            cfn = construct_name(key, file_name)
            mail_content_total['file_list'].update({file_name: (cfn, content_id)})
            if file_exists(cfn):
                return mail_content_total
            save_file(cfn, mail_message.get_payload(decode=True))
        return mail_content_total

    # This IS a multipart message.
    # So, we iterate over it and call decode_email_content() recursively for each part.
    y = 0
    while True:
        # If we cannot get the payload, it means we hit the end:
        try:
            pl = mail_message.get_payload(y)
            # pl = m.get_payload(y, decode=True)
        except:
            break
        # pl is a new Message object which goes back to decode_email_content
        email_contents_new = decode_mail_message(pl, key)
        mail_content_total['text'] += email_contents_new['text']
        mail_content_total['html'] += email_contents_new['html']
        mail_content_total['file_list'].update(email_contents_new['file_list'])
        mail_content_total['parts'] += email_contents_new['parts']
        y += 1
    return mail_content_total


def decode_mail_header_content(s):
    if s:
        return str(make_header(decode_header(s)))
    else:
        return ''


def decode_mail_header(origin):
    """Extracts: To, From, Subject and Date from email.Message() or mailbox.Message()
    origin -- Message() object
    Returns tuple(From, To, Subject, Date)
    If message doesn't contain one/more of them, the empty strings will be returned.
    """
    email_headers = dict()
    email_headers['date'] = origin.get('date', '')

    # FIXME(senseb): _from or _to is empty
    _from = origin.get('from', '')
    email_headers['from'] = decode_mail_header_content(parseaddr(_from)[0])

    _to = origin.get('to', '')
    email_headers['to'] = decode_mail_header_content(parseaddr(_to)[0])

    _subject = origin.get('subject', '')
    email_headers['subject'] = decode_mail_header_content(_subject)
    return email_headers


def get_html_from_email(content):
    # 将body中的内容给截取出来
    #content = re.findall(r'\<body([\s\S]*)\<\/body\>', content)[0]
    content = re.findall(r'<body([\s\S]*)</body>', content)[0]
    content = '<html><body' + content + '</body></html>'
    parser = etree.HTMLParser()
    return etree.parse(StringIO(content), parser=parser)


def get_link_from_html(html):
    return html.xpath('body/table[3]/tbody/tr[7]/td/text()')[0]


def get_detail_from_html(html):
    return html.xpath('body/table[3]/tbody/tr[4]/td/text()')[0]


def print_header():
    """张三 | 男 | 西安交通大学 | 硕士 | 2019年毕业"""
    print('| 姓名 | 性别 | 学校 | 学历 | 毕业时间 | 优势 | 初步沟通结论 | 优先级 |')
    print('| ---  | ---  | ---  | ---- | -------  | ---  | ---  | --- |')


def print_content(email_msg):
    html = get_html_from_email(email_msg['html'])
    link = get_link_from_html(html)
    detail = get_detail_from_html(html)
    name, gender, school, education, graduate_time = detail.split('|')
    pros, cons, rank = '', '', ''
    print('| [%s](%s) | %s | %s | %s | %s | %s | %s | %s |' % (
        name.strip(), link, gender, school, education, graduate_time, pros, cons, rank))


def process_eml(filename):
    with open(filename, "r", encoding="utf-8") as f:
        email_msg = extract_mail(f, f.name)
        print_content(email_msg)


def get_eml_list(dir_name):
    return [file_name for file_name in os.listdir(dir_name) if file_name.endswith('.eml')]


def abs_file_path(dir_path, file_name):
    return os.path.join(dir_path, file_name)


def file_exists(_abs_file_path):
    return os.path.exists(_abs_file_path)


def save_file(_abs_file_path, content):
    with open(_abs_file_path, "w", encoding="utf-8") as f:
        f.write(content)


def construct_name(id_src, fn):
    """Constructs a file name out of messages ID and packed file name"""
    ids = id_src.split(".")
    id_str = ids[0] + ids[1]
    return id_str + "." + fn


def disqo(s):
    """Removes double or single quotations."""
    s = s.strip()
    if s.startswith("'") and s.endswith("'"):
        return s[1:-1]
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    return s


def disgra(s):
    """Removes < and > from HTML-like tag or e-mail address or e-mail ID."""
    s = s.strip()
    if s.startswith("<") and s.endswith(">"):
        return s[1:-1]
    return s


if __name__ == '__main__':
    print_header()
    base_dir = '.'
    mails = get_eml_list(base_dir)
    for email in mails:
        try:
            process_eml(email)
        except TypeError:
            print('file[%s] process error' % email, file=sys.stderr)