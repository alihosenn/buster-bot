#===istalismanplugin===
# -*- coding: utf-8 -*-

import urllib2,re,urllib,socket

from re import compile as re_compile

strip_tags = re_compile(r'<[^<>]+>')

ALIAS_URL_FILE = 'dynamic/alias_url.txt'

db_file(ALIAS_URL_FILE, dict)

try: ALIAS_URL = eval(read_file(ALIAS_URL_FILE))
except: ALIAS_URL = {}

SOUND_LYRICS = {}

def hnd_sound_lyrics(t, s, p):
        global SOUND_LYRICS
        fn = inspect.stack()[0][3]
        jid = get_true_jid(s)
        if jid in SOUND_LYRICS and p.isdigit():
                try: reply(t, s, send_urlopen_q("http://webkind.ru/text/"+SOUND_LYRICS[jid][int(p)-1][0],1))
                except: reply(t, s, u'Что-то пошло не так')
                return
        
        n = 0
        rep = ''
        p=p.replace(' ','+')
        url = 'http://webkind.ru/search?q='+p.encode('utf8')
        page = urllib.urlopen(url).read()
        page = re.findall(r'<a href=\"http://webkind.ru/text/(.*?)\">(.*)</a>', page)
        for x in page:
                n+=1
                try: rep+=str(n)+') '+x[1]+'\n'
                except: pass
        SOUND_LYRICS[jid]=page
        DIGIT_MENU[jid]=fn
        reply(t, s, decode(rep))
        
def hnd_sound_lyrics2(t, s, p):
        jid = get_true_jid(s)
        #global SOUND_LYRICS
        if not p:
                reply(t, s, u'А что искать?')
                return
        p=p.replace(' ','+')
        p=p.encode('utf8','replace')
        url = 'http://wapsound.ru/texts/search.php?search='+p
        page = send_urlopen_q(url)
        
        if not page.count('/texts/read.php?text_id='):
                reply(t, s, u'Не нашел')
                return
        z = re.findall('text_id=(.*?)">', page, re.DOTALL|re.IGNORECASE)
        if not z: return
        z = z[0]
        url = 'http://wapsound.ru/texts/read.php?text_id='+z
        page = send_urlopen_q(url,1)
        reply(t, s, page.split(u'Скачать')[0])

register_command_handler(hnd_sound_lyrics, 'текст песни', ['все'], 0, 'показывает текст песни по названию', 'текст песни название', ['текст песни они летят'])                                        
register_command_handler(hnd_sound_lyrics2, 'текст песни+', ['все'], 0, 'показывает текст песни по названию', 'текст песни название', ['текст песни они летят'])                                        


def hnd_alias_url(t, s, p):
        if not s[1] in GROUPCHATS: return
        if not p:
                if not s[1] in ALIAS_URL.keys():
                        reply(t, s, u'Нет алиасов')
                        return
                reply(t, s, '\n'.join([str(ALIAS_URL[s[1]].keys().index(x)+1)+') '+x+' - '+ALIAS_URL[s[1]][x] for x in ALIAS_URL[s[1]].keys()]))
                return
        if p.isdigit():
                for x in ALIAS_URL[s[1]]:
                        if str(ALIAS_URL[s[1]].keys().index(x)+1) == p:
                                del ALIAS_URL[s[1]][x]
                                write_file(ALIAS_URL_FILE, str(ALIAS_URL))
                                reply(t, s, u'Удалил!')
                                return
                reply(t, s, u'Алиаса с таким номером нет в списке!')
                return
        if not p.count(' '):
                reply(t, s, u'Синтаксис - <команда> <url>')
                return
        ss = p.split()
        if ss[0].lower() in COMMANDS.keys():
                reply(t, s, u'Недопустимое имя алиаса!')
                return
        
        if not s[1] in ALIAS_URL.keys():
                ALIAS_URL[s[1]]={}
                
        ALIAS_URL[s[1]][ss[0].lower()]=ss[1]
        reply(t, s, u'Добавил!')
        write_file(ALIAS_URL_FILE, str(ALIAS_URL))

