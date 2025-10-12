import time
from pom.VipPage import Vip
from pom.Etc import Etc
from utils.TimeLogger import TimeLogger
from utils.db_check import DatabricksSPClient
import pytest
from case_data.vip_data import vip_testcases1, vip_testcases2, vip_testcases3, vip_testcases4
import json
import io
import contextlib
from datetime import datetime, timedelta

#pipenv run pytest --cache-clear test.py

@pytest.fixture(scope="module")
def file_start_time():
    # 이 모듈(파일) 내 테스트가 처음 실행될 때 한 번만 호출됨
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
@pytest.fixture(scope="module")
def file_start_dt():
    # 이 모듈(파일) 내 테스트가 처음 실행될 때 한 번만 호출됨
    return datetime.now().strftime("%Y%m%d")
@pytest.fixture(scope="module")
def file_start_hour():
    # 이 모듈(파일) 내 테스트가 처음 실행될 때 한 번만 호출됨
    return datetime.now().strftime("%H")


@pytest.mark.flaky(reruns=2, reruns_delay=1)
@pytest.mark.parametrize("goods_num, case_id", vip_testcases1, ids=[c for _, c in vip_testcases1])
def test_vip_1(page, goods_num, case_id, request):
    request.node._testrail_case_id = case_id
    etc = Etc(page)
    vip_page = Vip(page)
    logger = TimeLogger("json/test_vip.json")

    output_content = io.StringIO()
    with contextlib.redirect_stdout(output_content):
        # g마켓 홈 으로 이동
        etc.goto()
        # 일반회원 로그인
        etc.login()
        # vip 로 이동
        etc.goto_vip(goods_num)
        # 상품 노출 확인시간 저장
        logger.record_time("case1", goods_num, "exposure")
        # VT 모듈로 이동 후 확인
        vip_page.vip_module_by_title("함께 보면 좋은 상품이에요")
        # 광고상품 상품 번호 추출
        result = vip_page.assert_item_in_module("함께 보면 좋은 상품이에요")
        goodscode = result["goodscode"]
        # 상품 번호 저장
        logger.record_goodscode("case1",goods_num, goodscode)
        target = result["target"]
        # 상품 클릭시간 저장
        logger.record_time("case1", goods_num, "click")
        # 상품 클릭후 해당 vip 이동 확인
        vip_page.click_goods(goodscode, target)
    # hook에서 사용하기 위해 item에 저장
    request.node._stdout_capture = output_content.getvalue()

@pytest.mark.flaky(reruns=2, reruns_delay=1)
@pytest.mark.parametrize("goods_num, case_id", vip_testcases2, ids=[c for _, c in vip_testcases2])
def test_vip_2(page, goods_num, case_id, request):
    request.node._testrail_case_id = case_id
    logger = TimeLogger("json/test_vip.json")
    etc = Etc(page)
    vip_page = Vip(page)
    output_content = io.StringIO()
    with contextlib.redirect_stdout(output_content):
        # g마켓 홈 으로 이동
        etc.goto()
        # 일반회원 로그인
        etc.login()
        # vip 로 이동
        etc.goto_vip(goods_num)
        # 상품 노출 확인시간 저장
        logger.record_time("case2", goods_num, "exposure")
        # BT 모듈로 이동 후 확인
        parent = vip_page.vip_module_by_title("함께 구매하면 좋은 상품이에요")
        # 광고 태그 확인
        result = vip_page.check_bt_ad_tag(parent)
        goodscode = result["goodscode"]
        # 광고상품 상품 번호 추출
        logger.record_goodscode("case2", goods_num, goodscode)
        target = result["target"]
        # 상품 클릭시간 저장
        logger.record_time("case2", goods_num, "click")
        # 상품 클릭후 해당 vip 이동 확인
        vip_page.click_goods(goodscode, target)

    # hook에서 사용하기 위해 item에 저장
    request.node._stdout_capture = output_content.getvalue()

def test_wait_15min():
    # -----------------------------
    # DB에 데이터가 쌓일 때까지 대기
    # 약 15분 30초 (930초) 동안 대기
    # -----------------------------
    print("DB 데이터 반영 대기 시작... 약 15분 30초 대기합니다.")
    time.sleep(930)  # 실제 대기

click_db = None
imp_db = None
vimp_db = None
click_db_ai = None
imp_db_ai = None
vimp_db_ai = None

