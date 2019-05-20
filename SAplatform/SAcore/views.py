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
# from apscheduler.schedulers.background import BackgroundScheduler
# from django_apscheduler.jobstores import DjangoJobStore,register_events, register_job
from django.contrib.auth import authenticate, login
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
from django.core.mail import send_mail


# Create your views here.


def author_check(user):
    return user.Type == "E"


class AuthView(APIView):

    def post(self, request, *args, **kwargs):
        ret = {
            'code': 1000,
            'msg': None
        }
        try:
            username = request.data.get('username')
            pwd = request.data.get('password')
            user = authenticate(username=username, password=pwd)
            if user is not None:
                login(request, user)
            else:
                ret['code'] = 1001
                ret['msg'] = '用户名或密码错误'

        except Exception as e:
            print(e)
            ret['code'] = 1002
            ret['msg'] = '请求异常'

        return JsonResponse(ret)

# U2E_apply需要修改


class ProfileView(LoginRequiredMixin, APIView):
    '''
        个人信息相关业务
    '''
    login_url = '/login/'

    # 获得个人信息
    def get(self, request, *args, **kwargs):
        user = request.user
        user_se = UserSerializer(user)
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
        name = request.data['name']
        try:
            au=Author.nodes.get(name=name)
            email=au.email
            token=account_activation_token()
            AuthorToken.objects.create(email=email,token=token).save()
            send_mail(
                subject='科技资源交易平台验证邮件',
                message='欢迎来到科技资源交易平台，您的验证码为：%s,请输入验证码完成验证'%(token),
                from_email='xinghangliu233@gmail.com',
                recipient_list=email,
            )
            return JsonResponse({'email': email})
        except Exception as e:
            return JsonResponse({'msg': "申请失败"}, status=400)


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
        at=AuthorToken.objects.get(email='email')
        if token == at.token:
            return JsonResponse({'msg':"申请成功"},status=200)
        else:
            return JsonResponse({'msg':"验证码错误"},status=400)

# 用户经过认证后，作为专家登录还需修改


class AuthorView(LoginRequiredMixin, APIView):
    '''
    专家信息相关业务
    '''
    # 用户认证
    # authentication_classes = [Authentication,]

    # 文件parser
    parser_classes = (MultiPartParser,)
    # 获得专家个人信息

    def get(self, request, *args, **kwargs):
        name = request.GET['name']
        au = Author.nodes.get_or_none(name=name)
        res = au.serialize
        return JsonResponse(res, status=200)

    # 修改专家邮箱，可以考虑加入邮箱修改结合邮箱验证
    @user_passes_test(author_check)
    def post(self, request, *args, **kwargs):
        user = request.user
        email = request.data['email']
        token=account_activation_token()
        AuthorToken.objects.create(email=email,token=token).save()
        send_mail(
            subject='科技资源交易平台验证邮件',
            message='欢迎来到科技资源交易平台，您的验证码为：%s,请输入验证码完成验证'%(token),
            from_email='xinghangliu233@gmail.com',
            recipient_list=email,
        )
        return JsonResponse({'email':email})

    @user_passes_test(author_check)
    # 发布资源
    def put(self, request, *args, **kwargs):
        token = request.GET['token']
        data = request.data
        attach_file = request.FILES['file']
        user = request.user
        au = AuthorUser.objects.get(name=user.name)
        try:
            apply = publish_apply.objects.create(
                au=au,
                name=data['name'],
                abstract=data['abstract'],
                keywords=data['keywords'],
                url=data['url'],
                price=data['price'],
                created_time=timezone.now()
            )
        except Exception as e:
            print(e)
            return JsonResponse({'msg': "创建申请失败"}, status=400)
        if attach_file:
            apply.file.save(attach_file.name, attach_file, save=True)
        authors_text = data['authors']
        authors_names = authors_text.split(',')
        for name in authors_names:
            au_ = AuthorUser.objects.get(name=name)
            if not au_:
                au_ = AuthorUser.objects.create(name=name)
                Author(name=name).save()
            apply.authors.add(au_)
        apply.save()
        return JsonResponse({'msg': "创建成功"})


