import shutil
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, ViewportSize
from src.gtas_python_core_v2.gtas_python_core_vault_v2 import Vault
import json
import os
import pytest
import requests
from datetime import datetime

# 브라우저 fixture (세션 단위, 한 번만 실행)
@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # True/False로 headless 제어
        yield browser
        browser.close()


# 컨텍스트 fixture (브라우저 환경)
@pytest.fixture(scope="function")
def context(browser: Browser):
    context = browser.new_context(
        viewport=ViewportSize(width=420, height=844),
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
        device_scale_factor=3,
        is_mobile=True,
        has_touch=True,
    )

    # navigator.webdriver 우회
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

    yield context
    context.close()


# 페이지 fixture
@pytest.fixture(scope="function")
def page(context: BrowserContext):
    page = context.new_page()
    page.set_default_timeout(10000)  # 기본 10초 타임아웃
    yield page
    page.close()

def pytest_report_teststatus(report, config):
    # 이름에 'wait_'가 들어간 테스트는 리포트 출력에서 숨김
    if any(keyword in report.nodeid for keyword in ["wait_", "fetch"]):
        return report.outcome, None, ""
    return None

#
# with open('config.json') as config_file:
#     config = json.load(config_file)
#
# # 환경변수 기반 설정
# TESTRAIL_BASE_URL = config['tr_url']
# TESTRAIL_PROJECT_ID = config['project_id']
# TESTRAIL_SUITE_ID = config['suite_id']
# TESTRAIL_SECTION_ID = config['section_id']  # ✅ 섹션 이름으로 지정
# TESTRAIL_USER = (Vault("gmarket").get_Kv_credential("authentication/testrail/automation")).get("username")
# TESTRAIL_TOKEN = (Vault("gmarket").get_Kv_credential("authentication/testrail/automation")).get("password")
#
# testrail_run_id = None
# case_id_map = {}  # {섹션 이름: [케이스ID 리스트]}
#
#
# def testrail_get(endpoint):
#     url = f"{TESTRAIL_BASE_URL}/index.php?/api/v2/{endpoint}"
#     r = requests.get(url, auth=(TESTRAIL_USER, TESTRAIL_TOKEN))
#     r.raise_for_status()
#     return r.json()
#
#
# def testrail_post(endpoint, payload=None, files=None):
#     url = f"{TESTRAIL_BASE_URL}/index.php?/api/v2/{endpoint}"
#     if files:
#         r = requests.post(url, auth=(TESTRAIL_USER, TESTRAIL_TOKEN), files=files)
#     else:
#         r = requests.post(url, auth=(TESTRAIL_USER, TESTRAIL_TOKEN), json=payload)
#     r.raise_for_status()
#     return r.json()
#
#
# @pytest.hookimpl(tryfirst=True)
# def pytest_sessionstart(session):
#     """
#     테스트 실행 시작 시:
#     1. section_id 기반으로 해당 섹션의 케이스 ID 가져오기
#     2. 그 케이스들로 Run 생성
#     """
#     global testrail_run_id, case_id_map
#     # 1. section_id 직접 사용
#     if testrail_run_id is not None:
#         print(f"[TestRail] 이미 Run(ID={testrail_run_id})이 존재합니다. 새 Run 생성 생략")
#         return
#     if not TESTRAIL_SECTION_ID:
#         raise RuntimeError("[TestRail] TESTRAIL_SECTION_ID가 정의되지 않았습니다.")
#     # 2. 섹션 내 케이스 가져오기
#     cases = testrail_get(
#         f"get_cases/{TESTRAIL_PROJECT_ID}&suite_id={TESTRAIL_SUITE_ID}&section_id={TESTRAIL_SECTION_ID}"
#     )
#     case_ids = [c["id"] for c in cases]
#     case_id_map[TESTRAIL_SECTION_ID] = case_ids
#     if not case_ids:
#         raise RuntimeError(f"[TestRail] section_id '{TESTRAIL_SECTION_ID}'에 케이스가 없습니다.")
#     # 3. Run 생성
#     run_name = f"AD Regression test mweb {datetime.now():%Y-%m-%d %H:%M:%S}"
#     payload = {
#         "suite_id": TESTRAIL_SUITE_ID,
#         "name": run_name,
#         "include_all": False,
#         "case_ids": case_ids
#     }
#     run = testrail_post(f"add_run/{TESTRAIL_PROJECT_ID}", payload)
#     testrail_run_id = run["id"]
#     print(f"[TestRail] section_id '{TESTRAIL_SECTION_ID}' Run 생성 완료 (ID={testrail_run_id})")
#
# @pytest.hookimpl(hookwrapper=True)
# def pytest_runtest_makereport(item, call):
#     """
#     각 테스트 결과를 TestRail에 기록 + 실패 시 스크린샷 첨부
#     INTERNALERROR 방지를 위해 모든 외부 호출은 try/except로 보호
#     """
#     outcome = yield
#     result = outcome.get_result()
#
#     try:
#         case_id = item.funcargs.get("case_id")
#         if case_id is None or testrail_run_id is None:
#             return
#
#         # Cxxxx → 숫자만 추출
#         if isinstance(case_id, str) and case_id.startswith("C"):
#             case_id = case_id[1:]
#         case_id = int(case_id)  # API는 int만 허용
#
#         screenshot_path = None
#         if result.when == "call":  # 실행 단계만 기록
#             if result.failed:
#                 status_id = 5  # Failed
#                 comment = f"테스트 실패: {result.longrepr}"
#
#                 # 스크린샷 시도
#                 try:
#                     page = item.funcargs.get("page")
#                     if page and not page.is_closed():
#                         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#                         screenshot_path = f"screenshots/{case_id}_{timestamp}.png"
#                         os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
#                         page.screenshot(path=screenshot_path, timeout=2000)
#                 except Exception as e:
#                     print(f"[WARNING] 스크린샷 실패: {e}")
#
#             elif result.skipped:
#                 status_id = 2  # Blocked
#                 comment = "테스트 스킵"
#             else:
#                 status_id = 1  # Passed
#                 comment = "테스트 성공"
#
#             # 실행 시간 기록
#             duration_sec = getattr(result, "duration", 0)
#             if duration_sec and duration_sec > 0.1:
#                 elapsed = f"{duration_sec:.1f}s"
#             else:
#                 elapsed = None
#
#             # stdout 로그 추가
#             stdout = getattr(item, "_stdout_capture", None)
#             if stdout:
#                 comment += f"\n\n--- stdout 로그 ---\n{stdout.strip()}"
#
#             # TestRail 기록
#             payload = {
#                 "status_id": status_id,
#                 "comment": comment,
#             }
#             if elapsed:
#                 payload["elapsed"] = elapsed
#
#             result_id = None
#             try:
#                 result_obj = testrail_post(
#                     f"add_result_for_case/{testrail_run_id}/{case_id}", payload
#                 )
#                 result_id = result_obj.get("id")
#             except Exception as e:
#                 print(f"[WARNING] TestRail 기록 실패: {e}")
#
#             # 스크린샷 첨부
#             if screenshot_path and result_id:
#                 try:
#                     with open(screenshot_path, "rb") as f:
#                         testrail_post(
#                             f"add_attachment_to_result/{result_id}",
#                             files={"attachment": f},
#                         )
#                 except Exception as e:
#                     print(f"[WARNING] TestRail 스크린샷 업로드 실패: {e}")
#
#             print(f"[TestRail] case {case_id} 결과 기록 ({status_id})")
#
#     except Exception as e:
#         # 어떤 이유로든 pytest 자체 중단 방지
#         print(f"[ERROR] pytest_runtest_makereport 처리 중 예외 발생 (무시됨): {e}")
#
# @pytest.hookimpl(trylast=True)
# def pytest_sessionfinish(session, exitstatus):
#     """
#     전체 테스트 종료 후 Run 닫기
#     """
#     global testrail_run_id
#     if testrail_run_id:
#         testrail_post(f"close_run/{testrail_run_id}", {})
#         print(f"[TestRail] Run {testrail_run_id} 종료 완료")
#
#     screenshots_dir = "screenshots"
#     if os.path.exists(screenshots_dir):
#         shutil.rmtree(screenshots_dir)  # 폴더 통째로 삭제
#         print(f"[CLEANUP] '{screenshots_dir}' 폴더 삭제 완료")
























# STATE_PATH = "state.json"
#
# @pytest.fixture(scope="session")
# def ensure_login_state():
#     """로그인 상태가 저장된 state.json을 보장하는 fixture"""
#     if not os.path.exists(STATE_PATH):
#         with sync_playwright() as p:
#             browser = p.chromium.launch(headless=False)
#             context = browser.new_context()
#             page = context.new_page()
#
#             page.goto("https://www.gmarket.co.kr")
#             page.click("text=로그인")
#             page.fill("#typeMemberInputId", "cease2504")
#             page.fill("#typeMemberInputPassword", "asdf12!@")
#             page.click("#btn_memberLogin")
#
#             # state.json 저장
#             context.storage_state(path=STATE_PATH)
#             browser.close()
#     return STATE_PATH
#
#
# @pytest.fixture(scope="function")
# def page(ensure_login_state):
#     """로그인 상태가 보장된 페이지 fixture"""
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)
#         context = browser.new_context(storage_state=ensure_login_state)
#         page = context.new_page()
#         yield page
#         context.close()
#         browser.close()
