from lib2to3.fixes.fix_input import context

from cloudinary.uploader import upload
from django.conf import settings
from django.db.models import  Q
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from google.auth.transport.requests import Request
from google.cloud import vision
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from rest_framework import status
import json

from django.db.models import  Q
from rest_framework import status, parsers
from lib2to3.fixes.fix_input import context
from cloudinary.uploader import upload
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FileUploadParser, JSONParser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.files.storage import FileSystemStorage
from .models import *
from .serializers import *
from .permissions import *
import json
import base64
import requests
from django.shortcuts import render, redirect
import random
from .vnpay import vnpay
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

# Create your views here.
LIMIT_REPORT = 5
LIMIT_REPORT_DAY = 10
LIMIT_APPROVAL = 3
OAUTH_CREDENTIALS_FILE = "credentials/oauth_client.json"
SCOPES = ["https://www.googleapis.com/auth/cloud-vision"]

class UserViewSet(ViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        user = self.serializer_class.create(self, request.data)
        return Response(self.serializer_class(user, context={'request': request}).data, status=status.HTTP_200_OK)

    @action(methods = ['GET'], detail = False)
    def me(self, request):
        queryset = request.user
        data = {
            'user_info': self.serializer_class(queryset, context={"request": request}).data,
        }
        obj = {}
        if queryset.role == UserRole.CIVILIAN:
            queryset = queryset.civilian_info
            obj = CivilianFromUserSerializer(queryset, context={'request': request})
        elif queryset.role == UserRole.CHARITY_ORG:
            queryset = queryset.charity_org_info
            obj = CharityOrgFromUserSerializer(queryset, context={'request': request})
        data['further_info'] = obj.data
        return Response(data, status=status.HTTP_200_OK)

class DonationCampaignViewSet(ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = DonationCampaign.objects.filter(active=True, is_permitted = True).order_by("-created_date")
    serializer_class = CampagnSerializer
    parser_classes = [parsers.MultiPartParser, ]

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        self.action = self.action_map.get(request.method.lower())
        print(request.content_type)
        if request.method in ['POST'] and self.action == 'add_picture':
            request.parsers = [MultiPartParser(), FileUploadParser()]
        else:
            request.parsers = [JSONParser()]
        return request

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        self.action = self.action_map.get(request.method.lower())
        print(request.content_type)
        if request.method in ['POST'] and self.action in ['add_picture','report']:
            request.parsers = [MultiPartParser(), FileUploadParser()]
        else:
            request.parsers = [JSONParser()]
        return request

    # def get_permissions(self):
    #     if self.action in ['approve','add_picture']:
    #         return [AllowAny()]
    #     if self.action == 'create':
    #         return [IsAuthenticated()]
    #     return [IsAuthenticated()]

    def get_queryset(self):
        q = self.queryset;
        kw = self.request.query_params.get('kw')
        order_flag = self.request.query_params.get('ordered')
        if kw is not None:
            q = q.filter(Q(title__icontains=kw)|Q(content__icontains=kw))
        if order_flag is not None and order_flag == '1':
            print("hello")
            q = q.filter(org__badge__gt=0).order_by("-org__badge")
        return q

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        self.action = self.action_map.get(request.method.lower())
        print(request.content_type)
        if request.method in ['POST'] and self.action == 'report':
            request.parsers = [MultiPartParser(), FileUploadParser()]
        else:
            request.parsers = [JSONParser()]
        return request

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        res = "Not OK"
        if "locations" not in request.data:
            return Response("chưa có nơi cứu trợ", status=status.HTTP_200_OK)
        else:
            locations = request.data.pop("locations")

        supply_type = SupplyType.objects.filter(pk=request.data.pop('supply_type')).first()
        if(supply_type == None):
            return Response("Không tìm thấy loại hình quyên góp", status=status.HTTP_200_OK)
        try:
            with transaction.atomic():
                campaign = DonationCampaign(**request.data)
                campaign.org = request.user.charity_org_info
                campaign.is_permitted = False
                campaign.supply_type = supply_type
                if campaign.expected_charity_end_date < campaign.expected_charity_start_date:
                    raise ValueError("Lỗi thời gian tổ chức quyên góp")
                if campaign.expected_charity_start_date < date.today().__str__():
                    raise ValueError("Không thể xác nhận ngày quyên góp trước thời gian hiện tại")
                campaign.save()

                tmp = 0
                for lct in locations:
                    location = Location.objects.filter(pk=lct['id']).first()
                    if location is not None:
                        cplc = CampaignLocation(campaign = campaign, location = location, expected_fund = lct['expected_fund'])
                        cplc.save()
                        tmp += cplc.expected_fund

                if tmp == 0:
                    raise ValueError("ko tìm thấy bất kì nơi cứu trợ nào")

                if "enclosed" in request.data.keys():
                    for enc in request.data["enclosed"]:
                        tmp = Article.objects.filter(pk=enc).first()
                        if tmp is None:
                            continue
                        campaign.enclosed_article.add(tmp)
                    campaign.save()

                admin = Admin.objects.order_by('?').first()
                print(admin)
                first_approval = Approval(admin= admin, donation=campaign)
                first_approval.save()
                res = self.serializer_class(campaign, context={'request': request}).data
        except Exception as e:
            return Response(e.__str__(), status=status.HTTP_200_OK)
        return Response(res, status=status.HTTP_200_OK)

    @transaction.atomic()
    @action(methods=['POST'], detail=True)
    def add_picture(self, request, pk=None):
        res = []
        campagn = DonationCampaign.objects.filter(pk=pk).first()
        if campagn is None:
            return Response("Không tồn tại", status=status.HTTP_200_OK)
        with transaction.atomic():
            images = request.FILES.getlist('images')
            for image in images:
                cloudinary = upload(image)
                cp = ContentPicture(donation=campagn, path=cloudinary['secure_url'])
                cp.save()
                res.append(cloudinary['secure_url'])
        return Response(res, status=status.HTTP_200_OK)

    @transaction.atomic()
    @action(methods=['POST'], detail=True)
    def report(self, request, pk=None):
        res = "Not OK"
        print(pk)
        campagn = DonationCampaign.objects.filter(pk=pk).first()
        print(campagn)
        if campagn is None:
            return Response("Không tồn tại", status=status.HTTP_200_OK)
        if DonationReport.objects.filter(campaign=campagn).count() >= LIMIT_REPORT:
            return Response("Bạn đã hết số lần nộp báo cáo", status=status.HTTP_200_OK)
        if (date.today() - campagn.expected_charity_end_date).days > LIMIT_REPORT_DAY:
            return Response("Bạn đã quá hạn để báo cáo", status=status.HTTP_200_OK)
        with transaction.atomic():
            rp = DonationReport(campaign=campagn)
            rp.total_used = 0
            rp.save()
            tmp = 0
            details = json.loads(request.data['details'])
            for d in details:
                dt = DetailDonationReport(**d)
                dt.report = rp
                tmp += dt.paid
                dt.save()
            for file in request.FILES.getlist('file'):
                # fs = FileSystemStorage()
                # file_name = fs.save(file.name, file)
                # file_url = fs.url(file_name)
                cloudinary = upload(file)
                dp = DonationReportPicture(report=rp, path=cloudinary['secure_url'])
                dp.save()
            rp.total_used = tmp
            fund = sum(location.current_fund for location in campagn.locations.all())
            rp.total_left = fund - tmp
            rp.save()

            if rp.total_used == 0:
                return Response("Số tiền bạn quyên góp là 0, Cảnh Báo", status=status.HTTP_200_OK)
            if rp.total_left > 500000:
                return Response("Số tiền bạn quyên góp còn dư quá nhiều, Cảnh Báo", status=status.HTTP_200_OK)
        return Response(res, status=status.HTTP_200_OK)

    @transaction.atomic()
    @action(methods = ['POST'], detail = True)
    def cancel(self, request, pk=None):
        res = "Not OK"
        campagn = DonationCampaign.objects.filter(pk=pk).first()
        if campagn is None:
            return Response("Không tồn tại", status=status.HTTP_200_OK)
        if not campagn.is_permitted:
            return Response("Hoạt động này đang diễn ra, không thể huỷ", status=status.HTTP_200_OK)
        with transaction.atomic():
            campagn.active = False
            campagn.save()
            res = "Huỷ thành công"
        return Response(res, status=status.HTTP_200_OK)

    @transaction.atomic()
    @action(methods=['POST'], detail=True)
    def approve(self, request,pk=None):
        admin = Admin.objects.filter(user_info_id=request.data['cur_admin']).first()

        if admin is None:
            return Response("Không tìm thấy admin hiện tại", status=status.HTTP_403_FORBIDDEN)
        campaign = DonationCampaign.objects.filter(pk=pk).first()
        if campaign is None:
            return Response("Không tồn tại", status=status.HTTP_200_OK)
        approval = Approval.objects.filter(donation=campaign,is_approved=None).first()
        approval.is_approved = True
        is_final = request.data['is_final']

        if approval.time_id < LIMIT_APPROVAL and not is_final:
            ad = Admin.objects.filter(user_info_id= request.data['next_admin']).first()
            time_id = approval.time_id + 1
            tmp = Approval(admin= ad, donation=campaign, time_id = time_id, created_date = date.today())
            tmp.save()
            print(tmp)
        elif approval.time_id == LIMIT_APPROVAL or is_final:
            approval.is_final = True
            campaign.is_permitted = True
            campaign.save()
        approval.save()
        res = "OK"
        return Response(res, status=status.HTTP_200_OK)

class DonationReportViewSet(ViewSet, generics.ListAPIView):
    queryset = DonationReport.objects.filter(active=True)
    serializer_class = ReportSerializer

    @transaction.atomic()
    @action(methods=['POST'], detail=True)
    def approve(self, request, pk=None):
        admin = Admin.objects.filter(user_info_id=request.data['cur_admin']).first()
        if admin is None:
            return Response("Không tìm thấy admin hiện tại", status=status.HTTP_403_FORBIDDEN)
        report = DonationReport.objects.filter(pk=pk).first()
        if report is None:
            return Response("Không tồn tại", status=status.HTTP_200_OK)
        approval = Confimation(admin_id=request.user.id, report = report)
        approval.save()
        return Response(self.serializer_class(approval, context = {"request": request}), status=status.HTTP_200_OK)

class DonationPostViewSet(ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = DonationPost.objects.filter(active=True).exclude(donationpostapproval=None).order_by("-created_date")
    serializer_class = PostSerializer

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        self.action = self.action_map.get(request.method.lower())
        print(request.content_type)
        if request.method in ['POST'] and self.action in ['add_picture', 'create', 'analyze_picture']:
            request.parsers = [MultiPartParser(), FileUploadParser()]
        else:
            request.parsers = [JSONParser()]
        return request

    def create(self, request, *args, **kwargs):
        res = "NOT OK"
        with transaction.atomic():
            post = DonationPost(civilian_id = request.user.id, content = request.data['content'])
            post.save()
            images = request.FILES.getlist('images')
            print(images)
            for image in images:
                cloudinary = upload(image)
                pic = DonationPostPicture(post=post, picture=cloudinary['secure_url'])
                pic.save()
            res = self.serializer_class(post).data
        return Response(res, status=status.HTTP_200_OK)


    @action(methods=['POST'], detail=False)
    def analyze_picture(self, request):
        print("hello")
        if "credentials" not in request.session:
            return HttpResponseRedirect(reverse("start_oauth"))

        credentials_data = json.loads(request.session["credentials"])
        credentials = Credentials.from_authorized_user_info(credentials_data)

        if not credentials.valid and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

        vision_client = build("vision", "v1", credentials=credentials)

        image_files = request.FILES.getlist("images")
        for img in image_files:
            content = base64.b64encode(img.read()).decode("utf-8")
            data = {
                "requests": [
                    {
                        "image": {"content": content},
                        "features": [{"type": "LABEL_DETECTION", "maxResults": 5}],
                    }
                ]
            }
            response = vision_client.images().annotate(body=data).execute()

            request.session["credentials"] = json.dumps({
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes,
            })
            print(content)
            print(response)
            if response.status_code == 200:
                result = response.json()
                labels = result["responses"][0].get("labelAnnotations", [])
                print(labels)
        return Response("OK", status=status.HTTP_200_OK)

    @transaction.atomic()
    @action(methods=['POST'], detail=True)
    def approve(self, request, pk=None):
        admin = Admin.objects.filter(user_info_id=request.data['cur_admin']).first()
        print(admin)
        if admin is None:
            return Response("Không tìm thấy admin hiện tại", status=status.HTTP_403_FORBIDDEN)
        post = DonationPost.objects.filter(pk=pk).first()
        if post is None:
            return Response("Không tồn tại", status=status.HTTP_200_OK)
        approval = DonationPostApproval(admin = admin, post=post, priority = request.data['priority'])
        approval.save()
        return Response("OK", status=status.HTTP_200_OK)

class SupplyTypeViewSet(ViewSet, generics.ListAPIView):
    queryset =  SupplyType.objects.filter(active=True)
    serializer_class = SupplyTypeSerializer
    # permission_classes = [IsAuthenticated]

class LocationViewSet(ViewSet, generics.ListAPIView):
    queryset = Location.objects.filter(active=True).order_by("location")
    serializer_class = LocationSerializer
    # permission_classes = [IsAuthenticated]

    @action(methods = ["GET"], detail= False)
    def in_need(self, request):
        qs = Location.objects.filter(active=True).exclude(status=LocationState.NORMAL)
        return Response(LocationSerializer(qs, context={"request": request}).data, status = status.HTTP_200_OK)

class ArticleViewSet(ViewSet, generics.ListAPIView, generics.CreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    def get_permissions(self):
        return [AllowAny()]


def start_oauth(request):
    """Start OAuth 2.0 authorization flow."""
    flow = Flow.from_client_secrets_file(
        OAUTH_CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=request.build_absolute_uri(reverse("oauth_callback"))
    )
    authorization_url, state = flow.authorization_url(prompt="consent")
    request.session["oauth_state"] = state
    print(authorization_url)
    return HttpResponseRedirect(authorization_url)


def oauth_callback(request):
    """Handle the callback from the OAuth server."""
    state = request.session.get("oauth_state")

    if not state:
        return HttpResponse("State missing in session.", status=400)

    flow = Flow.from_client_secrets_file(
        OAUTH_CREDENTIALS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=request.build_absolute_uri(reverse("oauth_callback"))
    )
    flow.fetch_token(authorization_response=request.build_absolute_uri())

    credentials = flow.credentials
    request.session["credentials"] = json.dumps({
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    })
    return HttpResponseRedirect(reverse("analyze_image"))

def index(request):
    return render(request, "payment/index.html", {"title": "Danh sách demo"})


def hmacsha512(key, data):
    byteKey = key.encode('utf-8')
    byteData = data.encode('utf-8')
    return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()


def payment(request):

    if request.method == 'POST':
        # Process input data and build url payment
        form = PaymentForm(request.POST)
        if form.is_valid():
            order_type = form.cleaned_data['order_type']
            order_id = form.cleaned_data['order_id']
            amount = form.cleaned_data['amount']
            order_desc = form.cleaned_data['order_desc']
            bank_code = form.cleaned_data['bank_code']
            language = form.cleaned_data['language']
            ipaddr = get_client_ip(request)
            # Build URL Payment
            vnp = vnpay()
            vnp.requestData['vnp_Version'] = '2.1.0'
            vnp.requestData['vnp_Command'] = 'pay'
            vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
            vnp.requestData['vnp_Amount'] = amount * 100
            vnp.requestData['vnp_CurrCode'] = 'VND'
            vnp.requestData['vnp_TxnRef'] = order_id
            vnp.requestData['vnp_OrderInfo'] = order_desc
            vnp.requestData['vnp_OrderType'] = order_type
            # Check language, default: vn
            if language and language != '':
                vnp.requestData['vnp_Locale'] = language
            else:
                vnp.requestData['vnp_Locale'] = 'vn'
                # Check bank_code, if bank_code is empty, customer will be selected bank on VNPAY
            if bank_code and bank_code != "":
                vnp.requestData['vnp_BankCode'] = bank_code

            vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')  # 20150410063022
            vnp.requestData['vnp_IpAddr'] = ipaddr
            vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
            vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
            print(vnpay_payment_url)
            return redirect(vnpay_payment_url)
        else:
            print("Form input not validate")
    else:
        user_id = request.GET.get('user_id')
        campaign_id = request.GET.get('campaign_id')
        type = request.GET.get('type')
        response = render(request, "payment/payment.html", {"title": "Thanh toán"})
        response.set_cookie('user_id', user_id, max_age=600)
        response.set_cookie('campaign_id', campaign_id, max_age=600)
        response.set_cookie('type', type, max_age=600)
        return response


def payment_ipn(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        amount = inputData['vnp_Amount']
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            # Check & Update Order Status in your Database
            # Your code here
            firstTimeUpdate = True
            totalamount = True
            if totalamount:
                if firstTimeUpdate:
                    if vnp_ResponseCode == '00':
                        print('Payment Success. Your code implement here')
                    else:
                        print('Payment Error. Your code implement here')

                    # Return VNPAY: Merchant update success
                    result = JsonResponse({'RspCode': '00', 'Message': 'Confirm Success'})
                else:
                    # Already Update
                    result = JsonResponse({'RspCode': '02', 'Message': 'Order Already Update'})
            else:
                # invalid amount
                result = JsonResponse({'RspCode': '04', 'Message': 'invalid amount'})
        else:
            # Invalid Signature
            result = JsonResponse({'RspCode': '97', 'Message': 'Invalid Signature'})
    else:
        result = JsonResponse({'RspCode': '99', 'Message': 'Invalid request'})

    return result


def payment_return(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        amount = int(inputData['vnp_Amount']) / 100
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            if vnp_ResponseCode == "00":
                uid = request.COOKIES.get('user_id')
                cid = request.COOKIES.get('campaign_id')
                type = request.COOKIES.get('type')
                if type == 'campaign':
                    Donation.objects.create(civilian_id=uid, campaign_id= cid, donated=amount)
                    cp = CampaignLocation.objects.filter(pk=cid).first()
                    cp.current_fund += amount
                    cp.save()
                elif type == 'post':
                    DonationPostHistory.objects.create(user_id=uid,post_id=cid, donated=amount)
                return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán",
                                                               "result": "Thành công", "order_id": order_id,
                                                               "amount": amount,
                                                               "order_desc": order_desc,
                                                               "vnp_TransactionNo": vnp_TransactionNo,
                                                               "vnp_ResponseCode": vnp_ResponseCode})
            else:
                return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán",
                                                               "result": "Lỗi", "order_id": order_id,
                                                               "amount": amount,
                                                               "order_desc": order_desc,
                                                               "vnp_TransactionNo": vnp_TransactionNo,
                                                               "vnp_ResponseCode": vnp_ResponseCode})
        else:
            return render(request, "payment/payment_return.html",
                          {"title": "Kết quả thanh toán", "result": "Lỗi", "order_id": order_id, "amount": amount,
                           "order_desc": order_desc, "vnp_TransactionNo": vnp_TransactionNo,
                           "vnp_ResponseCode": vnp_ResponseCode, "msg": "Sai checksum"})
    else:
        return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán", "result": ""})


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

n = random.randint(10**11, 10**12 - 1)
n_str = str(n)
while len(n_str) < 12:
    n_str = '0' + n_str


def query(request):
    if request.method == 'GET':
        return render(request, "payment/query.html", {"title": "Kiểm tra kết quả giao dịch"})

    url = settings.VNPAY_API_URL
    secret_key = settings.VNPAY_HASH_SECRET_KEY
    vnp_TmnCode = settings.VNPAY_TMN_CODE
    vnp_Version = '2.1.0'

    vnp_RequestId = n_str
    vnp_Command = 'querydr'
    vnp_TxnRef = request.POST['order_id']
    vnp_OrderInfo = 'kiem tra gd'
    vnp_TransactionDate = request.POST['trans_date']
    vnp_CreateDate = datetime.now().strftime('%Y%m%d%H%M%S')
    vnp_IpAddr = get_client_ip(request)

    hash_data = "|".join([
        vnp_RequestId, vnp_Version, vnp_Command, vnp_TmnCode,
        vnp_TxnRef, vnp_TransactionDate, vnp_CreateDate,
        vnp_IpAddr, vnp_OrderInfo
    ])

    secure_hash = hmac.new(secret_key.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

    data = {
        "vnp_RequestId": vnp_RequestId,
        "vnp_TmnCode": vnp_TmnCode,
        "vnp_Command": vnp_Command,
        "vnp_TxnRef": vnp_TxnRef,
        "vnp_OrderInfo": vnp_OrderInfo,
        "vnp_TransactionDate": vnp_TransactionDate,
        "vnp_CreateDate": vnp_CreateDate,
        "vnp_IpAddr": vnp_IpAddr,
        "vnp_Version": vnp_Version,
        "vnp_SecureHash": secure_hash
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_json = json.loads(response.text)
    else:
        response_json = {"error": f"Request failed with status code: {response.status_code}"}

    return render(request, "payment/query.html", {"title": "Kiểm tra kết quả giao dịch", "response_json": response_json})

def refund(request):
    if request.method == 'GET':
        return render(request, "payment/refund.html", {"title": "Hoàn tiền giao dịch"})

    url = settings.VNPAY_API_URL
    secret_key = settings.VNPAY_HASH_SECRET_KEY
    vnp_TmnCode = settings.VNPAY_TMN_CODE
    vnp_RequestId = n_str
    vnp_Version = '2.1.0'
    vnp_Command = 'refund'
    vnp_TransactionType = request.POST['TransactionType']
    vnp_TxnRef = request.POST['order_id']
    vnp_Amount = request.POST['amount']
    vnp_OrderInfo = request.POST['order_desc']
    vnp_TransactionNo = '0'
    vnp_TransactionDate = request.POST['trans_date']
    vnp_CreateDate = datetime.now().strftime('%Y%m%d%H%M%S')
    vnp_CreateBy = 'user01'
    vnp_IpAddr = get_client_ip(request)

    hash_data = "|".join([
        vnp_RequestId, vnp_Version, vnp_Command, vnp_TmnCode, vnp_TransactionType, vnp_TxnRef,
        vnp_Amount, vnp_TransactionNo, vnp_TransactionDate, vnp_CreateBy, vnp_CreateDate,
        vnp_IpAddr, vnp_OrderInfo
    ])

    secure_hash = hmac.new(secret_key.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

    data = {
        "vnp_RequestId": vnp_RequestId,
        "vnp_TmnCode": vnp_TmnCode,
        "vnp_Command": vnp_Command,
        "vnp_TxnRef": vnp_TxnRef,
        "vnp_Amount": vnp_Amount,
        "vnp_OrderInfo": vnp_OrderInfo,
        "vnp_TransactionDate": vnp_TransactionDate,
        "vnp_CreateDate": vnp_CreateDate,
        "vnp_IpAddr": vnp_IpAddr,
        "vnp_TransactionType": vnp_TransactionType,
        "vnp_TransactionNo": vnp_TransactionNo,
        "vnp_CreateBy": vnp_CreateBy,
        "vnp_Version": vnp_Version,
        "vnp_SecureHash": secure_hash
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_json = json.loads(response.text)
    else:
        response_json = {"error": f"Request failed with status code: {response.status_code}"}

    return render(request, "payment/refund.html", {"title": "Kết quả hoàn tiền giao dịch", "response_json": response_json})