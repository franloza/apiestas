def extract_with_css(response, query):
    string = response.css(query).extract_first()
    if string is not None:
        return string.strip()