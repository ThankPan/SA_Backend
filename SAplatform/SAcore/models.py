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
    coworkers = Relationship('Author', 'COWORK')
    domains = RelationshipTo('Domain', 'WORKAT')
    owns = RelationshipTo('Paper', 'OWNSHIP')

    @property
    def serialize(self):
        p_list=[]
        co_list=[]
        do_list=[]
        own_list=[]
        for paper in self.publishes.all():
            p_list.append(paper.simple_serialize)
        for co in self.coworkers.all():
            co_list.append(co.simple_serialize)
        for do in self.domains.all():
            do_list.append(do.serialize)
        for own in self.owns.all():
            own_list.append(own.simple_serialize)
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

# # class UserToken(models.Model):
# #     user = models.OneToOneField(to="User", on_delete=models.CASCADE)
#     # token = models.CharField(max_length=64)

#     # def __str__(self):
#     #     return self.user.username
#     # class Meta:
#     #     verbose_name_plural = '用户Token'


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


# class Resource(models.Model):
#     '''
#     资源类
#     '''

#     TYPE_CHOICES = (
#         ("P1", "Paper"),
#         ("P2", "Patent"),
#         ("P3", "Project"),
#     )

#     title = models.CharField(max_length=255, unique=True)
#     authors = models.ManyToManyField(Author, blank=True)
#     intro = models.TextField(blank=True)
#     url = models.TextField(blank=True)
#     price = models.IntegerField(default=0)
#     Type = models.CharField(max_length=2, choices=TYPE_CHOICES)
#     publisher = models.CharField(max_length=255, blank=True)
#     publish_date = models.CharField(max_length=255, blank=True)
#     citation_nums = models.IntegerField(default=0, blank=True)
#     agency = models.CharField(max_length=255, blank=True)
#     patent_number = models.TextField(blank=True)
#     patent_applicant_number = models.TextField(blank=True)
#     file = models.FileField(upload_to="SAcore/static/files", blank=True)
#     owner = models.ForeignKey('Author', blank=True, related_name='owner', on_delete=models.CASCADE)

    # def __str__(self):
    #     return self.title

    # class Meta:
    #     verbose_name_plural = '科研资源信息'

# class U2E_apply(models.Model):
#     '''
#     普通用户申请成为专家的申请表
#     '''

#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     created_time = models.DateTimeField(auto_created=True)
#     name = models.CharField(max_length=255, default=" ")
#     instituition = models.CharField(max_length=255, blank=True)
#     domain = models.CharField(max_length=255, blank=True)

#     def __str__(self):
#         return self.user.username + " : " + self.name

#     # Author的操作需要修改
#     def approve(self):
#         au1 = Author.nodes.get_or_none(name=self.name)
#         if not au1:
#             au1 = Author(name=self.name).save()
#         au1.instituition = self.instituition
#         au1.domain = self.domain
#         self.user.Type = "E"
#         try:
#             au1.save()
#             self.delete()
#             return True
#         except Exception as e:
#             print(e)
#             return False

#     class Meta:
#         verbose_name_plural = '获取专家权限申请'


# 申请成功后，资源的创建需要修改
class publish_apply(models.Model):
    '''
    专家用户申请发布资源的申请表   '''

    au = models.ForeignKey(
        AuthorUser, on_delete=models.CASCADE, related_name="applicant")
    name = models.CharField(max_length=255)
    authors = models.ManyToManyField(
        AuthorUser, blank=True, related_name="authors")
    abstract = models.TextField()
    keywords = models.TextField()
    url = models.TextField(blank=True)
    price = models.IntegerField(default=0)
    created_time = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="SAcore/static/files", blank=True)

    def __str__(self):
        return self.au.name + " : " + self.title

    def approve(self):
        try:
            r1 = Paper(
                name=self.name,
                abstract=self.abstract,
                keywords=self.keyords,
                url=self.url,
                price=self.price,
                author1=self.au

            ).save()
            authors = self.authors.all()
            for aut in authors:
                r1.authors.connnect(aut)
                aut.publishes.connnect(r1)
                r1.save()
                aut.save()
            Resource.objects.create(Type="P1", name=self.name, files=self.file)
            Resource.save()
            r1.resource_url = os.path.join(
                "SAcore/static/files", self.file.name)
            r1.save()
            self.delete()
            return True
        except Exception as e:
            print(e)
            return False

    class Meta:
        verbose_name_plural = '发布资源申请'


# class Auction(models.Model):

#     '''
#     转让资源发起竞拍
#     '''

#     start_au = models.ForeignKey(
#         Author, related_name="start_au", on_delete=models.CASCADE)
#     #title = models.CharField(max_length=255, blank=True)
#     #participants = models.ManyToManyField(Author, related_name="participants", blank=True)
#     resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
#     started_time = models.DateTimeField()
#     period = models.IntegerField(default=3600)  # 以秒为单位记录持续时间
#     price = models.IntegerField(default=0)
#     candidate = models.ForeignKey(
#         Author, related_name="candidate", on_delete=models.CASCADE, blank=True, null=True)

#     def __str__(self):
#         return self.resource.title

#     class Meta:
#         verbose_name_plural = '竞拍信息'


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
