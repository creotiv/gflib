# -*- coding: utf-8 -*-
from gflib.utils import json_encode
import random
import time

class UserHTTPController(object):

    def __init__(self,env,response,request,headers):
        self.env      = env
        self.headers  = headers
        self.response = response
        self.request  = request
        
    def IndexAction(self):
        self.response('200 OK', self.headers )
        a = random.choice([time.sleep,lambda x:x])
        #a(0.5)
        return [
        """
            +Andrey Python Gmail Calendar Documents Photos Reader Web more Andrey Python Nikishaev 0 Share…  Google Search  Andrey Python Navigation Welcome Stream HR's Друзья Знакомые Остальные Работа More▾ Incoming Notifications Sparks Snowboarding Photography MTB Street Aggressive Skating Computer Programming MTB Freeride  Stream Share what's new... Stream Andrey Python Nikishaev Andrey Python Nikishaev - 5:56 PM (edited) - Public Вопрос к знатокам архитектуры приложений. Как правельно реализовать Глобальный конфиг для всех модулей приложений. Конфиг грузится при инициализации из файла и становится доступным для всех частей программы. При определенном сигнале конфиг может перегружаться. Я пока реально варианта кроме синглтона не вижу, по крайней мере удобного и красивого варианта.  Кто что посоветует?  - Comment - Share 5 comments from Andrey Python Nikishaev and Sergey Kirillov  Andrey Python Nikishaev - Вопрос в том есть ли вариант по лучше?) 7:04 PM - Edit   Andrey Python Nikishaev - Счас кста почти дошли руки до ZeroMQ. Пишу распределение заданий между серверами чере IPC ибо подход gunicorn мне как то не сильно нравитцо. Должен полутчиццо сервак с главным процессом на gevent и остальные как workers через ZeroMQ. В теории gevent может давать до 4-6к rps. Тоесть если не лягут буфера, то можно дежрать один сервак как лисенер и два-три для отработки заданий. Правда сие пока только догадки.. нада будет тестить и сатреть как оно в жизне. 7:10 PM - Edit  Add a comment... Sergey Kirillov Sergey Kirillov - Aug 24, 2011 - Limited Что-то я не пойму почему все радуются и празднуют. За 20 лет проебали страну, неужели это повод для праздника?  - 

        """
        ]
        
class UserAMFController(object):

    def __init__(self,env,request):
        self.env      = env
        self.request  = request
        
    def IndexAction(self):
        return [json_encode(self.request)]
