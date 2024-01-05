import requests
import json
from io import BytesIO
import io
from PIL import Image
from leadogconfig import *
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# TODO 根据域名查询相关信息
domainRes = requests.post(
    "http://xxl-dm.leadong.com/site/selectSiteInfoByDomain?domain=" + globalNewSiteDomain,proxies=proxiesBeta)
if domainRes.status_code == 200:
    domainInfo = json.loads(domainRes.text)
    comId = domainInfo["comId"]
    lanCode = domainInfo["lanCode"]
    logonName = domainInfo["logonName"]
    print(domainInfo) # {'siteSettingId': 415564, 'logonName': 'demo-litianjie', 'comId': 159804, 'lanCode': 0}

# 图片URL统一预处理
def photoUrlPreHandle(prodPhotoUrl):
    global globalDiyPhotoDomain
    #在这里调整使用http还是https
    scheme = "http:"
    if prodPhotoUrl.find("http://") == -1 and prodPhotoUrl.find("https://") == -1:
        if prodPhotoUrl.startswith("//"):
            prodPhotoUrl = scheme + prodPhotoUrl
        else:
            if len(globalDiyPhotoDomain):
                prodPhotoUrl = scheme + "//" + globalDiyPhotoDomain + prodPhotoUrl
            else:
                prodPhotoUrl = scheme + "//" + globalSiteDomain + prodPhotoUrl
    return  prodPhotoUrl


# 处理图片
def uploadToLeadongSystem(prodPhotoUrl):
    if prodPhotoUrl == None:
        return
        # 预处理图片URL
    prodPhotoUrl = photoUrlPreHandle(prodPhotoUrl)
    photoName = None
    try:
        picdomaininfo = prodPhotoUrl.replace('https://', '').replace('http://', '')
        infos = picdomaininfo.split('/')
        picdomain = infos[0]
        headersPic = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                      'Accept-Encoding': 'gzip, deflate, sdcn',
                      'Accept-Language': 'en-us;q=0.5,en;q=0.3',
                      'Cache-Control': 'max-age=0',
                      'Connection': 'keep-alive',
                      'Cookie': 'Site_Name=%E5%B9%BF%E4%B8%9C%E6%B1%89%E9%AB%98%E7%A7%91%E6%8A%80%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8; Site_Domain=www.hangaotech.com; Site_SubDomain=hangaotech.com; Name=site-2009231956-1.jumiweb.com; Site_EndTime=2023-12-04; Site_PackageType=3; Site_Id=069b7001fe004962908ae516bc46abcb; Site_ga_view_id=1; .AspNetCore.Session=CfDJ8Cw3ULz3j2hMlYWRSJzZMbj2uWuAvIPmoB4kVUDjp3BbEd0JgKA0EUwzyLw8HSAENPaFmeSHXi%2B%2B8gwMRyDPGWEIyaWzgoA1360Gj%2F4FonDor8eeWyq6nSTiZmFYiHa8CXtqW4czn%2FsJzfcvIxN6DCM7K7hLOHZF3f%2Fo6%2Fy%2Bm1yT; cf_clearance=.tVheXSoJRiT1zzyE5tqlR5b1ely4U2F.647V.on_aw-1701328776-0-1-51c6be7e.ace2558e.cbc673d2-0.2.1701328776',
                      'referer': picdomain,
                      'Host': picdomain,
                      'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 ('
                                    'KHTML, '
                                    'like Gecko) Chrome/77.0.3865.90 Safari/537.36'
                      }
        global globalIsUseVpn
        if "1" == globalIsUseVpn:
            response = requests.get(prodPhotoUrl, timeout=160, proxies=proxiesVpn).content
        else:
            # response = requests.get(prodPhotoUrl, timeout=60, headers=headersPic, verify=False)
            response = requests.get(prodPhotoUrl, timeout=160).content
        if response is None:
            print('下载失败！！！  请检查 url ' + prodPhotoUrl)
            return None
        print(prodPhotoUrl + " download success!")
        prodPhotoUrl = prodPhotoUrl.split("?")[0]
        photoName = prodPhotoUrl[prodPhotoUrl.rindex('/') + 1:]
    except requests.exceptions.RequestException as e:
        pass
    except:
        pass
    if photoName == None:
        return None
    context = response
    try:
        # 资料库无法上传webp图片，所以需要处理下载的图片
        byte_stream = BytesIO(response)
        roiImg = Image.open(byte_stream)  # Image打开Byte字节流数据
        imgByteArr = io.BytesIO()  # 创建一个空的Bytes对象
        roiImg.save(imgByteArr, format='PNG')  # PNG就是图片格式，我试过换成JPG/jpg都不行
        context = imgByteArr.getvalue()  # 这个就是保存的图片字节流
    except:
        pass
    # if response.status_code == 404:
    #     print("get photo 404 !!!!!! : %s" % prodPhotoUrl)
    #     return 404
    # if response.status_code != 200:
    #     return None
    metaType = "image/png"
    names = photoName.split("?")
    photoName = names[0]
    if photoName.endswith("png"):
        metaType = "image/png"
    if photoName.endswith(".jpg.webp"):
        photoName = photoName.replace('.jpg.webp', '.jpg')
    if photoName.endswith("webp"):
        photoName = photoName.replace('webp', 'jpg')
    files = {'filedata': (photoName, context,
                          metaType)}
    # logging.info(f"files: {files}")
    print("start upload photo: %s" % prodPhotoUrl)
    while True:
        try:
            '''
            资料库url
            '''
            global globalFfsUrl
            ffsUrl = globalFfsUrl + "&referType=9"
            logging.info("ffsUrl: %s" % ffsUrl)
            req = requests.post(ffsUrl, files=files)
            break
        except requests.exceptions.ProxyError as e:
            print("======!!!!!!上传失败")
            pass
    print("end upload photo: %s" % prodPhotoUrl)
    # print(req.content)
    # url = req.content["uploads"][0]["url"]
    url = json.loads(req.content)["uploads"][0]["url"]
    return url

if __name__ == '__main__':

    img_url = input("请输入图片链接：")
    # https://oaidalleapiprodscus.blob.core.windows.net/private/org-NPF8YbcBZUgltucCB1yi3PKy/user-wwPLAKPrvCxn3z2mj9JofFS3/img-NgeLK9WIwrAFmWwFS9pyNUg5.png?st=2024-01-05T07%3A59%3A00Z&amp;se=2024-01-05T09%3A59%3A00Z&amp;sp=r&amp;sv=2021-08-06&amp;sr=b&amp;rscd=inline&amp;rsct=image/png&amp;skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&amp;sktid=a48cca56-e6da-484e-a814-9c849652bcb3&amp;skt=2024-01-05T04%3A59%3A44Z&amp;ske=2024-01-06T04%3A59%3A44Z&amp;sks=b&amp;skv=2021-08-06&amp;sig=SnDiHRBLEi54KvV%2ByXilzvJ1rDW1%2B11dxz5OuJ0CpEU%3D
    res = uploadToLeadongSystem(img_url)
    print(res)
