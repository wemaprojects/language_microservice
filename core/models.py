from collections.abc import Iterable
from django.db import models

# Create your models here.
class Lang(models.Model):
    code = models.CharField(max_length=5)

    def __str__(self) -> str:
        return self.code
    
    def save(self, *args , **kwargs):
        res =  super(Lang, self).save(*args, **kwargs)
        for item in Item.objects.all():
            val = Value(item=item, lang=self)
            val.save() 
        return res 


class Item(models.Model):
    key = models.CharField(max_length=1024)
    
    def __str__(self) -> str:
        return self.key

    def save(self, *args, **kwargs) :
        res =  super(Item ,self).save(*args , **kwargs)
        for lang in Lang.objects.all():
            val = Value(item=self, lang=lang)
            val.save()
        return res 
     

class Value(models.Model):
    value = models.TextField(default='<not_defined>')
    lang = models.ForeignKey(Lang, on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.lang.code.upper()} {self.item.key}"