#register_command_handler(hnd_alias_url, 'alias_url', ['все'], 20, 'Просмотр сайтов и цитатников с помощью алиасов. Без параметров покажет список алиасов. Чтобы удалить алиас используем номер алиаса в списке. В строке url есть следующие переменные - $p -текст, $qot - параметры в виде %D0%BF%D0%B8%D0%B2%D0%BE, $n1 - рандомное число 0-10, $n2 число от 10-100 ну и $n3 до 1000', 'alias_url <command> <url>', ['poem'])                                        

def hnd_msg_alias_url(r, t, s, p):
        if not s[1] in ALIAS_URL.keys(): return
        pr = p.lower()
        pt = ''
        qot = ''
        if p.count(' '):
                ss = p.split()
                pr = ss[0].lower()
                try: pt = ss[1]
                except: pass
        if pr in ALIAS_URL[s[1]]:
                exc = ALIAS_URL[s[1]][pr].encode('utf8')
                if not pt.isdigit():
                        pt = pt.encode('utf8','replace')
                if pt:
                        qot = urllib.quote(pt)
                        
                exc = exc.replace('$p', pt)
                exc = exc.replace('$qot', qot)
                exc = exc.replace('$n1',str(random.randrange(0,10))).replace('$n2',str(random.randrange(10,100))).replace('$n3',str(random.randrange(100,1000)))
                reply(t, s, send_urlopen_q(exc,1))

register_message_handler(hnd_msg_alias_url)

def send_urlopen_q(url, i=0):
        req = urllib2.Request(url)
        req.add_header('User-Agent','Mozilla/5.0 (Linux; U; Android 2.2.1; sv-se; HTC Wildfire Build/FRG83D) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1')
	try:
                req = urllib2.urlopen(req, timeout = 3)
                enc = req.headers.getparam('charset')
                req = req.read()
                if not enc:
                        enc = re.findall('charset=(.*?)\">', req, re.DOTALL | re.IGNORECASE)
                        if enc:
                                enc = enc[0]
                        else: return u'Невозможно определить кодировку'
                rep = req.decode(enc, 'replace')
                if i: return universal_html_parser(rep)
                return rep
	except urllib2.URLError, e:
                if hasattr(e, 'reason') and isinstance(e.reason, socket.timeout): return u'Время ожидания вышло'
                elif hasattr(e, 'code'): return e.code     
                else: return u'Сайт упал'
        except Exception as err: return err.message
        return str()
        

def remove_trash(body):
        body = re.compile(r'<style[^<>]*?>.*?</style>',re.DOTALL | re.IGNORECASE).sub('', body)
        body = re.compile(r'<script.*?>.*?</script>',re.DOTALL | re.IGNORECASE).sub('', body)
        body = re.compile(r'<!--.*?-->',re.DOTALL | re.IGNORECASE).sub('', body)
        body = re.compile(r'&#.*?;',re.DOTALL | re.IGNORECASE).sub('', body)
        return body


def remove_space(body):
        if body.count('\n'):
                body = '\n'.join([x for x in body.split('\n') if not x.isspace() and len((x if not x.count(' ') else ''.join(x.split(' '))))>1])
        if body.count(chr(9)):
                body = body.replace(chr(9),'')
        last = 0
        try: body = ' '.join([x for x in body.split(' ') if x!=''])
        except: pass
        return body

def remove_link(body):
        body = re.compile(r'<a href=\".*?>.*?</a>',re.DOTALL | re.IGNORECASE).sub('', body)
        return body

def universal_html_parser(body):
        if not isinstance(body, basestring):
                return 'Object has not atrr string'
        return remove_space(decode_s(remove_link(remove_trash(body))))

