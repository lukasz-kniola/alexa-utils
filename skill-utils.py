import json

class Map(dict):
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]


class Slot(Map):
    def __init__(self, intentSlot):
        self.name = resolve(intentSlot,['name'])
        self.value = resolve(intentSlot,['value'])
        self.code = resolve(intentSlot,['resolutions'],['resolutionsPerAuthority'],[0],['values'],[0],['value'],['name'])
        self.id = resolve(intentSlot,['resolutions'],['resolutionsPerAuthority'],[0],['values'],[0],['value'],['id'])

    def __repr__(self):
        if self.code is not None:
            return self.code
        elif self.value is not None:
            return self.value
        else:
            return '-'


def resolve(*path):
    cur = path[0]
    for i in range(1,len(path)):
        if path[i] == [0]:
            if isinstance(cur,list):
                cur = cur[0]
            else:
                return None
        else:
            if path[i][0] in cur:
                cur = cur[path[i][0]]
            else:
                return None
    return cur


class Request():
    def __init__(self, event):
        self.newSession = event['session']['new']
        self.uid = event['session']['user']['userId']
        self.type = event['request']['type']
        self.timestamp = event['request']['timestamp']
        self.locale = event['request']['locale']
        self.intent = resolve(event,['request'],['intent'],['name'])
        self.slots = Map()
        slots = resolve(event,['request'],['intent'],['slots'])
        if isinstance(slots, dict):
            print("SLOTS:")
            for k,v in slots.items():
                self.slots[k] = Slot(v)
            print(self.slots)
        else:
            print("No SLOTS present.")

    def __repr__(self):
        r = ""
        r += "type:      " + self.type + "\n"
        r += "intent:    " + (self.intent if self.intent is not None else '_') + "\n"
        r += "timestamp: " + self.timestamp + "\n"
        r += "locale:    " + self.locale + "\n"
        r += "slots:    \n"
        for k,v in self.slots.items():
            r+=('  '+k+'\n')
            for par in ['name','value','code','id']:
                try:
                    r+=('    '+par+': ' + self.slots[k][par]+"\n")
                except:
                    r+=('    - \n')
        return r

    def isType(self, type):
        return self.type == type

    def isIntent(self, intent):
        return self.intent == intent

class Response():

    def __init__(self,event):
        self.uid = event['session']['user']['userId']
        self.loc = event['request']['locale']
        self.att = Map()
        self.atts_read(resolve(event,['session'],['attributes']))
        self.txt = ""
        self.rpt = ""
        self.crd = ""
        self.end = False

    def txt_clr(self):
        self.txt = ""
        return self

    def txt_set(self, text):
        self.txt = text
        return self

    def txt_add(self, text):
        self.txt = self.txt + " " + text
        return self

    def rpt_set(self, text):
        self.rpt = text
        return self

    def rpt_add(self, text):
        self.rpt = self.rpt + " " + text
        return self

    def att_clr(self):
        self.att = {}
        return self

    def atts_read(self, attrs):
        try:
            for k,v in attrs.items():
                self.att[k] = v
        except:
            pass
        
        print("ATTRIBUTES:")
        print(self.att)
        return self

    def att_set(self, k, v):
        self.att[k] = v
        return self

    def att_del(self, k):
        if k in self.att: del self.att[k]
        return self

    def end_set(self, end):
        if type(end) == bool:
            self.end = end
        return self

    def build(self):
        resp = {}
        resp['version'] = "1.0"
        resp['sessionAttributes'] = self.att
        resp['response'] = {}
        resp['response']['outputSpeech'] = {'type': 'SSML', 'ssml': '<speak>' + self.use_voice(self.txt, self.loc) + '</speak>'}
        print(">" + self.rpt + "<")
        resp['response']['reprompt'] = {'outputSpeech': {'type': 'SSML', 'ssml': '<speak>' + self.use_voice(self.rpt, self.loc) +'</speak>'}} if self.rpt != "" else  {'outputSpeech': resp['response']['outputSpeech']}
        if self.crd != "":
            resp['response']['card'] = {'type': 'Standard', 'title': 'Maths Mountain', 'text': self.crd}
        resp['response']['shouldEndSession'] = self.end
        return resp

    @staticmethod
    def use_voice(txt, locale):
        voices={
            "en-US": "Justin",
            "en-AU": "Nicole",
            "en-GB": "Emma",
            "en-IN": "Raveena"
        }

        return '<voice name="' + voices[locale] + '"><lang xml:lang="' + locale + '">' + txt + '</lang></voice>'


class Skill():
    def __init__(self):
        self.handlers=[]
        self.req, self.res = self.setup()

    def setup(self):
        global event
        return Request(event), Response(event)

    def addHandler(self,handler):
        self.handlers.append(handler)
    
    def lambda_handler(self):
        def wrapper(event, context):
            for s in self.handlers:
                print(s.__class__.__name__ + ": " + str(s.can_handle(self.req)))
                if (s.can_handle(self.req)):
                    return s.handle(self.req, self.res)
        return wrapper


