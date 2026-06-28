from django.test import SimpleTestCase, Client


class ChroniclePageTests(SimpleTestCase):
    def test_chronicle_renders_inline_svg(self):
        response = Client().get("/chronicle/")
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn("<svg", html)
        self.assertIn('id="hero-coin"', html)
        self.assertIn('id="btc-logo-coin"', html)
        self.assertIn('id="eth-top"', html)
        self.assertIn('id="mine-rack"', html)
        self.assertNotIn("<img", html)