def handler_bashorgru_get(type, source, parameters):
	if parameters.strip()=='':
		req = urllib2.Request('http://bash.im/random')
	else:
		req = urllib2.Request('http://bash.im/quote/'+parameters.strip())
	req.add_header('User-Agent','Mozilla/5.0 (Linux; U; Android 2.2.1; sv-se; HTC Wildfire Build/FRG83D) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1')
	try:
		r = urllib2.urlopen(req)
		target = r.read()
		target = re.compile(r'<script.*?>.*?</script>',re.DOTALL | re.IGNORECASE).sub('', target)
		"""link to the quote"""
		try: id = re.findall('<a href=\"/quote/(.*?)\" class=\"id\">#(.*?)</a>', target)[0][0]
		except: id = ''
		msg = random.choice(re.findall('<div class=\"text\">(.*?)</div>', target))
		msg = msg.replace('<br />','\n').replace('&quot;','\"').replace('&gt;',':').replace('<br>','\n')
		msg = decode_s(msg)
		reply(type,source,unicode(('#'+id+':\n' if id else '')+msg,'windows-1251'))
	except:
		reply(type,source,u'очевидно, они опять сменили разметку')
            

def decode_s(text):
    return strip_tags.sub('', text.replace('<br/>','\n').replace('<br />','\n').replace('&middot;','').replace('<br>','\n')).replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('\t','').replace('||||:]','').replace('>[:\n','')

def decode(text):
    return strip_tags.sub('', text.replace('<br/>','\n').replace('<br />','\n').replace('&middot;','').replace('<br>','\n')).replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('\t','').replace('||||:]','').replace('>[:\n','')


BEAF = {'last':0,'n':0}

def hnd_beaf(t, s, p):
        global BEAF
        #http://beafraid.ru/story/711/
        st = (711, 8906)
        page = send_urlopen_q('http://beafraid.ru/story/'+str(random.randrange(st[0],st[1])))
        vn = page
        try:
                title = re.findall('<title>(.*?)</title>', page, re.DOTALL | re.IGNORECASE)
        except:
                if time.time()-BEAF['last']<5:
                        BEAF['n']+=1
                        BEAF['last']=time.time()
                        if BEAF['n']<10:
                                hnd_beaf(t, s, p)
                else:
                        hnd_beaf(t, s, p)
                        BEAF['n'] = 0
                        BEAF['last']=time.time()
                return
        if title:
                title = title[0]
        else:
                title = str()
        page = re.findall('<p>.*?</p>', page, re.DOTALL | re.IGNORECASE)
        if page:
                page = '\n'.join(page)
                page = re.sub('<[^>]*>(.*?)</span>','',page)
                page = universal_html_parser(page)
                if page.isspace():
                        reply(t, s, u'Сервис отправил пустую страницу')
                        return
                reply(t, s, title+'\n'+page)
        else:
                reply(t, s, u'Не судьба')

register_command_handler(hnd_beaf, 'страш', ['все'], 0, 'beafraid.ru — сборник. Здесь собраны страшные истории из реальной жизни.', 'страш', ['страш'])                                              

        
def handler_celebration(type, source, parameters):
        try:
                rss = feedparser.parse('http://www.calend.ru/img/export/calend.rss')
                list = [(x.title,x.summary) for x in rss.entries]
                if parameters.isdigit() and len(list)>=int(parameters):
                        reply(type, source, list[int(parameters)-1][0]+'\n'+list[int(parameters)-1][1])
                        return
                rep = str()
                for x in list:
                        rep+=str(list.index(x)+1)+'. '+x[0]+'\n'
                reply(type, source, rep+u'\nКраткое описание - праздник <номер>\nИсточник calend.ru')
        except: reply(type, source, u'Что-то сломалось!')

def hnd_today_events(type, source, parameters):
        try:
                if parameters and not parameters.isdigit():
                        return
                rss = feedparser.parse('http://www.calend.ru/img/export/today-events.rss')
                list = [(x.title,x.summary) for x in rss.entries]
                if parameters.isdigit() and len(list)>=int(parameters):
                        reply(type, source, list[int(parameters)-1][0]+'\n'+list[int(parameters)-1][1])
                        return
                rep = str()
                for x in list:
                        rep+=str(list.index(x)+1)+'. '+x[0]+'\n'
                reply(type, source, rep+u'\nКраткое описание - сегодня <номер>\nИсточник calend.ru')
        except: reply(type, source, u'Что-то сломалось!')

