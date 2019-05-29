from django.shortcuts import render
from .models import *
from .Se import *
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework import exceptions
# from SAcore.utils.auth import Authentication
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FileUploadParser, MultiPartParser
from django.contrib.auth import authenticate, login
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated


User = get_user_model()

# Create your views here.

class ProfileView(APIView):
    '''
        个人信息相关业务
    '''
    permission_classes = (IsAuthenticated,)

    # 获得个人信息
    def get(self, request, *args, **kwargs):
        user = request.user
        user_se = UserSerializer(user)
        print(settings.STATICFILES_URL)
        return JsonResponse(user_se.data)

    # 修改个人信息
    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data['data']
        user_se = UserSerializer(user, data=data)
        if user_se.is_valid():
            user_se.save()
            return JsonResponse(user_se.data)
        return JsonResponse(user_se.errors, status=400)

    # 申请成为专家需要使用邮箱验证实现
    # 申请成为专家
    def put(self, request, *args, **kwargs):
        user = request.user
        uid = request.data['uid']        
        # try:
        au=Author.nodes.get(uid=uid)
        print(au)
        email=au.email
        token=account_activation_token.make_token(user)
        print(token)
        AuthorToken.objects.get_or_create(email=email,token=token)
        send_mail(
            subject='科技资源交易平台验证邮件',
            message='欢迎来到科技资源交易平台，您的验证码为：%s,请输入验证码完成验证'%(token),
            from_email='18807479812@163.com',
            recipient_list=[email],
        )
        return JsonResponse({'email': email})
        # except Exception as e:
        #     return JsonResponse({'msg': "申请失败"}, status=400)


#生成邮箱验证所需token
class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )
account_activation_token = TokenGenerator()

class VerifyView(APIView):
    def post(self, request, *args, **kwargs):
        data=request.data['data']
        email=data['email']
        token=data['token']
        username=data['username']        
        at=AuthorToken.objects.get(email=email)
        au=Author.nodes.get(email=email)
        if token == at.token:
            u=User.objects.get(username=username)
            u.Type='E'
            u.uid=au.uid
            u.save()
            return JsonResponse({'msg':"申请成功"},status=200)
        else:
            return JsonResponse({'msg':"验证码错误"},status=400)

# 用户经过认证后，作为专家登录还需修改


