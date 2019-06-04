****# API

## 登录 

url: login/  
post:{ username, password}  
return:{code,msg}
1001：用户名或密码错误
1002：请求异常

## 注册

url: register/  
post:{username, password}  
return:{status,msg}
400：该用户名已被注册，换一个试试吧
200：（注册成功，msg无内容）



## 获取个人信息

url: profile/ 
return:{id，username，Type(U为普通用户，E为专家用户)，avatar(头像的url),balance(余额),}

##  个人信息修改

url: profile/
post:一个字典data，可以修改username，balance
return:如果修改成功{id，username，Type(U为普通用户，E为专家用户)，avatar(头像的url),balance(余额),}，如果修改失败，HTTP状态码为400

## 申请成为专家

url: profile/
put:{name}(专家姓名)  
return:成功：{email}邮件所发给的邮箱
失败：{msg,status} msg:申请失败,status=400

## 邮箱验证码验证
url: verify/
post:{token}（用户输入的验证码）
return:{msg}
成功：msg:"申请成功" status:200
失败：mas:"验证码错误" status:400

## 批量收藏

url: star/
post:{资源的标题}  
return:{status，msg}
成功：status:200,msg:收藏成功
失败：status:400,msg:收藏失败

## 批量取消收藏

url: star/
delete:{资源标题}
return:{status，msg}
成功：status:200,msg:已取消收藏
失败：status:400,msg:取消收藏失败

## 获取用户收藏资源

url: star/
get:后端获取登录用户信息
return:{资源名，类型，作者，作者url, 价格,是否已购买}


## 获取用户已购资源

url: buy/
get:后端获取登录用户信息
return:{资源名，类型，作者，作者url，是否已收藏}

## 购买资源
url: buy/
post:{'title'}
return:{msg.status}
status:404 msg:"资源不存在"
status:400 msg:"余额不足"
status:401 msg:"交易失败"
status:200 msg:"交易成功" 还会返回用户余额balance


## 获取专家信息

url: au_profile/
post:{username}
return:{name，email，h_index，g_index，avator， publishes，coworkers，domains,owns} 其中：
publishes为list，为作者所发表的论文，返回示例：'publishes': [{'name': 'Test Paper 1', 'year': 'Test Paper 1', 'authors': [{'name': 'Test'}, {'name': 'Test coworkers'}]}, {'name': 'Test Paper', 'year': 'Test Paper', 'authors': [{'name': 'Test'}, {'name': 'Test coworkers'}]}]其中有两篇论文，返回标题与作者，作者可为多个
coworkers,domains,owns均为list，均可能为空
owns为作者上传的资源，格式与publishes一致
coworkers与domains格式均为[{'name}:'test']

## 获取资源详细信息
url:detail/
post:{Type,title}Type:P1为论文，P2为专利，title为标题
return:论文：{name,year,abstarct,keywords,ci_count,url,price,author1,authors,resource_url,citations,domains}
分别为：论文标题，发表时间，摘要，引用次数，资源链接，价格，第一作者，其他作者，资源文件链接，引用的其他文章，相关领域，其中：authors格式与之前的coworkers相同，citations与之前的publishes格式相同，domains格式不变
专利：{}还需根据数据情况稍作修改
除了以上内容，还有几个数据为公共数据{starred,bought}(True/False)
为当前用户的收藏与购买状态，未登陆时均为False


## 搜索
url:search/
post:{field,content}Field为搜索领域：标题，作者，全文，关键字，发表时间。content为用户输入的搜索内容
return：{Type}P1为论文，P2为专利
{title,authors,time}为标题，作者（发明者），发表时间
