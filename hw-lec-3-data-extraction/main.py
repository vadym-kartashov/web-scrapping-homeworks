import re
import lxml.etree as etree


def extract_dates(doc: str):
    date_pattern = r"""
    \b(                     # Start of word boundary
    (?:                     # Non-capturing group for different date formats
        \d{2}[/-]\d{2}[/-]\d{4}     # Matches MM/DD/YYYY or MM-DD-YYYY
      | \d{4}[./]\d{2}[./]\d{2}     # Matches YYYY.MM.DD or YYYY/MM/DD
      | \b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s\d{1,2},\s\d{4}\b
    )                       # End of non-capturing group
    \b)                     # End of word boundary
    """
    return re.findall(date_pattern, doc, re.VERBOSE)


def extract_emails(doc: str):
    email_pattern = r'''
    [a-zA-Z0-9._%+-]+       # Username part: Alphanumeric characters and special characters
    @                       # At symbol
    [a-zA-Z0-9.-]+          # Domain name part: Alphanumeric characters, dot and hyphen
    \.[a-zA-Z]{2,}          # Top level domain: Dot followed by 2 or more letters
    '''
    return re.findall(email_pattern, doc, re.VERBOSE)


def find_by_html_xpath(html: str, xpath: str) -> list:
    tree = etree.HTML(html)
    return tree.xpath(xpath)


def find_single_element_by_html_xpath(html: str, xpath: str):
    elements = find_by_html_xpath(html, xpath)
    if len(elements) != 1:
        raise ValueError(f"Expected exactly one element for XPath '{xpath}', but found {len(elements)}")
    return elements[0]


def read_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def validate_search_form_elements(title_element, region_element, search_element):
    validate_equal(title_element.attrib.get('placeholder'), 'Cargo, palavras-chave ou empresa')
    validate_equal(region_element.attrib.get('placeholder'), 'Cidade, estado, região ou “remoto”')
    validate_equal(search_element.text, 'Achar vagas')


def validate_equal(actual, expected):
    if actual != expected:
        raise AssertionError(f"Expected '{expected}', but got '{actual}'")


def test_find_by_html_xpath() -> None:
    html = read_file('indeed.html')

    # Option 1: Directly through id and values
    title_element = find_single_element_by_html_xpath(html, "//input[@id='text-input-what']")
    region_element = find_single_element_by_html_xpath(html, "//input[@id='text-input-where']")
    search_element = find_single_element_by_html_xpath(html, "//button[@type='submit' and text()='Achar vagas']")
    validate_search_form_elements(title_element, region_element, search_element)

    # Option 2: Using common element
    form_xpath = "//form[@id='jobsearch']"
    inputs = find_by_html_xpath(html, f"{form_xpath}//input|{form_xpath}//button")
    if len(inputs) < 3:
        raise ValueError("Expected at least three elements (title, region, search) in the form.")
    title_element, region_element, search_element = inputs[0], inputs[1], inputs[2]
    validate_search_form_elements(title_element, region_element, search_element)


def test_extract_with_regex():
    doc = read_file('regex-doc.txt')
    dates = extract_dates(doc)
    emails = extract_emails(doc)
    validate_equal(len(dates), 8)
    validate_equal(len(emails), 8)


if __name__ == '__main__':
    test_find_by_html_xpath()
    test_extract_with_regex()