register_command_handler(hnd_today_events, 'сегодня', ['все','mod','инфо'], 0, 'Памятные события сегодня http://www.calend.ru/', 'сегодня', ['сегодня'])

def handler_jc_show(type, source, parameters):
        if not parameters: return
        try:
                req = urllib2.Request('http://jc.jabber.ru/search.html?search='+parameters.encode('utf-8'))
                req.add_header('User-Agent','Mozilla/5.0 (Linux; U; Android 2.2.1; sv-se; HTC Wildfire Build/FRG83D) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1')
                req = urllib2.urlopen(req).read()
                rep = re.findall('<div>(.*?)</div>', req, re.DOTALL | re.IGNORECASE)[0]
                rep = remove_space(decode_s(rep))
                reply(type, source, rep)
        except: reply(type, source, send_urlopen_q('http://jc.jabber.ru/search.html?search='+parameters.encode('utf-8'), 1))


def handler_lurk(type, source, parameters):
        try:
                if parameters:
                        req = urllib2.Request('http://lurkmore.to/'+parameters.encode('utf-8'))
                        req.add_header = ('User-agent', 'Opera')
                        i = urllib2.urlopen(req)
                        page = i.read()
                        target=''
                        t = re.findall('<p>.*.',page,re.DOTALL | re.IGNORECASE)
                        for x in t:
                                x=x.replace('</p>','\n')
                                if not x.count('.') and not x.isspace():
                                        if x!='':
                                                x+'.'
                                target+=x
                        target = remove_trash(target)
                        target = remove_space(decode_s(target))
                        if target.count('См. также'):
                                target = 'См. также\n'.join(target.split('См. также')[:-1])
                        if target.isspace():
                                reply(type, source, u'аблом!')
                                return
                        reply(type, source, target)
                else:
                        reply(type, source, u'лурк - это тема,только слово еще напиши!')
                        return
        except:
                reply(type, source, u'Ничего не найдено!')

def handler_anek_s(type,source,parameters):
        reklama = [u'']
        try:
                u = urllib.urlopen('http://anekdot.odessa.ua/rand-anekdot.php')
                target = u.read()
                od = re.search('>',target)
                h1 = target[od.end():]
                h1 = h1[:re.search('<a href=',h1).start()]
                message = decode_s(h1)
                reply(type ,source, u'Анекдот: \n'+unicode(message,'windows-1251'))
        except:
                reply(type ,source, u'Упс.. Сайт упал..')

def clck_quest(type,source,parameters):
        if parameters:
                try:
                        fetcher = urllib2.urlopen('http://clck.ru/--?url='+parameters.encode('utf-8'))
                        rep=fetcher.read()
                        reply(type,source,rep)
                except:
                        reply(type,source,'что-то сломалось!')
                        pass

def dublicates(p):
        def upper_repl(match):
                return match.group(1).upper()
        def ggl(p):
                sp=p.split('\n')
                for x in sp:
                        cp=x.split(',')
                        if len(cp)>=4:
                                p=p.replace(cp[1]+',', cp[1]+',\n')
                return p
                                
        p='.'.join([x for x in p.split('.') if x.strip()!='.'])
        #p=p.replace(u'.','.\n').replace('\n\n','')
        #p = re.sub(r'[.]([^.!?])', r'.\n\1', p)
        p = re.sub(r'([.!?])([^.!?])', r'\1\n\2', p)
        p=re.sub(r'([.]\s{1,3}.)+', upper_repl, p)
        p=re.sub(r'([?]\s{1,3}.)+', upper_repl, p)
        p=re.sub(r'([!]\s{1,3}.)+', upper_repl, p)
        p=re.sub(r'(^\s{0,3}.)+', upper_repl, p)
        p=ggl(p)
        p=re.sub(r'(.)\1+', r'\1\1', p)
        p=re.sub(r'\s{3,}', '', p)
        
        return p
                
