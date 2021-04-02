import json
import time

from celery.task import task


# 自定义要执行的task任务


@task
def SplitTask(result_id):
    from Product.models import Result, SplitResult
    result = Result.objects.get(id=result_id)
    result.status = 20
    result.save()
    parameter = json.loads(result.parameter) if result.parameter else []
    browsers = json.loads(result.browsers) if result.environments else [1]
    environments = json.loads(result.environments) if result.environments else []
    for browser in browsers:
        if environments:
            for environmentId in environments:
                if parameter:
                    for params in parameter:
                        for k, v in params.items():
                            if v and isinstance(v, str):
                                if '##<time>' in v:
                                    v = v.replace('##<time>',
                                                  time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))
                                if '##<random>' in v:
                                    import random
                                    v = v.replace('##<random>', str(random.randint(1000, 9999)))
                                if '##<null>' == v:
                                    v = None
                                params[k] = v
                        sr = SplitResult.objects.create(environmentId=environmentId, browserId=browser,
                                                        resultId=result.id,
                                                        parameter=json.dumps(params, ensure_ascii=False),
                                                        expect=params.get('expect', True))
                        SplitTaskRunning.delay(sr.id)
                else:
                    sr = SplitResult.objects.create(environmentId=environmentId, browserId=browser, resultId=result.id,
                                                    parameter={}, expect=True)
                    SplitTaskRunning.delay(sr.id)
        else:
            if parameter:
                for params in parameter:
                    for k, v in params.items():
                        if v and isinstance(v, str):
                            if '##<time>' in v:
                                v = v.replace('##<time>', time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))
                            if '##<random>' in v:
                                import random
                                v = v.replace('##<random>', str(random.randint(1000, 9999)))
                            if '##<null>' == v:
                                v = None
                            params[k] = v
                    sr = SplitResult.objects.create(environmentId=0, browserId=browser, resultId=result.id,
                                                    parameter=json.dumps(params, ensure_ascii=False),
                                                    expect=params.get('expect', True))
                    SplitTaskRunning.delay(sr.id)
            else:
                sr = SplitResult.objects.create(environmentId=0, browserId=browser, resultId=result.id,
                                                parameter={}, expect=True)
                SplitTaskRunning.delay(sr.id)
    SplitTaskRan.delay(result_id)


@task
def SplitTaskRan(result_id):
    from Product.models import Result, SplitResult
    result = Result.objects.get(id=result_id)
    while len(SplitResult.objects.filter(resultId=result.id, status__in=[10, 20])) > 0:
        time.sleep(2)
    split_list = SplitResult.objects.filter(resultId=result.id)
    for split in split_list:
        expect = split.expect;
        result_ = True if split.status == 30 else False
        if expect != result_:
            result.status = 40
            result.save()
            return
    result.status = 30
    result.save()
    return


