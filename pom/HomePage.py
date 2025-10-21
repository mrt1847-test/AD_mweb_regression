import time

from playwright.sync_api import Page, expect


class HomePage():
    def __init__(self, page):
        self.page = page

    def search_product(self, keyword: str):
        self.page.fill("input[name='keyword']", keyword)
        self.page.press("input[name='keyword']", "Enter")

    def home_module_by_title(self, module_title):
        """
        특정 모듈의 타이틀 텍스트를 통해 해당 모듈 노출 확인하고 그 모듈 엘리먼트를 반환
        :param (str) module_title : 모듈 타이틀
        :return: 해당 모듈 element
        :example:
        """
        runtext = f'HOME > {module_title}모듈 노출 확인'
        print("#", runtext, "시작")
        child = self.page.get_by_text(module_title).first
        child.scroll_into_view_if_needed()
        #self.page.wait_for_timeout(500)

        parent = child.locator("xpath=../..")
        expect(parent).to_be_visible()
        print("#", runtext, "종료")

        return parent


    def assert_item_in_module(self, module_title):
        """
        특정 모듈의 타이틀 텍스트를 통해 해당 모듈내 상품 노출 확인하고 그상품번호 반환
        :param (str) module_title : 모듈 타이틀
        :return: 해당 모듈 노출 상품 번호
        :example:
        """
        runtext = f'HOME > {module_title}모듈내 상품 노출 확인'
        print("#", runtext, "시작")
        child = self.page.get_by_text(module_title)
        parent = child.locator("xpath=../..")
        target = parent.locator("ul li a").nth(0)
        target.scroll_into_view_if_needed()
        expect(target).to_be_visible()
        goodscode = target.get_attribute("data-montelena-goodscode")
        print("#", runtext, "종료")

        return goodscode


    def check_rvi_vt_cpc_ad_tag(self, parent):
        """
        특정 모듈의 광고 태그 노출 확인 (캐러셀 4페이지, 페이지당 최대 10개 상품)
        :param (element) parent: 모듈의 element
        :return (dict): {"goodscode": (str) 광고상품 코드 (없으면 None),"target": (Locator) 해당 상품 로케이터 (없으면 None)}
        """
        runtext = f'HOME > RVI_VT_CPC 광고상품 광고태그 확인'
        print("#", runtext, "시작")

        total_pages = 4
        found_page = None
        ad_products = []  # 광고 상품 정보 저장

        for page_index in range(total_pages):
            print(f"\n=== {page_index + 1}번째 페이지 확인 ===")

            # 현재 페이지의 상품 목록
            products = parent.locator(f'ul li a[data-montelena-tabasn="{page_index + 1}"]')
            total_count = products.count()
            check_count = min(total_count, 10)  # ✅ 최대 10개까지만 검사

            print(f"현재 페이지 상품 수: {total_count} (검사 대상: {check_count}개)")

            page_ads = []  # 이 페이지의 광고 상품들

            for i in range(check_count):
                product = products.nth(i)
                ad_tag_locator = product.locator("span.gds-item-card__ad-label")

                if ad_tag_locator.count() > 0:
                    goodscode = product.get_attribute("data-montelena-goodscode")
                    page_ads.append({"goodscode": goodscode, "target": product})
                    print(f"{page_index * 10 + i + 1}번째 ✅ 광고 태그 존재 (상품코드: {goodscode})")
                else:
                    print(f"{page_index * 10 + i + 1}번째 ❌ 광고 태그 없음")

            # ✅ 광고상품 발견 시 탐색 종료
            if page_ads:
                found_page = page_index + 1
                ad_products = page_ads
                print(f"🎯 {found_page}번째 페이지에서 광고상품 발견! 탐색 종료.")
                break

            # 다음 페이지로 이동
            if page_index < total_pages - 1:
                next_btn = parent.locator("button.gds-action-button:visible").first
                if next_btn.count() > 0 and next_btn.is_visible():
                    next_btn.click()
                    self.page.wait_for_timeout(2000)
                else:
                    print("다음 페이지 버튼이 없어 탐색을 종료합니다.")
                    break

        # 결과 처리
        if not ad_products:
            print("\n⚠️ 광고 태그가 붙은 상품이 없습니다. 클릭할 상품이 없습니다.")
            return {"goodscode": None, "target": None}

        # 발견된 페이지의 마지막 광고상품 선택
        last_ad = ad_products[-1]
        goodscode = last_ad["goodscode"]
        target = last_ad["target"]

        print(f"\n👉 선택된 광고 상품 코드: {goodscode} (페이지 {found_page})")
        print("#", runtext, "종료")

        return {"goodscode": goodscode, "target": target}


    def click_goods(self, goodscode, target):
        """
        특정 상품 번호 아이템 클릭 및 이동 확인
        :param (str) goodscode: 상품 번호
        :param (Locator) target: 상품 로케이터
        :return (str) url: 클릭한 상품 URL
        :example:
        """

        runtext = f'HOME > {goodscode} 상품 클릭'
        print("#", runtext, "시작")

        # # href 미리 추출 (혹시 클릭 후 URL이 바로 안 바뀌는 경우 대비)
        # try:
        #     href = target.get_attribute("href")
        # except Exception:
        #     href = None
        #
        # try:
        #     # 스크롤해서 보이게 한 뒤 클릭
        #     target.scroll_into_view_if_needed()
        #     target.click(timeout=10000)
        #     self.page.wait_for_timeout(3000)  # 페이지 로딩 대기
        # except Exception as e:
        #     print(f"❌ 상품 클릭 중 오류 발생: {e}")
        #     raise


        target.click()
        url = self.page.url
        print(f"현재 URL: {url}")

        # URL 검증 — goodscode 또는 href 기반
        runtext = f'HOME > {goodscode} 상품 이동확인'
        print("#", runtext, "시작")
        assert goodscode in url, f"상품 번호 {goodscode}가 URL에 포함되어야 합니다"
        print("#", runtext, "종료")

        return url
