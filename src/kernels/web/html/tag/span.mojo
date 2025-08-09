from python import Python

fn web_html_tag_span_kernel(attributes: String, children: String) -> String:
    """
    Render a <span> with attributes and children

    Args:
        attributes: HTML attributes as string
        children: Inner HTML content

    Returns:
        Rendered HTML string
    """
    var result = String("<span")
    if len(attributes) > 0:
        result += " " + attributes
    result += ">"
    result += children
    result += "</span>"
    return result

fn main():
    # Example usage
    let attrs = "class='container' id='main'"
    let content = "Hello, World!"
    let html = web_html_tag_span_kernel(attrs, content)
    print(html)