def test_fetch_from_db(file_start_time, file_start_dt, file_start_hour):
    db_check = DatabricksSPClient()  # Databricks 클라이언트 객체 생성

    # 전역 변수로 조회 결과를 저장 (다른 테스트에서 재사용)
    global click_db, imp_db, vimp_db, click_db_ai, imp_db_ai, vimp_db_ai

    with open("json/test_vip.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # 상품번호만 뽑기
    product_ids = []
    for case_group in data:
        for case, items in case_group.items():
            for _, info in items.items():
                product_ids.append(info["상품번호"])

    # 4. AI 매출업 클릭 로그(click_db) 조회
    sql = f"""
    SELECT item_no, ins_date
    FROM baikali1xs.ad_ats_silver.ub_ra_click_gmkt
    WHERE ins_date >= '{file_start_time}'
      AND cguid = '11758850530814005372000000'
      AND dt = '{file_start_dt}'
      AND hour IN ('{file_start_hour}', '{int(file_start_hour) + 1:02d}');
    """
    click_db_ai = db_check.query_databricks(sql)
    time.sleep(10)  # 조회 후 10초 대기 (DB 처리 반영 시간 고려)

    # 5. AI 매출업 노출 로그(imp_db) 조회
    sql = f"""
    SELECT item_no, ins_date
    FROM baikali1xs.ad_ats_silver.ub_ra_imp_gmkt
    WHERE ins_date >= '{file_start_time}'
      AND cguid = '11758850530814005372000000'
      AND item_no IN ({','.join(map(str, product_ids))})
      AND dt = '{file_start_dt}'
      AND hour IN ('{file_start_hour}', '{int(file_start_hour) + 1:02d}');
    """
    imp_db_ai = db_check.query_databricks(sql)
    time.sleep(10)  # 조회 후 10초 대기

    # 6. AI 매출업 가상노출 로그(vimp_db) 조회
    sql = f"""
    SELECT item_no, ins_date
    FROM baikali1xs.ad_ats_silver.ub_ra_vimp_gmkt
    WHERE ins_date >= '{file_start_time}'
      AND cguid = '11758850530814005372000000'
      AND item_no IN ({','.join(map(str, product_ids))})
      AND dt = '{file_start_dt}'
      AND hour IN ('{file_start_hour}', '{int(file_start_hour) + 1:02d}');
    """
    vimp_db_ai = db_check.query_databricks(sql)


@pytest.mark.flaky(reruns=2, reruns_delay=1)
@pytest.mark.parametrize("goods_num, case_id", vip_testcases3, ids=[c for _, c in vip_testcases3])
def test_srp_3(goods_num, case_id, request):
    # TestRail 케이스 ID를 현재 실행 노드에 저장
    request.node._testrail_case_id = case_id
    db_check = DatabricksSPClient()
    with open("json/test_vip.json", "r", encoding="utf-8") as f:
        test_record = json.load(f)
    output_content = io.StringIO()
    with contextlib.redirect_stdout(output_content):
        # JSON에서 테스트에 필요한 값 추출
        goodscode = test_record[0]["case1"][goods_num]["상품번호"]   # 상품 번호
        click_time = test_record[0]["case1"][goods_num]["click"]     # 클릭 발생 시간
        expose_time = test_record[0]["case1"][goods_num]["exposure"] # 노출 발생 시간

        # DB 기록 검증
        # - click_db : 클릭 로그 DB, 클릭 시간 검증
        # - imp_db   : 노출 로그 DB, 노출 시간 검증
        # - vimp_db  : 가상 노출 로그 DB, 노출 시간 검증
        db_check.assert_db_record_time(click_db_ai, click_time, goodscode)
        db_check.assert_db_record_time(imp_db_ai, expose_time, goodscode)
        db_check.assert_db_record_time(vimp_db_ai, expose_time, goodscode)

    # hook에서 사용하기 위해 item에 저장
    request.node._stdout_capture = output_content.getvalue()


@pytest.mark.flaky(reruns=2, reruns_delay=1)
@pytest.mark.parametrize("goods_num, case_id", vip_testcases4, ids=[c for _, c in vip_testcases4])
def test_srp_4(goods_num, case_id, request):
    # TestRail 케이스 ID를 현재 실행 노드에 저장
    request.node._testrail_case_id = case_id
    db_check = DatabricksSPClient()
    with open("json/test_vip.json", "r", encoding="utf-8") as f:
        test_record = json.load(f)
    output_content = io.StringIO()
    with contextlib.redirect_stdout(output_content):
        # JSON에서 테스트에 필요한 값 추출
        goodscode = test_record[0]["case2"][goods_num]["상품번호"]  # 상품 번호
        click_time = test_record[0]["case2"][goods_num]["click"]  # 클릭 발생 시간
        expose_time = test_record[0]["case2"][goods_num]["exposure"]  # 노출 발생 시간

        # DB 기록 검증
        # - click_db : 클릭 로그 DB, 클릭 시간 검증
        # - imp_db   : 노출 로그 DB, 노출 시간 검증
        # - vimp_db  : 가상 노출 로그 DB, 노출 시간 검증
        db_check.assert_db_record_time(click_db_ai, click_time, goodscode)
        db_check.assert_db_record_time(imp_db_ai, expose_time, goodscode)
        db_check.assert_db_record_time(vimp_db_ai, expose_time, goodscode)

    # hook에서 사용하기 위해 item에 저장
    request.node._stdout_capture = output_content.getvalue()