import bs4


def html_to_text(html):
    soup = bs4.BeautifulSoup(html, 'lxml')
    for s in ['#engadget-article-footer', '.reader-header']:
        for e in soup.select(s):
            e.decompose()
    return soup.get_text(' ')


def clean_text(text):
    """Preliminary text cleaning"""
    lines = text.split('\n')

    # Drop non-sentences (ones that don't have a dot in them), while relying on Reader View
    # plug-in HTML structure:
    lines = [line for line in lines if len(line) > 0 and '.' in line]

    return ' '.join(lines)


def html_to_clean_text(html):
    return clean_text(html_to_text(html))
