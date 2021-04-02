from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, "page/首页.html")


def project(request):
    return render(request, "page/2项目管理.html")


def project_config(request, project_id):
    from Product.models import Project
    from MiDuoTester.helper.util import get_model
    p = get_model(Project, id=project_id)
    name = p.name if p else ""
    return render(request, "page/2项目管理--环境配置.html", {"projectId": project_id, "projectName": name})


def page(request):
    return render(request, "page/3页面管理.html")


def element(request):
    return render(request, "page/4页面元素.html")


def keyword(request):
    return render(request, "page/5关键字库.html")


def keyword_create(request):
    return render(request, "page/5-1新建关键字.html")


def keyword_edit(request, keyword_id):
    from Product.models import Keyword, Project
    from MiDuoTester.helper.util import get_model
    kw = get_model(Keyword, id=keyword_id)
    projectId = kw.projectId if kw else 0
    p = get_model(Project, id=projectId)
    projectName = p.name if projectId > 0 and p else "通用"
    keywordName = kw.name if kw else ""
    return render(request, "page/5-2编辑关键字.html",
                  {"id": projectId, "projectName": projectName, "keywordId": keyword_id, "keywordName": keywordName})


def testcase(request):
    return render(request, "page/6测试用例.html")


def testcase_create(request):
    return render(request, "page/6-1新建测试用例.html")


def testcase_edit(request, testcase_id):
    return render(request, "page/6-1编辑测试用例.html", {"testcaseId": testcase_id})


def result(request):
    return render(request, "page/7测试结果.html")


def result_see(request, result_id):
    return render(request, "page/7-1查看测试结果.html", {"id": result_id})


def task(request):
    return render(request, "page/9任务管理.html")


def loginConfig(request):
    return render(request, "page/8登录配置.html")


def loginConfig_create(request):
    return render(request, "page/8-1新建登录配置.html")


def loginConfig_edit(request, login_id):
    return render(request, "page/8-1编辑登录配置.html", {"id": login_id})