class AuthorView(APIView):
    '''
    专家信息相关业务
    '''
    # 用户认证
    # permission_classes = (IsAuthenticated,)

    # 文件parser
    parser_classes = (MultiPartParser,)
    # 获得专家个人信息

    def get(self, request, *args, **kwargs):
        uid = request.GET['uid']
        au = Author.nodes.get_or_none(uid=uid)
        res = au.serialize
        return JsonResponse(res, status=200)

    # 修改专家邮箱，可以考虑加入邮箱修改结合邮箱验证
    @permission_classes(IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        user = request.user
        email = request.data['email']
        token=account_activation_token.make_token(user)
        AuthorToken.objects.create(email=email,token=token).save()
        send_mail(
            subject='科技资源交易平台验证邮件',
            message='欢迎来到科技资源交易平台，您的验证码为：%s,请输入验证码完成验证'%(token),
            from_email='xinghangliu233@gmail.com',
            recipient_list=email,
        )
        return JsonResponse({'email':email})

    
    # 发布资源
    @permission_classes(IsAuthenticated,)
    def put(self, request, *args, **kwargs):
        user=request.user
        data = request.data
        attach_file = request.FILES['file']
        r=Paper(name=data['name'],
                abstract=data['abstract'],
                keywords=data['keywords'],
                resource_url=data['url'],
                price=data['price'],).save()
        r.author1.connect(Author.nodes.get(uid=user.uid))
        authors_text = data['authors']
        authors_names = authors_text.split(',')
        au_list=[]        
        for name in authors_names:            
            au = Author.nodes.get_or_none(name=name)
            if au is None:
                au=Author(name=name).save()            
            au_list.append(au)
            r.authors.connect(au)
            au.publishes.connect(r)
            au.save()
        r.save()            
        for i in range(len(au_list)):
            au=au_list[i]
            for au1 in au_list:
                if au1!=au:
                    au.coworkers.connect(au1)
                    au.save()
        Resource.objects.create(Type="P1",name=r.name,files=attach_file,uid=r.uid).save()
        print(attach_file)
        return JsonResponse({'msg': "上传成功",'url':"files/"+attach_file.name})


class RegisterView(APIView):
    '''
    注册视图
    '''   

    def post(self, request, *args, **kwargs):
        data = request.data['data']
        username = data['username']
        user = User.objects.filter(username=username).first()
        if user:
            return JsonResponse({'msg': "该用户名已被注册， 换一个试试吧"}, status=400)
        else:
            password=data['password']
            User.objects.create_user(username=username,password=password)
            return JsonResponse({'msg':"注册成功！"}, status=200)        

# 搜索函数需要重新写
class SearchView(APIView):
    '''
    搜索视图
    '''
    # 用户认证
    # authentication_classes = [Authentication,]

    # 获取搜索结果
    def post(self, request, *args, **kwargs):
        Type=request.data['type']
        field = request.data['field']
        string=request.data['content']
        result=[]
        ret={}
        if Type=='P1':
            t="Paper"            
        else:
            t="Patent"            
        if field=='Title':
            query="match(n:"+t+") where n.name =~'.*"+string+".*' return n limit 50"
            results, meta = db.cypher_query(query)
            if Type=='P1':
                re = [Paper.inflate(row[0]) for row in results]
            else:
                re = [Patent.inflate(row[0]) for row in results]
            for pa in re:
                result.append(pa.serialize)                        
        elif field=='Author':
            if Type=='P1':                                     
                query="match(n:"+t+")-[r:AUTHOR1]-(a:Author) where a.name =~'.*"+string+".*' return n limit 50"
                results, meta = db.cypher_query(query)
                re = [Paper.inflate(row[0]) for row in results]
                for pa in re:
                    result.append(pa.serialize)
                query="match(n:"+t+")-[r:AUTHORS]-(a:Author) where a.name =~'.*"+string+".*' return n limit 50"
                results, meta = db.cypher_query(query)
                re = [Paper.inflate(row[0]) for row in results]            
                for pa in re:
                    result.append(pa.serialize)
            else:
                query="match(n:"+t+")-[r:INVENTOR]-(a:Author) where a.name =~'.*"+string+".*' return n limit 50"
                results, meta = db.cypher_query(query)
                re = [Patent.inflate(row[0]) for row in results]
                for pa in re:
                    result.append(pa.serialize)
        ret['result']=result
        return JsonResponse(ret)

class AdvanceSearchView(APIView):
    def post(self, request, *args, **kwargs):
        title=request.data['title']        
        author=request.data['author']
        Type=request.data['type']
        time_low=request.data['time_low']
        time_high=request.data['time_high']
        if len(time_low)==0:
            time_low=-100
        if len(time_high)==0:
            time_high=10000
        result=[]
        ret={}        
        if Type =='P2':
            query="match(n:Patent)-[r:INVENTOR]-(a:Author) where n.name =~'.*"+title+".*' \
            "" \
            and a.name =~'.*"+author+".*' \
            "" \
            "" \
            return n limit 50"
            results, meta = db.cypher_query(query)
            re = [Patent.inflate(row[0]) for row in results]
            for pa in re:
                result.append(pa.serialize)
        else:
            query="match(n:Paper)-[r:AUTHOR1]-(a:Author) where n.name =~'.*"+title+".*' \
            "" \
            and a.name =~'.*"+author+".*' \
            and n.year >= "+str(time_low)+" \
            and n.year <= "+str(time_high)+" \
            return n limit 50"            
            results, meta = db.cypher_query(query)
            re = [Paper.inflate(row[0]) for row in results]
            for pa in re:
                result.append(pa.serialize)
            query="match(n:Paper)-[r:AUTHORS]-(a:Author) where n.name =~'.*"+title+".*' \
            "" \
            and a.name =~'.*"+author+".*' \
            and n.year >= "+str(time_low)+" \
            and n.year <= "+str(time_high)+" \
            return n limit 50"
            results, meta = db.cypher_query(query)
            re = [Paper.inflate(row[0]) for row in results]
            for pa in re:
                result.append(pa.serialize)
        ret['result']=result
        return JsonResponse(ret)


# 对资源的获取需要修改


class DetailView(APIView):
    '''
        展示某一资源的详细信息
    '''
    # authentication_classes = [Authentication,]

    def post(self, request, *args, **kwargs):
        ret = {}
        t = request.data['Type']
        uid = request.data['uid']
        # try:
        if t == "P1":            
            r1 = Paper.nodes.get(uid=uid)
        else:
            r1 = Patent.nodes.get(uid=uid)
        ret = {**ret, **r1.serialize}
        # except Exception as e:
        #     return JsonResponse({'msg': "该资源不存在"}, status=400)
        if request.user.is_authenticated:
            r1 = request.user.star_list.filter(uid=uid).first()
            b1 = request.user.buyed_list.filter(uid=uid).first()
            if r1:
                ret['starred'] = True
            else:
                ret['starred'] = False
            if b1:
                ret['bought'] = True
            else:
                ret['bought'] = False
        else:
            ret['starred'] = False
            ret['bought'] = False        
        return JsonResponse(ret)

# Resource的get函数需要修改


class StarView(APIView):
    '''
    收藏视图
    '''
    permission_classes = (IsAuthenticated,)
    # 列出当前用户的所有收藏

    def get(self, request, *args, **kwargs):
        user = request.user
        result={}
        star=[]        
        res = user.star_list.all().order_by("uid")
        for p in res:
            if p.Type=="P1":
                star.append(Paper.nodes.get(uid=p.uid).simple_serialize)
            else:
                star.append(Patent.nodes.get(uid=p.uid).simple_serialize)
        result['star']=star 
        return JsonResponse(result)

    # Resource的get函数需要修改
    # 批量添加收藏
    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data['data']
        star_items = data['item_list']
        star_items_list=star_items.split(",")
        for i in star_items_list:            
            try:
                r1 = Resource.objects.get_or_create(uid=i)                
                user.star_list.add(r1)
                user.save()
            except Exception as e:                
                return JsonResponse({"msg": "收藏失败"}, status=400)


        return JsonResponse({"msg": "收藏成功"}, status=200)

    # 批量取消收藏
    def delete(self, request, *args, **kwargs):
        user = request.user
        data = request.data['data']
        star_items = data['item_list']
        star_items_list=star_items.split(",")
        for i in star_items_list:
            try:
                r1 = user.star_list.get(uid=i)
                user.star_list.remove(r1)
                user.save()
            except Exception as e:
                return JsonResponse({"msg": "取消收藏失败"}, status=400)
        return JsonResponse({"msg": "已取消收藏"}, status=200)

class BuyedView(APIView):
    '''
        已购资源视图
    '''
    # 用户认证
    
    # 列出所有已购资源
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        result={}
        buy=[]
        res = user.buyed_list.all()
        for p in res:
            if p.Type=="P1":
                buy.append(Paper.nodes.get(uid=p.uid).simplie_serialize)
            else:
                buy.append(Patent.nodes.get(uid=p.uid).simplie_serialize)
        result['buy']=buy
        return JsonResponse(result)

    # resource的get函数需要修改
    # 购买资源
    def post(self, request, *args, **kwargs):
        user = request.user
        uid = request.data['uid']        
        try:
            p=Paper.nodes.get(uid=uid)
        except Exception as e:
            return JsonResponse({"msg": "资源不存在"}, status=404)

        if user.balance < p.price:
            return JsonResponse({'msg': "余额不足"}, status=400)
        try:
            user.balance -= p.price
            r1=Resource.objects.get_or_create(uid=uid,Type="P1")
            user.buyed_list.add(r1)
            user.save()
        except Exception as e:
            return JsonResponse({'msg': "交易失败"}, status=401)
        return JsonResponse({"msg": "交易成功", "balance": user.balance}, status=200)


# 关于获取头像时返回的内容还需确认与修改
class AvatorView(APIView):
    '''
        头像相关业务
    '''

    # 验证身份
    

    # 关于获取头像时返回的内容还需确认与修改
    # 获取头像
    def get(self, request, *args, **kwargs):
        uid=request.GET['uid']
        try:
            a=Avator.objects.get(uid=uid)        
            return JsonResponse({"url":"author_avator/"+a.avator.name.split('/')[-1]})
        except Avator.DoesNotExists:
            return JsonResponse({"avator":"author_avator/default.jpg"})

    # 专家的头像上传还需修改
    # 上传头像
    @permission_classes(IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        user = request.user
        if user.Type == 'E':
            request.data['uid']=user.uid
            se = AuthorAvatorSerializer(data=request.data)
            if se.is_valid():
                se.save()
                return JsonResponse(se.data)
            return JsonResponse(se.errors, status=400)

class RechargeView(APIView):
    '''
        充值视图
    '''
    # 用户认证
    permission_classes = (IsAuthenticated,)

    # 充值
    def post(sefl, request, *args, **kwargs):
        user = request.user
        key = request.data['key']
        card = RechargeCard.objects.filter(token=key).first()
        if not card:
            return JsonResponse({'msg': "无效的充值卡"}, status=400)
        try:
            user.balance += card.amout
            card.delete()
        except Exception as e:
            return JsonResponse({'msg': "充值失败"}, status=400)
        return JsonResponse({'msg': "充值成功"}, status=200)

class CoGraphView(APIView):
    def post(sefl, request, *args, **kwargs):
        uid=request.data['uid']
        base=Author.nodes.get(uid=uid)        
        user_set=set((uid,))
        base_id=0
        nodes=[]
        links=[]
        l={}
        l["sourceWeight"]=1
        l["targetWeight"]=1
        n={"id":base_id,"name":base.name,"value":1}
        nodes.append(n)
        for co in base.coworkers.all():                    
            if co.uid not in user_set:
                user_set.add(co.uid)
                new={}
                new["id"]=len(user_set)-1
                new["name"]=co.name
                new["value"]=1
                print(new)
                nodes.append(new)
                new_link={}
                new_link["sourceWeight"]=1
                new_link["targetWeight"]=1
                new_link["source"]=base_id
                new_link["target"]=new["id"]
                print(new_link)
                links.append(new_link)
        print(nodes)
        for n in nodes[0:]:
            base=Author.nodes.get(name=n["name"])
            base_id=n["id"]
            for co in base.coworkers.all():
                print(co)                    
                if co.uid not in user_set:
                    user_set.add(co.uid)
                    new={}
                    new["id"]=len(user_set)-1
                    new["name"]=co.name
                    new["value"]=1
                    print(new)
                    nodes.append(new)
                    new_link={}
                    new_link["sourceWeight"]=1
                    new_link["targetWeight"]=1
                    new_link["source"]=base_id
                    new_link["target"]=new["id"]
                    print(new_link)
                    links.append(new_link)
        res={}
        res["nodes"]=nodes
        res["links"]=links
        return JsonResponse(res)
