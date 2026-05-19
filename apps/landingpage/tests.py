from django.test import TestCase
from django.urls import reverse


class LandingPageViewTest(TestCase):
    def test_landing_page_without_cms_content(self):
        response = self.client.get(reverse("landing_page"))
        self.assertEqual(response.status_code, 200)
