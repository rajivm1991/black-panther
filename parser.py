import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

months = {
    'January': '01',
    'February': '02',
    'March': '03',
    'April': '04',
    'May': '05',
    'June': '06',
    'July': '07',
    'August': '08',
    'September': '09',
    'October': '10',
    'November': '11',
    'December': '12'
}


def parse_date_text(text):
    month, year = text.split(' ')
    return '-'.join([
        year,
        months[month],
        '01'
    ])


def parse_address_text(text):
    logger.debug('text = %s' % text)
    # city, country = text.split(', ')
    address = {}
    # city and address.setdefault('city', city)
    # country and address.setdefault('country', country)
    return address


class BaseParser(object):
    soup = None

    def __init__(self, page_source):
        self.soup = BeautifulSoup(page_source, features="html.parser")


class LinkedinPublicProfileV3Desktop(BaseParser):
    def parse_name(self, section):
        return section and section.get_text()

    def parse_headline(self, section: BeautifulSoup):
        return section and section.get_text()

    def parse_summary(self, section: BeautifulSoup):
        description = section and section.find(name='div', attrs={'class': 'description'})  # type: BeautifulSoup
        # return description and '<br>'.join([c.prettify() for c in description.contents])
        return description and description.prettify()

    def parse_experience(self, section: BeautifulSoup):
        parsed_employer = []
        for position_group_li in section.find_all(name='li', attrs={'class': 'position-group'}):

            multi_position_ul = position_group_li.find(name='ul', attrs={'class': 'positions'})
            single_position_div = position_group_li.find(name='div', attrs={'class': 'position'})

            if multi_position_ul:
                e_company_logo = position_group_li.find(name='a', attrs={'data-tracking-control-name': 'pp_company_logo'})
                company_link = e_company_logo and e_company_logo.attrs['href']

                for single_position_li in multi_position_ul.find_all(name='li', attrs={'class': 'position--bullet'}):
                    parsed_exp = {}

                    e_role = single_position_li.find(name='h5', attrs={'class': 'item-title--small'})
                    if e_role:
                        role = e_role.get_text()
                        role and parsed_exp.setdefault('role', role)

                    e_company_name = single_position_li.find(name='h6', attrs={'class': 'item-title--small'})
                    if e_company_name:
                        company_name = e_company_name.get_text()
                        company_name and parsed_exp.setdefault('company_name', company_name)

                    company_link and parsed_exp.setdefault('company_link', company_link)

                    date_span = single_position_li.find(name='span', attrs={'class': 'date-range'})
                    for i, d in enumerate(date_span.find_all(name='time')):
                        dt = d.get_text()
                        dt and parsed_exp.setdefault(
                            ('from_date', 'to_date')[i],
                            parse_date_text(dt)
                        )
                    if 'Present' in date_span.get_text():
                        parsed_exp['is_current'] = True

                    e_address = single_position_li.find(name='div', attrs={'class': 'item-title--small item-title--muted'})
                    if e_address:
                        at = e_address.get_text()
                        address = at and parse_address_text(at)
                        address and parsed_exp.setdefault('address', address)

                    e_description = single_position_li.find(name='p', attrs={'class': 'item-body'})
                    if e_description:
                        # description = '<br>'.join([c.prettify() for c in e_description.contents])
                        description = e_description.prettify()
                        description and parsed_exp.setdefault('description', description)

                    if parsed_exp:
                        parsed_employer.append(parsed_exp)

            elif single_position_div:
                parsed_exp = {}

                e_role = single_position_div.find(name='h4', attrs={'class': 'item-title--large'})
                if e_role:
                    role = e_role.get_text()
                    role and parsed_exp.setdefault('role', role)

                e_company_name = single_position_div.find(name='h5', attrs={'class': 'item-title--small'})
                if e_company_name:
                    company_name = e_company_name.get_text()
                    company_name and parsed_exp.setdefault('company_name', company_name)

                e_company_logo = single_position_div.find(name='a', attrs={'data-tracking-control-name': 'pp_company_logo'})
                if e_company_logo:
                    company_link = e_company_logo.attrs['href']
                    company_link and parsed_exp.setdefault('company_link', company_link)

                date_span = single_position_div.find(name='span', attrs={'class': 'date-range'})
                for i, d in enumerate(date_span.find_all(name='time')):
                    dt = d.get_text()
                    dt and parsed_exp.setdefault(
                        ('from_date', 'to_date')[i],
                        parse_date_text(dt)
                    )
                if 'Present' in date_span.get_text():
                    parsed_exp['is_current'] = True

                e_address = single_position_div.find(name='div', attrs={'class': 'item-title--small item-title--muted'})
                if e_address:
                    at = e_address.get_text()
                    address = at and parse_address_text(at)
                    address and parsed_exp.setdefault('address', address)

                e_description = single_position_div.find(name='div', attrs={'class': 'item-body'})
                if e_description:
                    # description = '<br>'.join([c.prettify() for c in e_description.contents])
                    description = e_description.prettify()
                    description and parsed_exp.setdefault('description', description)

                if parsed_exp:
                    parsed_employer.append(parsed_exp)

        return parsed_employer

    def parse(self):
        soup = self.soup

        parsed_data = {}

        # EMPLOYER
        section = soup.find(name='section', attrs={'id': 'experience'})
        parsed_experience = self.parse_experience(section)
        parsed_experience and parsed_data.setdefault('experience', parsed_experience)

        # NAME
        section = soup.find(name='h1', attrs={'id': 'name'})
        parsed_name = self.parse_name(section)
        parsed_name and parsed_data.setdefault('name', parsed_name)

        # HEADLINE
        section = soup.find(name='p', attrs={'class': 'headline'})
        parsed_headline = self.parse_headline(section)
        parsed_headline and parsed_data.setdefault('headline', parsed_headline)

        # ADDRESS & INDUSTRY
        section = soup.find(name='dl', attrs={'id': 'demographics'})
        keys, values = [], []
        for n, tag in enumerate(section.childGenerator()):
            [keys, values][n % 2].append(tag.get_text())
        temp = dict(zip(keys, values))
        industry = temp.get('Industry')
        industry and parsed_data.setdefault('industry', industry)
        location = temp.get('Location')
        location and parsed_data.setdefault('address', location)

        # SUMMARY
        section = soup.find(name='section', attrs={'id': 'summary'})
        parsed_summary = self.parse_summary(section)
        parsed_summary and parsed_data.setdefault('profile_summary', parsed_summary)

        return parsed_data


class LinkedinCompanyOverview(BaseParser):
    def parse(self):
        soup = self.soup

        parsed_data = {}

        section = soup.find(name='h1', attrs={'class': 'top-card__title'})
        section and parsed_data.setdefault('company_name', section.get_text())

        section = soup.find(name='div', attrs={'class': 'top-card__information'})
        if section:
            for c in section.contents:
                print(c)
                text = c.get_text()
                if c.get('itemprop') == 'address':
                    parsed_data.setdefault('address', text)
                elif 'followers' in text:
                    parsed_data.setdefault('followers', int(text.split()[0].replace(',', '')))
                else:
                    parsed_data.setdefault('category', text)

        section = soup.find(name='div', attrs={'class': 'top-card__employees'})

        return parsed_data
