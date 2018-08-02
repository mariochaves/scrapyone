import scrapy
import logging
import urllib.parse as ul
import re
import email
import smtplib


class BrickSetSpider(scrapy.Spider):
    name = "spider"
    allowed_domains = ["www.gympass.com"]
    start_urls = ['https://www.gympass.com/']

    def parse(self, response):
        return scrapy.Request('https://www.gympass.com/pessoas/entrar?registration_type=reset',
                              callback=self.parse_loggin)

    def parse_loggin(self, response):
        self.log(response.text)
        person_search_info = '09812092463'
        person_type = 'b2b'
        commit = 'Continuar'
        utf8 = response.xpath('//input[@name="utf8"]/@value').get()
        authenticity_token = response.xpath('//input[@name="authenticity_token"]/@value').get()
        authenticity_token = ul.quote(authenticity_token)
        self.log(authenticity_token)
        start_url = 'https://www.gympass.com/pessoas/entrar'
        url = start_url + '?utf8=%E2%9C%93&authenticity_token=' + authenticity_token + '&person_search_info=09812092463&person_type=b2b&commit=Continuar'

        return scrapy.Request(url,
                              callback=self.parse_senha)

    def parse_senha(self, response):
        utf8 = '%E2%9C%93'
        authenticity_token = response.xpath('//input[@name="authenticity_token"]/@value').get()
        url = 'https://www.gympass.com/pessoas/entrar'
        self.log(url)

        formdata = {
            'utf8': '✓',
            'person[email]': 'mario.chaves@live.com',
            'person[password]': 'Gym05194310',
            'person[remember_me]': '0',
            'person[remember_me]': '1',
            'authenticity_token': authenticity_token,
            'button': ''
        }

        yield scrapy.FormRequest(
            url='https://www.gympass.com/pessoas/entrar',
            callback=self.parse_tamoDentro, formdata=formdata,
            method='POST'
        )

    def parse_tamoDentro(self, response):
        return scrapy.Request('https://www.gympass.com/checkin',
                              callback=self.parse_checkin)

    def parse_checkin(self, response):
        patternRegToken = r'"code.*?(\d{10})'
        regToken = re.compile(patternRegToken)
        token = regToken.search(response.text).group(1)

        self.send_email('mario.chaves@live.com', 'mario.chaves@live.com', f'Token - Mário Chaves - {token}', '')
        return {'token': token}

    @staticmethod
    def send_email(de, para, assunto, mensagem):
        msg = email.message_from_string('warning')
        msg['From'] = de
        msg['To'] = para
        msg['Subject'] = assunto
        # msg['Body'] = mensagem

        s = smtplib.SMTP("smtp.live.com", 587)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(msg['From'], '@Qblackstyle171943')
        s.sendmail(msg['From'], msg['To'], msg.as_string())
        s.quit()