def hnd_lust_ru(type,source,parameters):
        try:
                rep = send_urlopen_q('http://www.notproud.ru/random.html', 1)
                sp = re.findall('\d{1,2}:\d{1,2}', rep, re.DOTALL | re.IGNORECASE)
                data = re.findall('\d.*?:\d{1,2}', rep, re.DOTALL | re.IGNORECASE)
                if sp:
                        sp = sp[0]
                        #rep = rep.split(sp)[1]
                        #rep = rep.replace(u'.','.\n').replace('\n\n','')
                        rep = re.findall(sp+u'(.*?)читать дальше', rep, re.DOTALL | re.IGNORECASE)
                        if rep:
                                rep=rep[0]
                        
                else:
                        reply(type, source, u'Ups!, someone is doing wrong!')
                        return
                ###reply(type, source, rep)
                reply(type, source, data[0]+'\n'+dublicates(rep))
        except:
                raise
                reply(type,source,u'Что-то сломалось!')

def hnd_drem_talk(type,source,parameters):
        try:
                if not parameters: return

                try: z = urllib.urlopen('http://wap.horo.infan.ru/dreams/'+parameters.encode('utf8','replace')).read()
                except: z = ''
                page = re.findall('</b><br/>(.*?)Haзaд</a>',z)
                nex = re.findall('<a href=\"\.\/\?B=(\d{1,5})\">дaлee...</a>',z)
                if not page:
                        page = ['']
                page = page[0]
                page = page.replace('дaлee...','').replace('&#171;','')
                page = remove_space(decode(page))
                page = page.rpartition('.')[0]
                page = page+'.\n'
                
                reply(type, source, page)
                dream_talk(type, source, parameters)
                
        except:
                dream_talk(type, source, parameters)
                

def dream_talk(t, s, p):
        if p.count(' '):
                p = p.replace(' ','+')

        rep = send_urlopen_q('http://2yxa.ru/pics/sonnik.php?poisk='+urllib.quote(p.encode('utf8')),1)
        
        reply(t, s, rep)
                

def hnd_darvin_p(type,source,parameters):
        try:
                num = str(random.randrange(1,700))
                rep = send_urlopen_q('http://2yxa.ru/darwin/?st='+num.encode('utf-8'), 1)
                reply(type,source,rep)
        except: reply(type, source, u'Что-то сломалось!')

def kill_me_quotes(type, source, parameters):
        try:
                num = str(random.randrange(1, 7400))
                if parameters and parameters.isdigit():
                        num = parameters
                rep = send_urlopen_q('http://killmepls.ru/story/'+num, 0)
                rep = re.findall('\d{1,2}:\d{1,2}:\d{1,2}.*?\(\-\)', rep, re.DOTALL | re.IGNORECASE)
                #rep = rep.replace(u'•  • Пишите нам:  • 18+','')
                #rep = re.sub('([Да ну, фигня].*?$)+','',rep)
                if rep:
                        rep=rep[0]
                        rep=universal_html_parser(rep)
                reply(type, source, (rep if rep else u'It\'s doesnt work'))
        except:
                reply(type, source, u'Что-то сломалось!')

