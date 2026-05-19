from django.test import TestCase
from django.urls import reverse


class LandingPageViewTest(TestCase):
    def test_landing_page_without_cms_content(self):
        response = self.client.get(reverse("landing_page"))
        self.assertEqual(response.status_code, 200)

    def test_landing_page_at_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_landingpage_redirects_to_root(self):
        response = self.client.get("/landingpage/")
        self.assertRedirects(
            response, "/", status_code=301, fetch_redirect_response=False
        )
