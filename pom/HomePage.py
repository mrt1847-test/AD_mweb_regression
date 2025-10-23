import time

from playwright.sync_api import Page, expect


class HomePage():
    def __init__(self, page):
        self.page = page

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

    def check_vip_product_in_rvi_vt_cpc_module(self, parent, goodscode):
        """
        특정 모듈의 좌측에 특정 상품이 노출되는지 확인
        :param parent : 해당 모듈의 부모 element
        :param goodscode: 노출을 검증할 상품번호
        :return: None
        :example:
        """
        runtext = f'HOME > {goodscode} 상품 rvi_vt_cpc 모듈 타이틀 좌측 노출 확인'
        print("#", runtext, "시작")

        product_locator = parent.locator(f'[data-montelena-goodscode="{goodscode}"]').first
        expect(product_locator).to_be_visible()

        print(f"✅ 상품({goodscode})이 rvi_vt_cpc모듈 타이틀 좌측에 노출됨")
        print("#", runtext, "종료")


    def check_rvi_vt_cpc_ad_tag(self, parent, max_pages=4):
        """
        특정 모듈의 광고 태그 노출 확인 (캐러셀 4페이지, 페이지당 최대 10개 상품)
        :param (Locator) parent: 광고 모듈의 루트 element
        :param (int) max_pages: 탐색할 최대 페이지 수 (기본값: 4)
        :return (dict): {"goodscode": (str)   (없으면 None), "target": (Locator) 상품 Locator (없으면 None)}
        :example:
        """
        print("# HOME > RVI_VT_CPC 광고상품 광고태그 확인 시작")

        for page_index in range(max_pages):
            print(f"\n=== {page_index + 1}번째 페이지 확인 ===")

            products = parent.locator(f'ul li a[data-montelena-tabasn="{page_index + 1}"]')
            total_count = products.count()

            for i in range(total_count):
                product = products.nth(i)
                ad_tag = product.locator("span.gds-item-card__ad-label")

                if ad_tag.count() > 0:
                    goodscode = product.get_attribute("data-montelena-goodscode")
                    print(f"✅ 광고 태그 발견: 상품코드={goodscode} (페이지 {page_index + 1})")
                    return {"goodscode": goodscode, "target": product}

            # 다음 페이지 이동
            next_btn = parent.locator("button.gds-action-button:visible").first
            if next_btn.count() > 0 and next_btn.is_visible():
                next_btn.click()
                self.page.wait_for_timeout(2000)
                print("다음 페이지로 이동합니다 (마지막 페이지면 첫 페이지로 순환).")
            else:
                print("⚠️ 다음 페이지 버튼을 찾지 못했습니다. 탐색을 종료합니다.")
                break

        print("⚠️ 광고 태그가 붙은 상품이 없습니다.")
        return {"goodscode": None, "target": None}


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

        target.click()
        self.page.wait_for_url(lambda url: goodscode in url, timeout=10000)  # 10초 대기
        url = self.page.url
        print(f"현재 URL: {url}")

        # URL 검증 — goodscode 또는 href 기반
        runtext = f'HOME > {goodscode} 상품 이동확인'
        print("#", runtext, "시작")
        assert goodscode in url, f"상품 번호 {goodscode}가 URL에 포함되어야 합니다"
        print("#", runtext, "종료")

        return url