class RegisterView(APIView):
    '''
    注册视图
    '''
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        data = request.data['data']
        username = data['username']
        user = User.objects.filter(username=username).first()
        if user:
            return JsonResponse({'msg': "该用户名已被注册， 换一个试试吧"}, status=400)
        user_se = RegisterSerializer(data=data)
        if user_se.is_valid():
            user_se.save()
            return JsonResponse(user_se.data, status=200)
        return JsonResponse(user_se.errors, status=400)


# 搜索函数需要重新写
class SearchView(APIView):
    '''
    搜索视图
    '''
    # 用户认证
    # authentication_classes = [Authentication,]

    # 获取搜索结果
    def get(self, request, *args, **kwargs):

        keyword = request.GET['keyword']
        result = Resource.objects.filter(
            title__contains=keyword).order_by("id")
        pg = PageNumberPagination()
        page_result = pg.paginate_queryset(
            queryset=result, request=request, view=self)
        result_se = ResourceSerializer(instance=page_result, many=True)
        return JsonResponse(result_se.data, safe=False)

# 对资源的获取需要修改


class DetailView(APIView):
    '''
        展示某一资源的详细信息
    '''
    # authentication_classes = [Authentication,]

    def post(self, request, *args, **kwargs):
        ret = {}
        t = request.data['Type']
        title = request.data['title']
        try:
            if t == "P1":
                r1 = Paper.nodes.get(name=title)
            else:
                r1 = Patent.nodes.get(name=title)
            ret = {**ret, **r1.serialize}
        except Exception as e:
            return JsonResponse({'msg': "该资源不存在"}, status=400)
        if request.user.is_authenticated:
            r1 = request.user.star_list.filter(name=title).first()
            b1 = request.user.buyed_list.filter(name=title).first()
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


class StarView(LoginRequiredMixin, APIView):
    '''
    收藏视图
    '''
    # authentication_classes = [Authentication,]
    login_url = '/login/'
    # 列出当前用户的所有收藏

    def get(self, request, *args, **kwargs):
        user = request.user()
        result={}
        star=[]        
        res = user.star_list.all().order_by("id")
        for p in res:
            if p.Type=="P1":
                star.append(Paper.nodes.get(name=p.name).simplie_serialize)
            else:
                star.append(Patent.nodes.get(name=p.name).simplie_serialize)
        result['star']=star 
        return JsonResponse(result)

    # Resource的get函数需要修改
    # 批量添加收藏
    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data['data']
        star_items = data['item_list']
        for i in star_items:
            try:
                r1 = Resource.objects.get(name=i)
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
        for i in star_items:
            try:
                r1 = user.star_list.get(name=i)
                user.star_list.remove(r1)
                user.save()
            except Exception as e:
                return JsonResponse({"msg": "取消收藏失败"}, status=400)
        return JsonResponse({"msg": "已取消收藏"}, status=200)


# Author的get需要修改
# class FollowView(LoginRequiredMixin, APIView):
#     '''
#         关注视图
#     '''
#     login_url = '/login/'
#     # authentication_classes = [Authentication,]

#     # 列出所有关注的专家
#     def get(self, request, *args, **kwargs):
#         user = request.user
#         res = user.followed_list.all()
#         pg = PageNumberPagination()
#         page_result = pg.paginate_queryset(
#             queryset=res, request=request, view=self)
#         result_se = AuthorSerializer(instance=page_result, many=True)
#         return JsonResponse(result_se.data, safe=False)

    # Author的get需要修改
    # 批量添加关注
#     def post(self, request, *args, **kwargs):
#         user = request.user
#         data = request.data['data']
#         follow_aus = data['au_list']
#         for i in follow_aus:
#             try:
#                 au = Author.objects.get(pk=i)
#                 user.followed_list.add(au)
#                 user.save()
#             except Exception as e:
#                 print(e)
#                 return JsonResponse({"msg": "添加关注失败"}, status=400)
#         return JsonResponse({"msg": "关注成功"}, status=200)

#     # 批量取消关注
#     def delete(self, request, *args, **kwargs):
#         user = request.user
#         data = request.data['data']
#         follow_aus = data['au_list']
#         for i in follow_aus:
#             try:
#                 au = user.followed_list.get(pk=i)
#                 user.followed_list.remove(au)
#                 user.save()
#             except Exception as e:
#                 return JsonResponse({"msg": "取消关注失败"}, status=400)
#         return JsonResponse({"msg": "已取消关注"})

