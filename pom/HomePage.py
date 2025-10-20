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
        child = self.page.get_by_text(module_title)
        child.scroll_into_view_if_needed()

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
       특정 모듈의 광고 태그 노출 확인 (캐러셀 4페이지, 페이지당 10개 상품)
       :param (element) parent : 모듈의 element
       :return: 해당 모듈 노출 광고 상품 번호, 해당 상품 로케이터
       :example:
       """
        runtext = f'HOME > RVI_VT_CPC 광고상품 광고태그 확인'
        print("#", runtext, "시작")

        total_pages = 4
        ad_count = 0
        goodscode, target = None, None

        for page_index in range(total_pages):
            print(f"\n=== {page_index + 1}번째 페이지 확인 ===")

            # data-montelena-tabasn 기반으로 현재 페이지 상품만 가져오기
            products = parent.locator(f'ul li a[data-montelena-tabasn="{page_index + 1}"]')

            count = products.count()
            print(f"현재 페이지 상품 수: {count}")

            for i in range(count):
                product = products.nth(i)
                ad_tag_locator = product.locator("span.gds-item-card__ad-label")

                if ad_tag_locator.count() > 0:
                    ad_count += 1
                    goodscode = product.get_attribute("data-montelena-goodscode")
                    target = product
                    print(f"{page_index * 10 + i + 1}번째 ✅ 광고 태그 존재")
                else:
                    print(f"{page_index * 10 + i + 1}번째 ❌ 광고 태그 없음")

            # 마지막 그룹이 아니라면 버튼 클릭
            if page_index < total_pages - 1:
                next_btn = parent.locator("button.gds-action-button:visible").first
                next_btn.click()
                self.page.wait_for_timeout(2000)

        print(f"\n총 광고태그가 있는 상품 개수: {ad_count} / {total_pages * 10}")
        print("#", goodscode)
        print("#", runtext, "종료")

        return {"goodscode": goodscode, "target": target}

