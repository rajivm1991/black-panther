from bs4 import BeautifulSoup
from . import parser


def get_site_meta(url, page_source):
    meta = {'url': url}

    url_split = url.split('/')
    domain = url_split[2]
    if 'linkedin' in domain:
        meta['site'] = 'linkedin'

        soup = BeautifulSoup(page_source, features='html.parser')
        page_key = soup.find(name='meta', attrs={'name': 'pageKey'})
        if page_key:
            meta['page_key'] = page_key['content']

        profile_pic = soup.find(name='img', attrs={'class': 'nav-item__profile-member-photo'})
        meta['logged_in'] = profile_pic is not None

        # for tag in soup.find_all(name='meta'):
        #     print(tag)

    return meta


def get_parser(meta):
    if meta.get('site') == 'linkedin':
        if meta.get('page_key') == 'public_profile_v3_desktop':
            return parser.LinkedinPublicProfileV3Desktop
        elif meta.get('page_key') == 'd_org_guest_company_overview':
            return parser.LinkedinCompanyOverview