# # resource的get函数需要修改


class BuyedView(LoginRequiredMixin, APIView):
    '''
        已购资源视图
    '''
    # 用户认证
    # authentication_classes = [Authentication,]
    # 列出所有已购资源
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        user = request.user
        result={}
        buy=[]
        res = user.buyed_list.all()
        for p in res:
            if p.Type=="P1":
                buy.append(Paper.nodes.get(name=p.name).simplie_serialize)
            else:
                buy.append(Patent.nodes.get(name=p.name).simplie_serialize)
        result['buy']=buy
        return JsonResponse(result)

    # resource的get函数需要修改
    # 购买资源
    def post(self, request, *args, **kwargs):
        user = request.user
        title = request.data['title']
        try:
            r1 = Resource.objects.get(name=title)
        except Resource.DoesNotExist:
            return JsonResponse({"msg": "资源不存在"}, status=404)

        if user.balance < r1.price:
            return JsonResponse({'msg': "余额不足"}, status=400)
        try:
            user.balance -= r1.price
            user.buyed_list.add(r1)
            user.save()
        except Exception as e:
            return JsonResponse({'msg': "交易失败"}, status=401)
        return JsonResponse({"msg": "交易成功", "balance": user.balance}, status=200)


# 关于获取头像时返回的内容还需确认与修改
class AvatorView(LoginRequiredMixin, APIView):
    '''
        头像相关业务
    '''

    # 验证身份
    # authentication_classes = [Authentication,]

    # 关于获取头像时返回的内容还需确认与修改
    # 获取头像
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.Type == 'U':
            ret = {
                'url': user.avator.name.split('/')[-1]
            }
            return JsonResponse(ret)
        elif user.Type == 'E':
            au = Author.objects.filter(bind=user).first()
            if not au:
                return JsonResponse({'msg': '未找到对应专家用户，请确认身份'}, status=400)
            ret = {
                'url': au.avator.name.split('/')[-1]
            }
            return JsonResponse(ret)

    # 专家的头像上传还需修改
    # 上传头像
    def post(self, request, *args, **kwargs):
        user = request.user
        image = request.FILES['image']
        if user.Type == 'U':
            se = UserAvatorSerializer(user, data={'avator': image})
            if se.is_valid():
                se.save()
                return JsonResponse(se.data)
            return JsonResponse(se.errors, status=400)
        elif user.Type == 'E':
            au = Author.objects.filter(bind=user).first()
            if not au:
                return JsonResponse({'msg': '未找到对应专家用户，请确认身份'}, status=400)
            se = AuthorAvatorSerializer(au, data={'avator': image})
            if se.is_valid():
                se.save()
                return JsonResponse(se.data)
            return JsonResponse(se.errors, status=400)


# 专家对象的获取还需修改
# class CoworkerView(APIView):
#     '''
#         关系图相关业务
#     '''

#     # 验证身份
#     # authentication_classes = [Authentication,]

#     # 获取关系矩阵
#     def get(self, request, *args, **kwargs):
#         au = Author.objects.filter(bind=user).first()
#         if not au:
#             return JsonResponse({'msg': "该用户不是专家用户"}, status=400)
#         user = au
#         nodes = []
#         edges = []
#         query_set = user.coworkers.all()
#         for n1 in query_set:
#             name = n1.name
#             if name not in nodes:
#                 nodes.append(name)
#             edges.append(
#                 {
#                     'source': user.name,
#                     'target': n1.name,
#                     'weight': 1,
#                     'name': 'coworker'
#                 }
#             )
#             n2_query_set = n1.coworkers.all()
#             for n2 in n2_query_set:
#                 if n2.name in nodes:
#                     edges.append(
#                         {
#                             'source': user.name,
#                             'target': n1.name,
#                             'weight': 1,
#                             'name': 'coworker'
#                         }
#                     )
#                 else:
#                     continue
#         names = [
#             {"name": x} for x in nodes
#         ]
#         names.append(
#             {"name": user.name,
#              "symbol": "star"}
#         )
#         ret = {
#             "nodes": names,
#             "links": edges
#         }
#         return JsonResponse(ret)


class RechargeView(LoginRequiredMixin, APIView):
    '''
        充值视图
    '''
    # 用户认证
    # authentication_classes = [Authentication,]

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
