from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import timedelta
from neomodel import *
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
import os


config.DATABASE_URL = "bolt://neo4j:123456@www.buaatech.top:7687"

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Paper(StructuredNode):
    '''
        论文
    '''
    uid=UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)
    year = IntegerProperty()
    abstract = StringProperty()
    keywords = StringProperty()    
    ci_count = IntegerProperty(default=0)    
    price = IntegerProperty(default=0)
    author1 = RelationshipTo('Author', 'AUTHOR1')
    authors = RelationshipTo('Author', 'AUTHORS')
    citations = RelationshipTo('Paper', 'CITATION')
    domains = RelationshipTo('Domain', 'BELONGTO')
    resource_url = StringProperty()

    @property
    def serialize(self):
        au_list1=[]
        au_list2=[]
        ci_list=[]
        do_list=[]
        for au in self.author1.all():
            au_list1.append(au.simple_serialize)
        for au in self.authors.all():
            au_list2.append(au.simple_serialize)
        for ci in self.citations.all():
            ci_list.append(ci.simple_serialize)
        for do in self.domains.all():
            do_list.append(do.serialize)
        return{
            "uid":self.uid,
            "name":self.name,
            "year":self.year,
            "abstract":self.abstract,
            "keywords":self.keywords,            
            "ci_count":self.ci_count,            
            "price":self.price,
            "author1":au_list1,
            "authors":au_list2,
            "resource_url":self.resource_url,
            "citations":ci_list,
            "domains":do_list,
        }

    @property
    def simple_serialize(self):
        au_list=[]
        for au in self.author1.all():
            au_list.append(au.simple_serialize)
        for au in self.authors.all():
            au_list.append(au.simple_serialize)
        return{
            "uid":self.uid,
            "name":self.name,
            "year":self.year,
            "authors":au_list,
            "ci_count":self.ci_count,
        }

#专利具体的field还需根据数据稍作修改
class Patent(StructuredNode):
    uid=UniqueIdProperty()    
    patent_id = StringProperty(unique_index=True, required=True)
    applicant_date = StringProperty()
    name = StringProperty()
    classification_no = StringProperty()
    DOI = StringProperty()
    corresponding_au = StringProperty()
    address = StringProperty()
    agency = StringProperty()
    agent = StringProperty()
    inventor = RelationshipTo('Author', 'INVENTOR')
    domains = RelationshipTo('Domain', 'BELONGTO')
    resouce_url = StringProperty()

    @property
    def serialize(self):
        au_list=[]
        for au in self.inventor.all():
            au_list.append(au.simple_serialize)
        return{
            "uid":self.uid,
            "patent_id":self.patent_id,
            "applicant_date":self.applicant_date,
            "name":self.name, 
            "inventor":au_list,
        }



class Author(StructuredNode):
    uid=UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)
    email = EmailProperty()
    h_index = IntegerProperty()
    g_index = IntegerProperty()
    avator = StringProperty()
    publishes = RelationshipTo('Paper', 'PUBLICATION')
    invent=RelationshipTo('Patent', 'INVENT')
    coworkers = Relationship('Author', 'COWORK')
    domains = RelationshipTo('Domain', 'WORKAT')
    owns = RelationshipTo('Paper', 'OWNSHIP')

    @property
    def serialize(self):
        p_list=[]
        co_list=[]
        do_list=[]
        own_list=[]
        pa_list=[]
        for paper in self.publishes.all():
            p_list.append(paper.simple_serialize)
        for co in self.coworkers.all():
            co_list.append(co.simple_serialize)
        for do in self.domains.all():
            do_list.append(do.serialize)
        for own in self.owns.all():
            own_list.append(own.simple_serialize)
        for pa in self.invent.all():
            pa_list.append(pa.serialize)
        return{
            "uid":self.uid,
            "name": self.name,
            "email": self.email,
            "h_index": self.h_index,
            "g_index":self.g_index,
            "avator":self.avator,
            "publishes":p_list,
            "coworkers":co_list,
            "domains":do_list,
            "owns":own_list,
            "patent":pa_list,
        }
    @property
    def simple_serialize(self):
        return{
            "uid":self.uid,
            "name":self.name,
        }


class UserNode(StructuredNode):
    name = StringProperty(unique_index=True)
    star_papers = RelationshipTo('Paper', 'STAR')
    star_patents = RelationshipTo('Patent', 'STAR')
    follows = RelationshipTo('Author', 'FOLLOW')
    bind = RelationshipTo('Author', 'BIND')


class Domain(StructuredNode):
    name = StringProperty(unique_index=True)
    @property
    def serialize(self):
        return{
            "name":self.name
        }
    


class Resource(models.Model):
    CHOICES = (
        ('P1', 'Paper'),
        ('P2', "Patent")
    )

    name = models.CharField(max_length=255)
    uid = models.CharField(max_length=255,default=0)
    Type = models.CharField(max_length=2, choices=CHOICES)
    files = models.FileField(upload_to="SAcore/static/files",blank=True)


class Avator(models.Model):

    uid = models.CharField(max_length=255)
    avator = models.ImageField(upload_to="SAcore/static/author_avator")
# # def md5(user):
# #         import hashlib
# #         import time

# #         ctime = str(time.time())

# #         m = hashlib.md5(bytes(user, encoding='utf-8'))
# #         m.update(bytes(ctime, encoding='utf-8'))
# #         return m.hexdigest()

# # Create your models here.


class User(AbstractUser):
    '''
    用户类
    '''
    TYPE_CHOICES = (
        ('U', 'User'),
        ('E', 'Expert'),
    )    
    Type = models.CharField(max_length=1, choices=TYPE_CHOICES, default='U')    
    balance = models.IntegerField(default=0)
    star_list = models.ManyToManyField(
        'Resource', blank=True, related_name="star_list")
    buyed_list = models.ManyToManyField(
        'Resource', blank=True, related_name="buyed_list")
    followed_list = models.ManyToManyField('User', blank=True)
    name = models.CharField(max_length=255, blank=True)
    avator = models.CharField(max_length=255,default="author_avator/default.jpg")
    uid=models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = '用户'


class AuthorUser(models.Model):
    '''
    专家，只有绑定用户才会成为专家用户
    '''
    name = models.CharField(max_length=255, unique=True)
    bind = models.OneToOneField(
        User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '专家信息'

class AuthorToken(models.Model):
    email=models.CharField(max_length=255)
    token=models.CharField(max_length=255)

class RechargeCard(models.Model):
    '''
        充值卡
    '''
    token = models.CharField(max_length=128, unique=True)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return self.token

    class Meta:
        verbose_name_plural = '充值卡信息'


class Message(models.Model):
    '''
        消息
    '''
    text = models.CharField(max_length=256)
    created_time = models.DateTimeField(auto_now_add=True)
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name_plural = '消息'

class interested(models.Model):    
    patent_id=models.CharField(max_length=256)
    send_user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="send_user")
    receive_user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="receive_user")
    message=models.CharField(max_length=256)
    status=models.BooleanField(default=False)