@task
def SplitTaskRunning(splitResult_id):
    from Product.models import SplitResult, Browser, Environment, Element, Check, Result, EnvironmentLogin, LoginConfig
    import django.utils.timezone as timezone
    from MiDuoTester.PageObject.Base import PageObject
    from MiDuoTester.helper.util import get_model
    split = SplitResult.objects.get(id=splitResult_id)
    result_ = Result.objects.get(id=split.resultId)
    steps = json.loads(result_.steps) if result_.steps else []
    parameter = json.loads(split.parameter) if split.parameter else {}
    checkType = result_.checkType
    checkValue = result_.checkValue
    beforeLogin = json.loads(result_.beforeLogin) if result_.beforeLogin else []
    split.status = 20
    split.save()
    split.startTime = timezone.now()
    environment = get_model(Environment, id=split.environmentId)
    host = environment.host if environment and environment.host else ''
    try:
        driver = Browser.objects.get(id=split.browserId).buid()
    except:
        split.status = 40
        split.remark = '浏览器初始化失败'
        split.finishTime = timezone.now()
        split.save()
        return
    if beforeLogin and len(beforeLogin) > 0:  # 判断是否需要登陆 [1,2]
        for bl in beforeLogin:  # 1
            login = get_model(LoginConfig, id=bl)
            loginCheckType = login.checkType
            loginCheckValue = login.checkValue
            if not login:
                split.loginStatus = 3
                split.status = 50
                split.remark = "找不到登陆配置,id=" + str(bl)
                split.finishTime = timezone.now()
                split.save()
                driver.quit()
                return
            loginSteps = json.loads(login.steps) if login.steps else []
            loginParameter = {}
            if environment:
                environmentLogin = get_model(EnvironmentLogin, loginId=bl, environmentId=environment.id)
                if environmentLogin:
                    loginParameter = json.loads(environmentLogin.parameter) if environmentLogin.parameter else {}
            for loginStep in loginSteps:
                try:
                    Step(loginStep.get("keywordId"), loginStep.get("values")).perform(driver, loginParameter, host)
                except Exception as e:
                    split.loginStatus = 2
                    split.status = 50
                    split.remark = "初始化登陆失败[ 登陆名称:" + login.name + " , 错误信息：" + str(e.args)
                    split.finishTime = timezone.now()
                    split.save()
                    driver.quit()
                    return
            if loginCheckType:
                time.sleep(2)
                if loginCheckType == Check.TYPE_URL:
                    if not driver.current_url.endswith(str(loginCheckValue)):
                        split.loginStatus = 2
                        split.status = 50
                        split.remark = "初始化登陆失败[ 登陆名称:" + login.name + " , 错误信息：断言不通过"
                        split.finishTime = timezone.now()
                        split.save()
                        driver.quit()
                        return
                elif loginCheckType == Check.TYPE_ELEMENT:
                    element = loginCheckValue
                    if str(loginCheckValue).isdigit():
                        element = get_model(Element, id=int(loginCheckValue))
                    if not PageObject.find_element(driver, element):
                        split.loginStatus = 2
                        split.status = 50
                        split.remark = "初始化登陆失败[ 登陆名称:" + login.name + " , 错误信息：断言不通过"
                        split.finishTime = timezone.now()
                        split.save()
                        driver.quit()
                        return
        else:
            split.loginStatus = 1
    for step in steps:
        try:
            Step(step.get("keywordId"), step.get("values")).perform(driver, parameter, host)
        except RuntimeError as re:
            split.status = 40
            split.remark = "测试用例执行失败，错误信息:" + str(re.args)
            split.finishTime = timezone.now()
            split.save()
            driver.quit()
            return
        except Exception as info:
            split.status = 40
            split.remark = "执行测试用例时发生错误，请检查测试用例:" + str(info.args)
            split.finishTime = timezone.now()
            split.save()
            driver.quit()
            return
    Test_Result = True
    remark = '测试用例未设置断言,建议设置'
    if checkType:
        time.sleep(2)
        if checkType == Check.TYPE_URL:
            TestResult = driver.current_url.endswith(checkValue)
            if not TestResult:
                Test_Result = False
                if not split.expect:
                    remark = '测试通过'
                else:
                    remark = '测试不通过,预期[' + str(split.expect) + '], 但实际结果为[' + str(TestResult) + ']'
            else:
                Test_Result = True
                if split.expect:
                    remark = '测试通过'
                else:
                    remark = '测试不通过,预期[' + str(split.expect) + '], 但实际结果为[' + str(TestResult) + ']'
        elif checkType == Check.TYPE_ELEMENT:
            element = checkValue
            if str(checkValue).isdigit():
                element = get_model(Element, id=int(element))
            TestResult = True if PageObject.find_element(driver, element) else False
            if not TestResult:
                if not split.expect:
                    remark = '测试通过'
                else:
                    remark = '测试不通过,预期[' + str(split.expect) + '], 但实际结果为[' + str(TestResult) + ']'
            else:
                if split.expect:
                    remark = '测试通过'
                else:
                    remark = '测试不通过,预期[' + str(split.expect) + '], 但实际结果为[' + str(TestResult) + ']'
    split.status = 30 if Test_Result == True else 40
    split.remark = remark
    split.finishTime = timezone.now()
    split.save()
    driver.quit()
    return


class Step:
    def __init__(self, keyword_id, values):
        from .models import Keyword, Params
        from MiDuoTester.helper.util import get_model
        self.keyword = get_model(Keyword, id=keyword_id)
        self.params = [Params(value) for value in values]
        '''
            [
              {
                "isParameter": true,
                "type": "string",
                "key": "用户名",
                "value": "用户名"
              },
              {
                "isParameter": true,
                "type": "string",
                "key": "密码",
                "value": "密码"
              },
              {
                "isParameter": false,
                "type": "string",
                "key": "验证码",
                "value": "1234"
              }
            ]
        '''

    def perform(self, driver, parameter, host):
        from .models import Params, Element
        if self.keyword.type == 1:
            values = list()
            for p in self.params:
                if p.isParameter:
                    if p.Type == Params.TYPE_ELEMENT:
                        v = Element.objects.get(id=parameter.get(p.value, None))
                    else:
                        v = parameter.get(p.value, None)
                elif p.Type == Params.TYPE_ELEMENT:
                    v = Element.objects.get(id=p.value)
                else:
                    v = p.value
                if self.keyword.method == 'open_url' and not ('http://' in v or 'https://' in v):
                    v = host + v
                values.append(v)
            try:
                self.sys_method__run(driver, tuple(values))
            except:
                raise
        elif self.keyword.type == 2:
            steps = json.loads(self.keyword.steps)
            for pa in self.params:
                if not pa.isParameter:
                    if pa.Type == Params.TYPE_ELEMENT:
                        parameter[pa.key] = Element.objects.get(id=pa.value)
                    else:
                        parameter[pa.key] = pa.value
            for step in steps:
                try:
                    Step(step.get("keywordId"), step.get("values")).perform(driver, parameter, host)
                except:
                    raise

    def sys_method__run(self, driver, value):
        package = __import__(self.keyword.package, fromlist=True)
        clazz = getattr(package, self.keyword.clazz)
        setattr(clazz, "driver", driver)
        method = getattr(clazz, self.keyword.method)

        def running(*args):
            c = clazz()
            para = (c,)
            args = para + args[0]
            method(*args)

        try:
            running(value)
        except Exception:
            raise RuntimeError('执行[ ' + self.keyword.name + " ]失败，参数值:  " + str(list(value)))
