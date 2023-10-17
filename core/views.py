import json
import ssl
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse 
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Lang, Value, Item
from rest_framework import status 

# Create your views here.
def statusResp(message , error=False):
    resp = {"status" : ("error" if error else "success"), "message" : message}

class LangSet(APIView):
    def get(self, request, code):
        try : lang = Lang.objects.get(code=code)
        except : return Response(statusResp("Something wrong with language code", error=True), status=400)
        return Response(lang_getter(code), status=200)
    
    def post(self, request ,code):
        data : dict = json.loads(request.body)
        try: lang = Lang.objects.get(code = code)
        except : return Response(statusResp("Something wrong with language code", error=True), status=400)
        # validation 
        val_error_resp = [] 
        for key in data.keys():    
            try:
                Item.objects.get(key=key)
                val_error_resp.append({"message" : f"key {key} already exists"})
            except: pass 
        if val_error_resp:
            return Response({"status" : "error", "message" : "There are existing keys. Use PATCH method to update them", 'stack' : val_error_resp }, status=400)
        # end validation
        for key , value in data.items():
            new_item = Item(key=key)
            new_item.save()
            valobj = Value.objects.get(item=new_item, lang=lang)
            valobj.value = value
            valobj.save() 
        lang_getter.clear_cache()
        return Response(statusResp("success"), status=200)
    
    def patch(self, request ,code):
        data : dict = json.loads(request.body)
        try: lang = Lang.objects.get(code = code)
        except : return Response(statusResp("Something wrong with language code", error=True), status=400)
        # validation 
        val_error_resp = [] 
        for key in data.keys():    
            try:
                Item.objects.get(key=key)
            except: val_error_resp.append({"message" : f"key {key} does not exists"})
        if val_error_resp:
            return Response({"status" : "error", "message" : "Some keys not found. Use PUT method to add them", 'stack' : val_error_resp }, status=400)
        # end validation
        for key , value in data.items():
            item = Item.objects.get(key=key)
            valobj = Value.objects.get(item=item, lang=lang)
            valobj.value = value
            valobj.save()
        lang_getter.clear_cache() 
        return Response(statusResp("success"), status=200)

# class SmartChange(APIView):
#     def post(self, request , code):


class cache:
    def __init__(self, func) -> None:
        self.func = func 
        self.__cache = dict() 

    def __call__(self, *args, **kwargs):
        keyword = str(args) + str(sorted(tuple(kwargs.items()))) 
        if keyword not in self.__cache:
            res = self.func(*args, **kwargs)
            self.__cache[keyword] = res 
        #     print('to cache')         # check caching operations 
        # else : print('from cache')
        return self.__cache[keyword]
        
    def clear_cache(self):
        self.__cache.clear() 
        print('cache cleaned')

@cache
def lang_getter(code):
    lang = Lang.objects.get(code=code)
    result = {} 
    for item in Item.objects.all():
        value_obj  = Value.objects.get(item=item, lang=lang)
        result.setdefault(item.key , value_obj.value)
    return result


class getLangList(APIView):
    def get(*args):
        queryset = Lang.objects.all() 
        resp = []  
        for lang in queryset:
            resp.append({'value' : lang.code})
        return Response(resp, status=200)
    
class getAllLanguagesSet(APIView):
    def get(*args,**kwargs):
        items = Item.objects.all() 
        langs = Lang.objects.all() 
        resp = [] 
        for item in items:
            curr = { "key" : item.key }
            for lang in langs:
                val = Value.objects.get(item=item, lang=lang)
                curr[lang.code] = val.value
            resp.append(curr)
        return Response(resp, status=200)
    