def hnd_poem(type, source, parameters):
        a=[u"Я помню",u"Не помню",u"Забыть бы",u"Купите",u"Очкуеш",u"Какое",u"Угробил",u"Хреново",u"Открою",u"Ты чуешь?"]
        b=[u"чудное",u"странное",u"некое",u"вкусное",u"пьяное",u"свинское",u"чоткое",u"сраное",u"нужное",u"конское"]
        c=[u"мнгновенье",u"затменье",u"хотенье",u"варенье",u"творенье",u"везенье",u"рожденье",u"смущенье",u"печенье",u"ученье"]
        d=[u"передомной",u"под косячком",u"на кладбище",u"в моих мечтах",u"под скальпилем",u"в моих штанах",u"из-за угла",u"в моих ушах",u"в ночном горшке",u"из головы"]
        e=[u"явилась ты",u"добилась ты",u"торчат кресты",u"стихов листы",u"забилась ты",u"мои трусы",u"поют дрозды",u"из темноты",u"помылась ты",u"дают пизды"]
        f=u'как'
        g=[u"мимолётное",u"детородное",u"психотропное",u"кайфоломное",u"очевидное",u"у воробушков",u"эдакое вот",u"нам не чуждое",u"благородное",u"ябывдульское"]
        j=[u"виденье",u"сиденье",u"паренье",u"сужденье",u"вращенье",u"сношенье",u"смятенье",u"теченье",u"паденье",u"сплетенье"]
        h=[u"как гений",u"как сторож",u"как символ",u"как спарта",u"как правда",u"как ангел",u"как водка",u"как пиво","как ахтунг",u"как жопа"]
        i=[u"чистой",u"вечной",u"тухлой",u"просит",u"грязной",u"липкой",u"на хрен",u"в пене",u"женской",u"жаждет"]
        k=[u"красоты",u"мерзлоты",u"суеты",u"наркоты",u"срамоты",u"школоты",u"типа ты",u"простоты",u"хуиты",u"наготы"]
        reply(type, source, random.choice(a)+'\n'+random.choice(b)+'\n'+random.choice(c)+'\n'+random.choice(d)+'\n'+random.choice(e)+'\n'+f+' '+random.choice(g)+'\n'+random.choice(j)+'\n'+random.choice(h)+'\n'+random.choice(i)+'\n'+random.choice(k))

register_command_handler(hnd_poem, 'poem', ['все'], 0, 'random poem', 'poem', ['poem'])                                        
register_command_handler(kill_me_quotes, 'killme', ['все'], 0, 'Кажется, что жизнь повернулась спиной? Поверьте, бывает и хуже... http://killmepls.ru/', 'killme', ['killme'])                                        
register_command_handler(hnd_darvin_p, 'дарвин', ['все'], 0, 'премия дарвина', 'дарвин', ['дарвин'])                                        
register_command_handler(hnd_drem_talk, 'сон', ['все'], 0, 'толкование сна по ключевому слову', 'сон <слово>', ['сон деньги'])                                
register_command_handler(hnd_lust_ru, 'признание', ['фан','все'], 0, 'признание с http://www.notproud.ru/lust/', 'признание', ['признание'])                
register_command_handler(clck_quest, 'clck', ['все'], 0, 'Выдает короткую ссылку взамен введенного URL', 'clck <url>', ['clck http://40tman.ucoz.ru'])
register_command_handler(handler_anek_s, 'анекдот', ['фан','все'], 0, 'Случайный анекдот из http://wap.obas.ru/', 'анекдот', ['анекдот'])
register_command_handler(handler_lurk, 'лурк', ['инфо','фан','все'], 0, 'Показывает статью из http://lurkmore.ru/','лурк <слово>', ['лурк херка'])
register_command_handler(handler_jc_show, 'jc', ['все','mod','инфо'], 0, 'Поиск конференций в рейтинге jc.jabber.ru', 'jc <конфа>', ['jc goth'])
register_command_handler(handler_jc_show, 'рейтинг', ['все','mod','инфо'], 0, 'Поиск конференций в рейтинге jc.jabber.ru', 'рейтинг <конфа>', ['рейтинг goth'])
register_command_handler(handler_celebration, 'праздники', ['все','mod','инфо'], 0, 'Показывает праздники сегодня/завтра с http://www.calend.ru/', 'праздники', ['праздники'])
register_command_handler(handler_bashorgru_get, 'бор', ['фан','инфо','все'], 0, 'Показывает случайную цитату из бора (bash.org.ru). Также может по заданному номеру вывести.', 'бор', ['бор 223344','бор'])
